import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
import requests
import re
import zipfile
import io

class Config:
    YTDLP_FILENAME = "yt-dlp.exe"
    ARIA2_FILENAME = "aria2c.exe"
    YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    # Aria2 Windows 64-bit 穩定載點
    ARIA2_URL = "https://github.com/aria2/aria2/releases/latest/download/aria2-1.37.0-win-64bit-build1.zip"

    @staticmethod
    def get_app_path():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_ytdlp_path():
        return os.path.join(Config.get_app_path(), Config.YTDLP_FILENAME)

    @staticmethod
    def get_aria2_path():
        return os.path.join(Config.get_app_path(), Config.ARIA2_FILENAME)

    @staticmethod
    def get_ffmpeg_path():
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

class ComponentManager:
    def __init__(self, status_callback):
        self.status_callback = status_callback

    def check_all(self):
        # 管理 yt-dlp
        y_path = Config.get_ytdlp_path()
        if not os.path.exists(y_path):
            self.status_callback("正在下載核心 (yt-dlp)...")
            self._download_direct(Config.YTDLP_URL, y_path)
        else:
            self.status_callback("正在檢查 yt-dlp 更新...")
            try:
                subprocess.run([y_path, "-U"], capture_output=True, creationflags=0x08000000)
            except: pass

        # 管理 aria2
        a_path = Config.get_aria2_path()
        if not os.path.exists(a_path):
            self.status_callback("正在自動配置 Aria2 加速器...")
            try:
                r = requests.get(Config.ARIA2_URL)
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    for f_name in z.namelist():
                        if f_name.endswith("aria2c.exe"):
                            with open(a_path, 'wb') as f:
                                f.write(z.read(f_name))
                self.status_callback("Aria2 配置成功")
            except:
                self.status_callback("Aria2 自動下載失敗，將使用一般模式")

    def _download_direct(self, url, dest):
        r = requests.get(url, stream=True)
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(8192): f.write(chunk)

class Downloader:
    def __init__(self, progress_callback, status_callback, finished_callback):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.finished_callback = finished_callback

    def start(self, url, folder, filename, fmt, browser="chrome"):
        threading.Thread(target=self._run, args=(url, folder, filename, fmt, browser), daemon=True).start()

    def _run(self, url, folder, filename, fmt, browser):
        y_path = Config.get_ytdlp_path()
        a_path = Config.get_aria2_path()
        f_path = Config.get_ffmpeg_path()

        if not os.path.exists(y_path):
            self.finished_callback(False, "核心組件缺失")
            return

        # 完整補全參數
        cmd = [
            y_path, url,
            "--ffmpeg-location", f_path,
            "--newline", # 關鍵：讓輸出變成一行一行，方便解析
            "--no-warnings",
            "--progress-template", "%(progress._percent_str)s", # 只輸出百分比
            "--no-check-certificate", # 忽略 SSL 憑證錯誤
            "--legacy-server-connect",
            # "--cookies-from-browser", "chrome", # 讀取 Chrome 登入狀態（需先關閉 Chrome）
            "--windows-filenames",            # 防止存檔字元報錯
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # 偽裝成瀏覽器
            "--referer", "https://istudy.way-to-win.com/", # 嘗試加入 Referer
        ]

        # Cookie 處理策略
        # 1. 優先尋找目錄下的 cookies.txt (推薦，最穩定)
        # 2. 如果沒有，才嘗試直接讀取 Chrome (需要關閉瀏覽器)
        local_cookie = os.path.join(Config.get_app_path(), "cookies.txt")
        if os.path.exists(local_cookie):
            cmd.extend(["--cookies", local_cookie])
        elif browser and browser.lower() != "none":
            cmd.extend(["--cookies-from-browser", browser])

        if os.path.exists(a_path):
            cmd.extend(["--external-downloader", a_path, "--external-downloader-args", "aria2c:-x 16 -k 1M -j 16"])

        outtmpl = os.path.join(folder, (filename if filename else "%(title)s") + ".%(ext)s")
        cmd.extend(["-o", outtmpl])

        if fmt == "MP3": cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "192K"])
        elif fmt == "WAV": cmd.extend(["-x", "--audio-format", "wav"])
        else: cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])

        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', creationflags=0x08000000)
            while True:
                line = p.stdout.readline()
                if not line and p.poll() is not None: break
                if "%" in line:
                    try:
                        # 優化進度條解析邏輯，使用正則表達式抓取百分比數字
                        # 這樣無論是 yt-dlp 原生格式還是 aria2 的格式都能正確抓到
                        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line) # 移除顏色碼
                        match = re.search(r'(\d+\.?\d*)%', clean_line)
                        if match:
                            val = float(match.group(1))
                            self.progress_callback(val)
                            self.status_callback(f"下載中... {val:.1f}%")
                    except: pass
            if p.returncode == 0: self.finished_callback(True, "下載成功！")
            else: 
                err = p.stderr.read()
                # 針對 Chrome 鎖定問題提供中文提示
                if "Could not copy Chrome cookie database" in err:
                    err = "抓取 Cookie 失敗！\n請「完全關閉 Chrome 瀏覽器」後再試。\n(或是使用 cookies.txt 方式)"
                self.finished_callback(False, f"失敗: {err}")
        except Exception as e: self.finished_callback(False, str(e))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("影音下載器")
        self.setup_ui()
        self.manager = ComponentManager(self.update_status)
        self.downloader = Downloader(self.update_progress, self.update_status, self.on_download_finished)
        self.root.after(100, self.start_check)

    def setup_ui(self):
        # 這裡完整保留並優化你的原版 UI 排版
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()

        # URL
        ttk.Label(frame, text="輸入影片或音樂連結:").grid(column=0, row=0, sticky=tk.W)
        self.url_entry = ttk.Entry(frame, width=50)
        self.url_entry.grid(column=0, row=1, sticky=tk.W)

        # 支援列表
        support_text = "支援平台: YouTube, FB, IG, Twitch, SoundCloud..."
        ttk.Label(frame, text=support_text).grid(column=0, row=2, sticky=tk.W, pady=(5, 15))

        # 檔名
        ttk.Label(frame, text="自訂檔名 (留空則使用原標題):").grid(column=0, row=3, sticky=tk.W)
        self.filename_entry = ttk.Entry(frame, width=50)
        self.filename_entry.grid(column=0, row=4, sticky=tk.W)

        # 瀏覽器選擇 (新增)
        ttk.Label(frame, text="登入來源 (若 Chrome 失敗請改用 Edge):").grid(column=0, row=5, sticky=tk.W, pady=(10, 0))
        self.browser_var = tk.StringVar(value="chrome")
        browser_frame = ttk.Frame(frame)
        browser_frame.grid(column=0, row=6, sticky=tk.W)
        ttk.Radiobutton(browser_frame, text="Chrome", variable=self.browser_var, value="chrome").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(browser_frame, text="Edge", variable=self.browser_var, value="edge").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(browser_frame, text="Firefox", variable=self.browser_var, value="firefox").pack(side=tk.LEFT)

        # 格式
        ttk.Label(frame, text="選擇下載格式:").grid(column=0, row=7, sticky=tk.W, pady=(10, 0))
        self.format_var = tk.StringVar(value="MP3")
        ttk.Radiobutton(frame, text="MP3 (音訊)", variable=self.format_var, value="MP3").grid(column=0, row=8, sticky=tk.W)
        ttk.Radiobutton(frame, text="WAV (無損音訊)", variable=self.format_var, value="WAV").grid(column=0, row=9, sticky=tk.W)
        ttk.Radiobutton(frame, text="MP4 (最高畫質影片)", variable=self.format_var, value="MP4").grid(column=0, row=10, sticky=tk.W)

        # 資料夾
        self.folder_var = tk.StringVar(value=os.getcwd())
        ttk.Label(frame, text="下載位置:").grid(column=0, row=11, sticky=tk.W, pady=(15, 0))
        ttk.Entry(frame, textvariable=self.folder_var, width=50).grid(column=0, row=12, sticky=tk.W)
        ttk.Button(frame, text="瀏覽...", command=self.choose_folder).grid(column=0, row=13, sticky=tk.W, pady=5)

        # 下載按鈕與進度條
        self.download_btn = ttk.Button(frame, text="開始下載", command=self.start_download, state="disabled")
        self.download_btn.grid(column=0, row=14, pady=15)

        self.progress_var = tk.DoubleVar(value=0)
        self.progressbar = ttk.Progressbar(frame, length=400, variable=self.progress_var)
        self.progressbar.grid(column=0, row=15, pady=5)

        self.status_label = ttk.Label(frame, text="初始化中...")
        self.status_label.grid(column=0, row=16)

    def start_check(self):
        def _task():
            self.manager.check_all()
            self.update_status("就緒")
            self.download_btn.config(state="normal")
        threading.Thread(target=_task, daemon=True).start()

    def choose_folder(self):
        d = filedialog.askdirectory()
        if d: self.folder_var.set(d)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url: return
        self.download_btn.config(state="disabled")
        self.downloader.start(url, self.folder_var.get(), self.filename_entry.get().strip(), self.format_var.get(), self.browser_var.get())

    def update_progress(self, val): self.progress_var.set(val)
    def update_status(self, text): self.status_label.config(text=text)
    def on_download_finished(self, success, msg):
        self.download_btn.config(state="normal")
        if success: messagebox.showinfo("成功", "下載完成！")
        else: messagebox.showerror("錯誤", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()