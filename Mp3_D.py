import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
import requests
import re
import time

class Config:
    # 應用程式設定
    YTDLP_FILENAME = "yt-dlp.exe"
    # 官方最新版下載連結
    GITHUB_RELEASE_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

    @staticmethod
    def get_base_path():
        """取得資源解壓路徑 (用於讀取打包的 ffmpeg)"""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_app_path():
        """取得應用程式執行路徑 (用於存放 yt-dlp.exe)"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_ffmpeg_path():
        return Config.get_base_path()

    @staticmethod
    def get_ytdlp_path():
        return os.path.join(Config.get_app_path(), Config.YTDLP_FILENAME)

class YtDlpManager:
    """負責管理 yt-dlp.exe 的下載與更新"""
    
    def __init__(self, status_callback):
        self.status_callback = status_callback
        self.exe_path = Config.get_ytdlp_path()

    def is_installed(self):
        return os.path.exists(self.exe_path)

    def download_or_update(self):
        """檢查並下載/更新 yt-dlp"""
        if not self.is_installed():
            self.status_callback("正在下載核心元件 (yt-dlp)...")
            self._download_fresh()
        else:
            self.status_callback("正在檢查核心更新...")
            self._run_update_command()

    def _download_fresh(self):
        try:
            response = requests.get(Config.GITHUB_RELEASE_URL, stream=True)
            response.raise_for_status()
            
            with open(self.exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.status_callback("核心元件下載完成")
        except Exception as e:
            raise Exception(f"下載 yt-dlp 失敗: {e}")

    def _run_update_command(self):
        try:
            # 使用 -U 參數自我更新
            # creationflags=0x08000000 (CREATE_NO_WINDOW) 防止跳出黑窗
            subprocess.run(
                [self.exe_path, "-U"], 
                capture_output=True, 
                text=True, 
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            self.status_callback("核心元件檢查完畢")
        except subprocess.CalledProcessError:
            # 即使更新失敗通常也能繼續用舊的
            self.status_callback("核心更新失敗，嘗試使用現有版本...")
        except Exception as e:
            self.status_callback(f"更新檢查錯誤: {e}")

class Downloader:
    """負責執行下載任務"""
    def __init__(self, progress_callback, status_callback, finished_callback):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.finished_callback = finished_callback

    def start(self, url, folder, filename, fmt):
        threading.Thread(target=self._run, args=(url, folder, filename, fmt), daemon=True).start()

    def _run(self, url, folder, filename, fmt):
        ytdlp_path = Config.get_ytdlp_path()
        ffmpeg_path = Config.get_ffmpeg_path()

        if not os.path.exists(ytdlp_path):
            self.finished_callback(False, "找不到 yt-dlp.exe，請重啟程式")
            return
        
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                self.finished_callback(False, "無法建立下載資料夾")
                return

        # 建構指令
        cmd = [
            ytdlp_path,
            url,
            "--ffmpeg-location", ffmpeg_path,
            "--newline", # 關鍵：讓輸出變成一行一行，方便解析
            "--no-warnings",
            "--progress-template", "%(progress._percent_str)s", # 只輸出百分比
            "--no-check-certificate", # 忽略 SSL 憑證錯誤
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", # 偽裝成瀏覽器
            "--referer", "https://istudy.way-to-win.com/", # 嘗試加入 Referer
        ]

        # 輸出檔名模板
        if filename:
            outtmpl = os.path.join(folder, filename + ".%(ext)s")
        else:
            outtmpl = os.path.join(folder, '%(title)s.%(ext)s')
        
        cmd.extend(["-o", outtmpl])

        # 格式選擇
        if fmt == "MP3":
            cmd.extend([
                "-x", # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "192K",
            ])
        elif fmt == "WAV":
            cmd.extend([
                "-x",
                "--audio-format", "wav",
            ])
        else: # MP4
            cmd.extend([
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4"
            ])

        try:
            # 執行 subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    line = line.strip()
                    # 解析進度 (例如 " 45.5%")
                    if "%" in line:
                        try:
                            # 移除 ANSI code 如果有
                            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                            percent_str = clean_line.replace('%', '').strip()
                            percent = float(percent_str)
                            self.progress_callback(percent)
                            self.status_callback(f"下載中... {percent:.1f}%")
                        except:
                            pass
                    else:
                        # 可能是其他訊息
                        if line.startswith('[download]'):
                            self.status_callback("正在下載...")
                        elif line.startswith('[ExtractAudio]'):
                            self.status_callback("正在轉檔為音訊...")
                        elif line.startswith('[Merger]'):
                            self.status_callback("正在合併影音...")

            if process.returncode == 0:
                self.finished_callback(True, "下載完成！")
            else:
                stderr = process.stderr.read()
                self.finished_callback(False, f"下載失敗: {stderr}")

        except Exception as e:
            self.finished_callback(False, str(e))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("影音下載器 (Pro版)")
        self.setup_ui()
        
        self.manager = YtDlpManager(self.update_status)
        self.downloader = Downloader(self.update_progress, self.update_status, self.on_download_finished)

        # 啟動時檢查更新
        self.root.after(100, self.check_components)

    def setup_ui(self):
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

        # 格式
        self.format_var = tk.StringVar(value="MP3")
        ttk.Radiobutton(frame, text="MP3 (音訊)", variable=self.format_var, value="MP3").grid(column=0, row=5, sticky=tk.W)
        ttk.Radiobutton(frame, text="WAV (無損音訊)", variable=self.format_var, value="WAV").grid(column=0, row=6, sticky=tk.W)
        ttk.Radiobutton(frame, text="MP4 (最高畫質影片)", variable=self.format_var, value="MP4").grid(column=0, row=7, sticky=tk.W)

        # 資料夾
        self.folder_var = tk.StringVar(value=os.getcwd())
        ttk.Label(frame, text="下載位置:").grid(column=0, row=8, sticky=tk.W, pady=(15, 0))
        ttk.Entry(frame, textvariable=self.folder_var, width=50).grid(column=0, row=9, sticky=tk.W)
        ttk.Button(frame, text="瀏覽...", command=self.choose_folder).grid(column=0, row=10, sticky=tk.W, pady=5)

        # 按鈕與進度
        self.download_btn = ttk.Button(frame, text="開始下載", command=self.start_download)
        self.download_btn.grid(column=0, row=11, pady=15)

        self.progress_var = tk.DoubleVar(value=0)
        self.progressbar = ttk.Progressbar(frame, length=400, variable=self.progress_var)
        self.progressbar.grid(column=0, row=12, pady=5)

        self.status_label = ttk.Label(frame, text="初始化中...")
        self.status_label.grid(column=0, row=13)

    def check_components(self):
        def _check():
            try:
                self.download_btn.config(state=tk.DISABLED)
                self.manager.download_or_update()
                self.update_status("就緒")
                self.download_btn.config(state=tk.NORMAL)
            except Exception as e:
                self.update_status(f"元件檢查失敗: {e}")
                messagebox.showerror("錯誤", f"無法準備下載核心: {e}")
                # 即使失敗也啟用按鈕，讓使用者可以重試
                self.download_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=_check, daemon=True).start()

    def choose_folder(self):
        d = filedialog.askdirectory()
        if d: self.folder_var.set(d)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("提示", "請輸入網址")
            return
        
        self.download_btn.config(state=tk.DISABLED)
        self.downloader.start(
            url, 
            self.folder_var.get(), 
            self.filename_entry.get().strip(), 
            self.format_var.get()
        )

    def update_progress(self, val):
        self.progress_var.set(val)

    def update_status(self, text):
        self.status_label.config(text=text)

    def on_download_finished(self, success, msg):
        self.download_btn.config(state=tk.NORMAL)
        if success:
            self.update_status("下載完成")
            self.progress_var.set(100)
            messagebox.showinfo("成功", msg)
        else:
            self.update_status("失敗")
            messagebox.showerror("錯誤", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()