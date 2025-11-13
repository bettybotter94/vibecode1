"""
FastAPI приложение для анализа совместимости резюме и вакансий
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import aiofiles

from resume_parser import ResumeParser
from job_parser import JobParser
from analyzer import CompatibilityAnalyzer

app = FastAPI(title="CV Analysis Service", version="1.0.0")

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем директорию для временных файлов
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Инициализируем парсеры и анализатор
resume_parser = ResumeParser()
job_parser = JobParser()
analyzer = CompatibilityAnalyzer()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "message": "Сервис работает"}


@app.post("/api/analyze")
async def analyze_resume_and_job(
    resume: UploadFile = File(...),
    job_url: str = Form(...)
):
    """
    Анализирует резюме и вакансию
    
    Args:
        resume: Загруженный файл резюме
        job_url: URL вакансии
    
    Returns:
        JSON с результатами анализа
    """
    try:
        # 1. Сохраняем загруженный файл
        file_ext = os.path.splitext(resume.filename)[1].lower()
        if file_ext not in ['.pdf', '.docx', '.txt']:
            raise HTTPException(
                status_code=400,
                detail="Неподдерживаемый формат файла. Используйте PDF, DOCX или TXT"
            )
        
        temp_file_path = os.path.join(TEMP_DIR, f"resume_{os.urandom(8).hex()}{file_ext}")
        
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await resume.read()
            await out_file.write(content)
        
        try:
            # 2. Парсим резюме
            resume_data = resume_parser.parse(temp_file_path)
            
            # 3. Парсим вакансию
            job_data = job_parser.parse(job_url)
            
            # 4. Анализируем совместимость
            analysis_result = analyzer.analyze(resume_data, job_data)
            
            return JSONResponse(content={
                "success": True,
                "result": analysis_result
            })
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=str(e),
            headers={"X-Error-Type": "ValidationError"}
        )
    except Exception as e:
        import traceback
        error_details = str(e)
        # Логируем полную ошибку для отладки
        import logging
        logging.error(f"Ошибка при анализе: {error_details}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка: {error_details}",
            headers={"X-Error-Type": "InternalError"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

