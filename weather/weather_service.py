import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

class WeatherService:
    def __init__(self, api_key=""):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city, date_str):
        if not self.api_key:
            return self._get_demo_weather(city, date_str)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 40
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data, date_str)
            else:
                return self._get_demo_weather(city, date_str)
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_demo_weather(city, date_str)
    
    def _parse_weather_data(self, data, date_str):
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        for item in data.get("list", []):
            forecast_date = datetime.fromtimestamp(item["dt"]).date()
            if forecast_date == target_date:
                return {
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "wind_direction": item["wind"].get("deg", 0),
                    "weather": item["weather"][0]["description"],
                    "weather_main": item["weather"][0]["main"],
                    "rain": item.get("rain", {}).get("3h", 0),
                    "snow": item.get("snow", {}).get("3h", 0),
                    "clouds": item["clouds"]["all"],
                    "visibility": item.get("visibility", 10000),
                    "pressure": item["main"]["pressure"],
                }
        
        return self._get_demo_weather("", date_str)
    
    def _get_demo_weather(self, city, date_str):
        return {
            "temperature": 18,
            "feels_like": 16,
            "humidity": 65,
            "wind_speed": 3.5,
            "wind_direction": 180,
            "weather": "Partly cloudy",
            "weather_main": "Clouds",
            "rain": 0,
            "snow": 0,
            "clouds": 40,
            "visibility": 10000,
            "pressure": 1013,
            "note": "Demo data - Add weather API key for real data"
        }
    
    def get_weather_impact(self, weather_data):
        if not weather_data:
            return "neutral"
        
        temp = weather_data.get("temperature", 20)
        wind = weather_data.get("wind_speed", 0)
        rain = weather_data.get("rain", 0)
        humidity = weather_data.get("humidity", 50)
        
        impacts = []
        
        if temp > 30:
            impacts.append("高温可能导致球员体能下降")
        elif temp > 25:
            impacts.append("温暖天气有利于比赛进行")
        elif temp < 5:
            impacts.append("寒冷天气可能影响球感和传球精度")
        
        if wind > 15:
            impacts.append("强风会影响长传和射门精度")
        elif wind > 10:
            impacts.append("中等风力对高空球有一定影响")
        
        if rain > 10:
            impacts.append("大雨会影响场地条件和球的运行")
        elif rain > 5:
            impacts.append("中雨使场地湿滑，影响控球")
        elif rain > 0:
            impacts.append("小雨对比赛影响不大")
        
        if humidity > 80:
            impacts.append("高湿度会增加球员疲劳感")
        
        if not impacts:
            return "天气条件良好，适合比赛"
        
        return "；".join(impacts)
    
    def format_weather_report(self, weather_data):
        if not weather_data:
            return "天气信息不可用"
        
        report = f"""【天气信息】
温度: {weather_data.get('temperature', 'N/A')}°C (体感 {weather_data.get('feels_like', 'N/A')}°C)
天气: {weather_data.get('weather', 'N/A')}
湿度: {weather_data.get('humidity', 'N/A')}%
风速: {weather_data.get('wind_speed', 'N/A')} m/s
降雨: {weather_data.get('rain', 0)} mm
气压: {weather_data.get('pressure', 'N/A')} hPa
能见度: {weather_data.get('visibility', 1000)} m

【天气影响分析】
{self.get_weather_impact(weather_data)}"""
        
        return report
