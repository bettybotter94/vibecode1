"""
Модуль для анализа совместимости резюме и вакансии
"""
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class CompatibilityAnalyzer:
    """Анализатор совместимости резюме и вакансии"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    
    def analyze(self, resume_data: Dict, job_data: Dict) -> Dict[str, any]:
        """
        Анализирует совместимость резюме и вакансии
        
        Returns:
            Dict с полями: compatibility_percentage, gaps, recommendations
        """
        # 1. Расчет общего процента совместимости
        compatibility = self._calculate_compatibility(resume_data, job_data)
        
        # 2. Gap-анализ
        gaps = self._find_gaps(resume_data, job_data)
        
        # 3. Рекомендации
        recommendations = self._generate_recommendations(gaps, resume_data, job_data)
        
        return {
            'compatibility_percentage': round(compatibility, 2),
            'gaps': gaps,
            'recommendations': recommendations,
            'resume_skills': resume_data.get('skills', []),
            'job_skills': job_data.get('skills', []),
        }
    
    def _calculate_compatibility(self, resume_data: Dict, job_data: Dict) -> float:
        """Рассчитывает процент совместимости"""
        scores = []
        
        # 1. Совместимость навыков (40% веса)
        skills_score = self._compare_skills(
            resume_data.get('skills', []),
            job_data.get('skills', [])
        )
        scores.append(('skills', skills_score, 0.4))
        
        # 2. Семантическая схожесть текстов (30% веса)
        text_similarity = self._compare_texts(
            resume_data.get('text', ''),
            job_data.get('text', '')
        )
        scores.append(('text_similarity', text_similarity, 0.3))
        
        # 3. Совместимость опыта (20% веса)
        experience_score = self._compare_experience(
            resume_data.get('experience', ''),
            job_data.get('requirements', '')
        )
        scores.append(('experience', experience_score, 0.2))
        
        # 4. Совместимость образования (10% веса)
        education_score = self._compare_education(
            resume_data.get('education', ''),
            job_data.get('education_required', '')
        )
        scores.append(('education', education_score, 0.1))
        
        # Взвешенная сумма
        total_score = sum(score * weight for _, score, weight in scores)
        
        return total_score * 100
    
    def _compare_skills(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Сравнивает навыки"""
        if not job_skills:
            return 1.0  # Если нет требований к навыкам, считаем 100%
        
        if not resume_skills:
            return 0.0
        
        # Нормализуем к нижнему регистру для сравнения
        resume_skills_lower = [s.lower() for s in resume_skills]
        job_skills_lower = [s.lower() for s in job_skills]
        
        # Находим пересечение
        matching_skills = set(resume_skills_lower) & set(job_skills_lower)
        
        # Процент совпадения
        match_ratio = len(matching_skills) / len(job_skills_lower)
        
        return min(match_ratio, 1.0)
    
    def _compare_texts(self, resume_text: str, job_text: str) -> float:
        """Сравнивает тексты используя TF-IDF и косинусное сходство"""
        if not resume_text or not job_text:
            return 0.0
        
        try:
            # Ограничиваем длину текстов для производительности
            resume_text = resume_text[:5000]
            job_text = job_text[:5000]
            
            # Векторизуем тексты
            texts = [resume_text, job_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Вычисляем косинусное сходство
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception:
            # Если ошибка, используем простое сравнение по ключевым словам
            return self._simple_text_comparison(resume_text, job_text)
    
    def _simple_text_comparison(self, text1: str, text2: str) -> float:
        """Простое сравнение текстов по ключевым словам"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words2:
            return 1.0
        
        common_words = words1 & words2
        return len(common_words) / len(words2)
    
    def _compare_experience(self, resume_experience: str, job_requirements: str) -> float:
        """Сравнивает опыт работы"""
        if not job_requirements:
            return 1.0
        
        return self._simple_text_comparison(resume_experience, job_requirements)
    
    def _compare_education(self, resume_education: str, job_education: str) -> float:
        """Сравнивает образование"""
        if not job_education:
            return 1.0
        
        if not resume_education:
            return 0.0
        
        resume_lower = resume_education.lower()
        job_lower = job_education.lower()
        
        # Проверяем наличие ключевых слов об образовании
        education_keywords = ['образование', 'education', 'университет', 'институт', 'вуз']
        
        resume_has_education = any(kw in resume_lower for kw in education_keywords)
        job_requires_education = any(kw in job_lower for kw in education_keywords)
        
        if not job_requires_education:
            return 1.0
        
        return 1.0 if resume_has_education else 0.5
    
    def _find_gaps(self, resume_data: Dict, job_data: Dict) -> List[Dict[str, str]]:
        """Находит пробелы (что не хватает в резюме)"""
        gaps = []
        
        # 1. Отсутствующие навыки
        resume_skills = [s.lower() for s in resume_data.get('skills', [])]
        job_skills = [s.lower() for s in job_data.get('skills', [])]
        
        missing_skills = set(job_skills) - set(resume_skills)
        if missing_skills:
            gaps.append({
                'category': 'Навыки',
                'items': list(missing_skills),
                'description': f'Отсутствуют навыки: {", ".join(missing_skills[:5])}'
            })
        
        # 2. Проверка опыта
        job_requirements = job_data.get('requirements', '').lower()
        resume_experience = resume_data.get('experience', '').lower()
        
        # Ищем ключевые слова в требованиях, которых нет в опыте
        requirement_keywords = ['опыт', 'experience', 'работал', 'проект', 'project']
        missing_experience = []
        
        for keyword in requirement_keywords:
            if keyword in job_requirements and keyword not in resume_experience:
                missing_experience.append(keyword)
        
        if missing_experience and not resume_experience:
            gaps.append({
                'category': 'Опыт работы',
                'items': ['Опыт работы не описан в резюме'],
                'description': 'В резюме отсутствует описание опыта работы'
            })
        
        # 3. Проверка образования
        job_education = job_data.get('education_required', '').lower()
        resume_education = resume_data.get('education', '').lower()
        
        if job_education and not resume_education:
            gaps.append({
                'category': 'Образование',
                'items': ['Информация об образовании не указана'],
                'description': 'В резюме отсутствует информация об образовании'
            })
        
        return gaps
    
    def _generate_recommendations(self, gaps: List[Dict], resume_data: Dict, job_data: Dict) -> List[str]:
        """Генерирует рекомендации для улучшения резюме"""
        recommendations = []
        
        for gap in gaps:
            if gap['category'] == 'Навыки':
                recommendations.append(
                    f"Изучите следующие технологии: {', '.join(gap['items'][:3])}"
                )
            elif gap['category'] == 'Опыт работы':
                recommendations.append(
                    "Добавьте подробное описание вашего опыта работы и проектов"
                )
            elif gap['category'] == 'Образование':
                recommendations.append(
                    "Укажите информацию об образовании в резюме"
                )
        
        # Общие рекомендации
        compatibility = self._calculate_compatibility(resume_data, job_data)
        if compatibility < 50:
            recommendations.append(
                "Рекомендуется переработать резюме, чтобы лучше соответствовать требованиям вакансии"
            )
        elif compatibility < 70:
            recommendations.append(
                "Есть потенциал для улучшения. Сфокусируйтесь на развитии недостающих навыков"
            )
        
        return recommendations

