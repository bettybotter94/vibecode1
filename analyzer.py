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
        Анализирует совместимость резюме и вакансии с детальной разбивкой
        
        Returns:
            Dict с полями: compatibility_percentage, breakdown, skills_table, gaps, recommendations
        """
        # 1. Детальная разбивка совместимости
        breakdown = self._calculate_detailed_breakdown(resume_data, job_data)
        
        # 2. Расчет общего процента совместимости (только для категорий, которые указаны в резюме)
        # Исключаем категории, которые не указаны в резюме (not_specified = True)
        valid_categories = {k: v for k, v in breakdown.items() if not v.get('not_specified', False)}
        
        # Считаем процент только по валидным категориям
        if valid_categories:
            compatibility = sum(cat['score'] for cat in valid_categories.values()) / sum(cat['max'] for cat in valid_categories.values()) * 100
        else:
            compatibility = 0
        
        # 3. Сводная таблица навыков
        skills_table = self._create_skills_table(resume_data, job_data)
        
        # 4. Gap-анализ
        gaps = self._find_gaps(resume_data, job_data)
        
        # 5. Мотивационные рекомендации
        recommendations = self._generate_motivational_recommendations(
            compatibility, breakdown, gaps, resume_data, job_data
        )
        
        # 6. Мотивационное сообщение
        motivational_message = self._generate_motivational_message(compatibility, breakdown)
        
        return {
            'compatibility_percentage': round(compatibility, 2),
            'breakdown': breakdown,
            'skills_table': skills_table,
            'gaps': gaps,
            'recommendations': recommendations,
            'motivational_message': motivational_message,
            'resume_skills': resume_data.get('skills', []),
            'job_skills': job_data.get('skills', []),
        }
    
    def _calculate_detailed_breakdown(self, resume_data: Dict, job_data: Dict) -> Dict[str, Dict]:
        """
        Рассчитывает детальную разбивку совместимости по категориям
        
        Returns:
            Dict с разбивкой по категориям: required_skills, preferred_skills, experience, education, soft_skills
        """
        resume_skills = resume_data.get('skills', [])
        job_skills = job_data.get('skills', [])
        
        # Разделяем навыки на обязательные и желательные (первые 60% - обязательные)
        if job_skills:
            split_point = max(1, int(len(job_skills) * 0.6))
            required_skills = job_skills[:split_point]
            preferred_skills = job_skills[split_point:]
        else:
            required_skills = []
            preferred_skills = []
        
        # 1. Обязательные навыки (50 баллов)
        required_score = self._compare_skills_detailed(resume_skills, required_skills, max_score=50)
        
        # 2. Желательные навыки (30 баллов)
        preferred_score = self._compare_skills_detailed(resume_skills, preferred_skills, max_score=30)
        
        # 3. Опыт работы (10 баллов)
        experience_score = self._compare_experience_detailed(
            resume_data.get('experience', ''),
            job_data.get('requirements', ''),
            max_score=10
        )
        
        # 4. Образование (5 баллов)
        education_score = self._compare_education_detailed(
            resume_data.get('education', ''),
            job_data.get('education_required', ''),
            max_score=5
        )
        
        # 5. Soft skills (5 баллов)
        soft_skills_score = self._compare_soft_skills(
            resume_data.get('text', ''),
            job_data.get('text', ''),
            max_score=5
        )
        
        # Определяем, какие категории не указаны в резюме
        result_breakdown = {
            'required_skills': {
                'score': required_score['score'],
                'max': required_score['max'],
                'percentage': round(required_score['score'] / required_score['max'] * 100, 1) if required_score['max'] > 0 else 0,
                'details': required_score['details'],
                'matching_skills': required_score.get('matching_skills', []),
                'missing_skills': required_score.get('missing_skills', []),
                'not_specified': not bool(resume_data.get('skills')) or len(resume_data.get('skills', [])) == 0
            },
            'preferred_skills': {
                'score': preferred_score['score'],
                'max': preferred_score['max'],
                'percentage': round(preferred_score['score'] / preferred_score['max'] * 100, 1) if preferred_score['max'] > 0 else 0,
                'details': preferred_score['details'],
                'matching_skills': preferred_score.get('matching_skills', []),
                'missing_skills': preferred_score.get('missing_skills', []),
                'not_specified': not bool(resume_data.get('skills')) or len(resume_data.get('skills', [])) == 0
            },
            'experience': {
                'score': experience_score['score'],
                'max': experience_score['max'],
                'percentage': round(experience_score['score'] / experience_score['max'] * 100, 1) if experience_score['max'] > 0 else 0,
                'details': experience_score['details'],
                'not_specified': not bool(resume_data.get('experience'))
            },
            'education': {
                'score': education_score['score'],
                'max': education_score['max'],
                'percentage': round(education_score['score'] / education_score['max'] * 100, 1) if education_score['max'] > 0 else 0,
                'details': education_score['details'],
                'not_specified': not bool(resume_data.get('education'))
            },
            'soft_skills': {
                'score': soft_skills_score['score'],
                'max': soft_skills_score['max'],
                'percentage': round(soft_skills_score['score'] / soft_skills_score['max'] * 100, 1) if soft_skills_score['max'] > 0 else 0,
                'details': soft_skills_score['details'],
                'not_specified': False  # Soft skills всегда учитываем
            }
        }
        
        return result_breakdown
    
    def _compare_skills_detailed(self, resume_skills: List[str], job_skills: List[str], max_score: int) -> Dict:
        """Детальное сравнение навыков с возвратом деталей и конкретных навыков"""
        if not job_skills:
            return {'score': max_score, 'max': max_score, 'details': [], 'matching_skills': [], 'missing_skills': []}
        
        if not resume_skills:
            return {
                'score': 0, 
                'max': max_score, 
                'details': [f'Отсутствуют все {len(job_skills)} навыков'],
                'matching_skills': [],
                'missing_skills': job_skills
            }
        
        resume_skills_lower = [s.lower() for s in resume_skills]
        job_skills_lower = [s.lower() for s in job_skills]
        
        # Находим совпадающие навыки (сохраняем оригинальные названия)
        matching_skills_set = set(resume_skills_lower) & set(job_skills_lower)
        missing_skills_set = set(job_skills_lower) - set(resume_skills_lower)
        
        # Восстанавливаем оригинальные названия навыков
        matching_skills = []
        for job_skill in job_skills:
            if job_skill.lower() in matching_skills_set:
                matching_skills.append(job_skill)
        
        missing_skills = []
        for job_skill in job_skills:
            if job_skill.lower() in missing_skills_set:
                missing_skills.append(job_skill)
        
        score = (len(matching_skills_set) / len(job_skills_lower)) * max_score
        
        details = []
        if matching_skills:
            details.append(f'✅ Найдено: {len(matching_skills)} из {len(job_skills)}')
            # Показываем первые 5 найденных навыков
            skills_list = ', '.join(matching_skills[:5])
            if len(matching_skills) > 5:
                skills_list += f' и еще {len(matching_skills) - 5}'
            details.append(f'Навыки: {skills_list}')
        if missing_skills:
            details.append(f'❌ Отсутствует: {len(missing_skills)} навыков')
            # Показываем первые 5 отсутствующих навыков
            skills_list = ', '.join(missing_skills[:5])
            if len(missing_skills) > 5:
                skills_list += f' и еще {len(missing_skills) - 5}'
            details.append(f'Не хватает: {skills_list}')
        
        # Добавляем объяснение расчета
        details.append(f'Расчет: {len(matching_skills_set)}/{len(job_skills_lower)} × {max_score} = {round(score, 1)} баллов')
        
        return {
            'score': round(score, 1), 
            'max': max_score, 
            'details': details,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
    
    def _compare_experience_detailed(self, resume_experience: str, job_requirements: str, max_score: int) -> Dict:
        """Детальное сравнение опыта работы"""
        if not job_requirements:
            return {'score': max_score, 'max': max_score, 'details': ['Требования к опыту не указаны']}
        
        similarity = self._simple_text_comparison(resume_experience, job_requirements)
        score = similarity * max_score
        
        details = []
        if resume_experience:
            details.append('✅ Опыт работы описан в резюме')
            # Показываем первые 100 символов опыта
            exp_preview = resume_experience[:100].replace('\n', ' ')
            if len(resume_experience) > 100:
                exp_preview += '...'
            details.append(f'Описание: {exp_preview}')
        else:
            details.append('❌ Опыт работы не описан в резюме')
        
        # Добавляем объяснение расчета
        details.append(f'Расчет: схожесть {round(similarity * 100, 1)}% × {max_score} = {round(score, 1)} баллов')
        
        return {'score': round(score, 1), 'max': max_score, 'details': details}
    
    def _compare_education_detailed(self, resume_education: str, job_education: str, max_score: int) -> Dict:
        """Детальное сравнение образования"""
        if not job_education:
            return {'score': max_score, 'max': max_score, 'details': ['Требования к образованию не указаны']}
        
        if not resume_education:
            return {'score': 0, 'max': max_score, 'details': ['❌ Образование не указано в резюме', f'Расчет: 0/{max_score} = 0 баллов']}
        
        resume_lower = resume_education.lower()
        job_lower = job_education.lower()
        
        education_keywords = ['образование', 'education', 'университет', 'институт', 'вуз', 'бакалавр', 'магистр']
        
        resume_has_education = any(kw in resume_lower for kw in education_keywords)
        job_requires_education = any(kw in job_lower for kw in education_keywords)
        
        details = []
        if not job_requires_education:
            score = max_score
            details = ['✅ Требования к образованию не критичны']
            details.append(f'Расчет: {max_score}/{max_score} = {max_score} баллов')
        elif resume_has_education:
            score = max_score
            # Показываем информацию об образовании
            edu_preview = resume_education[:80].replace('\n', ' ')
            if len(resume_education) > 80:
                edu_preview += '...'
            details = ['✅ Образование соответствует требованиям']
            details.append(f'Указано: {edu_preview}')
            details.append(f'Расчет: {max_score}/{max_score} = {max_score} баллов')
        else:
            score = max_score * 0.5
            details = ['⚠️ Образование указано, но может не соответствовать требованиям']
            details.append(f'Расчет: частичное соответствие × {max_score} = {round(score, 1)} баллов')
        
        return {'score': round(score, 1), 'max': max_score, 'details': details}
    
    def _compare_soft_skills(self, resume_text: str, job_text: str, max_score: int) -> Dict:
        """Сравнение soft skills"""
        soft_skills_keywords = {
            'коммуникабельность': ['коммуника', 'общение', 'команд', 'взаимодействие'],
            'лидерство': ['лидер', 'руковод', 'управление командой'],
            'адаптивность': ['адаптив', 'быстрое обучение', 'гибкость'],
            'ответственность': ['ответствен', 'надежн', 'обязательн'],
            'креативность': ['креатив', 'творческ', 'инновацион']
        }
        
        resume_lower = resume_text.lower()
        job_lower = job_text.lower()
        
        found_soft_skills = 0
        details = []
        
        for skill_name, keywords in soft_skills_keywords.items():
            job_mentions = sum(1 for kw in keywords if kw in job_lower)
            resume_mentions = sum(1 for kw in keywords if kw in resume_lower)
            
            if job_mentions > 0:
                if resume_mentions > 0:
                    found_soft_skills += 1
                    details.append(f'{skill_name}: найдено')
                else:
                    details.append(f'{skill_name}: не найдено')
        
        # Если в вакансии не упоминаются soft skills, даем полный балл
        if not any(kw in job_lower for keywords in soft_skills_keywords.values() for kw in keywords):
            score = max_score
            details = ['✅ Soft skills не требуются']
            details.append(f'Расчет: {max_score}/{max_score} = {max_score} баллов')
        else:
            total_soft_skills_required = len([name for name, keywords in soft_skills_keywords.items() 
                                            if any(kw in job_lower for kw in keywords)])
            score = (found_soft_skills / total_soft_skills_required) * max_score if total_soft_skills_required > 0 else 0
            if not details:
                details = ['❌ Soft skills не найдены в резюме']
            # Добавляем объяснение расчета
            details.append(f'Расчет: найдено {found_soft_skills} из {total_soft_skills_required} × {max_score} = {round(score, 1)} баллов')
        
        return {'score': round(score, 1), 'max': max_score, 'details': details}
    
    def _create_skills_table(self, resume_data: Dict, job_data: Dict) -> List[Dict]:
        """Создает сводную таблицу навыков со статусами"""
        resume_skills = [s.lower() for s in resume_data.get('skills', [])]
        job_skills = job_data.get('skills', [])
        
        skills_table = []
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            
            # Проверяем статус навыка
            if job_skill_lower in resume_skills:
                status = "present"
                status_icon = "✅"
                status_text = "Есть"
                level = self._determine_skill_level(job_skill, resume_data.get('text', ''))
                action = "-"
            elif self._has_partial_match(job_skill_lower, resume_skills, resume_data.get('text', '')):
                status = "partial"
                status_icon = "⚠️"
                status_text = "Почти есть"
                level = "Средний"
                action = f"Практиковать {job_skill}"
            else:
                status = "missing"
                status_icon = "❌"
                status_text = "Не хватает"
                level = "Начальный"
                action = f"Изучить {job_skill}"
            
            skills_table.append({
                'skill': job_skill,
                'status': status,
                'status_icon': status_icon,
                'status_text': status_text,
                'level': level,
                'action': action
            })
        
        return skills_table
    
    def _has_partial_match(self, skill: str, resume_skills: List[str], resume_text: str) -> bool:
        """Проверяет, есть ли частичное совпадение навыка"""
        # Проверяем похожие навыки
        skill_variations = {
            'docker': ['контейнер', 'container'],
            'kubernetes': ['k8s', 'оркестрация'],
            'python': ['django', 'flask', 'fastapi'],
            'javascript': ['js', 'node', 'react', 'vue'],
        }
        
        resume_text_lower = resume_text.lower()
        
        for key, variations in skill_variations.items():
            if key in skill:
                if any(var in resume_text_lower for var in variations):
                    return True
        
        return False
    
    def _determine_skill_level(self, skill: str, resume_text: str) -> str:
        """Определяет уровень владения навыком"""
        resume_lower = resume_text.lower()
        skill_lower = skill.lower()
        
        # Ищем индикаторы уровня
        advanced_keywords = ['продвинут', 'expert', 'senior', 'глубок', 'опытный']
        intermediate_keywords = ['средн', 'intermediate', 'middle', 'хорош']
        
        skill_context = resume_lower[max(0, resume_lower.find(skill_lower)-50):
                                     resume_lower.find(skill_lower)+50]
        
        if any(kw in skill_context for kw in advanced_keywords):
            return "Продвинутый"
        elif any(kw in skill_context for kw in intermediate_keywords):
            return "Средний"
        else:
            return "Базовый"
    
    def _generate_motivational_message(self, compatibility: float, breakdown: Dict) -> str:
        """Генерирует мотивационное сообщение"""
        if compatibility >= 80:
            return f"🎉 Поздравляем! Ты уже на {compatibility:.0f}% готов к этой позиции! Ты отлично подходишь!"
        elif compatibility >= 60:
            return f"🚀 Отличный результат! Ты уже на {compatibility:.0f}% готов! Осталось совсем немного до идеального соответствия!"
        elif compatibility >= 40:
            return f"💪 Ты уже на {compatibility:.0f}% готов к этой позиции! Всего несколько навыков отделяют тебя от мечты!"
        else:
            return f"📚 Твой текущий уровень: {compatibility:.0f}%. Давай вместе составим план развития и достигнем цели!"
    
    def _generate_motivational_recommendations(
        self, compatibility: float, breakdown: Dict, gaps: List[Dict], 
        resume_data: Dict, job_data: Dict
    ) -> List[str]:
        """Генерирует мотивационные рекомендации"""
        recommendations = []
        
        # Начинаем с мотивации
        if compatibility >= 70:
            recommendations.append(f"🎯 Твой текущий уровень: {compatibility:.0f}% - отличная база!")
        elif compatibility >= 50:
            recommendations.append(f"🎯 Твой текущий уровень: {compatibility:.0f}% - хорошая база, есть куда расти!")
        else:
            recommendations.append(f"🎯 Твой текущий уровень: {compatibility:.0f}% - начнем с основ!")
        
        # Анализируем breakdown
        weak_categories = []
        strong_categories = []
        
        for cat_name, cat_data in breakdown.items():
            if cat_data['percentage'] < 50:
                weak_categories.append(cat_name)
            elif cat_data['percentage'] >= 80:
                strong_categories.append(cat_name)
        
        # Сильные стороны
        if strong_categories:
            strong_text = {
                'required_skills': 'обязательные навыки',
                'preferred_skills': 'желательные навыки',
                'experience': 'опыт работы',
                'education': 'образование',
                'soft_skills': 'soft skills'
            }
            strong_list = [strong_text.get(cat, cat) for cat in strong_categories[:2]]
            recommendations.append(f"💪 Твои сильные стороны: {', '.join(strong_list)}")
        
        # Что подкачать
        if weak_categories or gaps:
            recommendations.append("🚀 Что подкачать:")
            
            # Навыки из gaps
            for gap in gaps:
                if gap['category'] == 'Навыки' and gap.get('items'):
                    missing = gap['items'][:3]
                    recommendations.append(f"• {', '.join(missing)} - ключевые навыки для позиции")
            
            # Категории из breakdown
            if 'required_skills' in weak_categories:
                recommendations.append("• Обязательные навыки - критично для позиции")
            if 'experience' in weak_categories:
                recommendations.append("• Опыт работы - добавь больше деталей о проектах")
        
        # План действий
        recommendations.append("📚 План действий:")
        action_num = 1
        
        for gap in gaps[:3]:  # Берем первые 3 пробела
            if gap['category'] == 'Навыки' and gap.get('items'):
                skill = gap['items'][0]
                recommendations.append(f"{action_num}. Изучи {skill} - пройди курс или сделай pet-project")
                action_num += 1
        
        if action_num == 1:
            recommendations.append("1. Продолжай развивать текущие навыки")
            recommendations.append("2. Обнови резюме с новыми достижениями")
        
        return recommendations
    
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
            missing_skills_list = list(missing_skills)
            gaps.append({
                'category': 'Навыки',
                'items': missing_skills_list,
                'description': f'Отсутствуют навыки: {", ".join(missing_skills_list[:5])}'
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
        """Генерирует конкретные рекомендации для улучшения резюме"""
        recommendations = []
        
        for gap in gaps:
            if gap['category'] == 'Навыки':
                missing_skills = gap.get('items', [])[:5]
                if missing_skills:
                    skills_text = ', '.join(missing_skills[:3])
                    if len(missing_skills) > 3:
                        skills_text += f" и еще {len(missing_skills) - 3}"
                    recommendations.append(
                        f"**Критично:** Изучите недостающие технологии: {skills_text}. "
                        f"Рекомендуем начать с онлайн-курсов или документации."
                    )
            elif gap['category'] == 'Опыт работы':
                recommendations.append(
                    "**Важно:** Добавьте подробное описание вашего опыта работы. "
                    "Укажите конкретные проекты, достижения и используемые технологии. "
                    "Используйте формат: 'Что делал → Какой результат получил'."
                )
            elif gap['category'] == 'Образование':
                recommendations.append(
                    "**Желательно:** Укажите информацию об образовании в резюме. "
                    "Включите название учебного заведения, специальность и год окончания."
                )
        
        # Общие рекомендации на основе совместимости
        compatibility = self._calculate_compatibility(resume_data, job_data)
        resume_skills = resume_data.get('skills', [])
        job_skills = job_data.get('skills', [])
        
        if compatibility < 50:
            if resume_skills and job_skills:
                missing_count = len(set(s.lower() for s in job_skills) - set(s.lower() for s in resume_skills))
                recommendations.append(
                    f"**Общая рекомендация:** Совместимость низкая ({compatibility:.0f}%). "
                    f"Не хватает {missing_count} ключевых навыков. "
                    f"Рекомендуем переработать резюме, добавив недостающие технологии и опыт."
                )
            else:
                recommendations.append(
                    f"**Общая рекомендация:** Совместимость низкая ({compatibility:.0f}%). "
                    f"Рекомендуем детально изучить требования вакансии и адаптировать резюме."
                )
        elif compatibility < 70:
            recommendations.append(
                f"**Общая рекомендация:** Совместимость средняя ({compatibility:.0f}%). "
                f"Есть потенциал для улучшения. Сфокусируйтесь на развитии недостающих навыков "
                f"и улучшении формулировок в резюме."
            )
        elif compatibility >= 70:
            recommendations.append(
                f"**Отлично!** Ваше резюме хорошо соответствует вакансии ({compatibility:.0f}%). "
                f"Рекомендуем только небольшие доработки для идеального соответствия."
            )
        
        # Дополнительные рекомендации
        if resume_skills and job_skills:
            matching_ratio = len(set(s.lower() for s in resume_skills) & set(s.lower() for s in job_skills)) / len(job_skills)
            if matching_ratio < 0.5:
                recommendations.append(
                    "**Совет:** Переформулируйте описание опыта работы, используя ключевые слова из вакансии. "
                    "Это поможет пройти автоматический отбор (ATS)."
                )
        
        return recommendations

