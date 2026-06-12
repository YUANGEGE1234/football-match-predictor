import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "summary_base_url": "",
    "summary_api_key": "",
    "llm_model_summary": "",
    "analysis_base_url": "",
    "analysis_api_key": "",
    "llm_model_analysis": "",
    "weather_api_key": ""
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
            return config
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
