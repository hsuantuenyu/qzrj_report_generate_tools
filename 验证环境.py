# -*- coding: utf-8 -*-
"""
快速验证脚本 - 使用指定 Python 路径
"""

import sys
import os

print("=" * 70)
print("Report Generator 环境验证")
print("=" * 70)
print()

print(f"Python 版本：{sys.version}")
print(f"Python 路径：{sys.executable}")
print()

# 检查依赖包
print("检查依赖包:")
dependencies = {
    'tkinter': 'tkinter',
    'duckdb': 'duckdb',
    'pandas': 'pandas',
    'openpyxl': 'openpyxl'
}

all_installed = True
for name, module in dependencies.items():
    try:
        __import__(module)
        print(f"  [OK] {name}")
    except ImportError:
        print(f"  [MISSING] {name}")
        all_installed = False

print()

# 检查代码文件
print("检查代码文件:")
files_to_check = [
    'report_generator.py',
    'qzrj_quality_report.db',
    'qzrj_generate_data.sql'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  [OK] {file}")
    else:
        print(f"  [NOT FOUND] {file}")

print()

# 验证代码修改
print("验证代码修改:")
with open('report_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

modifications = {
    '禁用最大化': 'self.root.resizable(False, False)',
    '合计行检测': 'has_total_row',
    '批量写入': 'ws.append(row_values)'
}

for name, code in modifications.items():
    if code in content:
        print(f"  [OK] {name}")
    else:
        print(f"  [NOT FOUND] {name}")

print()
print("=" * 70)
if all_installed:
    print("[SUCCESS] 所有依赖已安装，可以运行程序!")
    print()
    print("下一步:")
    print("  1. 双击运行 '启动程序.bat'")
    print("  2. 或在命令行运行：D:\\SoftWare\\Python\\Python312\\python.exe report_generator.py")
else:
    print("[ERROR] 部分依赖未安装，请先运行 '安装依赖.bat'")
print("=" * 70)
