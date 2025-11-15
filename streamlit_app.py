"""
Streamlit приложение для анализа совместимости резюме и вакансий
Запуск: двойной клик на файл или streamlit run streamlit_app.py
"""
import streamlit as st
import os
import tempfile
from typing import Dict
import pandas as pd

from resume_parser import ResumeParser
from job_parser import JobParser
from analyzer import CompatibilityAnalyzer

# Настройка страницы в стиле Школы 21
st.set_page_config(
    page_title="Анализ резюме и вакансий | Школа 21",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Глобальные стили Школы 21
SCHOOL21_GREEN = "#00B956"
SCHOOL21_BLUE = "#00AEEF"
SCHOOL21_BG = "#F5F5F5"
SCHOOL21_TEXT = "#333333"

# Применяем стили
st.markdown(f"""
    <style>
    /* Основные стили */
    .main {{
        background-color: {SCHOOL21_BG};
    }}
    
    /* Заголовки */
    h1, h2, h3 {{
        color: {SCHOOL21_TEXT};
    }}
    
    /* Кнопки */
    .stButton > button {{
        background: linear-gradient(135deg, {SCHOOL21_BLUE} 0%, {SCHOOL21_GREEN} 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 174, 239, 0.3);
        filter: brightness(0.9);
    }}
    
    /* Метрики */
    [data-testid="stMetricValue"] {{
        color: {SCHOOL21_GREEN};
    }}
    
    /* Боковая панель */
    .css-1d391kg {{
        background-color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# Инициализация парсеров и анализатора
@st.cache_resource
def get_parsers():
    """Инициализирует парсеры (кэшируется для производительности)"""
    return {
        'resume_parser': ResumeParser(),
        'job_parser': JobParser(),
        'analyzer': CompatibilityAnalyzer()
    }

parsers = get_parsers()
resume_parser = parsers['resume_parser']
job_parser = parsers['job_parser']
analyzer = parsers['analyzer']


def display_results(result: Dict) -> None:
    """Отображает результаты анализа в стиле Школы 21"""
    compatibility = result['compatibility_percentage']
    breakdown = result.get('breakdown', {})
    motivational_message = result.get('motivational_message', '')
    
    # Определяем цвет в стиле Школы 21
    if compatibility >= 70:
        color_hex = SCHOOL21_GREEN
        status = "Отлично!"
    elif compatibility >= 50:
        color_hex = SCHOOL21_BLUE
        status = "Хорошо"
    else:
        color_hex = "#FF6B6B"
        status = "Требуется улучшение"
    
    # Мотивационное сообщение
    if motivational_message:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {SCHOOL21_BLUE} 0%, {SCHOOL21_GREEN} 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">
            <h3 style="color: white; margin: 0;">{motivational_message}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Главный процент совместимости
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 30px;">
            <h1 style="font-size: 5em; color: {color_hex}; margin: 0; font-weight: bold;">{compatibility}%</h1>
            <h3 style="color: {SCHOOL21_TEXT}; margin-top: 10px;">{status}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Прогресс-бар с градиентом Школы 21 (улучшенный)
        progress_color = SCHOOL21_GREEN if compatibility >= 70 else SCHOOL21_BLUE if compatibility >= 50 else "#FF6B6B"
        progress_html = f"""
        <div style="background: {SCHOOL21_BG}; border-radius: 15px; height: 40px; margin: 20px 0; 
                    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
            <div style="background: linear-gradient(90deg, {progress_color} 0%, {progress_color}dd 100%);
                        width: {compatibility}%; height: 100%; border-radius: 15px; 
                        transition: width 1s ease; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                        display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-weight: bold; font-size: 1.1em; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">
                    {compatibility}%
                </span>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Детальная разбивка совместимости
    if breakdown:
        st.subheader("📊 Детальная разбивка совместимости")
        
        breakdown_names = {
            'required_skills': 'Обязательные навыки',
            'preferred_skills': 'Желательные навыки',
            'experience': 'Опыт работы',
            'education': 'Образование',
            'soft_skills': 'Soft skills'
        }
        
        for key, name in breakdown_names.items():
            if key in breakdown:
                cat_data = breakdown[key]
                score = cat_data['score']
                max_score = cat_data['max']
                percentage = cat_data.get('percentage', 0)
                details = cat_data.get('details', [])
                
                # Определяем цвет прогресс-бара
                if percentage >= 80:
                    progress_color = SCHOOL21_GREEN
                    bg_color = "#E8F5E9"
                elif percentage >= 50:
                    progress_color = SCHOOL21_BLUE
                    bg_color = "#E3F2FD"
                else:
                    progress_color = "#FF6B6B"
                    bg_color = "#FFEBEE"
                
                # Создаем красивую карточку для категории используя Streamlit компоненты
                # Заголовок и процент в одной строке
                col_title, col_percent = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### {name}")
                with col_percent:
                    st.metric("", f"{percentage}%")
                
                # Прогресс-бар с цветом
                progress_value = percentage / 100
                st.progress(progress_value)
                
                # Счет и детали
                st.caption(f"**{score}/{max_score}** баллов")
                
                # Детали
                if details:
                    for detail in details:
                        st.caption(f"  • {detail}")
                
                # Разделитель между категориями
                st.markdown("<br>", unsafe_allow_html=True)
        
        st.divider()
    
    # Детальный анализ требований и соответствия
    st.subheader("📋 Детальный анализ требований")
    
    # Показываем требования из вакансии
    job_skills = result.get('job_skills', [])
    resume_skills = result.get('resume_skills', [])
    
    if job_skills:
        st.markdown("#### 🎯 Требования из вакансии:")
        
        # Группируем навыки по статусу
        present_skills = []
        partial_skills = []
        missing_skills = []
        
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        for skill in job_skills:
            skill_lower = skill.lower()
            if skill_lower in resume_skills_lower:
                present_skills.append(skill)
            elif any(skill_lower in rs or rs in skill_lower for rs in resume_skills_lower):
                partial_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Показываем найденные навыки
        if present_skills:
            st.markdown(f"**✅ Найдено в резюме ({len(present_skills)}):**")
            cols = st.columns(min(3, len(present_skills)))
            for i, skill in enumerate(present_skills[:9]):  # Показываем до 9 навыков
                with cols[i % 3]:
                    st.success(f"✅ {skill}")
            if len(present_skills) > 9:
                st.caption(f"... и еще {len(present_skills) - 9} навыков")
            st.markdown("")
        
        # Показываем частично найденные
        if partial_skills:
            st.markdown(f"**⚠️ Частично найдено ({len(partial_skills)}):**")
            cols = st.columns(min(3, len(partial_skills)))
            for i, skill in enumerate(partial_skills[:9]):
                with cols[i % 3]:
                    st.warning(f"⚠️ {skill}")
            if len(partial_skills) > 9:
                st.caption(f"... и еще {len(partial_skills) - 9} навыков")
            st.markdown("")
        
        # Показываем отсутствующие
        if missing_skills:
            st.markdown(f"**❌ Не найдено в резюме ({len(missing_skills)}):**")
            cols = st.columns(min(3, len(missing_skills)))
            for i, skill in enumerate(missing_skills[:9]):
                with cols[i % 3]:
                    st.error(f"❌ {skill}")
            if len(missing_skills) > 9:
                st.caption(f"... и еще {len(missing_skills) - 9} навыков")
            st.markdown("")
        
        # Метрики
        total_required = len(job_skills)
        found_count = len(present_skills)
        partial_count = len(partial_skills)
        missing_count = len(missing_skills)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Всего требований", total_required)
        with col2:
            st.metric("✅ Найдено", found_count, delta=f"{int(found_count/total_required*100) if total_required > 0 else 0}%")
        with col3:
            st.metric("⚠️ Частично", partial_count)
        with col4:
            st.metric("❌ Не найдено", missing_count, delta=f"-{missing_count}", delta_color="inverse")
        
        st.divider()
    
    # Сводная таблица навыков
    skills_table = result.get('skills_table', [])
    if skills_table:
        st.subheader("📊 Сводная таблица навыков")
        
        # Создаем DataFrame для таблицы
        table_data = []
        for item in skills_table:
            table_data.append({
                'Навык': item['skill'],
                'Статус': f"{item['status_icon']} {item['status_text']}",
                'Уровень': item['level'],
                'Что делать': item['action']
            })
        
        df = pd.DataFrame(table_data)
        
        # Стилизуем таблицу
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Навык": st.column_config.TextColumn("Навык", width="medium"),
                "Статус": st.column_config.TextColumn("Статус", width="small"),
                "Уровень": st.column_config.TextColumn("Уровень", width="small"),
                "Что делать": st.column_config.TextColumn("Что делать", width="large")
            }
        )
        
        st.divider()
    
    # Визуализация сравнения навыков (если нет таблицы)
    resume_skills = result.get('resume_skills', [])
    job_skills = result.get('job_skills', [])
    
    if (resume_skills or job_skills) and not skills_table:
        st.subheader("🛠️ Сравнение навыков")
        
        if resume_skills and job_skills:
            matching_skills = set(s.lower() for s in resume_skills) & set(s.lower() for s in job_skills)
            missing_skills = set(s.lower() for s in job_skills) - set(s.lower() for s in resume_skills)
            
            # Метрики
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего навыков в резюме", len(resume_skills))
            with col2:
                st.metric("Требуется навыков", len(job_skills))
            with col3:
                st.metric("Совпадает", len(matching_skills), delta=f"{len(job_skills) and int(len(matching_skills)/len(job_skills)*100) or 0}%")
            with col4:
                st.metric("Не хватает", len(missing_skills), delta=f"-{len(missing_skills)}", delta_color="inverse")
        
        st.divider()
    
    
    # Gap-анализ с приоритетами
    st.subheader("🔍 Gap-анализ (чего не хватает)")
    
    if result.get('gaps') and len(result['gaps']) > 0:
        # Сортируем gaps по важности (навыки - критично, остальное - важно)
        sorted_gaps = sorted(result['gaps'], key=lambda x: 0 if x['category'] == 'Навыки' else 1)
        
        for gap in sorted_gaps:
            # Определяем приоритет
            if gap['category'] == 'Навыки':
                priority_icon = "🔴"
                priority_text = "Критично"
            elif gap['category'] == 'Опыт работы':
                priority_icon = "🟡"
                priority_text = "Важно"
            else:
                priority_icon = "🟢"
                priority_text = "Желательно"
            
            with st.expander(f"{priority_icon} {gap['category']} ({priority_text})", expanded=True):
                st.write(f"**Описание:** {gap['description']}")
                if gap.get('items'):
                    st.write("**Детали:**")
                    # Показываем только первые 10 элементов
                    for item in gap['items'][:10]:
                        st.write(f"- {item}")
                    if len(gap['items']) > 10:
                        st.caption(f"... и еще {len(gap['items']) - 10} элементов")
    else:
        st.success("✅ Отлично! Все основные требования выполнены.")
    
    st.divider()
    
    # Мотивационные рекомендации в стиле Школы 21
    st.subheader("💡 Рекомендации по улучшению")
    
    recommendations = result.get('recommendations', [])
    if recommendations and len(recommendations) > 0:
        # Группируем рекомендации по типам
        current_section = None
        for rec in recommendations:
            # Определяем тип секции
            if "🎯" in rec:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {SCHOOL21_BLUE} 0%, {SCHOOL21_GREEN} 100%);
                            padding: 15px; border-radius: 8px; margin: 10px 0; color: white;">
                    <strong style="color: white; font-size: 1.1em;">{rec}</strong>
                </div>
                """, unsafe_allow_html=True)
            elif "💪" in rec or "🚀" in rec:
                st.markdown(f"### {rec}")
            elif "📚" in rec:
                st.markdown(f"### {rec}")
            elif rec.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                st.markdown(f"**{rec}**")
            else:
                st.info(f"💡 {rec}")
    else:
        st.success("✅ Ваше резюме хорошо соответствует вакансии!")
    
    st.divider()


# Заголовок приложения в стиле Школы 21
st.markdown("""
    <div style="text-align: center; padding: 30px 0; background: linear-gradient(135deg, #00AEEF 0%, #00B956 100%);
                border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0, 174, 239, 0.2);">
        <h1 style="font-size: 3.5em; color: white; margin: 0; font-weight: bold;">
            📄 Анализ совместимости резюме и вакансий
        </h1>
        <p style="font-size: 1.3em; color: white; margin-top: 15px; opacity: 0.95;">
            Загрузите резюме и вакансию (по ссылке или из файла) для анализа совместимости
        </p>
    </div>
""", unsafe_allow_html=True)

# Создаем две колонки для формы
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📎 Загрузите резюме")
    uploaded_file = st.file_uploader(
        "Выберите файл резюме",
        type=['pdf', 'docx', 'txt'],
        help="Поддерживаются форматы: PDF, DOCX, TXT",
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"✅ Загружен: {uploaded_file.name}")

with col2:
    st.markdown("### 📋 Вакансия")
    
    # Переключатель: ссылка или файл
    input_method = st.radio(
        "Выберите способ",
        ["🔗 По ссылке", "📄 Из файла"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    job_url = None
    job_file = None
    
    if input_method == "🔗 По ссылке":
        job_url = st.text_input(
            "Вставьте URL вакансии",
            placeholder="https://hh.ru/vacancy/12345678",
            help="Вставьте ссылку на вакансию с любого сайта (HeadHunter, Habr и т.д.)",
            label_visibility="collapsed"
        )
        if job_url:
            st.info(f"🔗 Анализируем: {job_url[:50]}...")
    else:
        job_file = st.file_uploader(
            "Загрузите файл с текстом вакансии",
            type=['txt', 'docx', 'pdf'],
            help="Загрузите файл с текстом вакансии (TXT, DOCX, PDF). Можно скопировать текст вакансии и сохранить в файл, или загрузить PDF вакансии.",
            label_visibility="collapsed"
        )
        if job_file:
            st.success(f"✅ Загружен: {job_file.name}")
            st.info("💡 **Совет:** Скопируйте текст вакансии с сайта и сохраните в текстовый файл для более точного анализа")

# Кнопка анализа в стиле Школы 21
st.markdown("<br>", unsafe_allow_html=True)
analyze_button = st.button("🔍 Анализировать совместимость", type="primary", use_container_width=True)

# Обработка анализа
if analyze_button:
    # Валидация входных данных
    if not uploaded_file:
        st.error("❌ Пожалуйста, загрузите файл резюме")
        st.stop()
    
    if not job_url and not job_file:
        st.error("❌ Пожалуйста, введите ссылку на вакансию или загрузите файл")
        st.stop()
    
    # Показываем индикатор загрузки
    with st.spinner("⏳ Анализируем резюме и вакансию... Это может занять несколько секунд"):
        try:
            # Сохраняем загруженный файл резюме во временную директорию
            resume_file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=resume_file_ext) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_resume_path = tmp_file.name
            
            # Сохраняем файл вакансии, если загружен
            temp_job_path = None
            job_file_ext = None
            if job_file:
                job_file_ext = os.path.splitext(job_file.name)[1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=job_file_ext, mode='wb') as tmp_job_file:
                    tmp_job_file.write(job_file.read())
                    temp_job_path = tmp_job_file.name
            
            try:
                # Парсим резюме
                resume_data = resume_parser.parse(temp_resume_path)
                
                # Парсим вакансию (из файла или по ссылке)
                if job_file and temp_job_path:
                    # Парсим из файла
                    if job_file_ext == '.txt':
                        # Для TXT файлов используем простой парсер
                        job_data = job_parser.parse_from_file(temp_job_path)
                    else:
                        # Для DOCX и PDF используем resume_parser для извлечения текста
                        temp_text = resume_parser.parse(temp_job_path)
                        extracted_text = temp_text.get('text', '')
                        
                        if not extracted_text or len(extracted_text.strip()) < 50:
                            raise ValueError(f"Не удалось извлечь текст из файла {job_file.name}. Убедитесь, что файл содержит текст вакансии.")
                        
                        # Извлекаем информацию из текста
                        job_data = {
                            'title': job_parser._extract_title_from_text(extracted_text),
                            'text': extracted_text,
                            'description': extracted_text[:1000],
                            'requirements': job_parser._extract_requirements(extracted_text),
                            'skills': job_parser._extract_skills(extracted_text),
                            'experience_required': job_parser._extract_experience_requirement(extracted_text),
                            'education_required': job_parser._extract_education_requirement(extracted_text),
                        }
                else:
                    # Парсим по ссылке
                    job_data = job_parser.parse(job_url)
                
                # Анализируем совместимость
                analysis_result = analyzer.analyze(resume_data, job_data)
                
                # Отображаем результаты
                display_results(analysis_result)
                
            finally:
                # Удаляем временные файлы
                if os.path.exists(temp_resume_path):
                    os.remove(temp_resume_path)
                if temp_job_path and os.path.exists(temp_job_path):
                    os.remove(temp_job_path)
        
        except ValueError as e:
            error_msg = str(e)
            st.error(f"❌ **Ошибка:** {error_msg}")
            
            # Дополнительные подсказки в зависимости от типа ошибки
            if "URL" in error_msg or "ссылка" in error_msg.lower():
                st.info("💡 **Подсказка:** Убедитесь, что ссылка начинается с http:// или https:// и ведет на страницу вакансии")
            elif "HeadHunter" in error_msg or "hh.ru" in error_msg.lower():
                st.info("💡 **Подсказка для HeadHunter:** Убедитесь, что ссылка ведет на открытую вакансию (не требует авторизации). Попробуйте скопировать ссылку из адресной строки браузера.")
            elif "загрузке" in error_msg.lower() or "подключения" in error_msg.lower():
                st.info("💡 **Подсказка:** Проверьте интернет-соединение и попробуйте еще раз")
            elif "блокирует" in error_msg.lower() or "запрещен" in error_msg.lower():
                st.info("💡 **Подсказка:** Некоторые сайты блокируют автоматические запросы. Попробуйте другую ссылку или скопируйте текст вакансии вручную")
            elif "timeout" in error_msg.lower() or "время ожидания" in error_msg.lower():
                st.info("💡 **Подсказка:** Превышено время ожидания. Попробуйте еще раз или проверьте скорость интернета")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ **Произошла неожиданная ошибка:** {error_msg}")
            
            # Показываем более понятное сообщение
            if "AttributeError" in str(type(e)):
                st.warning("⚠️ Ошибка в коде. Возможно, проблема с парсингом данных.")
            elif "KeyError" in str(type(e)):
                st.warning("⚠️ Отсутствует необходимый ключ в данных. Возможно, проблема с форматом резюме или вакансии.")
            elif "FileNotFoundError" in str(type(e)):
                st.warning("⚠️ Файл не найден. Убедитесь, что файл резюме загружен корректно.")
            
            st.info("💡 **Попробуйте:**\n- Проверить правильность ссылки на вакансию\n- Убедиться, что файл резюме не поврежден\n- Попробовать другую ссылку на вакансию\n- Проверить формат файла резюме (PDF, DOCX, TXT)")
            
            # Логируем полную ошибку для отладки
            import traceback
            with st.expander("🔍 Детали ошибки (для разработчиков)"):
                st.code(traceback.format_exc())
                st.write(f"**Тип ошибки:** {type(e).__name__}")
                st.write(f"**Сообщение:** {error_msg}")


# Информация в боковой панели в стиле Школы 21
with st.sidebar:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {SCHOOL21_BLUE} 0%, {SCHOOL21_GREEN} 100%);
                padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">
        <h2 style="color: white; margin: 0;">ℹ️ О сервисе</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Этот сервис анализирует совместимость вашего резюме с вакансией.
    
    **Что анализируется:**
    - ✅ Обязательные навыки (50%)
    - ⭐ Желательные навыки (30%)
    - 💼 Опыт работы (10%)
    - 🎓 Образование (5%)
    - 🤝 Soft skills (5%)
    
    **Результаты включают:**
    - 📊 Детальную разбивку совместимости
    - 📋 Сводную таблицу навыков
    - 🔍 Gap-анализ с приоритетами
    - 💡 Мотивационные рекомендации
    """)
    
    st.divider()
    
    st.markdown("### 📝 Поддерживаемые форматы")
    st.markdown("- 📄 PDF")
    st.markdown("- 📝 DOCX (Word)")
    st.markdown("- 📄 TXT")
    
    st.divider()
    
    st.markdown("### 🔗 Как загрузить вакансию")
    st.markdown("""
    **Способ 1: По ссылке**
    - Скопируйте ссылку из адресной строки
    - Убедитесь, что вакансия открыта
    - Пример: `https://hh.ru/vacancy/12345678`
    
    **Способ 2: Из файла (рекомендуется)**
    - Скопируйте текст вакансии с сайта
    - Сохраните в файл (.txt, .docx или .pdf)
    - Или загрузите PDF вакансии напрямую
    - Загрузите файл
    - ✅ Более точный анализ
    - ✅ Работает даже если сайт недоступен
    - ✅ Поддерживает PDF, DOCX, TXT
    """)
    
    st.divider()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: {SCHOOL21_BG}; border-radius: 8px;">
        <p style="color: {SCHOOL21_TEXT}; margin: 0; font-size: 0.9em;">
            🎓 Сделано для «Школы 21»
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Обновить страницу", use_container_width=True):
        st.rerun()

