"""
Модуль для парсинга вакансий с веб-страниц
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobParser:
    """Парсер вакансий с различных сайтов"""
    
    def __init__(self):
        # Улучшенные заголовки для обхода блокировок
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        # Настройка сессии для сохранения cookies
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def parse_from_file(self, file_path: str) -> Dict[str, any]:
        """
        Парсит вакансию из текстового файла
        
        Args:
            file_path: Путь к файлу с текстом вакансии
        
        Returns:
            Dict с полями: title, description, requirements, skills, etc.
        """
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text or len(text.strip()) < 50:
                raise ValueError("Файл вакансии слишком короткий или пустой")
            
            logger.info(f"Парсинг вакансии из файла: {file_path}")
            
            # Извлекаем информацию из текста
            parsed_data = {
                'title': self._extract_title_from_text(text),
                'text': text,
                'description': text[:1000],  # Первые 1000 символов как описание
                'requirements': self._extract_requirements(text),
                'skills': self._extract_skills(text),
                'experience_required': self._extract_experience_requirement(text),
                'education_required': self._extract_education_requirement(text),
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге файла вакансии: {str(e)}")
            raise ValueError(f"Ошибка при чтении файла вакансии: {str(e)}")
    
    def _extract_title_from_text(self, text: str) -> str:
        """Извлекает заголовок вакансии из текста"""
        # Ищем заголовок в первых строках
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # Проверяем, не является ли это заголовком
                if any(keyword in line.lower() for keyword in ['вакансия', 'требуется', 'ищем', 'ищемся', 'vacancy', 'position']):
                    return line
                # Если строка выглядит как заголовок (короткая, без точек)
                if not line.endswith('.') and len(line.split()) < 15:
                    return line
        
        # Если не нашли, берем первую строку
        first_line = text.split('\n')[0].strip()
        return first_line[:100] if first_line else "Вакансия"
    
    def parse(self, url: str) -> Dict[str, any]:
        """
        Парсит вакансию по URL
        
        Args:
            url: URL вакансии (например, с hh.ru, habr.com и т.д.)
        
        Returns:
            Dict с полями: title, description, requirements, skills, etc.
        
        Raises:
            ValueError: При ошибках загрузки или парсинга
        """
        try:
            # Валидация URL
            if not url or not url.startswith(('http://', 'https://')):
                raise ValueError("Некорректный URL. Убедитесь, что ссылка начинается с http:// или https://")
            
            logger.info(f"Парсинг вакансии: {url}")
            
            # Загружаем страницу с обработкой редиректов
            response = self.session.get(
                url, 
                timeout=15,
                allow_redirects=True,
                verify=True  # Проверка SSL сертификатов
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Проверяем кодировку
            if response.encoding is None or response.encoding.lower() == 'iso-8859-1':
                response.encoding = 'utf-8'
            
            html = response.text
            
            # Проверяем, что получили контент
            if not html or len(html) < 100:
                raise ValueError("Страница пуста или содержит слишком мало контента. Возможно, требуется авторизация или сайт блокирует автоматические запросы.")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Специальная обработка для HeadHunter
            if 'hh.ru' in url:
                return self._parse_hh_vacancy(soup, url, html)
            
            # Стандартная обработка для других сайтов
            # Удаляем скрипты и стили
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Извлекаем текст
            text = soup.get_text()
            # Очищаем текст
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Проверяем, что текст не пустой
            if not text or len(text) < 50:
                raise ValueError("Не удалось извлечь текст со страницы. Возможно, контент загружается через JavaScript.")
            
            # Пытаемся найти заголовок
            title = self._extract_title(soup, text)
            
            # Извлекаем структурированную информацию
            parsed_data = {
                'url': url,
                'title': title,
                'text': text,
                'requirements': self._extract_requirements(text),
                'skills': self._extract_skills(text),
                'experience_required': self._extract_experience_requirement(text),
                'education_required': self._extract_education_requirement(text),
            }
            
            logger.info(f"Успешно распарсена вакансия: {title}")
            return parsed_data
            
        except requests.exceptions.Timeout:
            raise ValueError("Превышено время ожидания ответа от сервера. Попробуйте еще раз.")
        except requests.exceptions.ConnectionError:
            raise ValueError("Ошибка подключения к серверу. Проверьте интернет-соединение и правильность ссылки.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("Доступ запрещен. Сайт может блокировать автоматические запросы. Попробуйте другую ссылку.")
            elif e.response.status_code == 404:
                raise ValueError("Страница не найдена. Проверьте правильность ссылки на вакансию.")
            else:
                raise ValueError(f"Ошибка HTTP {e.response.status_code}: {str(e)}")
        except requests.RequestException as e:
            raise ValueError(f"Ошибка при загрузке страницы: {str(e)}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге: {str(e)}", exc_info=True)
            raise ValueError(f"Ошибка при парсинге вакансии: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup, text: str) -> str:
        """Извлекает заголовок вакансии"""
        # Пробуем найти в различных тегах
        title_tags = soup.find_all(['h1', 'h2', 'title'])
        for tag in title_tags:
            title_text = tag.get_text().strip()
            if title_text and len(title_text) < 200:
                return title_text
        
        # Если не нашли, берем первые слова из текста
        words = text.split()[:10]
        return ' '.join(words)
    
    def _extract_requirements(self, text: str) -> str:
        """Извлекает требования из текста"""
        # Ищем ключевые слова
        requirement_keywords = [
            'требования', 'requirements', 'обязательно', 'необходимо',
            'нужно', 'должен', 'должна', 'must have', 'required'
        ]
        
        text_lower = text.lower()
        lines = text.split('\n')
        requirement_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in requirement_keywords):
                # Берем текущую строку и несколько следующих
                requirement_lines.extend(lines[i:i+5])
        
        if requirement_lines:
            return '\n'.join(requirement_lines[:20])
        
        # Если не нашли специальный раздел, возвращаем весь текст
        return text[:2000]  # Ограничиваем длину
    
    def _extract_skills(self, text: str) -> List[str]:
        """Извлекает требуемые навыки с улучшенным поиском"""
        # Используем тот же словарь навыков, что и в resume_parser
        from resume_parser import ResumeParser
        temp_parser = ResumeParser()
        return temp_parser._extract_skills(text)
    
    def _extract_experience_requirement(self, text: str) -> str:
        """Извлекает требования к опыту работы"""
        # Ищем паттерны типа "3+ года", "от 2 лет" и т.д.
        patterns = [
            r'(\d+)\+?\s*(год|лет|года|years?|year)',
            r'от\s+(\d+)\s*(год|лет|года)',
            r'(\d+)\s*-\s*(\d+)\s*(год|лет|года)',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                return f"Требуется опыт: {matches[0]}"
        
        return ""
    
    def _extract_education_requirement(self, text: str) -> str:
        """Извлекает требования к образованию"""
        education_keywords = [
            'высшее образование', 'higher education', 'университет',
            'бакалавр', 'магистр', 'bachelor', 'master', 'degree'
        ]
        
        text_lower = text.lower()
        for keyword in education_keywords:
            if keyword in text_lower:
                return f"Требуется: {keyword}"
        
        return ""
    
    def _parse_hh_vacancy(self, soup: BeautifulSoup, url: str, html: str) -> Dict[str, any]:
        """
        Специальный парсер для вакансий HeadHunter
        
        Args:
            soup: BeautifulSoup объект
            url: URL вакансии
            html: HTML контент
        
        Returns:
            Dict с распарсенными данными
        """
        try:
            # Удаляем ненужные элементы
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Пытаемся найти основной контент вакансии
            # HeadHunter использует различные селекторы
            content_selectors = [
                {'data-qa': 'vacancy-description'},
                {'class': 'vacancy-description'},
                {'class': 'g-user-content'},
                {'id': 'vacancy-description'},
            ]
            
            text = ""
            title = ""
            
            # Ищем описание вакансии
            for selector in content_selectors:
                content_div = soup.find(attrs=selector)
                if content_div:
                    text = content_div.get_text()
                    break
            
            # Если не нашли через селекторы, используем общий подход
            if not text or len(text) < 50:
                # Ищем все div с классом, содержащим "description" или "content"
                content_divs = soup.find_all('div', class_=re.compile(r'description|content|text', re.I))
                for div in content_divs:
                    div_text = div.get_text().strip()
                    if len(div_text) > 100:  # Берем только достаточно большие блоки
                        text += div_text + "\n"
            
            # Если все еще нет текста, используем весь body
            if not text or len(text) < 50:
                body = soup.find('body')
                if body:
                    text = body.get_text()
            
            # Очищаем текст
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Ищем заголовок вакансии
            title_selectors = [
                {'data-qa': 'vacancy-title'},
                {'class': re.compile(r'title|vacancy-title', re.I)},
                'h1',
            ]
            
            for selector in title_selectors:
                if isinstance(selector, str):
                    title_tag = soup.find(selector)
                else:
                    title_tag = soup.find(attrs=selector)
                
                if title_tag:
                    title = title_tag.get_text().strip()
                    if title and len(title) < 200:
                        break
            
            # Если заголовок не найден, используем стандартный метод
            if not title:
                title = self._extract_title(soup, text)
            
            # Проверяем, что получили достаточно данных
            if not text or len(text) < 50:
                raise ValueError("Не удалось извлечь описание вакансии с HeadHunter. Возможно, страница требует авторизации или использует динамическую загрузку контента.")
            
            # Извлекаем структурированную информацию
            parsed_data = {
                'url': url,
                'title': title,
                'text': text,
                'requirements': self._extract_requirements(text),
                'skills': self._extract_skills(text),
                'experience_required': self._extract_experience_requirement(text),
                'education_required': self._extract_education_requirement(text),
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге HeadHunter: {str(e)}")
            # Пробуем стандартный парсинг как fallback
            raise ValueError(f"Ошибка при парсинге вакансии HeadHunter: {str(e)}")

