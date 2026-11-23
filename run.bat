@echo off
echo ========================================================
echo Levantando Sistema Intelligence de Grado de Produccion
echo ========================================================

call venv\Scripts\activate
uvicorn App.main:app --host 0.0.0.0 --port 8000 --reload