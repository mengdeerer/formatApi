#!/usr/bin/env python3
"""
macOS App 打包脚本
使用 PyInstaller 将应用打包为 .app 文件
"""

import os
import subprocess
import sys
from pathlib import Path


def build_app():
    """构建 macOS .app 应用"""

    print("🚀 开始构建 macOS App...")

    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # PyInstaller 配置
    app_name = "FormatApi"
    main_script = "main.py"

    # 构建命令
    cmd = [
        "pyinstaller",
        "--name",
        app_name,
        "--windowed",  # macOS GUI 应用（不显示终端）
        # "--onefile",  # macOS .app 模式下不建议使用 onefile，会导致双图标和启动缓慢
        "--noconfirm",  # 覆盖现有构建而不询问
        "--icon",
        "/Users/meng/tools/formatApi/assets/icon.icns",  # 应用图标（如果有）
        # 添加数据文件
        "--add-data",
        "ui/styles.qss:ui",
        # Python 优化
        "--optimize",
        "2",
        # 清理之前的构建
        "--clean",
        # 隐藏导入（PyQt6 相关）
        "--hidden-import",
        "PyQt6.QtCore",
        "--hidden-import",
        "PyQt6.QtGui",
        "--hidden-import",
        "PyQt6.QtWidgets",
        # macOS 特定选项
        "--osx-bundle-identifier",
        "com.meng.formatapi",
        main_script,
    ]

    # 移除图标参数（如果图标文件不存在）
    icon_path = project_root / "assets" / "icon.icns"
    if not icon_path.exists():
        print("⚠️  图标文件不存在，将使用默认图标")
        if "--icon" in cmd:
            cmd.remove("--icon")
        if "assets/icon.icns" in cmd:
            cmd.remove("assets/icon.icns")

    try:
        # 执行打包命令
        print(f"📦 执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        print("\n✅ 打包成功！")
        print(f"📁 App 位置: dist/{app_name}.app")
        print("📦 可直接分发或拖入 /Applications")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ PyInstaller 未安装！")
        print("请运行: uv pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
