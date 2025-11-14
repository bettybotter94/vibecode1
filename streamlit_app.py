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
        
        # Прогресс-бар с градиентом Школы 21
        progress_html = f"""
        <div style="background: {SCHOOL21_BG}; border-radius: 10px; height: 30px; margin: 20px 0;">
            <div style="background: linear-gradient(90deg, {SCHOOL21_BLUE} 0%, {SCHOOL21_GREEN} 100%);
                        width: {compatibility}%; height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
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
                
                # Прогресс-бар для категории
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{name}**")
                    # Кастомный прогресс-бар
                    progress_color = SCHOOL21_GREEN if percentage >= 80 else SCHOOL21_BLUE if percentage >= 50 else "#FF6B6B"
                    st.markdown(f"""
                    <div style="background: {SCHOOL21_BG}; border-radius: 5px; height: 25px; margin: 5px 0;">
                        <div style="background: {progress_color}; width: {percentage}%; height: 100%; 
                                    border-radius: 5px; display: flex; align-items: center; padding-left: 10px;">
                            <span style="color: white; font-weight: bold;">{score}/{max_score} ({percentage}%)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if details:
                        for detail in details:
                            st.caption(f"  • {detail}")
                
                with col2:
                    st.metric("", f"{percentage}%")
        
        st.divider()
    
    # Сводная таблица навыков
    skills_table = result.get('skills_table', [])
    if skills_table:
        st.subheader("📋 Сводная таблица навыков")
        
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
            Загрузите ваше резюме и ссылку на вакансию для анализа совместимости
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
    st.markdown("### 🔗 Ссылка на вакансию")
    job_url = st.text_input(
        "Вставьте URL вакансии",
        placeholder="https://hh.ru/vacancy/12345678",
        help="Вставьте ссылку на вакансию с любого сайта (HeadHunter, Habr и т.д.)",
        label_visibility="collapsed"
    )
    if job_url:
        st.info(f"🔗 Анализируем: {job_url[:50]}...")

# Кнопка анализа в стиле Школы 21
st.markdown("<br>", unsafe_allow_html=True)
analyze_button = st.button("🔍 Анализировать совместимость", type="primary", use_container_width=True)

# Обработка анализа
if analyze_button:
    # Валидация входных данных
    if not uploaded_file:
        st.error("❌ Пожалуйста, загрузите файл резюме")
        st.stop()
    
    if not job_url:
        st.error("❌ Пожалуйста, введите ссылку на вакансию")
        st.stop()
    
    # Показываем индикатор загрузки
    with st.spinner("⏳ Анализируем резюме и вакансию... Это может занять несколько секунд"):
        try:
            # Сохраняем загруженный файл во временную директорию
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name
            
            try:
                # Парсим резюме
                resume_data = resume_parser.parse(temp_file_path)
                
                # Парсим вакансию
                job_data = job_parser.parse(job_url)
                
                # Анализируем совместимость
                analysis_result = analyzer.analyze(resume_data, job_data)
                
                # Отображаем результаты
                display_results(analysis_result)
                
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        
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
    
    st.markdown("### 🔗 Как использовать ссылки")
    st.markdown("""
    **HeadHunter (hh.ru):**
    - Скопируйте ссылку из адресной строки
    - Убедитесь, что вакансия открыта
    - Пример: `https://hh.ru/vacancy/12345678`
    
    **Другие сайты:**
    - Работают ссылки с большинства сайтов
    - Ссылка должна начинаться с http:// или https://
    """)
    
    st.divider()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background: {SCHOOL21_BG}; border-radius: 8px;">
        <p style="color: {SCHOOL21_TEXT}; margin: 0; font-size: 0.9em;">
            🎓 Сделано для Школы 21
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Обновить страницу", use_container_width=True):
        st.rerun()

