@echo off
cd /d %~dp0

:: Check if virtual environment exists
if not exist venv\Scripts\activate (
    echo 仮想環境が見つかりません。作成します...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Start the application
echo マッチング返信AIアプリを起動しています...
echo ブラウザで http://127.0.0.1:8000 にアクセスしてください
echo.
echo ［Ctrl+C］で停止できます
echo.

python -m api.app