@echo off
chcp 65001 >nul
echo ================================================
echo 检查 Python 依赖包
echo ================================================
echo.

set PYTHON="D:\SoftWare\Python\Python312\python.exe"

echo 正在检查依赖包...
echo.

%PYTHON% -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [缺失] tkinter
) else (
    echo [已安装] tkinter
)

%PYTHON% -c "import duckdb" 2>nul
if errorlevel 1 (
    echo [缺失] duckdb
) else (
    echo [已安装] duckdb
)

%PYTHON% -c "import pandas" 2>nul
if errorlevel 1 (
    echo [缺失] pandas
) else (
    echo [已安装] pandas
)

%PYTHON% -c "import openpyxl" 2>nul
if errorlevel 1 (
    echo [缺失] openpyxl
) else (
    echo [已安装] openpyxl
)

echo.
echo ================================================
echo 如需安装缺失的依赖包，请运行:
echo %PYTHON% -m pip install duckdb pandas openpyxl
echo ================================================
echo.
pause
