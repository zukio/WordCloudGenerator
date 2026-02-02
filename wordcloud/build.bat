@echo off
chcp 65001 > nul
echo ========================================
echo WordCloud Generator - EXE ビルドスクリプト
echo ========================================
echo.

cd /d %~dp0

REM 仮想環境のPythonパスを設定
set PYTHON_EXE=..\venv\Scripts\python.exe

REM Pythonが存在するか確認
if not exist "%PYTHON_EXE%" (
    echo エラー: 仮想環境のPythonが見つかりません
    echo パス: %PYTHON_EXE%
    pause
    exit /b 1
)

echo 仮想環境のPythonを使用: %PYTHON_EXE%
echo.

REM PyInstallerのインストール確認
echo PyInstallerの確認中...
%PYTHON_EXE% -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstallerがインストールされていません
    echo インストール中...
    %PYTHON_EXE% -m pip install pyinstaller
    if errorlevel 1 (
        echo エラー: PyInstallerのインストールに失敗しました
        pause
        exit /b 1
    )
) else (
    echo PyInstallerが見つかりました
)
echo.

REM 既存のビルド成果物を削除
echo 既存のビルドファイルをクリーンアップ中...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo.

REM PyInstallerでEXEを作成
echo EXEファイルをビルド中...
echo.

REM アイコンファイルの確認
set ICON_PARAM=
if exist "assets\icon.ico" (
    echo アイコンファイルを使用: assets\icon.ico
    set ICON_PARAM=--icon "assets\icon.ico"
) else (
    echo 警告: assets\icon.ico が見つかりません（アイコンなしでビルド）
)

%PYTHON_EXE% -m PyInstaller ^
    --onedir ^
    --noconsole ^
    --name "WordCloudGenerator" ^
    --add-data "content/Noto_Sans_JP;content/Noto_Sans_JP" ^
    %ICON_PARAM% ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo エラー: ビルドに失敗しました
    pause
    exit /b 1
)

echo.
echo ユーザー編集可能ファイルをコピー中...

REM ユーザー編集可能なファイルをdistフォルダにコピー
if not exist "dist\WordCloudGenerator\config.json" (
    copy "config.json" "dist\WordCloudGenerator\" > nul
    echo   config.json をコピーしました
)

if not exist "dist\WordCloudGenerator\content" (
    mkdir "dist\WordCloudGenerator\content"
)

if not exist "dist\WordCloudGenerator\content\sample_text.txt" (
    copy "content\sample_text.txt" "dist\WordCloudGenerator\content\" > nul
    echo   content\sample_text.txt をコピーしました
)

if exist "content\cat.png" (
    if not exist "dist\WordCloudGenerator\content\cat.png" (
        copy "content\cat.png" "dist\WordCloudGenerator\content\" > nul
        echo   content\cat.png をコピーしました
    )
)

if not exist "dist\WordCloudGenerator\logs" (
    mkdir "dist\WordCloudGenerator\logs"
    echo   logs フォルダを作成しました
)

echo.
echo ========================================
echo ビルド完了！
echo ========================================
echo 実行ファイル: dist\WordCloudGenerator\WordCloudGenerator.exe
echo.
echo 以下のファイルをユーザーが編集できます：
echo   - dist\WordCloudGenerator\config.json
echo   - dist\WordCloudGenerator\content\sample_text.txt
echo   - dist\WordCloudGenerator\content\cat.png
echo.
echo 配布する場合は dist\WordCloudGenerator フォルダ全体を配布してください
echo.
pause
