import PyInstaller.__main__
import os
import shutil

def build_exe():
    print("=" * 50)
    print("足球比赛预测工具 - 打包程序")
    print("=" * 50)
    
    app_name = "足球比赛预测工具"
    script = "main.py"
    
    icon_path = ""
    if os.path.exists("icon.ico"):
        icon_path = "--icon=icon.ico"
    
    pyinstaller_args = [
        script,
        f'--name={app_name}',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--add-data=scraper;scraper',
        '--add-data=analyzer;analyzer',
        '--add-data=gui;gui',
        '--add-data=weather;weather',
        '--add-data=config.py;.',
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--hidden-import=lxml',
        '--hidden-import=openai',
        f'--distpath={os.path.join(os.getcwd(), "dist")}',
        f'--workpath={os.path.join(os.getcwd(), "build")}',
        f'--specpath={os.path.join(os.getcwd())}',
    ]
    
    if icon_path:
        pyinstaller_args.append(icon_path)
    
    print("\n开始打包...")
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n" + "=" * 50)
        print(f"打包完成！")
        print(f"可执行文件位置: dist/{app_name}.exe")
        print("=" * 50)
    except Exception as e:
        print(f"\n打包失败: {e}")
        print("请确保已安装 pyinstaller: pip install pyinstaller")

if __name__ == "__main__":
    build_exe()
