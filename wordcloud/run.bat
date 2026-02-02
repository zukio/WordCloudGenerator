@echo off
chcp 65001 > nul
echo ========================================
echo WordCloud Generator - 実行スクリプト
echo ========================================
echo.

cd /d %~dp0

REM 仮想環境のPythonパスを設定
set PYTHON_EXE=..\venv\Scripts\python.exe

REM Pythonが存在するか確認
if not exist "%PYTHON_EXE%" (
    echo エラー: 仮想環境のPythonが見つかりません
    echo パス: %PYTHON_EXE%
    echo.
    echo 仮想環境を作成してください:
    echo   python -m venv ..\venv
    echo   ..\venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 必要なパッケージがインストールされているか確認
echo 必要なパッケージを確認中...
%PYTHON_EXE% -c "import wordcloud, MeCab" 2>nul
if errorlevel 1 (
    echo 警告: 必要なパッケージがインストールされていない可能性があります
    echo 依存関係をインストールしますか？ (Y/N)
    set /p INSTALL_DEPS=選択: 
    if /i "%INSTALL_DEPS%"=="Y" (
        echo.
        echo パッケージをインストール中...
        %PYTHON_EXE% -m pip install -r requirements.txt
        if errorlevel 1 (
            echo エラー: パッケージのインストールに失敗しました
            pause
            exit /b 1
        )
    )
)

echo.
echo WordCloud Generatorを起動中...
echo キーボードショートカット: Homeキーでテキストを再読み込み
echo.
echo ========================================
echo.

REM アプリケーションを実行
%PYTHON_EXE% main.py %*

if errorlevel 1 (
    echo.
    echo エラー: アプリケーションの実行中にエラーが発生しました
    pause
    exit /b 1
)

echo.
echo アプリケーションが終了しました
pause
