@echo off
echo.
echo ================================================================
echo    LEGALIZE AI MUSIC - DEMO TEST
echo ================================================================
echo.
echo This will test if the app works...
echo.
pause

cd /mnt/d/AI_Projects/ralph_app/src

echo.
echo [TEST 1] Checking Ollama...
python -c "import urllib.request; print('Ollama Status:', urllib.request.urlopen('http://localhost:11434/api/version').read().decode())"

echo.
echo [TEST 2] Testing CLI Connection...
..\venv\Scripts\python.exe -m workflow.cli test-ollama --model llama3.1:8b

echo.
echo [TEST 3] Checking Status...
..\venv\Scripts\python.exe -m workflow.cli status

echo.
echo [TEST 4] Running AI Task (this takes 10-20 seconds)...
..\venv\Scripts\python.exe -m workflow.cli start --prompt "What is MIDI?" --model llama3.1:8b

echo.
echo ================================================================
echo    DEMO COMPLETE!
echo ================================================================
echo.
pause
