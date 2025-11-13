@echo off
REM Скрипт для запуска Streamlit приложения на Windows (можно запустить двойным кликом)

cd /d "%~dp0"

echo ==========================================
echo   Запуск сервиса анализа резюме
echo ==========================================
echo.

REM Проверяем наличие Python
echo [ПРОВЕРКА] Поиск Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установите Python 3.8 или выше:
    echo https://www.python.org/downloads/
    echo.
    echo При установке обязательно отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Найден: %PYTHON_VERSION%
echo.

REM Проверяем наличие pip
echo [ПРОВЕРКА] Поиск pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] pip не найден!
    echo Переустановите Python с опцией "pip"
    pause
    exit /b 1
)
echo [OK] pip найден
echo.

REM Устанавливаем зависимости
echo [УСТАНОВКА] Проверка зависимостей...
echo Это может занять несколько минут при первом запуске...
echo.
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Ошибка при установке зависимостей!
    echo Попробуйте выполнить вручную: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Зависимости установлены
echo.

REM Проверяем наличие streamlit
echo [ПРОВЕРКА] Проверка Streamlit...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [УСТАНОВКА] Streamlit не найден, устанавливаем...
    python -m pip install streamlit
)
echo [OK] Streamlit готов
echo.

echo [ЗАПУСК] Запуск приложения...
echo [ИНФО] Откроется браузер автоматически через несколько секунд
echo.
echo [ИНФО] Для остановки закройте это окно или нажмите Ctrl+C
echo.

REM Запускаем Streamlit
python -m streamlit run streamlit_app.py

echo.
echo Приложение закрыто.
pause

