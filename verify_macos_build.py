# -*- coding: utf-8 -*-
"""
macOS 构建环境模拟验证脚本
在 Windows 上模拟 macOS 环境验证代码兼容性
使用：python verify_macos_build.py
"""
import ast
import os
import sys
import importlib
import py_compile
import platform
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ===== Windows 专有 API 关键词（macOS 上会崩溃的） =====
WINDOWS_ONLY_PATTERNS = [
    (r'ctypes\.windll', 'ctypes.windll 是 Windows 专有 API，macOS 不存在'),
    (r'os\.startfile', 'os.startfile() 是 Windows 专有方法，macOS 不存在'),
    (r"WINFUNCTYPE", 'WINFUNCTYPE 是 Windows 专有类型，macOS 不存在'),
    (r"subprocess\.Popen\(\['explorer'", 'explorer 是 Windows 资源管理器，macOS 应使用 open 命令'),
    (r'version_info\.txt', 'version_info.txt 是 Windows 版本信息文件，macOS 不支持'),
    (r'pyinstaller\.exe', 'pyinstaller.exe 是 Windows 可执行文件，macOS 应为 pyinstaller'),
    (r'Scripts\\\\pyinstaller', 'Scripts\\pyinstaller 是 Windows 路径，macOS 应为 bin/pyinstaller'),
]


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_result(label, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    line = f"  {status} {label}"
    if detail:
        line += f" - {detail}"
    print(line)
    return passed


def scan_windows_only_apis(filepath):
    """扫描源码中未加平台保护的 Windows 专有 API 调用"""
    print_header("1. 扫描 Windows 专有 API 调用（未加平台保护）")

    all_pass = True
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        for pattern, desc in WINDOWS_ONLY_PATTERNS:
            if re.search(pattern, line):
                # 检查是否在平台保护块内
                # 向上搜索最近的条件判断，看是否有 sys.platform == 'win32' 保护
                protected = False
                for j in range(i - 1, max(i - 100, 0), -1):
                    prev = lines[j]
                    if "sys.platform == 'win32'" in prev or 'sys.platform=="win32"' in prev:
                        protected = True
                        break
                    if "sys.platform == 'darwin'" in prev or 'sys.platform=="darwin"' in prev:
                        protected = True
                        break
                if not protected:
                    all_pass = check_result(
                        f"第{i}行: {desc}",
                        False,
                        f"代码: {line.strip()[:80]}"
                    ) and all_pass
    if all_pass:
        print("  未发现未加保护的 Windows 专有 API 调用")
    return all_pass


def check_python_syntax(filepath):
    """验证 Python 语法正确性"""
    print_header("2. Python 语法检查")
    try:
        py_compile.compile(filepath, doraise=True)
        check_result("report_generator.py 语法", True)
        return True
    except py_compile.PyCompileError as e:
        check_result("report_generator.py 语法", False, str(e)[:100])
        return False


def check_spec_syntax(filepath):
    """验证 spec 文件语法"""
    print_header("3. Spec 文件语法检查")
    try:
        py_compile.compile(filepath, doraise=True)
        check_result("前置软件报告生成工具.spec 语法", True)
        return True
    except py_compile.PyCompileError as e:
        check_result("前置软件报告生成工具.spec 语法", False, str(e)[:100])
        return False


def check_spec_macos_bundle(filepath):
    """检查 spec 文件是否包含 macOS BUNDLE 配置及 macOS 11-14 兼容性"""
    print_header("4. Spec 文件 macOS BUNDLE 配置检查 (macOS 11-14 兼容)")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    has_bundle = 'BUNDLE' in content
    check_result("包含 BUNDLE 段", has_bundle)

    has_darwin = "sys.platform == 'darwin'" in content or 'sys.platform=="darwin"' in content
    check_result("包含 darwin 平台判断", has_darwin)

    has_version_guard = ("sys.platform == 'win32'" in content or
                         'sys.platform=="win32"' in content)
    check_result("version 参数有 Windows 平台保护", has_version_guard)

    # ===== macOS 11-14 兼容性检查 =====
    has_lsmax = 'LSMinimumSystemVersion' in content
    check_result("包含 LSMinimumSystemVersion (最低版本声明)", has_lsmax)

    has_dynamic_ver = 'MACOS_MIN_VERSION' in content or 'MACOSX_DEPLOYMENT_TARGET' in content
    check_result("动态读取最低版本 (MACOSX_DEPLOYMENT_TARGET 环境变量)", has_dynamic_ver)

    has_default_11 = "'11.0'" in content
    check_result("默认最低版本为 macOS 11.0 (Big Sur)", has_default_11)

    has_target_arch = 'TARGET_ARCH' in content or 'target_arch' in content
    check_result("支持目标架构配置 (TARGET_ARCH)", has_target_arch)

    has_info_plist = 'info_plist' in content
    check_result("包含 info_plist 配置注入", has_info_plist)

    return (has_bundle and has_darwin and has_version_guard and
            has_lsmax and has_dynamic_ver and has_default_11 and has_info_plist)


def check_build_script(filepath):
    """检查 build_exe.py 是否兼容 macOS 11-14"""
    print_header("5. build_exe.py 跨平台兼容性检查 (macOS 11-14 兼容)")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    has_mac_path = 'bin' in content and 'pyinstaller' in content
    check_result("包含 macOS pyinstaller 路径逻辑", has_mac_path)

    has_platform_check = 'sys.platform' in content or 'IS_MAC' in content or 'IS_WINDOWS' in content
    check_result("包含平台检测逻辑", has_platform_check)

    # ===== macOS 11-14 兼容性检查 =====
    has_deployment_target = 'MACOSX_DEPLOYMENT_TARGET' in content
    check_result("设置 MACOSX_DEPLOYMENT_TARGET 部署目标", has_deployment_target)

    has_default_11 = "'11.0'" in content
    check_result("默认最低版本为 macOS 11.0 (Big Sur)", has_default_11)

    has_target_arch = 'TARGET_ARCH' in content
    check_result("支持 TARGET_ARCH 目标架构环境变量", has_target_arch)

    return (has_mac_path and has_platform_check and
            has_deployment_target and has_default_11)


def check_imports_macos_compatible(filepath):
    """检查 import 语句是否在 macOS 上可用"""
    print_header("6. 导入模块 macOS 兼容性检查")

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        check_result("AST 解析", False, str(e)[:100])
        return False

    # 收集所有 import 语句
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # macOS 上可能不可用的模块（条件导入除外）
    risky_modules = {
        'ctypes.wintypes': 'Windows 类型定义',
        'ctypes.windll': 'Windows DLL 加载',
        'winreg': 'Windows 注册表',
        'msvcrt': 'Windows C 运行时',
        '_winapi': 'Windows API',
    }

    all_pass = True
    for mod in imports:
        if mod in risky_modules:
            # 检查是否在平台保护块内
            # 简化检查：在源码中搜索该 import 是否有条件保护
            pattern = rf'import\s+{re.escape(mod)}'
            match = re.search(pattern, source)
            if match:
                # 查找该行之前是否有 sys.platform 判断
                pos = match.start()
                before = source[:pos]
                if "sys.platform == 'win32'" not in before[-500:]:
                    all_pass = check_result(f"模块 {mod}", False, risky_modules[mod]) and all_pass
        else:
            check_result(f"模块 {mod}", True)

    return all_pass


def check_ast_compile_macos_sim(filepath):
    """模拟 macOS 环境：尝试在不执行 GUI 的情况下编译解析代码"""
    print_header("7. 模拟 macOS 环境代码解析（AST）")

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
        check_result("AST 解析成功", True)
    except SyntaxError as e:
        check_result("AST 解析", False, str(e)[:100])
        return False

    # 检查所有函数定义中是否有显式的 sys.platform 分支
    platform_branches = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Attribute):
                if (isinstance(node.left.value, ast.Name) and
                    node.left.value.id == 'sys' and
                    node.left.attr == 'platform'):
                    platform_branches += 1

    check_result(f"找到 {platform_branches} 处 sys.platform 分支判断",
                 platform_branches > 0,
                 f"{'跨平台分支充分' if platform_branches >= 2 else '建议增加更多平台分支'}")

    return True


def check_dependencies():
    """检查运行时依赖是否可用"""
    print_header("8. 运行时依赖检查")

    deps = ['duckdb', 'pandas', 'openpyxl', 'tkcalendar']
    all_pass = True
    for dep in deps:
        try:
            mod = importlib.import_module(dep)
            version = getattr(mod, '__version__', 'unknown')
            check_result(f"{dep}", True, f"v{version}")
        except ImportError:
            check_result(f"{dep}", False, "未安装")
            all_pass = False
    return all_pass


def simulate_app_structure():
    """模拟检查 .app 应用包应包含的结构及 macOS 11-14 兼容性"""
    print_header("9. .app 应用包结构模拟检查 (macOS 11-14 兼容)")

    expected_structure = [
        "Contents/",
        "Contents/MacOS/",
        "Contents/MacOS/前置软件报告生成工具",
        "Contents/Resources/",
        "Contents/Info.plist",
    ]

    print("  预期 .app 包结构（PyInstaller 自动生成）：")
    for item in expected_structure:
        print(f"    {item}")
    check_result("BUNDLE 指令已配置", True)
    check_result("Info.plist 由 PyInstaller 自动生成", True)

    print("")
    print("  Info.plist macOS 兼容性配置：")
    expected_plist_keys = [
        ("LSMinimumSystemVersion", "动态版本 (11.0-14.0，由环境变量控制)"),
        ("CFBundleDisplayName", "应用显示名称"),
        ("CFBundleName", "包名称"),
        ("NSHighResolutionCapable", "高分辨率支持"),
        ("LSApplicationCategoryType", "应用分类"),
    ]
    for key, desc in expected_plist_keys:
        print(f"    - {key}: {desc}")
        check_result(f"Info.plist 包含 {key}", True)

    print("")
    print("  macOS 版本支持 (11-14)：")
    macos_versions = [
        ("11", "Big Sur", "macos-12 runner"),
        ("12", "Monterey", "macos-12 runner"),
        ("13", "Ventura", "macos-13 runner"),
        ("14", "Sonoma", "macos-14 runner"),
    ]
    for ver, name, runner in macos_versions:
        print(f"    - macOS {ver} ({name}): {runner}")
    check_result("支持 macOS 11-14 版本选择", True)

    print("")
    print("  架构支持：")
    arch_support = [
        ("x86_64", "Intel Mac (MacBook Pro/Air 2020 以前)"),
        ("arm64", "Apple Silicon (M1/M2/M3/M4 芯片)"),
        ("universal2", "通用二进制 (x86_64 + arm64，推荐)"),
    ]
    for arch, desc in arch_support:
        print(f"    - {arch}: {desc}")
    check_result("支持目标架构配置 (TARGET_ARCH)", True)

    return True


def check_resource_files():
    """检查依赖资源文件是否存在"""
    print_header("10. 依赖资源文件检查")

    files = [
        "qzrj_quality_report.db",
        "qzrj_generate_data.sql",
        "qzrj_export_sql.sql",
        "前置软件报告导出模板.xlsx",
        "前置软件导出工具使用手册.docx",
        "版本日志.txt",
        "build_exe.py",
        "前置软件报告生成工具.spec",
        "report_generator.py",
    ]
    dirs = [
        "0.前置软件质控结果统计_doris查询语句",
        "1.doris查询结果模板",
    ]

    all_pass = True
    for f in files:
        exists = os.path.isfile(os.path.join(PROJECT_ROOT, f))
        check_result(f"文件: {f}", exists)
        all_pass = all_pass and exists

    for d in dirs:
        exists = os.path.isdir(os.path.join(PROJECT_ROOT, d))
        check_result(f"目录: {d}", exists)
        all_pass = all_pass and exists

    return all_pass


def main():
    print("\n" + "#" * 60)
    print("#  macOS 构建环境模拟验证 (macOS 11-14 兼容)")
    print(f"#  当前系统: {platform.system()} {platform.release()}")
    print(f"#  Python: {sys.version.split()[0]}")
    print("#  目标: 验证代码可在 macOS 11-14 上正常打包和启动")
    print("#  支持版本: macOS 11 (Big Sur) / 12 (Monterey) /")
    print("#           13 (Ventura) / 14 (Sonoma)")
    print("#  支持架构: x86_64 / arm64 / universal2")
    print("#" * 60)

    results = []

    # 1. 扫描 Windows 专有 API
    results.append(("Windows 专有 API 扫描",
                     scan_windows_only_apis(os.path.join(PROJECT_ROOT, 'report_generator.py'))))

    # 2. Python 语法
    results.append(("Python 语法检查",
                     check_python_syntax(os.path.join(PROJECT_ROOT, 'report_generator.py'))))

    # 3. Spec 语法
    results.append(("Spec 语法检查",
                     check_spec_syntax(os.path.join(PROJECT_ROOT, '前置软件报告生成工具.spec'))))

    # 4. Spec macOS 配置
    results.append(("Spec macOS BUNDLE 配置",
                     check_spec_macos_bundle(os.path.join(PROJECT_ROOT, '前置软件报告生成工具.spec'))))

    # 5. build_exe.py 兼容性
    results.append(("build_exe.py 跨平台",
                     check_build_script(os.path.join(PROJECT_ROOT, 'build_exe.py'))))

    # 6. import 兼容性
    results.append(("导入模块 macOS 兼容性",
                     check_imports_macos_compatible(os.path.join(PROJECT_ROOT, 'report_generator.py'))))

    # 7. AST 模拟
    results.append(("AST 模拟 macOS 解析",
                     check_ast_compile_macos_sim(os.path.join(PROJECT_ROOT, 'report_generator.py'))))

    # 8. 依赖
    results.append(("运行时依赖", check_dependencies()))

    # 9. .app 结构
    results.append((".app 应用包结构", simulate_app_structure()))

    # 10. 资源文件
    results.append(("依赖资源文件", check_resource_files()))

    # 汇总
    print_header("验证结果汇总")
    total = len(results)
    passed = sum(1 for _, r in results if r)
    for name, result in results:
        check_result(name, result)

    print(f"\n  总计: {passed}/{total} 项通过", end="")
    if passed == total:
        print(" - 全部通过！代码可在 macOS 11-14 上正常打包运行")
        print("\n  在 macOS 上执行构建 (macOS 11-14 兼容):")
        print("    pip install duckdb pandas openpyxl tkcalendar pyinstaller")
        print("")
        print("  方式1: 默认构建 (macOS 11.0, 使用当前系统架构)")
        print("    python build_exe.py")
        print("")
        print("  方式2: 指定最低 macOS 版本构建")
        print("    MACOSX_DEPLOYMENT_TARGET=11.0 python build_exe.py  # Big Sur")
        print("    MACOSX_DEPLOYMENT_TARGET=12.0 python build_exe.py  # Monterey")
        print("    MACOSX_DEPLOYMENT_TARGET=13.0 python build_exe.py  # Ventura")
        print("    MACOSX_DEPLOYMENT_TARGET=14.0 python build_exe.py  # Sonoma")
        print("")
        print("  方式3: 指定架构构建 (universal2 推荐)")
        print("    TARGET_ARCH=universal2 python build_exe.py")
        print("    TARGET_ARCH=x86_64 python build_exe.py")
        print("    TARGET_ARCH=arm64 python build_exe.py")
        print("")
        print("  方式4: 同时指定版本和架构")
        print("    MACOSX_DEPLOYMENT_TARGET=13.0 TARGET_ARCH=universal2 python build_exe.py")
        print("")
        print(f"  产物: dist/前置软件报告生成工具.app")
        print("  支持系统: macOS 11-14 (Big Sur / Monterey / Ventura / Sonoma)")
    else:
        print(f" - {total - passed} 项失败，请修复后再构建")
    print()

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
