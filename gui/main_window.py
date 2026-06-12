import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
from datetime import datetime

class FootballPredictorGUI:
    def __init__(self, root, scraper, weather_service, analyzer, config_manager):
        self.root = root
        self.scraper = scraper
        self.weather = weather_service
        self.analyzer = analyzer
        self.config_manager = config_manager
        
        self.matches = []
        self.selected_match = None
        
        self._setup_window()
        self._create_widgets()
        self._load_config()
        self._refresh_matches()
    
    def _setup_window(self):
        self.root.title("足球比赛预测工具 - 商业级分析")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        style = ttk.Style()
        style.theme_use('clam')
    
    def _create_widgets(self):
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        self._create_config_section(main)
        
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        left = ttk.Frame(paned, padding="5")
        paned.add(left, weight=1)
        
        right = ttk.Frame(paned, padding="5")
        paned.add(right, weight=2)
        
        self._create_match_list(left)
        self._create_detail_panel(right)
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=(10, 0))
    
    def _create_config_section(self, parent):
        config = ttk.LabelFrame(parent, text="模型配置", padding="10")
        config.pack(fill=tk.X, pady=(0, 10))
        
        summary = ttk.LabelFrame(config, text="归纳模型 (信息整理)", padding="5")
        summary.pack(fill=tk.X, pady=(0, 5))
        
        r1 = ttk.Frame(summary)
        r1.pack(fill=tk.X, pady=2)
        
        ttk.Label(r1, text="API地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.summary_url_var = tk.StringVar()
        ttk.Entry(r1, textvariable=self.summary_url_var, width=35).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(r1, text="密钥:").pack(side=tk.LEFT, padx=(0, 5))
        self.summary_key_var = tk.StringVar()
        ttk.Entry(r1, textvariable=self.summary_key_var, width=25, show="*").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(r1, text="模型:").pack(side=tk.LEFT, padx=(0, 5))
        self.summary_model_var = tk.StringVar()
        self.summary_model_combo = ttk.Combobox(r1, textvariable=self.summary_model_var, width=18)
        self.summary_model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(r1, text="测试", command=self._test_summary).pack(side=tk.LEFT, padx=2)
        ttk.Button(r1, text="获取模型", command=self._fetch_summary_models).pack(side=tk.LEFT, padx=2)
        
        analysis = ttk.LabelFrame(config, text="分析模型 (深度预测)", padding="5")
        analysis.pack(fill=tk.X, pady=(0, 5))
        
        r2 = ttk.Frame(analysis)
        r2.pack(fill=tk.X, pady=2)
        
        ttk.Label(r2, text="API地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.analysis_url_var = tk.StringVar()
        ttk.Entry(r2, textvariable=self.analysis_url_var, width=35).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(r2, text="密钥:").pack(side=tk.LEFT, padx=(0, 5))
        self.analysis_key_var = tk.StringVar()
        ttk.Entry(r2, textvariable=self.analysis_key_var, width=25, show="*").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(r2, text="模型:").pack(side=tk.LEFT, padx=(0, 5))
        self.analysis_model_var = tk.StringVar()
        self.analysis_model_combo = ttk.Combobox(r2, textvariable=self.analysis_model_var, width=18)
        self.analysis_model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(r2, text="测试", command=self._test_analysis).pack(side=tk.LEFT, padx=2)
        ttk.Button(r2, text="获取模型", command=self._fetch_analysis_models).pack(side=tk.LEFT, padx=2)
        
        r3 = ttk.Frame(config)
        r3.pack(fill=tk.X, pady=2)
        
        ttk.Label(r3, text="天气API密钥:").pack(side=tk.LEFT, padx=(0, 5))
        self.weather_key_var = tk.StringVar()
        ttk.Entry(r3, textvariable=self.weather_key_var, width=20, show="*").pack(side=tk.LEFT, padx=(0, 5))
        
        link = ttk.Label(r3, text="免费获取: openweathermap.org/api", foreground="blue", cursor="hand2")
        link.pack(side=tk.LEFT, padx=(0, 10))
        link.bind("<Button-1>", lambda e: self._open_url("https://openweathermap.org/api"))
        
        ttk.Button(r3, text="保存配置", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(r3, text="刷新比赛", command=self._refresh_matches).pack(side=tk.LEFT, padx=5)
    
    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def _test_connection(self, url, key, callback):
        def test():
            try:
                resp = requests.get(f"{url.rstrip('/')}/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=10)
                msg = "连接成功!" if resp.status_code == 200 else f"HTTP {resp.status_code}"
                self.root.after(0, lambda: callback(resp.status_code == 200, msg))
            except Exception as e:
                self.root.after(0, lambda: callback(False, str(e)))
        threading.Thread(target=test, daemon=True).start()
    
    def _test_summary(self):
        if not self.summary_url_var.get() or not self.summary_key_var.get():
            messagebox.showwarning("提示", "请填写API地址和密钥")
            return
        self.status_var.set("测试中...")
        def cb(ok, msg):
            self.status_var.set(msg)
            messagebox.showinfo("测试结果", msg)
        self._test_connection(self.summary_url_var.get(), self.summary_key_var.get(), cb)
    
    def _test_analysis(self):
        if not self.analysis_url_var.get() or not self.analysis_key_var.get():
            messagebox.showwarning("提示", "请填写API地址和密钥")
            return
        self.status_var.set("测试中...")
        def cb(ok, msg):
            self.status_var.set(msg)
            messagebox.showinfo("测试结果", msg)
        self._test_connection(self.analysis_url_var.get(), self.analysis_key_var.get(), cb)
    
    def _fetch_models(self, url, key, combo):
        def fetch():
            try:
                resp = requests.get(f"{url.rstrip('/')}/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=15)
                if resp.status_code == 200:
                    models = sorted([m['id'] for m in resp.json().get('data', []) if m.get('id')])
                    self.root.after(0, lambda: combo.configure(values=models))
                    self.root.after(0, lambda: self.status_var.set(f"获取到 {len(models)} 个模型"))
                    if models:
                        self.root.after(0, lambda: combo.set(models[0]))
                else:
                    self.root.after(0, lambda: self.status_var.set(f"获取失败: HTTP {resp.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"错误: {e}"))
        threading.Thread(target=fetch, daemon=True).start()
    
    def _fetch_summary_models(self):
        if not self.summary_url_var.get() or not self.summary_key_var.get():
            messagebox.showwarning("提示", "请填写API地址和密钥")
            return
        self._fetch_models(self.summary_url_var.get(), self.summary_key_var.get(), self.summary_model_combo)
    
    def _fetch_analysis_models(self):
        if not self.analysis_url_var.get() or not self.analysis_key_var.get():
            messagebox.showwarning("提示", "请填写API地址和密钥")
            return
        self._fetch_models(self.analysis_url_var.get(), self.analysis_key_var.get(), self.analysis_model_combo)
    
    def _create_match_list(self, parent):
        ttk.Label(parent, text="未来比赛", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.match_listbox = tk.Listbox(frame, font=('Consolas', 10), yscrollcommand=scrollbar.set)
        self.match_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.match_listbox.yview)
        
        self.match_listbox.bind('<<ListboxSelect>>', self._on_match_select)
    
    def _create_detail_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="比赛信息")
        
        self.info_text = scrolledtext.ScrolledText(info_frame, font=('Consolas', 10), wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        pred_frame = ttk.Frame(notebook)
        notebook.add(pred_frame, text="AI预测分析")
        
        self.pred_text = scrolledtext.ScrolledText(pred_frame, font=('Consolas', 10), wrap=tk.WORD, state=tk.DISABLED)
        self.pred_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(pred_frame, text="开始AI预测分析", command=self._start_prediction).pack(pady=10)
    
    def _load_config(self):
        cfg = self.config_manager()
        self.summary_url_var.set(cfg.get("summary_base_url", ""))
        self.summary_key_var.set(cfg.get("summary_api_key", ""))
        self.summary_model_var.set(cfg.get("llm_model_summary", ""))
        self.analysis_url_var.set(cfg.get("analysis_base_url", ""))
        self.analysis_key_var.set(cfg.get("analysis_api_key", ""))
        self.analysis_model_var.set(cfg.get("llm_model_analysis", ""))
        self.weather_key_var.set(cfg.get("weather_api_key", ""))
    
    def _save_config(self):
        from config import save_config
        save_config({
            "summary_base_url": self.summary_url_var.get(),
            "summary_api_key": self.summary_key_var.get(),
            "llm_model_summary": self.summary_model_var.get(),
            "analysis_base_url": self.analysis_url_var.get(),
            "analysis_api_key": self.analysis_key_var.get(),
            "llm_model_analysis": self.analysis_model_var.get(),
            "weather_api_key": self.weather_key_var.get()
        })
        messagebox.showinfo("成功", "配置已保存")
    
    def _refresh_matches(self):
        self.match_listbox.delete(0, tk.END)
        self.match_listbox.insert(tk.END, "正在获取比赛...")
        
        def progress(msg):
            self.root.after(0, lambda: self.status_var.set(msg))
        
        self.scraper.set_progress_callback(progress)
        
        def fetch():
            try:
                self.matches = self.scraper.get_matches()
                self.root.after(0, self._update_list)
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"获取失败: {e}"))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _update_list(self):
        self.match_listbox.delete(0, tk.END)
        
        if not self.matches:
            self.match_listbox.insert(tk.END, "未找到比赛")
            return
        
        current_date = ""
        for m in self.matches:
            if m['date'] != current_date:
                current_date = m['date']
                try:
                    dt = datetime.strptime(m['date'], "%Y-%m-%d")
                    weekday = ["周一","周二","周三","周四","周五","周六","周日"][dt.weekday()]
                    self.match_listbox.insert(tk.END, f"── {m['date']} {weekday} ──")
                    self.match_listbox.itemconfig(tk.END, fg='gray')
                except:
                    self.match_listbox.insert(tk.END, f"── {m['date']} ──")
            
            display = f"  {m['time']:12s} {m['home_team']} vs {m['away_team']}"
            self.match_listbox.insert(tk.END, display)
        
        self.status_var.set(f"共 {len(self.matches)} 场比赛")
    
    def _on_match_select(self, event):
        sel = self.match_listbox.curselection()
        if not sel:
            return
        
        idx = sel[0]
        match_idx = 0
        for i, m in enumerate(self.matches):
            if i == 0 or m['date'] != self.matches[i-1]['date']:
                if idx == match_idx:
                    return
                match_idx += 1
            if match_idx == idx:
                self.selected_match = m
                self._load_match_info(m)
                break
            match_idx += 1
    
    def _load_match_info(self, match):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"正在收集 {match['home_team']} vs {match['away_team']} 的信息...\n")
        self.info_text.config(state=tk.DISABLED)
        
        def progress(msg):
            self.root.after(0, lambda: self._append_info(f"  {msg}\n"))
        
        self.scraper.set_progress_callback(progress)
        
        def load():
            try:
                details = self.scraper.get_match_details(match)
                self.root.after(0, lambda: self._display_details(match, details))
            except Exception as e:
                self.root.after(0, lambda: self._append_info(f"\n错误: {e}\n"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _append_info(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _display_details(self, match, details):
        home = details.get('home_team_info', {})
        away = details.get('away_team_info', {})
        odds = details.get('odds_info', {})
        weather = details.get('weather_info', {})
        coaches = details.get('coach_info', {})
        referee = details.get('referee_info', {})
        
        def format_players(team_info):
            lines = []
            for p in team_info.get('players', []):
                status = ""
                if p.get('suspended'):
                    status = " [停赛]"
                elif p.get('out'):
                    status = " [受伤]"
                elif p.get('doubtful'):
                    status = " [存疑]"
                lines.append(f"    {p['position_full']:20s} {p['full_name']}{status}")
            return "\n".join(lines)
        
        def format_injuries(team_info):
            injuries = team_info.get('injuries', [])
            if not injuries:
                return "    无缺阵球员"
            lines = []
            for p in injuries:
                lines.append(f"    {p['full_name']} ({p['position_full']}) - {p['injury_status']}")
            return "\n".join(lines)
        
        def format_coach(c):
            return f"""    姓名: {c.get('name', 'N/A')}
    国籍: {c.get('nationality', 'N/A')}
    年龄: {c.get('age', 'N/A')}
    执教风格: {c.get('style', 'N/A')}
    执教经历: {c.get('experience', 'N/A')}
    世界杯经验: {c.get('world_cup_experience', 'N/A')}"""
        
        def format_weather(w):
            if not w or not w.get('available'):
                return "    天气信息暂不可用"
            return f"""    温度: {w.get('temperature_f', 'N/A')}°F / {w.get('temperature_c', 'N/A')}°C
    风速: {w.get('wind_mph', 'N/A')} mph / {w.get('wind_kmh', 'N/A')} km/h
    降雨概率: {w.get('rain_chance', 'N/A')}%
    比赛条件: {w.get('conditions', 'N/A')}"""
        
        def format_odds(o):
            if not o.get('available'):
                return "    赔率数据暂不可用"
            
            platforms = o.get('platforms', {})
            lines = [f"    数据来源: {o.get('source', 'N/A')}"]
            lines.append("")
            lines.append(f"    {'平台':<15s} {'主胜':<10s} {'平局':<10s} {'客胜':<10s}")
            lines.append(f"    {'-'*45}")
            
            for name, vals in platforms.items():
                if vals['home'] != 'N/A' or vals['draw'] != 'N/A' or vals['away'] != 'N/A':
                    lines.append(f"    {name:<15s} {vals['home']:<10s} {vals['draw']:<10s} {vals['away']:<10s}")
            
            lines.append("")
            lines.append(f"    最佳赔率:")
            lines.append(f"      主胜: {o.get('best_home', 'N/A')} (隐含概率: {o.get('home_implied_prob', 'N/A')})")
            lines.append(f"      平局: {o.get('best_draw', 'N/A')} (隐含概率: {o.get('draw_implied_prob', 'N/A')})")
            lines.append(f"      客胜: {o.get('best_away', 'N/A')} (隐含概率: {o.get('away_implied_prob', 'N/A')})")
            
            return "\n".join(lines)
        
        def format_referee(r):
            return f"""    姓名: {r.get('name', 'N/A')}
    国籍: {r.get('nationality', 'N/A')}
    年龄: {r.get('age', 'N/A')}
    执法经验: {r.get('experience', 'N/A')}
    执法风格: {r.get('style', 'N/A')}
    场均黄牌: {r.get('avg_yellows', 'N/A')}张
    场均犯规: {r.get('avg_fouls', 'N/A')}次
    世界杯经验: {r.get('world_cup', 'N/A')}"""
        
        info = f"""
{'='*65}
  比赛: {match['home_team']} vs {match['away_team']}
  日期: {match['date']}  时间: {match['time']}
  联赛: {match['league']}
{'='*65}

╔═══════════════════════════════════════════════════════════════╗
║                      赔率信息 (多平台对比)                   ║
╚═══════════════════════════════════════════════════════════════╝
{format_odds(odds)}

╔═══════════════════════════════════════════════════════════════╗
║                      天气信息                                ║
╚═══════════════════════════════════════════════════════════════╝
{format_weather(weather)}

╔═══════════════════════════════════════════════════════════════╗
║                      裁判信息                                ║
╚═══════════════════════════════════════════════════════════════╝
{format_referee(referee)}

{'='*65}
  主队: {match['home_team']}
  阵型: {home.get('formation', 'N/A')} | 状态: {home.get('status', 'N/A')}
  球员: {home.get('player_count', 0)}人 | 可用: {home.get('available_count', 0)}人 | 伤病: {home.get('injury_count', 0)}人
{'='*65}

╔═══════════════════════════════════════════════════════════════╗
║  主队教练: {match['home_team']}
╚═══════════════════════════════════════════════════════════════╝
{format_coach(coaches.get('home', {}))}

╔═══════════════════════════════════════════════════════════════╗
║  主队首发阵容
╚═══════════════════════════════════════════════════════════════╝
{format_players(home)}

╔═══════════════════════════════════════════════════════════════╗
║  主队伤病/停赛
╚═══════════════════════════════════════════════════════════════╝
{format_injuries(home)}

{'='*65}
  客队: {match['away_team']}
  阵型: {away.get('formation', 'N/A')} | 状态: {away.get('status', 'N/A')}
  球员: {away.get('player_count', 0)}人 | 可用: {away.get('available_count', 0)}人 | 伤病: {away.get('injury_count', 0)}人
{'='*65}

╔═══════════════════════════════════════════════════════════════╗
║  客队教练: {match['away_team']}
╚═══════════════════════════════════════════════════════════════╝
{format_coach(coaches.get('away', {}))}

╔═══════════════════════════════════════════════════════════════╗
║  客队首发阵容
╚═══════════════════════════════════════════════════════════════╝
{format_players(away)}

╔═══════════════════════════════════════════════════════════════╗
║  客队伤病/停赛
╚═══════════════════════════════════════════════════════════════╝
{format_injuries(away)}

{'='*65}
"""
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        self.status_var.set("信息收集完成，可以开始AI分析")
    
    def _start_prediction(self):
        if not self.selected_match:
            messagebox.showwarning("提示", "请先选择比赛")
            return
        
        s_url = self.summary_url_var.get()
        s_key = self.summary_key_var.get()
        s_model = self.summary_model_var.get()
        a_url = self.analysis_url_var.get()
        a_key = self.analysis_key_var.get()
        a_model = self.analysis_model_var.get()
        
        if not all([s_url, s_key, s_model, a_url, a_key, a_model]):
            messagebox.showwarning("提示", "请填写完整的模型配置")
            return
        
        self.status_var.set("AI分析中...")
        self.pred_text.config(state=tk.NORMAL)
        self.pred_text.delete(1.0, tk.END)
        self.pred_text.insert(1.0, "正在进行AI分析，请稍候...\n\n")
        self.pred_text.config(state=tk.DISABLED)
        
        def predict():
            try:
                from analyzer.ai_analyzer import AIAnalyzer
                ai = AIAnalyzer(s_url, s_key, s_model, a_url, a_key, a_model)
                
                details = self.scraper.get_match_details(self.selected_match)
                
                result = ai.predict_match(details, {})
                
                self.root.after(0, lambda: self._display_prediction(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"分析失败: {e}"))
                self.root.after(0, lambda: self.status_var.set(f"分析失败: {e}"))
        
        threading.Thread(target=predict, daemon=True).start()
    
    def _display_prediction(self, result):
        info = result.get('match_info', {})
        analysis = result.get('analysis', '无结果')
        
        header = f"""
{'='*60}
  AI预测分析报告
  {info.get('home_team', '')} vs {info.get('away_team', '')}
  {info.get('date', '')} {info.get('time', '')}
{'='*60}

"""
        
        self.pred_text.config(state=tk.NORMAL)
        self.pred_text.delete(1.0, tk.END)
        self.pred_text.insert(1.0, header + analysis)
        self.pred_text.config(state=tk.DISABLED)
        self.status_var.set("AI分析完成")
