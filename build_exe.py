# -*- coding: utf-8 -*-
"""
前置软件报告生成工具 - 打包脚本
使用：python build_exe.py
功能：1. 使用 PyInstaller 打包（Windows 生成 exe，macOS 生成 .app）
      2. 将依赖的目录和文件复制到 dist 目录

环境变量（可选）：
  MACOSX_DEPLOYMENT_TARGET: macOS 最低部署版本，默认 11.0，可选 11.0-14.0
  TARGET_ARCH:              目标架构 (x86_64 / arm64 / universal2)
"""
import os
import platform
import shutil
import subprocess
import sys

# 平台检测
IS_WINDOWS = sys.platform == 'win32'
IS_MAC = sys.platform == 'darwin'

# ===== macOS 兼容性配置 =====
if IS_MAC:
    # 读取最低部署目标版本 (默认 11.0，支持 11-14)
    macos_min = os.environ.get('MACOSX_DEPLOYMENT_TARGET', '11.0')
    os.environ.setdefault('MACOSX_DEPLOYMENT_TARGET', macos_min)
    # 输出当前配置
    print(f"[macOS 配置] MACOSX_DEPLOYMENT_TARGET = {macos_min}")
    target_arch = os.environ.get('TARGET_ARCH', None)
    if target_arch:
        print(f"[macOS 配置] TARGET_ARCH = {target_arch}")
    else:
        print(f"[macOS 配置] TARGET_ARCH = (使用当前系统架构 {platform.machine()})")

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
PYTHON_EXE = sys.executable

# 根据平台确定 PyInstaller 可执行文件路径
if IS_WINDOWS:
    PYINSTALLER_CMD = os.path.join(os.path.dirname(PYTHON_EXE), "Scripts", "pyinstaller.exe")
else:
    # macOS / Linux: 使用 bin/pyinstaller，找不到则回退到 PATH 中的 pyinstaller
    _candidate = os.path.join(os.path.dirname(PYTHON_EXE), "bin", "pyinstaller")
    PYINSTALLER_CMD = _candidate if os.path.isfile(_candidate) else "pyinstaller"

# PyInstaller spec 文件
SPEC_FILE = os.path.join(PROJECT_ROOT, "前置软件报告生成工具.spec")

# 需要复制到 dist 的目录和文件
DIRS_TO_COPY = [
    # "0.前置软件质控结果统计_doris查询语句",
    # "1.doris查询结果模板",
]
FILES_TO_COPY = [
    "qzrj_quality_report.db",
    "qzrj_generate_data.sql",
    "qzrj_export_sql.sql",
    "前置软件报告导出模板.xlsx",
    "前置软件导出工具使用手册.docx",
    "版本日志.txt"
]


def check_pyinstaller():
    """检查 pyinstaller 是否已安装"""
    try:
        result = subprocess.run(
            [PYTHON_EXE, "-m", "PyInstaller", "--version"],
            capture_output=True,
            check=True,
        )
        print(f"PyInstaller 版本: {result.stdout.decode().strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def clean_old_builds():
    """清理旧的构建目录"""
    for folder in ("build", "dist"):
        folder_path = os.path.join(PROJECT_ROOT, folder)
        if os.path.isdir(folder_path):
            print(f"  删除目录: {folder}")
            shutil.rmtree(folder_path)


def run_pyinstaller():
    """执行 PyInstaller 打包"""
    print("=" * 60)
    print(f"开始执行 PyInstaller 打包...")
    print(f"操作系统：{platform.system()} {platform.release()}")
    print(f"Python：{sys.version.split()[0]}")
    print(f"PyInstaller：{PYINSTALLER_CMD}")
    print("=" * 60)

    cmd = [PYINSTALLER_CMD, "--clean", "--noconfirm", SPEC_FILE]
    print(f"执行命令：{' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise Exception(f"PyInstaller 打包失败，返回码：{result.returncode}")

    print("\n✓ PyInstaller 打包完成！\n")


def copy_to_dist():
    """将依赖目录和文件复制到 dist 目录"""
    print("=" * 60)
    print("复制依赖文件到 dist 目录...")
    print("=" * 60)

    # 确保 dist 目录存在
    os.makedirs(DIST_DIR, exist_ok=True)

    # 复制目录
    for dir_name in DIRS_TO_COPY:
        src = os.path.join(PROJECT_ROOT, dir_name)
        dst = os.path.join(DIST_DIR, dir_name)
        if os.path.isdir(src):
            # 清理旧目录再复制
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  [OK] 目录：{dir_name}")
        else:
            print(f"  [!] 目录不存在：{dir_name}")

    # 复制文件
    for file_name in FILES_TO_COPY:
        src = os.path.join(PROJECT_ROOT, file_name)
        dst = os.path.join(DIST_DIR, file_name)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  [OK] 文件：{file_name}")
        else:
            print(f"  [!] 文件不存在：{file_name}")

    print("\n✓ 文件复制完成！\n")


def show_result():
    """显示 dist 目录中的内容"""
    print("=" * 60)
    print("dist 目录内容：")
    print("=" * 60)
    if os.path.isdir(DIST_DIR):
        for item in sorted(os.listdir(DIST_DIR)):
            item_path = os.path.join(DIST_DIR, item)
            size = ""
            if os.path.isfile(item_path):
                size_bytes = os.path.getsize(item_path)
                if size_bytes > 1024 * 1024:
                    size = f" ({size_bytes / 1024 / 1024:.1f} MB)"
                elif size_bytes > 1024:
                    size = f" ({size_bytes / 1024:.1f} KB)"
            elif os.path.isdir(item_path) and item.endswith('.app'):
                size = " (macOS 应用)"
            print(f"  - {item}{size}")
    print("\n" + "=" * 60)
    print(f"产物路径：{DIST_DIR}")
    if IS_MAC:
        app_path = os.path.join(DIST_DIR, "前置软件报告生成工具.app")
        if os.path.isdir(app_path):
            print(f"macOS 应用：{app_path}")
    elif IS_WINDOWS:
        exe_path = os.path.join(DIST_DIR, "前置软件报告生成工具.exe")
        if os.path.isfile(exe_path):
            print(f"Windows 可执行文件：{exe_path}")
    print("=" * 60)


def main():
    try:
        print_separator = lambda: print("=" * 60)
        print_separator()
        print("   前置软件报告生成工具 - 打包构建")
        print_separator()
        print()

        # 1. 检查 pyinstaller
        print("[1/4] 检查 PyInstaller...")
        if not check_pyinstaller():
            print("  [错误] 未找到 PyInstaller，请先安装依赖:")
            print("         pip install pyinstaller")
            sys.exit(1)
        print("  检查通过")
        print()

        # 2. 清理旧文件
        print("[2/4] 清理旧构建文件...")
        clean_old_builds()
        print("  清理完成")
        print()

        # 3. 执行打包
        print("[3/4] 开始打包...")
        run_pyinstaller()

        # 4. 复制文件
        print("[4/4] 复制额外文件到 dist...")
        copy_to_dist()

        show_result()
        print("\n✓ 打包全部完成！")
    except Exception as e:
        print(f"\n✗ 打包失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
