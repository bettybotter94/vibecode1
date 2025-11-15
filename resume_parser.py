"""
Модуль для парсинга резюме из различных форматов
"""
import os
import re
from typing import Dict, List
import PyPDF2
from docx import Document


class ResumeParser:
    """Парсер резюме из PDF, DOCX и TXT файлов"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """
        Парсит резюме и извлекает ключевую информацию
        
        Returns:
            Dict с полями: text, skills, experience, education, etc.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self._parse_pdf(file_path)
        elif file_ext == '.docx':
            text = self._parse_docx(file_path)
        elif file_ext == '.txt':
            text = self._parse_txt(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_ext}")
        
        # Извлекаем структурированную информацию
        parsed_data = {
            'text': text,
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'languages': self._extract_languages(text),
        }
        
        return parsed_data
    
    def _parse_pdf(self, file_path: str) -> str:
        """Парсит PDF файл"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"Ошибка при чтении PDF: {str(e)}")
        return text
    
    def _parse_docx(self, file_path: str) -> str:
        """Парсит DOCX файл"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Ошибка при чтении DOCX: {str(e)}")
        return text
    
    def _parse_txt(self, file_path: str) -> str:
        """Парсит TXT файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise ValueError(f"Ошибка при чтении TXT: {str(e)}")
        return text
    
    def _extract_skills(self, text: str) -> List[str]:
        """Извлекает навыки из текста с улучшенным поиском и проверкой контекста"""
        # Расширенный список навыков с синонимами
        skills_dict = {
            # Языки программирования
            'Python': ['python', 'python3', 'python 3', 'py', 'django', 'flask', 'fastapi'],
            'JavaScript': ['javascript', 'js', 'ecmascript', 'node.js', 'nodejs', 'node'],
            'TypeScript': ['typescript', 'ts'],
            'Java': ['java', 'spring', 'spring boot'],
            'C++': ['c++', 'cpp', 'c plus plus'],
            'C#': ['c#', 'csharp', 'dotnet', '.net', 'asp.net'],
            'Go': ['go', 'golang'],
            'Rust': ['rust'],
            'PHP': ['php'],
            'Ruby': ['ruby', 'rails', 'ruby on rails'],
            'Swift': ['swift'],
            'Kotlin': ['kotlin'],
            'Scala': ['scala'],
            'R': ['r language', 'r programming'],
            
            # Фреймворки и библиотеки
            'React': ['react', 'react.js', 'reactjs'],
            'Vue': ['vue', 'vue.js', 'vuejs'],
            'Angular': ['angular', 'angularjs'],
            'Node.js': ['node.js', 'nodejs', 'node', 'express'],
            'Django': ['django'],
            'Flask': ['flask'],
            'FastAPI': ['fastapi', 'fast api'],
            'Spring': ['spring', 'spring boot', 'spring framework'],
            'Laravel': ['laravel'],
            'Symfony': ['symfony'],
            
            # Базы данных
            'SQL': ['sql', 'mysql', 'postgresql', 'oracle', 'mssql'],
            'PostgreSQL': ['postgresql', 'postgres', 'pg'],
            'MySQL': ['mysql', 'mariadb'],
            'MongoDB': ['mongodb', 'mongo'],
            'Redis': ['redis'],
            'Elasticsearch': ['elasticsearch', 'elastic'],
            'Cassandra': ['cassandra'],
            'DynamoDB': ['dynamodb', 'dynamo db'],
            
            # Облачные платформы
            'AWS': ['aws', 'amazon web services', 'amazon aws'],
            'Azure': ['azure', 'microsoft azure'],
            'GCP': ['gcp', 'google cloud', 'google cloud platform'],
            'Docker': ['docker', 'dockerfile', 'docker compose'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'Terraform': ['terraform'],
            'Ansible': ['ansible'],
            
            # Инструменты
            'Git': ['git', 'github', 'gitlab', 'bitbucket'],
            'Linux': ['linux', 'unix', 'bash', 'shell'],
            'CI/CD': ['ci/cd', 'jenkins', 'gitlab ci', 'github actions', 'circleci'],
            'Jira': ['jira'],
            'Confluence': ['confluence'],
            
            # Методологии
            'Agile': ['agile', 'scrum', 'kanban'],
            'Scrum': ['scrum', 'scrum master'],
            'DevOps': ['devops', 'dev ops'],
            
            # Data Science & ML
            'Machine Learning': ['machine learning', 'ml', 'deep learning'],
            'Data Science': ['data science', 'data scientist'],
            'TensorFlow': ['tensorflow', 'tf'],
            'PyTorch': ['pytorch', 'torch'],
            'Pandas': ['pandas', 'pd'],
            'NumPy': ['numpy', 'np'],
            'Scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
            
            # Frontend
            'HTML': ['html', 'html5'],
            'CSS': ['css', 'css3', 'sass', 'scss', 'less'],
            'Bootstrap': ['bootstrap'],
            'Tailwind CSS': ['tailwind', 'tailwind css'],
            'Webpack': ['webpack'],
            'Vite': ['vite'],
            
            # API
            'REST API': ['rest', 'rest api', 'restful', 'restful api'],
            'GraphQL': ['graphql', 'graph ql'],
            'gRPC': ['grpc', 'g rpc'],
            
            # Другие
            'Microservices': ['microservices', 'micro services'],
            'RabbitMQ': ['rabbitmq', 'rabbit mq'],
            'Kafka': ['kafka', 'apache kafka'],
        }
        
        text_lower = text.lower()
        found_skills = []
        found_skill_names = set()  # Чтобы избежать дубликатов
        
        # Ключевые слова, указывающие на навык (контекст)
        skill_context_keywords = [
            'работал', 'работала', 'работаю', 'работает',
            'опыт', 'опытом', 'опыте',
            'знаю', 'знает', 'знание',
            'владею', 'владеет', 'владение',
            'использую', 'использует', 'использование',
            'применяю', 'применяет', 'применение',
            'умею', 'умеет', 'умение',
            'навык', 'навыки', 'навыками',
            'технология', 'технологии', 'технологиями',
            'инструмент', 'инструменты', 'инструментами',
            'язык', 'языки', 'языками',
            'фреймворк', 'фреймворки', 'фреймворками',
            'библиотека', 'библиотеки', 'библиотеками',
            'с', 'в', 'на', 'через', 'посредством'
        ]
        
        # Слова, которые исключают навык (ложные срабатывания)
        exclude_keywords = [
            'не знаю', 'не умею', 'не владею', 'не использую',
            'не работал', 'не работала', 'не работаю',
            'без опыта', 'нет опыта', 'не имею опыта'
        ]
        
        # Ищем навыки по синонимам с проверкой контекста
        for skill_name, synonyms in skills_dict.items():
            for synonym in synonyms:
                synonym_lower = synonym.lower()
                
                # Проверяем, что синоним не является частью другого слова
                # Ищем слово целиком (с границами слов)
                pattern = r'\b' + re.escape(synonym_lower) + r'\b'
                matches = list(re.finditer(pattern, text_lower))
                
                if not matches:
                    continue
                
                # Проверяем каждый случай вхождения
                found_valid = False
                for match in matches:
                    start_pos = match.start()
                    end_pos = match.end()
                    
                    # Берем контекст вокруг найденного слова (50 символов до и после)
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(text_lower), end_pos + 50)
                    context = text_lower[context_start:context_end]
                    
                    # Проверяем, нет ли исключающих слов
                    has_exclude = any(exc in context for exc in exclude_keywords)
                    if has_exclude:
                        continue
                    
                    # Для некоторых навыков нужна более строгая проверка
                    if skill_name == 'Git':
                        # Git должен быть упомянут отдельно, не только как часть GitHub/GitLab
                        if 'github' in context or 'gitlab' in context or 'bitbucket' in context:
                            # Проверяем, что Git упомянут отдельно
                            if not re.search(r'\bgit\b', context.replace('github', '').replace('gitlab', '').replace('bitbucket', '')):
                                continue
                    
                    if skill_name == 'REST API':
                        # REST API должен быть упомянут в контексте API/разработки
                        api_context = ['api', 'интерфейс', 'endpoint', 'запрос', 'response', 'http', 'https']
                        if not any(api_ctx in context for api_ctx in api_context):
                            # Если нет контекста API, проверяем наличие ключевых слов навыка
                            if not any(keyword in context for keyword in skill_context_keywords):
                                continue
                    
                    # Проверяем наличие контекстных слов (для большинства навыков)
                    # Исключение: если навык упомянут в списке навыков или технологий
                    is_in_skills_section = any(keyword in context for keyword in ['навык', 'технологи', 'инструмент', 'язык', 'фреймворк', 'библиотека'])
                    has_context = any(keyword in context for keyword in skill_context_keywords)
                    
                    # Навык считается валидным, если:
                    # 1. Он в секции навыков/технологий, ИЛИ
                    # 2. Есть контекстные слова рядом
                    if is_in_skills_section or has_context:
                        found_valid = True
                        break
                
                if found_valid and skill_name not in found_skill_names:
                    found_skills.append(skill_name)
                    found_skill_names.add(skill_name)
                    break  # Нашли один синоним, переходим к следующему навыку
        
        # Дополнительный поиск: ищем паттерны типа "работал с X", "опыт работы с Y"
        # (этот поиск уже учитывает контекст через паттерны)
        patterns = [
            r'(?:работал|работала|работаю|опыт|знаю|владею|использую|применяю|умею)[\s\w,]+(?:с|в|на)\s+([A-Z][a-zA-Z\s\+#\.]+)',
            r'(?:технологии|технология|навыки|навык|инструменты|инструмент)[\s:]+([A-Z][a-zA-Z\s,]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Очищаем и проверяем, не является ли это уже найденным навыком
                cleaned = match.strip().rstrip(',').split(',')[0].strip()
                if len(cleaned) > 2 and len(cleaned) < 50:  # Ограничиваем длину
                    # Проверяем, не является ли это известным навыком
                    cleaned_lower = cleaned.lower()
                    for skill_name, synonyms in skills_dict.items():
                        # Проверяем точное совпадение или вхождение синонима
                        if any(syn.lower() == cleaned_lower or syn.lower() in cleaned_lower for syn in synonyms):
                            if skill_name not in found_skill_names:
                                found_skills.append(skill_name)
                                found_skill_names.add(skill_name)
                            break
        
        return found_skills
    
    def _extract_experience(self, text: str) -> str:
        """Извлекает информацию об опыте работы"""
        # Ищем ключевые слова, связанные с опытом
        experience_keywords = ['опыт', 'experience', 'работал', 'работала', 'работаю']
        lines = text.split('\n')
        experience_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in experience_keywords):
                # Берем текущую строку и несколько следующих
                experience_lines.extend(lines[i:i+3])
        
        return '\n'.join(experience_lines[:10])  # Ограничиваем длину
    
    def _extract_education(self, text: str) -> str:
        """Извлекает информацию об образовании"""
        education_keywords = ['образование', 'education', 'университет', 'институт', 'вуз']
        lines = text.split('\n')
        education_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education_lines.extend(lines[i:i+3])
        
        return '\n'.join(education_lines[:10])
    
    def _extract_languages(self, text: str) -> List[str]:
        """Извлекает информацию о языках"""
        languages = ['русский', 'английский', 'немецкий', 'французский', 'испанский',
                    'russian', 'english', 'german', 'french', 'spanish']
        text_lower = text.lower()
        found_languages = []
        
        for lang in languages:
            if lang in text_lower:
                found_languages.append(lang)
        
        return found_languages

