"""
Модуль для парсинга резюме из различных форматов
"""
import os
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
        """Извлекает навыки из текста"""
        # Список популярных навыков для поиска
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'Git', 'Linux', 'Agile', 'Scrum', 'CI/CD',
            'Machine Learning', 'Data Science', 'TensorFlow', 'PyTorch',
            'HTML', 'CSS', 'TypeScript', 'REST API', 'GraphQL'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
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

