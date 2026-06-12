import requests
import json
import time

class AIAnalyzer:
    def __init__(self, summary_url, summary_key, summary_model, 
                 analysis_url, analysis_key, analysis_model):
        self.summary_url = summary_url.rstrip('/')
        self.summary_key = summary_key
        self.summary_model = summary_model
        self.analysis_url = analysis_url.rstrip('/')
        self.analysis_key = analysis_key
        self.analysis_model = analysis_model
        self.max_retries = 3
        self.retry_delay = 2
    
    def _call_llm(self, base_url, api_key, model, system_prompt, user_prompt):
        url = f"{base_url}/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return f"API错误: HTTP {response.status_code}"
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return "API超时，请稍后重试"
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return f"错误: {str(e)}"
        
        return "API调用失败，已达最大重试次数"
    
    def _format_odds_platforms(self, odds):
        platforms = odds.get('platforms', {})
        if not platforms:
            return "无平台赔率数据"
        
        lines = []
        lines.append(f"{'平台':<15s} {'主胜':<10s} {'平局':<10s} {'客胜':<10s}")
        lines.append(f"{'-'*45}")
        
        for name, vals in platforms.items():
            home = vals.get('home', 'N/A')
            draw = vals.get('draw', 'N/A')
            away = vals.get('away', 'N/A')
            if home != 'N/A' or draw != 'N/A' or away != 'N/A':
                lines.append(f"{name:<15s} {home:<10s} {draw:<10s} {away:<10s}")
        
        return "\n".join(lines) if len(lines) > 2 else "无可用赔率数据"
    
    def _get_competition_type(self, league_code):
        """根据联赛代码返回比赛性质"""
        competition_map = {
            "WOC": {
                "name": "2026年FIFA世界杯",
                "type": "世界杯小组赛",
                "level": "最高级别国际赛事",
                "importance": "4年一度的足球最高荣誉赛事",
                "format": "小组赛阶段，每场比赛都至关重要"
            },
            "EPL": {
                "name": "英格兰足球超级联赛",
                "type": "联赛",
                "level": "顶级职业联赛",
                "importance": "全球最受关注的足球联赛之一",
                "format": "38轮联赛制"
            },
            "UCL": {
                "name": "欧洲冠军联赛",
                "type": "欧冠",
                "level": "欧洲俱乐部最高荣誉",
                "importance": "欧洲俱乐部最高水平赛事",
                "format": "小组赛+淘汰赛制"
            },
            "LIGA": {
                "name": "西班牙足球甲级联赛",
                "type": "联赛",
                "level": "顶级职业联赛",
                "importance": "技术流足球代表联赛",
                "format": "38轮联赛制"
            },
            "BUND": {
                "name": "德国足球甲级联赛",
                "type": "联赛",
                "level": "顶级职业联赛",
                "importance": "战术纪律严明的联赛",
                "format": "34轮联赛制"
            },
            "SERI": {
                "name": "意大利足球甲级联赛",
                "type": "联赛",
                "level": "顶级职业联赛",
                "importance": "防守艺术的代表联赛",
                "format": "38轮联赛制"
            },
            "FRAN": {
                "name": "法国足球甲级联赛",
                "type": "联赛",
                "level": "顶级职业联赛",
                "importance": "新兴足球强国联赛",
                "format": "34轮联赛制"
            },
            "MLS": {
                "name": "美国职业足球大联盟",
                "type": "联赛",
                "level": "职业联赛",
                "importance": "北美顶级足球联赛",
                "format": "常规赛+季后赛制"
            }
        }
        return competition_map.get(league_code, {
            "name": "足球比赛",
            "type": "未知",
            "level": "未知",
            "importance": "未知",
            "format": "未知"
        })
    
    def summarize_match_data(self, match_details):
        system_prompt = """你是一位资深的足球数据分析师，拥有20年的足球情报收集和分析经验。你的任务是整理和归纳比赛相关的所有信息，为专业的比赛预测提供最详实的数据支持。

【重要指令】
1. 首先必须准确识别比赛性质（世界杯/联赛/杯赛/友谊赛等）
2. 根据比赛性质调整分析的重点和角度
3. 世界杯等大赛要特别强调国家荣誉、球员压力、赛程影响等因素
4. 联赛要强调积分榜位置、赛季目标、保级/争冠压力等因素

请严格按照以下结构整理信息，不遗漏任何细节："""

        match_info = match_details.get('match_info', {})
        home_info = match_details.get('home_team_info', {})
        away_info = match_details.get('away_team_info', {})
        odds = match_details.get('odds_info', {})
        weather = match_details.get('weather_info', {})
        coaches = match_details.get('coach_info', {})
        referee = match_details.get('referee_info', {})
        
        league_code = match_info.get('league', '')
        competition = self._get_competition_type(league_code)
        
        def format_players(players):
            lines = []
            for p in players:
                status = ""
                if p.get('suspended'):
                    status = " [停赛]"
                elif p.get('out'):
                    status = " [受伤]"
                elif p.get('doubtful'):
                    status = " [存疑]"
                lines.append(f"    {p['position_full']:20s} {p['full_name']}{status}")
            return "\n".join(lines)
        
        def format_injuries(injuries):
            if not injuries:
                return "    无缺阵球员"
            lines = []
            for p in injuries:
                lines.append(f"    {p['full_name']} ({p['position_full']}) - {p['injury_status']}")
            return "\n".join(lines)
        
        def format_coach(coach):
            return f"""    姓名: {coach.get('name', 'N/A')}
    国籍: {coach.get('nationality', 'N/A')}
    年龄: {coach.get('age', 'N/A')}
    风格: {coach.get('style', 'N/A')}
    经历: {coach.get('experience', 'N/A')}
    世界杯经验: {coach.get('world_cup_experience', 'N/A')}"""
        
        def format_weather(w):
            if not w or not w.get('available'):
                return "天气信息暂不可用"
            return f"""    温度: {w.get('temperature_f', 'N/A')}°F / {w.get('temperature_c', 'N/A')}°C
    风速: {w.get('wind_mph', 'N/A')} mph / {w.get('wind_kmh', 'N/A')} km/h
    降雨概率: {w.get('rain_chance', 'N/A')}%
    影响分析: {w.get('conditions', 'N/A')}"""
        
        user_prompt = f"""请整理以下比赛的详细信息：

═══════════════════════════════════════════════════════════════
【比赛性质识别】
═══════════════════════════════════════════════════════════════
赛事名称: {competition['name']}
比赛类型: {competition['type']}
赛事级别: {competition['level']}
赛事重要性: {competition['importance']}
赛制说明: {competition['format']}

═══════════════════════════════════════════════════════════════
比赛信息
═══════════════════════════════════════════════════════════════
主队: {match_info.get('home_team', 'N/A')}
客队: {match_info.get('away_team', 'N/A')}
日期: {match_info.get('date', 'N/A')}
时间: {match_info.get('time', 'N/A')}
联赛代码: {match_info.get('league', 'N/A')}

═══════════════════════════════════════════════════════════════
主队信息: {match_info.get('home_team', 'N/A')}
═══════════════════════════════════════════════════════════════
阵容状态: {home_info.get('status', 'N/A')}
阵型: {home_info.get('formation', 'N/A')}
球员人数: {home_info.get('player_count', 0)}
可用球员: {home_info.get('available_count', 0)}
伤病人数: {home_info.get('injury_count', 0)}

教练信息:
{format_coach(coaches.get('home', {}))}

首发阵容:
{format_players(home_info.get('players', []))}

伤病/停赛:
{format_injuries(home_info.get('injuries', []))}

═══════════════════════════════════════════════════════════════
客队信息: {match_info.get('away_team', 'N/A')}
═══════════════════════════════════════════════════════════════
阵容状态: {away_info.get('status', 'N/A')}
阵型: {away_info.get('formation', 'N/A')}
球员人数: {away_info.get('player_count', 0)}
可用球员: {away_info.get('available_count', 0)}
伤病人数: {away_info.get('injury_count', 0)}

教练信息:
{format_coach(coaches.get('away', {}))}

首发阵容:
{format_players(away_info.get('players', []))}

伤病/停赛:
{format_injuries(away_info.get('injuries', []))}

═══════════════════════════════════════════════════════════════
裁判信息
═══════════════════════════════════════════════════════════════
姓名: {referee.get('name', 'N/A')}
国籍: {referee.get('nationality', 'N/A')}
年龄: {referee.get('age', 'N/A')}
经验: {referee.get('experience', 'N/A')}
风格: {referee.get('style', 'N/A')}
场均黄牌: {referee.get('avg_yellows', 'N/A')}
场均犯规: {referee.get('avg_fouls', 'N/A')}
世界杯经验: {referee.get('world_cup', 'N/A')}

═══════════════════════════════════════════════════════════════
赔率信息 (多平台对比)
═══════════════════════════════════════════════════════════════
数据来源: {odds.get('source', 'N/A')}

各平台赔率:
{self._format_odds_platforms(odds)}

最佳赔率:
  主胜: {odds.get('best_home', 'N/A')} (隐含概率: {odds.get('home_implied_prob', 'N/A')})
  平局: {odds.get('best_draw', 'N/A')} (隐含概率: {odds.get('draw_implied_prob', 'N/A')})
  客胜: {odds.get('best_away', 'N/A')} (隐含概率: {odds.get('away_implied_prob', 'N/A')})

═══════════════════════════════════════════════════════════════
天气信息
═══════════════════════════════════════════════════════════════
{format_weather(weather)}

请首先明确指出这是什么性质的比赛（世界杯/联赛/杯赛/友谊赛），然后进行详细的信息整理和归纳。"""

        return self._call_llm(self.summary_url, self.summary_key, self.summary_model, 
                             system_prompt, user_prompt)
    
    def analyze_match(self, summary, match_info):
        league_code = match_info.get('league', '')
        competition = self._get_competition_type(league_code)
        
        system_prompt = f"""你是一位世界顶级的足球比赛预测分析师，拥有以下专业背景：
- 20年职业足球分析经验
- 曾为欧洲顶级俱乐部提供战术分析
- 精通各大联赛的战术体系和球员特点
- 擅长数据建模和概率分析
- 对世界杯等大赛有深入研究

【重要提醒】
这场比赛是：{competition['name']} - {competition['type']}

请根据比赛性质进行针对性分析：
- 如果是世界杯：强调国家荣誉、球员为国出战的动力、小组赛出线压力、赛程密集度对体能的影响
- 如果是联赛：强调积分榜形势、赛季目标（争冠/保级/欧战资格）、主客场优势
- 如果是杯赛淘汰赛：强调两回合赛制、客场进球规则等

请基于提供的详细比赛信息，进行专业、深入、全面的比赛预测分析。

你的分析必须包含以下部分，每部分都要有详细的论述和数据支持：

═══════════════════════════════════════════════════════════════
【第一部分：比赛性质与背景分析】
═══════════════════════════════════════════════════════════════

1.1 赛事背景
- 明确说明这是什么赛事（{competition['name']}）
- 赛事的重要性和意义
- 比赛在赛事中的位置和意义

1.2 双方出线/积分形势
- 双方目前的排名或积分情况
- 这场比赛对双方的意义
- 双方的出线/争冠/保级压力

═══════════════════════════════════════════════════════════════
【第二部分：阵容与战术分析】
═══════════════════════════════════════════════════════════════

2.1 阵型对比分析
- 双方阵型的优劣势
- 阵型之间的克制关系
- 关键位置的对位分析

2.2 首发阵容评估
- 各位置球员能力评估
- 阵容完整度评分（1-10分）
- 缺阵球员对战术的影响

2.3 战术风格预测
- 双方可能的进攻策略
- 防守组织方式
- 定位球战术

═══════════════════════════════════════════════════════════════
【第三部分：教练因素分析】
═══════════════════════════════════════════════════════════════

3.1 教练战术理念
- 执教风格对比
- 战术灵活性评估
- 大赛经验对比

3.2 临场指挥能力
- 换人策略
- 战术调整能力
- 落后/领先时的应对

═══════════════════════════════════════════════════════════════
【第四部分：关键球员分析】
═══════════════════════════════════════════════════════════════

4.1 双方核心球员
- 技术特点分析
- 近期状态评估
- 对比赛的影响力

4.2 关键对位
- 可能决定比赛的球员对决
- 优势/劣势分析

═══════════════════════════════════════════════════════════════
【第五部分：裁判与环境因素】
═══════════════════════════════════════════════════════════════

5.1 裁判影响分析
- 执法风格对比赛的影响
- 对不同战术风格的偏好
- 黄牌/犯规趋势

5.2 天气影响分析
- 温度对体能的影响
- 风速对技术发挥的影响
- 场地条件评估

═══════════════════════════════════════════════════════════════
【第六部分：数据与概率分析】
═══════════════════════════════════════════════════════════════

6.1 赔率分析
- 市场隐含概率解读
- 赔率变化趋势
- 价值投注机会

6.2 历史数据参考
- 双方历史交锋记录
- 类似对阵情况分析

═══════════════════════════════════════════════════════════════
【第七部分：风险评估】
═══════════════════════════════════════════════════════════════

7.1 不确定因素
- 可能影响比赛结果的意外因素
- 冷门可能性评估

7.2 预测局限性
- 数据不足的方面
- 可能的偏差

═══════════════════════════════════════════════════════════════
【第八部分：最终预测】
═══════════════════════════════════════════════════════════════

8.1 胜负预测
- 主胜概率: XX%
- 平局概率: XX%
- 客胜概率: XX%

8.2 比分预测
- 最可能比分: X:X (概率XX%)
- 次可能比分: X:X (概率XX%)
- 第三可能比分: X:X (概率XX%)

8.3 其他预测
- 总进球数预测: 大/小 X.5球
- 双方进球预测: 是/否
- 半场/全场预测

8.4 投注建议（仅供参考）
- 推荐方向
- 置信度评分（1-10分）

请确保分析专业、深入、有理有据，充分发挥你的专业能力。"""

        user_prompt = f"""请基于以下详细比赛信息，进行专业的比赛预测分析：

═══════════════════════════════════════════════════════════════
比赛: {match_info.get('home_team', '主队')} vs {match_info.get('away_team', '客队')}
赛事: {competition['name']} ({competition['type']})
日期: {match_info.get('date', '')} {match_info.get('time', '')}
═══════════════════════════════════════════════════════════════

【详细信息摘要】
{summary}

请首先明确这是{competition['name']}的比赛，然后给出你的专业分析和比分预测。"""

        return self._call_llm(self.analysis_url, self.analysis_key, self.analysis_model, 
                             system_prompt, user_prompt)
    
    def predict_match(self, match_details, weather_data):
        summary = self.summarize_match_data(match_details)
        
        analysis = self.analyze_match(summary, match_details.get('match_info', {}))
        
        return {
            "summary": summary,
            "analysis": analysis,
            "match_info": match_details.get('match_info', {}),
            "odds": match_details.get('odds_info', {}),
        }
