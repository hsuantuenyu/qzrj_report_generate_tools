#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前置软件报告生成工具 - 打包构建脚本
用法: python build_exe.py
"""

import os
import shutil
import subprocess
import sys


def print_separator():
    print("=" * 42)


def check_pyinstaller():
    """检查 pyinstaller 是否已安装"""
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def clean_old_builds():
    """清理旧的构建目录"""
    for folder in ("build", "dist"):
        if os.path.isdir(folder):
            print(f"  删除目录: {folder}")
            shutil.rmtree(folder)


def copy_extra_files():
    """打包完成后复制额外文件和目录到 dist"""
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        return

    items_to_copy = [
        "qzrj_export_sql.sql",
        "qzrj_generate_data.sql",
        "前置软件报告导出模板.xlsx",
        "前置软件导出工具使用手册.docx",
        "qzrj_quality_report.db",
        "0.前置软件质控结果统计_doris查询语句",
        "1.doris查询结果模板",
    ]

    print("[4/4] 复制额外文件到 dist...")
    for item in items_to_copy:
        if not os.path.exists(item):
            print(f"  跳过（不存在）: {item}")
            continue

        dest = os.path.join(dist_dir, item)
        try:
            if os.path.isdir(item):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
                print(f"  复制目录: {item}")
            else:
                shutil.copy2(item, dest)
                print(f"  复制文件: {item}")
        except Exception as e:
            print(f"  复制失败: {item} - {e}")
    print("  复制完成")


def build_exe():
    """执行打包"""
    print_separator()
    print("   前置软件报告生成工具 - 打包构建")
    print_separator()
    print()

    # 1. 检查 pyinstaller
    print("[1/3] 检查 PyInstaller...")
    if not check_pyinstaller():
        print("  [错误] 未找到 PyInstaller，请先安装依赖:")
        print("         pip install pyinstaller")
        input("\n按回车键退出...")
        sys.exit(1)
    print("  检查通过")
    print()

    # 2. 清理旧文件
    print("[2/3] 清理旧构建文件...")
    clean_old_builds()
    print("  清理完成")
    print()

    # 3. 执行打包
    print("[3/3] 开始打包 EXE...")
    spec_file = "前置软件报告生成工具.spec"
    if not os.path.exists(spec_file):
        print(f"  [错误] 找不到 spec 文件: {spec_file}")
        input("\n按回车键退出...")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", spec_file],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    print()
    if result.returncode == 0 and os.path.exists("dist\前置软件报告生成工具.exe"):
        copy_extra_files()
        print()
        print_separator()
        print("   打包成功！")
        print("   输出文件: dist\前置软件报告生成工具.exe")
        print_separator()
    else:
        print_separator()
        print("   打包失败，请检查上方错误信息")
        print_separator()

    input("\n按回车键退出...")


if __name__ == "__main__":
    build_exe()
