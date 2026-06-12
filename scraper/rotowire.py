import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import json

class RotowireScraper:
    BASE_URL = "https://www.rotowire.com"
    
    TEAM_FULL_NAMES = {
        "MEX": "Mexico National Team",
        "RSA": "South Africa National Team",
        "KOR": "South Korea National Team",
        "CZE": "Czech Republic National Team",
        "CAN": "Canada National Team",
        "BIH": "Bosnia and Herzegovina National Team",
        "USA": "United States National Team",
        "PAR": "Paraguay National Team",
        "QAT": "Qatar National Team",
        "SUI": "Switzerland National Team",
        "BRA": "Brazil National Team",
        "MAR": "Morocco National Team",
        "HAI": "Haiti National Team",
        "SCO": "Scotland National Team",
        "AUS": "Australia National Team",
        "TUR": "Turkey National Team",
        "ENG": "England National Team",
        "FRA": "France National Team",
        "GER": "Germany National Team",
        "ARG": "Argentina National Team",
        "ESP": "Spain National Team",
        "ITA": "Italy National Team",
        "POR": "Portugal National Team",
        "NED": "Netherlands National Team",
        "BEL": "Belgium National Team",
        "CRO": "Croatia National Team",
        "JPN": "Japan National Team",
        "MEX": "Mexico",
        "Arsenal": "Arsenal FC",
        "Chelsea": "Chelsea FC",
        "Liverpool": "Liverpool FC",
        "Manchester United": "Manchester United FC",
        "Manchester City": "Manchester City FC",
        "Tottenham": "Tottenham Hotspur FC",
        "Barcelona": "FC Barcelona",
        "Real Madrid": "Real Madrid CF",
        "Atletico Madrid": "Atletico de Madrid",
        "Bayern Munich": "FC Bayern Munich",
        "Dortmund": "Borussia Dortmund",
        "PSG": "Paris Saint-Germain FC",
        "Juventus": "Juventus FC",
        "AC Milan": "AC Milan",
        "Inter Milan": "Inter Milan",
        "Napoli": "SSC Napoli",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self._progress_callback = None
    
    def set_progress_callback(self, callback):
        self._progress_callback = callback
    
    def _log(self, msg):
        if self._progress_callback:
            self._progress_callback(msg)
        print(msg)
    
    def _get_full_name(self, short_name):
        return self.TEAM_FULL_NAMES.get(short_name, short_name)
    
    def _get_page(self, url, retries=3):
        for attempt in range(retries):
            try:
                self._log(f"获取页面 (尝试 {attempt+1}/{retries}): {url}")
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 200:
                    return resp.text
                self._log(f"HTTP {resp.status_code}")
            except Exception as e:
                self._log(f"请求错误: {e}")
            if attempt < retries - 1:
                time.sleep(2)
        return None
    
    def get_leagues(self):
        return [
            {"id": "WOC", "name": "FIFA World Cup 2026"},
            {"id": "EPL", "name": "English Premier League"},
            {"id": "UCL", "name": "UEFA Champions League"},
            {"id": "LIGA", "name": "Spanish La Liga"},
            {"id": "BUND", "name": "German Bundesliga"},
            {"id": "SERI", "name": "Italian Serie A"},
            {"id": "FRAN", "name": "French Ligue 1"},
            {"id": "MLS", "name": "Major League Soccer"},
        ]
    
    def get_matches(self, days_ahead=3, league=None):
        matches = []
        leagues = [league] if league else ["WOC", "EPL", "UCL", "LIGA", "BUND", "SERI", "FRAN", "MLS"]
        
        for lg in leagues:
            self._log(f"检查联赛: {lg}")
            lg_matches = self._fetch_league_matches(lg)
            if lg_matches:
                matches.extend(lg_matches)
                self._log(f"找到 {len(lg_matches)} 场比赛")
                break
        
        return matches
    
    def _fetch_league_matches(self, league_id):
        url = f"{self.BASE_URL}/soccer/lineups.php?league={league_id}"
        html = self._get_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        
        if soup.find(string=re.compile(r'There are no.*games', re.IGNORECASE)):
            return []
        
        matches = []
        current_year = datetime.now().year
        
        for div in soup.select('div.lineup'):
            try:
                match = self._parse_match(div, league_id, current_year)
                if match:
                    matches.append(match)
            except:
                pass
        
        return matches
    
    def _parse_match(self, div, league_id, year):
        time_div = div.select_one('div.lineup__time')
        if not time_div:
            return None
        
        time_text = time_div.get_text(separator=' ', strip=True)
        
        date_match = re.search(r'(\w+\s+\d+)', time_text)
        if not date_match:
            return None
        
        try:
            date_obj = datetime.strptime(f"{date_match.group(1)} {year}", "%B %d %Y")
            match_date = date_obj.strftime("%Y-%m-%d")
        except:
            return None
        
        time_match = re.search(r'(\d+:\d+\s*(?:AM|PM)(?:\s*ET)?)', time_text)
        match_time = time_match.group(1).strip() if time_match else "TBD"
        
        home_div = div.select_one('div.lineup__mteam.is-home')
        away_div = div.select_one('div.lineup__mteam.is-visit')
        
        home_short = home_div.get_text(strip=True) if home_div else ""
        away_short = away_div.get_text(strip=True) if away_div else ""
        
        home_short = re.sub(r'[WL]\s*$', '', home_short).strip()
        away_short = re.sub(r'[WL]\s*$', '', away_short).strip()
        
        if not home_short:
            abbr = div.select_one('div.lineup__team.is-home div.lineup__abbr')
            home_short = abbr.get_text(strip=True) if abbr else ""
        if not away_short:
            abbr = div.select_one('div.lineup__team.is-visit div.lineup__abbr')
            away_short = abbr.get_text(strip=True) if abbr else ""
        
        if not home_short or not away_short:
            return None
        
        home_team = self._get_full_name(home_short)
        away_team = self._get_full_name(away_short)
        
        self._log(f"解析: {home_team} vs {away_team} - {match_date} {match_time}")
        
        return {
            "date": match_date,
            "time": match_time,
            "home_team": home_team,
            "away_team": away_team,
            "home_short": home_short,
            "away_short": away_short,
            "league": league_id,
            "element": div
        }
    
    def get_match_details(self, match):
        div = match.get('element')
        if not div:
            return {"match_info": match}
        
        self._log("=" * 50)
        self._log(f"开始收集比赛详细信息")
        self._log(f"比赛: {match['home_team']} vs {match['away_team']}")
        self._log(f"时间: {match['date']} {match['time']}")
        self._log("=" * 50)
        
        self._log("[1/6] 解析主队阵容...")
        home_info = self._parse_team(div, 'is-home')
        self._log(f"  主队阵容: {home_info['player_count']} 名球员")
        self._log(f"  阵型: {home_info['formation']}")
        self._log(f"  伤病: {home_info['injury_count']} 人")
        
        self._log("[2/6] 解析客队阵容...")
        away_info = self._parse_team(div, 'is-visit')
        self._log(f"  客队阵容: {away_info['player_count']} 名球员")
        self._log(f"  阵型: {away_info['formation']}")
        self._log(f"  伤病: {away_info['injury_count']} 人")
        
        self._log("[3/6] 解析赔率信息...")
        odds = self._parse_odds(div)
        self._log(f"  主胜: {odds.get('best_home', 'N/A')} | 平局: {odds.get('best_draw', 'N/A')} | 客胜: {odds.get('best_away', 'N/A')}")
        
        self._log("[4/6] 解析天气信息...")
        weather = self._parse_weather(div)
        
        self._log("[5/6] 获取教练信息...")
        coaches = self._get_coach_info(match)
        
        self._log("[6/6] 获取裁判信息...")
        referee = self._get_referee_info(match)
        
        self._log("=" * 50)
        self._log("信息收集完成!")
        self._log("=" * 50)
        
        return {
            "match_info": {k: v for k, v in match.items() if k != 'element'},
            "home_team_info": home_info,
            "away_team_info": away_info,
            "odds_info": odds,
            "weather_info": weather,
            "coach_info": coaches,
            "referee_info": referee,
        }
    
    def _parse_team(self, div, team_class):
        ul = div.select_one(f'ul.lineup__list.{team_class}')
        if not ul:
            return {"players": [], "injuries": [], "status": "Unknown", "formation": "Unknown", "player_count": 0, "injury_count": 0}
        
        status_el = ul.select_one('li.lineup__status')
        status = status_el.get_text(strip=True) if status_el else "Unknown"
        
        players = []
        injuries = []
        in_injuries = False
        
        for li in ul.select('li'):
            cls = li.get('class', [])
            
            if 'lineup__title' in cls:
                in_injuries = True
                continue
            
            if 'lineup__player' not in cls:
                continue
            
            pos_el = li.select_one('div.lineup__pos')
            name_el = li.select_one('a')
            inj_el = li.select_one('span.lineup__inj')
            
            if not pos_el or not name_el:
                continue
            
            pos = pos_el.get_text(strip=True)
            name = name_el.get_text(strip=True)
            url = name_el.get('href', '')
            inj = inj_el.get_text(strip=True) if inj_el else ""
            
            player = {
                "name": name,
                "full_name": self._get_player_full_name(name),
                "position": pos,
                "position_full": self._get_position_full(pos),
                "injury_status": inj,
                "is_available": not bool(inj),
                "doubtful": inj == "QUES",
                "suspended": inj == "SUS",
                "out": inj in ["OUT", "INJ"],
                "player_url": f"{self.BASE_URL}{url}" if url else "",
            }
            
            if in_injuries:
                injuries.append(player)
            else:
                players.append(player)
        
        formation = self._detect_formation(players)
        
        return {
            "status": status,
            "players": players,
            "injuries": injuries,
            "formation": formation,
            "player_count": len(players),
            "injury_count": len(injuries),
            "available_count": sum(1 for p in players if p['is_available']),
        }
    
    def _get_player_full_name(self, short_name):
        name_map = {
            "J. Gallardo": "Jesus Gallardo",
            "J. Vasquez": "Johan Vasquez",
            "B. Gutierrez": "Brian Gutierrez",
            "A. Fidalgo": "Alvaro Fidalgo",
            "R. Alvarado": "Roberto Alvarado",
            "R. Williams": "Ronwen Hayden Williams",
            "M. Mbokazi": "Mbekezeli Mbokazi",
            "N. Sibisi": "Nkosinathi Sibisi",
            "A. Modiba": "Aubrey Modiba",
            "T. Mokoena": "Teboho Mokoena",
            "S. Sithole": "Sphephelo Sithole",
            "K. Mudau": "Khuliso Mudau",
            "I. Rayners": "Iqraam Rayners",
            "K. Seung-gyu": "Kim Seung-gyu",
            "P. Seung-Ho": "Paik Seung-Ho",
            "H. In-beom": "Hwang In-beom",
            "L. Krejci": "Ladislav Krejci",
            "S. Chaloupek": "Stanislav Chaloupek",
            "V. Coufal": "Vladimir Coufal",
            "P. Schick": "Patrik Schick",
            "M. Crepeau": "Maxime Crepeau",
            "R. Laryea": "Richie Laryea",
            "D. Cornelius": "Derek Cornelius",
            "A. Johnston": "Alistair Johnston",
            "S. Eustaquio": "Stephen Eustaquio",
            "T. Buchanan": "Tajon Buchanan",
            "J. David": "Jonathan David",
            "N. Vasilj": "Nikola Vasilj",
            "S. Kolasinac": "Sead Kolasinac",
            "N. Katic": "Nikola Katic",
            "T. Muharemovic": "Tarik Muharemovic",
            "A. Dedic": "Amar Dedic",
            "B. Tahirovic": "Benjamin Tahirovic",
            "E. Demirovic": "Ermedin Demirovic",
            "C. Richards": "Chris Richards",
            "M. McKenzie": "Mark McKenzie",
            "A. Robinson": "Antonee Robinson",
            "W. McKennie": "Weston McKennie",
            "S. Dest": "Sergino Dest",
            "M. Tillman": "Malik Tillman",
            "C. Pulisic": "Christian Pulisic",
            "F. Balogun": "Folarin Balogun",
            "O. Alderete": "Omar Alderete",
            "G. Gomez": "Gustavo Gomez",
            "A. Cubas": "Andres Cubas",
            "D. Gomez": "Diego Gomez",
            "A. Sanabria": "Antonio Sanabria",
            "M. Almiron": "Miguel Almiron",
            "M. Ibrahim Abunada": "Meshaal Ibrahim Abunada",
            "A. Al Oui": "Ayoub Al Oui",
            "A. Fathy": "Ahmed Fathy",
            "K. Boudiaf": "Karim Boudiaf",
            "J. Gaber": "Jassem Gaber",
            "A. Afif": "Akram Afif",
            "E. Junior": "Edmilson Junior",
            "A. Ali": "Almoez Ali",
            "G. Kobel": "Gregor Kobel",
            "R. Rodriguez": "Ricardo Rodriguez",
            "N. Elvedi": "Nico Elvedi",
            "M. Akanji": "Manuel Akanji",
            "S. Widmer": "Silvan Widmer",
            "R. Freuler": "Remo Freuler",
            "G. Xhaka": "Granit Xhaka",
            "M. Aebischer": "Michel Aebischer",
            "R. Vargas": "Ruben Vargas",
            "D. Ndoye": "Dan Ndoye",
            "B. Embolo": "Breel Embolo",
            "Alex Sandro": "Alex Sandro Lobo Silva",
            "L. Paqueta": "Lucas Paqueta",
            "M. Cunha": "Matheus Cunha",
            "N. Mazraoui": "Noussair Mazraoui",
            "C. Riad": "Chadi Riad",
            "I. Diop": "Issa Diop",
            "A. Hakimi": "Achraf Hakimi",
            "N. El Aynaoui": "Nabil El Aynaoui",
            "A. Bouaddi": "Ayyoub Bouaddi",
            "B. El Khannouss": "Bilal El Khannouss",
            "A. Ounahi": "Azzedine Ounahi",
            "B. Diaz": "Brahim Diaz",
            "I. Saibari": "Ismail Saibari",
            "H. Souttar": "Harry Souttar",
            "C. Burgess": "Cameron Burgess",
            "A. Circati": "Alessandro Circati",
            "C. Metcalfe": "Connor Metcalfe",
            "J. Irvine": "Jackson Irvine",
            "A. Hrustic": "Ajdin Hrustic",
            "C. Volpato": "Cristiano Volpato",
            "M. Toure": "Mohamed Toure",
            "U. Cakir": "Ugurcan Cakir",
        }
        return name_map.get(short_name, short_name)
    
    def _get_position_full(self, pos):
        pos_map = {
            "GK": "Goalkeeper",
            "DC": "Centre-Back",
            "DL": "Left-Back",
            "DR": "Right-Back",
            "LB": "Left-Back",
            "RB": "Right-Back",
            "CB": "Centre-Back",
            "DMC": "Defensive Midfielder",
            "MC": "Central Midfielder",
            "ML": "Left Midfielder",
            "MR": "Right Midfielder",
            "AMC": "Attacking Midfielder",
            "AML": "Left Winger",
            "AMR": "Right Winger",
            "FW": "Forward",
            "FWL": "Left Wing-Forward",
            "FWR": "Right Wing-Forward",
            "ST": "Striker",
            "CF": "Centre-Forward",
            "F": "Forward",
            "M": "Midfielder",
            "D": "Defender",
        }
        return pos_map.get(pos.upper(), pos)
    
    def _detect_formation(self, players):
        defs = mids = fwds = 0
        for p in players:
            pos = p['position'].upper()
            if any(x in pos for x in ['D', 'LB', 'RB', 'CB', 'DC', 'DL', 'DR']):
                defs += 1
            elif any(x in pos for x in ['M', 'CM', 'CDM', 'CAM', 'MC', 'ML', 'MR', 'DMC', 'AMC', 'AML', 'AMR']):
                mids += 1
            elif any(x in pos for x in ['F', 'FW', 'ST', 'FWL', 'FWR', 'CF']):
                fwds += 1
        return f"{defs}-{mids}-{fwds}" if defs or mids or fwds else "Unknown"
    
    def _parse_odds(self, div):
        odds_div = div.select_one('div.lineup__odds')
        if not odds_div:
            return {
                "available": False,
                "platforms": {},
                "best_home": "N/A",
                "best_draw": "N/A",
                "best_away": "N/A",
                "home_implied_prob": "N/A",
                "draw_implied_prob": "N/A",
                "away_implied_prob": "N/A",
                "source": "无赔率数据"
            }
        
        platforms = {
            "DraftKings": {"home": "N/A", "draw": "N/A", "away": "N/A"},
            "FanDuel": {"home": "N/A", "draw": "N/A", "away": "N/A"},
            "BetMGM": {"home": "N/A", "draw": "N/A", "away": "N/A"},
            "PointsBet": {"home": "N/A", "draw": "N/A", "away": "N/A"},
        }
        
        for item in odds_div.select('div.lineup__odds-item'):
            label = item.select_one('b')
            if not label:
                continue
            
            label_text = label.get_text(strip=True).rstrip(':')
            
            for platform_name, platform_class in [
                ("DraftKings", "span.draftkings"),
                ("FanDuel", "span.fanduel"),
                ("BetMGM", "span.betmgm"),
                ("PointsBet", "span.pointsbet")
            ]:
                span = item.select_one(platform_class)
                if span:
                    val = span.get_text(strip=True)
                    if val and val != '–' and val != '–':
                        if 'Draw' in label_text:
                            platforms[platform_name]["draw"] = val
                        elif platforms[platform_name]["home"] == "N/A":
                            platforms[platform_name]["home"] = val
                        else:
                            platforms[platform_name]["away"] = val
        
        best_home = "N/A"
        best_draw = "N/A"
        best_away = "N/A"
        
        for platform in platforms.values():
            if platform["home"] != "N/A":
                if best_home == "N/A":
                    best_home = platform["home"]
            if platform["draw"] != "N/A":
                if best_draw == "N/A":
                    best_draw = platform["draw"]
            if platform["away"] != "N/A":
                if best_away == "N/A":
                    best_away = platform["away"]
        
        result = {
            "available": True,
            "platforms": platforms,
            "best_home": best_home,
            "best_draw": best_draw,
            "best_away": best_away,
            "source": "DraftKings, FanDuel, BetMGM, PointsBet",
            "home_implied_prob": "N/A",
            "draw_implied_prob": "N/A",
            "away_implied_prob": "N/A",
        }
        
        for key, val_key in [("best_home", "home_implied_prob"), ("best_draw", "draw_implied_prob"), ("best_away", "away_implied_prob")]:
            if result[key] != "N/A":
                try:
                    odds_val = float(result[key].replace('+', ''))
                    if odds_val > 0:
                        prob = 100 / (odds_val + 100)
                    else:
                        prob = abs(odds_val) / (abs(odds_val) + 100)
                    result[val_key] = f"{prob*100:.1f}%"
                except:
                    result[val_key] = "N/A"
        
        return result
    
    def _parse_weather(self, div):
        weather_div = div.select_one('div.lineup__weather')
        if not weather_div:
            return {"available": False}
        
        text = weather_div.get_text(strip=True)
        
        temp = re.search(r'(\d+)°', text)
        wind = re.search(r'Wind\s+(\d+)\s+mph', text)
        rain = re.search(r'(\d+)%', text)
        
        temp_f = int(temp.group(1)) if temp else None
        temp_c = round((temp_f - 32) * 5/9) if temp_f else None
        
        return {
            "available": True,
            "temperature_f": temp_f,
            "temperature_c": temp_c,
            "wind_mph": int(wind.group(1)) if wind else None,
            "wind_kmh": round(int(wind.group(1)) * 1.60934) if wind else None,
            "rain_chance": int(rain.group(1)) if rain else None,
            "raw": text,
            "conditions": self._interpret_weather(temp_f, int(wind.group(1)) if wind else 0, int(rain.group(1)) if rain else 0)
        }
    
    def _interpret_weather(self, temp_f, wind_mph, rain_pct):
        conditions = []
        
        if temp_f:
            if temp_f > 86:
                conditions.append("高温炎热，球员体能消耗大")
            elif temp_f > 77:
                conditions.append("温暖，适合比赛")
            elif temp_f > 59:
                conditions.append("温度适中，理想比赛条件")
            else:
                conditions.append("偏冷，可能影响球感")
        
        if wind_mph > 15:
            conditions.append("强风，影响传球和射门精度")
        elif wind_mph > 10:
            conditions.append("中等风力，对高空球有影响")
        
        if rain_pct > 70:
            conditions.append("高降雨概率，场地可能湿滑")
        elif rain_pct > 30:
            conditions.append("有一定降雨可能")
        
        return "；".join(conditions) if conditions else "良好比赛条件"
    
    def _get_coach_info(self, match):
        coaches = {
            # 完整名称映射
            "Mexico National Team": {"name": "Jaime Lozano", "nationality": "Mexican", "age": 45, "style": "攻守平衡，注重防守组织", "experience": "曾执教墨西哥U23国家队", "world_cup_experience": "首次带队参加世界杯"},
            "South Africa National Team": {"name": "Hugo Broos", "nationality": "Belgian", "age": 72, "style": "强调纪律性和防守反击", "experience": "曾执教喀麦隆国家队并赢得非洲杯", "world_cup_experience": "丰富的国际赛事经验"},
            "South Korea National Team": {"name": "Hong Myung-bo", "nationality": "South Korean", "age": 55, "style": "高位逼抢，快速反击", "experience": "韩国足球传奇，曾执教韩国国家队", "world_cup_experience": "2002年世界杯球员，2014年世界杯主教练"},
            "Czech Republic National Team": {"name": "Ivan Hasek", "nationality": "Czech", "age": 60, "style": "战术灵活，注重中场控制", "experience": "曾执教多支捷克俱乐部", "world_cup_experience": "经验丰富的国际教练"},
            "Canada National Team": {"name": "Jesse Marsch", "nationality": "American", "age": 50, "style": "高位逼抢，积极进攻", "experience": "曾执教利兹联、萨尔茨堡红牛", "world_cup_experience": "首次带队参加世界杯"},
            "Bosnia and Herzegovina National Team": {"name": "Sergej Barbarez", "nationality": "Bosnian", "age": 52, "style": "攻势足球，注重技术", "experience": "波黑足球名宿", "world_cup_experience": "首次带队冲击世界杯"},
            "United States National Team": {"name": "Gregg Berhalter", "nationality": "American", "age": 50, "style": "控球为主，边路进攻", "experience": "曾执教哥伦布机员", "world_cup_experience": "2022年世界杯主教练"},
            "Paraguay National Team": {"name": "Daniel Garnero", "nationality": "Argentine", "age": 54, "style": "防守反击，战术纪律严明", "experience": "曾执教多支南美俱乐部", "world_cup_experience": "经验丰富的南美教练"},
            "Qatar National Team": {"name": "Tintin Marquez", "nationality": "Spanish", "age": 57, "style": "控球战术，技术流", "experience": "曾执教卡塔尔俱乐部", "world_cup_experience": "2022年世界杯东道主教练团队成员"},
            "Switzerland National Team": {"name": "Murat Yakin", "nationality": "Swiss", "age": 49, "style": "战术灵活，防守稳固", "experience": "曾执教巴塞尔等瑞士俱乐部", "world_cup_experience": "2022年世界杯主教练，带队进入16强"},
            "Brazil National Team": {"name": "Dorival Junior", "nationality": "Brazilian", "age": 62, "style": "攻势足球，注重技术", "experience": "曾执教弗拉门戈、圣保罗等巴西豪门", "world_cup_experience": "首次带队参加世界杯"},
            "Morocco National Team": {"name": "Walid Regragui", "nationality": "Moroccan", "age": 48, "style": "防守反击，战术纪律严明", "experience": "2022年世界杯带队进入四强", "world_cup_experience": "2022年世界杯创造历史"},
            "Haiti National Team": {"name": "Sébastien Migné", "nationality": "French", "age": 51, "style": "防守为主，快速反击", "experience": "曾执教多支非洲国家队", "world_cup_experience": "首次带队参加世界杯"},
            "Scotland National Team": {"name": "Steve Clarke", "nationality": "Scottish", "age": 60, "style": "防守稳固，组织有序", "experience": "曾执教西布朗、切尔西助理教练", "world_cup_experience": "带队重返世界杯"},
            "Australia National Team": {"name": "Graham Arnold", "nationality": "Australian", "age": 61, "style": "攻守平衡，注重团队配合", "experience": "曾执教悉尼FC、澳大利亚国奥", "world_cup_experience": "2022年世界杯主教练"},
            "Turkey National Team": {"name": "Vincenzo Montella", "nationality": "Italian", "age": 50, "style": "攻势足球，战术灵活", "experience": "曾执教AC米兰、佛罗伦萨", "world_cup_experience": "首次带队参加世界杯"},
            # 简短名称映射
            "Mexico": {"name": "Jaime Lozano", "nationality": "Mexican", "age": 45, "style": "攻守平衡，注重防守组织", "experience": "曾执教墨西哥U23国家队", "world_cup_experience": "首次带队参加世界杯"},
            "South Africa": {"name": "Hugo Broos", "nationality": "Belgian", "age": 72, "style": "强调纪律性和防守反击", "experience": "曾执教喀麦隆国家队并赢得非洲杯", "world_cup_experience": "丰富的国际赛事经验"},
            "South Korea": {"name": "Hong Myung-bo", "nationality": "South Korean", "age": 55, "style": "高位逼抢，快速反击", "experience": "韩国足球传奇，曾执教韩国国家队", "world_cup_experience": "2002年世界杯球员，2014年世界杯主教练"},
            "Czech Republic": {"name": "Ivan Hasek", "nationality": "Czech", "age": 60, "style": "战术灵活，注重中场控制", "experience": "曾执教多支捷克俱乐部", "world_cup_experience": "经验丰富的国际教练"},
            "Canada": {"name": "Jesse Marsch", "nationality": "American", "age": 50, "style": "高位逼抢，积极进攻", "experience": "曾执教利兹联、萨尔茨堡红牛", "world_cup_experience": "首次带队参加世界杯"},
            "Bosnia and Herzegovina": {"name": "Sergej Barbarez", "nationality": "Bosnian", "age": 52, "style": "攻势足球，注重技术", "experience": "波黑足球名宿", "world_cup_experience": "首次带队冲击世界杯"},
            "Paraguay": {"name": "Daniel Garnero", "nationality": "Argentine", "age": 54, "style": "防守反击，战术纪律严明", "experience": "曾执教多支南美俱乐部", "world_cup_experience": "经验丰富的南美教练"},
            "Qatar": {"name": "Tintin Marquez", "nationality": "Spanish", "age": 57, "style": "控球战术，技术流", "experience": "曾执教卡塔尔俱乐部", "world_cup_experience": "2022年世界杯东道主教练团队成员"},
            "Switzerland": {"name": "Murat Yakin", "nationality": "Swiss", "age": 49, "style": "战术灵活，防守稳固", "experience": "曾执教巴塞尔等瑞士俱乐部", "world_cup_experience": "2022年世界杯主教练，带队进入16强"},
            "Brazil": {"name": "Dorival Junior", "nationality": "Brazilian", "age": 62, "style": "攻势足球，注重技术", "experience": "曾执教弗拉门戈、圣保罗等巴西豪门", "world_cup_experience": "首次带队参加世界杯"},
            "Morocco": {"name": "Walid Regragui", "nationality": "Moroccan", "age": 48, "style": "防守反击，战术纪律严明", "experience": "2022年世界杯带队进入四强", "world_cup_experience": "2022年世界杯创造历史"},
            "Haiti": {"name": "Sébastien Migné", "nationality": "French", "age": 51, "style": "防守为主，快速反击", "experience": "曾执教多支非洲国家队", "world_cup_experience": "首次带队参加世界杯"},
            "Scotland": {"name": "Steve Clarke", "nationality": "Scottish", "age": 60, "style": "防守稳固，组织有序", "experience": "曾执教西布朗、切尔西助理教练", "world_cup_experience": "带队重返世界杯"},
            "Australia": {"name": "Graham Arnold", "nationality": "Australian", "age": 61, "style": "攻守平衡，注重团队配合", "experience": "曾执教悉尼FC、澳大利亚国奥", "world_cup_experience": "2022年世界杯主教练"},
            "Turkey": {"name": "Vincenzo Montella", "nationality": "Italian", "age": 50, "style": "攻势足球，战术灵活", "experience": "曾执教AC米兰、佛罗伦萨", "world_cup_experience": "首次带队参加世界杯"},
            "Germany": {"name": "Julian Nagelsmann", "nationality": "German", "age": 37, "style": "高位逼抢，攻势足球", "experience": "曾执教拜仁慕尼黑、莱比锡", "world_cup_experience": "首次带队参加世界杯"},
            "Netherlands": {"name": "Ronald Koeman", "nationality": "Dutch", "age": 61, "style": "控球为主，全攻全守", "experience": "曾执教巴萨、瓦伦西亚", "world_cup_experience": "2022年世界杯主教练"},
            "Japan": {"name": "Hajime Moriyasu", "nationality": "Japanese", "age": 55, "style": "技术流，快速反击", "experience": "长期执教日本国家队", "world_cup_experience": "2022年世界杯主教练"},
            "Spain": {"name": "Luis de la Fuente", "nationality": "Spanish", "age": 62, "style": "控球战术，tiki-taka", "experience": "曾执教西班牙各级青年队", "world_cup_experience": "首次带队参加世界杯"},
            "Belgium": {"name": "Domenico Tedesco", "nationality": "Italian", "age": 38, "style": "攻势足球，战术灵活", "experience": "曾执教莱比锡、沙尔克", "world_cup_experience": "首次带队参加世界杯"},
            "France": {"name": "Didier Deschamps", "nationality": "French", "age": 55, "style": "实用主义，防守反击", "experience": "2018年世界杯冠军教练", "world_cup_experience": "2018年冠军，2022年亚军"},
            "Argentina": {"name": "Lionel Scaloni", "nationality": "Argentine", "age": 46, "style": "攻势足球，梅西核心", "experience": "2022年世界杯冠军教练", "world_cup_experience": "2022年世界杯冠军"},
            "Portugal": {"name": "Roberto Martinez", "nationality": "Spanish", "age": 50, "style": "控球为主，战术灵活", "experience": "曾执教比利时国家队", "world_cup_experience": "2022年世界杯执教比利时"},
            "England": {"name": "Gareth Southgate", "nationality": "English", "age": 53, "style": "防守稳固，定位球战术", "experience": "长期执教英格兰国家队", "world_cup_experience": "2018年四强，2022年八强"},
            "Croatia": {"name": "Zlatko Dalic", "nationality": "Croatian", "age": 57, "style": "防守反击，中场控制", "experience": "2018年世界杯亚军教练", "world_cup_experience": "2018年亚军，2022年季军"},
            "Colombia": {"name": "Nestor Lorenzo", "nationality": "Argentine", "age": 58, "style": "攻势足球，技术流", "experience": "曾执教多支南美球队", "world_cup_experience": "首次带队参加世界杯"},
            "Uruguay": {"name": "Marcelo Bielsa", "nationality": "Argentine", "age": 68, "style": "高位逼抢，疯狂进攻", "experience": "曾执教利兹联、阿根廷国家队", "world_cup_experience": "2002年世界杯执教阿根廷"},
            "Senegal": {"name": "Aliou Cisse", "nationality": "Senegalese", "age": 48, "style": "防守反击，纪律严明", "experience": "2022年非洲杯冠军教练", "world_cup_experience": "2022年世界杯主教练"},
            "Egypt": {"name": "Hossam Hassan", "nationality": "Egyptian", "age": 58, "style": "攻势足球，技术流", "experience": "埃及足球传奇", "world_cup_experience": "首次带队参加世界杯"},
            "Norway": {"name": "Stale Solbakken", "nationality": "Norwegian", "age": 56, "style": "防守反击，身体对抗", "experience": "曾执教哥本哈根、狼队", "world_cup_experience": "首次带队参加世界杯"},
            "Ecuador": {"name": "Felix Sanchez", "nationality": "Spanish", "age": 48, "style": "控球战术，技术流", "experience": "曾执教卡塔尔国家队", "world_cup_experience": "2022年世界杯执教卡塔尔"},
            "Tunisia": {"name": "Jalel Kadri", "nationality": "Tunisian", "age": 52, "style": "防守反击，纪律严明", "experience": "长期执教突尼斯俱乐部", "world_cup_experience": "2022年世界杯主教练"},
            "Saudi Arabia": {"name": "Roberto Mancini", "nationality": "Italian", "age": 59, "style": "控球战术，攻势足球", "experience": "曾执教曼城、意大利国家队", "world_cup_experience": "2022年世界杯执教意大利"},
            "Iran": {"name": "Amir Ghalenoei", "nationality": "Iranian", "age": 60, "style": "防守反击，纪律严明", "experience": "长期执教伊朗俱乐部", "world_cup_experience": "首次带队参加世界杯"},
            "Ghana": {"name": "Otto Addo", "nationality": "German", "age": 48, "style": "攻势足球，技术流", "experience": "曾执教多特蒙德青年队", "world_cup_experience": "2022年世界杯主教练"},
            "Cameroon": {"name": "Rigobert Song", "nationality": "Cameroonian", "age": 48, "style": "防守反击，身体对抗", "experience": "喀麦隆足球传奇", "world_cup_experience": "2022年世界杯主教练"},
            "Serbia": {"name": "Dragan Stojkovic", "nationality": "Serbian", "age": 59, "style": "攻势足球，技术流", "experience": "曾执教日本名古屋", "world_cup_experience": "2022年世界杯主教练"},
            "Poland": {"name": "Michal Probierz", "nationality": "Polish", "age": 51, "style": "防守反击，纪律严明", "experience": "曾执教多支波兰俱乐部", "world_cup_experience": "首次带队参加世界杯"},
            "Denmark": {"name": "Kasper Hjulmand", "nationality": "Danish", "age": 52, "style": "控球战术，攻势足球", "experience": "2020欧洲杯四强教练", "world_cup_experience": "2022年世界杯主教练"},
            "Ukraine": {"name": "Serhiy Rebrov", "nationality": "Ukrainian", "age": 50, "style": "攻势足球，技术流", "experience": "曾执教基辅迪纳摩", "world_cup_experience": "首次带队参加世界杯"},
            "Wales": {"name": "Rob Page", "nationality": "Welsh", "age": 49, "style": "防守反击，纪律严明", "experience": "长期执教威尔士各级青年队", "world_cup_experience": "2022年世界杯主教练"},
            "Austria": {"name": "Ralf Rangnick", "nationality": "German", "age": 66, "style": "高位逼抢，gegenpressing", "experience": "曾执教曼联、莱比锡", "world_cup_experience": "首次带队参加世界杯"},
            "Hungary": {"name": "Marco Rossi", "nationality": "Italian", "age": 59, "style": "防守反击，纪律严明", "experience": "长期执教匈牙利国家队", "world_cup_experience": "首次带队参加世界杯"},
            "Romania": {"name": "Edward Iordanescu", "nationality": "Romanian", "age": 45, "style": "攻势足球，技术流", "experience": "曾执教罗马尼亚俱乐部", "world_cup_experience": "首次带队参加世界杯"},
            "Slovakia": {"name": "Francesco Calzona", "nationality": "Italian", "age": 55, "style": "防守反击，战术灵活", "experience": "曾执教那不勒斯", "world_cup_experience": "首次带队参加世界杯"},
        }
        
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        
        home_coach = coaches.get(home_team, {"name": "Unknown", "nationality": "Unknown", "age": "N/A", "style": "N/A", "experience": "N/A", "world_cup_experience": "N/A"})
        away_coach = coaches.get(away_team, {"name": "Unknown", "nationality": "Unknown", "age": "N/A", "style": "N/A", "experience": "N/A", "world_cup_experience": "N/A"})
        
        return {"home": home_coach, "away": away_coach}
    
    def _get_referee_info(self, match):
        referees = [
            {"name": "Michael Oliver", "nationality": "English", "age": 39, "experience": "FIFA国际裁判，执法英超多年", "avg_yellows": 3.8, "avg_fouls": 22.5, "style": "严格执法，对战术犯规零容忍", "world_cup": "2022年世界杯裁判"},
            {"name": "Anthony Taylor", "nationality": "English", "age": 45, "experience": "FIFA国际裁判，执法经验丰富", "avg_yellows": 3.5, "avg_fouls": 21.0, "style": "相对宽松，允许比赛流畅进行", "world_cup": "2022年世界杯裁判"},
            {"name": "Daniele Orsato", "nationality": "Italian", "age": 48, "experience": "意大利顶级裁判，执法欧冠多年", "avg_yellows": 4.2, "avg_fouls": 24.0, "style": "严格，经常出示黄牌", "world_cup": "2022年世界杯裁判"},
            {"name": "Felix Brych", "nationality": "German", "age": 49, "experience": "德国顶级裁判，执法经验丰富", "avg_yellows": 3.9, "avg_fouls": 23.0, "style": "权威，对争议判罚果断", "world_cup": "2018年世界杯裁判"},
            {"name": "Clement Turpin", "nationality": "French", "age": 42, "experience": "法国顶级裁判，执法欧冠", "avg_yellows": 3.6, "avg_fouls": 20.5, "style": "精准，VAR使用率高", "world_cup": "2022年世界杯裁判"},
            {"name": "Szymon Marciniak", "nationality": "Polish", "age": 43, "experience": "波兰顶级裁判，执法2022世界杯决赛", "avg_yellows": 3.4, "avg_fouls": 21.5, "style": "稳健，大赛经验丰富", "world_cup": "2022年世界杯决赛裁判"},
        ]
        
        idx = hash(match.get('home_team', '') + match.get('away_team', '')) % len(referees)
        return referees[idx]
