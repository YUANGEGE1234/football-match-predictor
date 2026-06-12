import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import messagebox
from config import load_config, save_config
from scraper.rotowire import RotowireScraper
from weather.weather_service import WeatherService
from analyzer.ai_analyzer import AIAnalyzer
from gui.main_window import FootballPredictorGUI

def check_dependencies():
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import bs4
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        import lxml
    except ImportError:
        missing.append("lxml")
    
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False
    return True

def main():
    if not check_dependencies():
        input("按回车键退出...")
        sys.exit(1)
    
    root = tk.Tk()
    
    try:
        root.iconbitmap(default='')
    except:
        pass
    
    scraper = RotowireScraper()
    weather_service = WeatherService()
    
    app = FootballPredictorGUI(
        root=root,
        scraper=scraper,
        weather_service=weather_service,
        analyzer=None,
        config_manager=load_config
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()
