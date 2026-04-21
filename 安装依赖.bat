@echo off
chcp 65001 >nul
echo ================================================
echo 安装 Python 依赖包
echo ================================================
echo.

set PYTHON="D:\SoftWare\Python\Python312\python.exe"

echo 正在安装必要的依赖包...
echo.

echo [1/3] 安装 duckdb...
%PYTHON% -m pip install duckdb --upgrade

echo.
echo [2/3] 安装 pandas...
%PYTHON% -m pip install pandas --upgrade

echo.
echo [3/3] 安装 openpyxl...
%PYTHON% -m pip install openpyxl --upgrade

echo.
echo [4/4] 安装 tkcalendar...
%PYTHON% -m pip install tkcalendar --upgrade

echo.
echo ================================================
echo 安装完成!
echo.
echo 提示：tkinter 通常随 Python 一起安装，无需单独安装
echo ================================================
echo.
pause
