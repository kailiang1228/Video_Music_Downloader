# 🎵 影音下載器 Pro (Video & Audio Downloader)

<div align="center">

**一個強大、簡潔且具備自動更新功能的跨平台影音下載工具**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

</div>

---

## 📖 簡介

基於 `yt-dlp` 與 `FFmpeg` 強大核心開發的現代化影音下載工具。不僅支援 YouTube，還能處理 Facebook、Instagram、Twitch、SoundCloud 等主流平台，甚至能突破部分自架站或加密串流的限制。

### 為什麼選擇這個工具？

- ✅ **完全免費**：開源且無任何廣告
- ✅ **自動更新**：核心引擎自動保持最新，永不過時
- ✅ **無需安裝**：單一執行檔，開箱即用
- ✅ **高品質輸出**：支援最高畫質影片與無損音訊
- ✅ **智能加速**：整合 Aria2 多線程下載，速度提升高達 16 倍

---

## ✨ 核心特色

### 🎬 多格式支援
- **MP3 (192K)**：適合音樂聆聽，壓縮音訊格式
- **WAV**：無損音訊格式，適合專業編輯
- **MP4**：最高畫質影片，自動合併音視頻流

### 🔄 智能核心管理
- 首次啟動自動下載 `yt-dlp` 核心
- 每次啟動檢查並更新至最新版本
- **永不擔心因平台更新而失效**

### ⚡ 進階下載功能
- **Aria2 加速**：自動配置多線程並行下載 (16 連線)
- **內建 FFmpeg**：無需額外安裝，自動處理音視頻轉檔
- **防盜連突破**：
  - 自動讀取瀏覽器 Cookie (Chrome/Edge/Firefox)
  - 智能偽裝 User-Agent 與 Referer
  - 忽略 SSL 憑證錯誤
- **智能檔名處理**：自動處理特殊字元，避免存檔錯誤

### 🎨 友善的圖形介面
- 簡潔直觀的 Tkinter GUI
- 即時進度條顯示
- 自訂下載路徑與檔案名稱
- 狀態提示與錯誤處理

---

## 🚀 快速開始

### 方法一：直接使用 (推薦)

1. **下載執行檔**
   - 取得 `Mp3_D.exe` 檔案
   - 雙擊執行（首次啟動需等待 3-5 秒下載核心）

2. **貼上連結**
   - 複製影片或音樂的網址
   - 貼入程式的輸入框

3. **選擇設定**
   - 【可選】自訂檔案名稱（留空則使用原標題）
   - 選擇格式：MP3 / WAV / MP4
   - 選擇下載資料夾

4. **開始下載**
   - 點擊「開始下載」按鈕
   - 等待進度條完成即可！


## 🛠️ 進階使用技巧

### 下載「難以解析」的影片

如果直接貼上網址無法下載（例如某些教學網站、彈出式視窗或自架影音站），請使用以下方法：

#### 📌 方法：F12 開發者工具抓取串流網址

1. **開啟開發者工具**
   - 在瀏覽器開啟該影片頁面
   - 按下鍵盤 `F12` (或右鍵 → 檢查)

2. **切換到 Network 分頁**
   - 點擊 **「Network (網路)」** 標籤
   - 在過濾框輸入：`m3u8` 或 `mp4`

3. **重新載入並播放**
   - 按 `Ctrl+R` 重新整理頁面
   - 播放影片幾秒鐘

4. **複製串流網址**
   - 在列表中找到 `.m3u8` 或 `.mp4` 結尾的項目
   - 右鍵 → **Copy** → **Copy URL**

5. **貼入下載器**
   - 將複製的網址貼入本工具
   - 即可開始下載

> **💡 小提示**：
> - 有些網站使用 `.m3u8` (HLS 串流格式)，本工具完全支援
> - 如果有多個 m3u8 檔案，通常檔案大小最大的是主檔
> - 若仍無法下載，可能是使用了 DRM 加密（如 Netflix、Disney+），這類內容受法律保護無法下載

### 批次下載播放清單

直接貼上播放清單網址即可自動下載所有影片：

```
# YouTube 播放清單範例
https://www.youtube.com/playlist?list=PLxxxxxx

# 程式會自動識別並逐一下載
```


## 📦 技術架構

### 核心技術棧

```
┌─────────────────────────────────────┐
│         Python GUI (Tkinter)        │  ← 使用者介面層
├─────────────────────────────────────┤
│    下載管理 (Threading + Subprocess) │  ← 邏輯控制層
├─────────────────────────────────────┤
│  yt-dlp (核心引擎) + Aria2 (加速器)   │  ← 下載引擎層
├─────────────────────────────────────┤
│  FFmpeg (音視頻處理) + FFprobe       │  ← 媒體處理層
└─────────────────────────────────────┘
```

### 依賴組件

| 組件 | 版本 | 用途 | 取得方式 |
|------|------|------|---------|
| Python | 3.11+ | 主程式語言 | [python.org](https://www.python.org/) |
| yt-dlp | Latest | 影音下載核心 | 自動下載 |
| FFmpeg | 8.0.1 | 音視頻轉檔 | 內建於 EXE |
| Aria2 | 1.37.0 | 多線程加速 | 自動下載 |
| Tkinter | Built-in | GUI 框架 | Python 內建 |

### Python 套件依賴

```python
requests        # HTTP 請求處理
pyinstaller     # EXE 打包工具
```

---

## 💻 開發者指南

### 環境需求

- Python 3.11 或更高版本
- Windows 10/11 (64-bit)
- 至少 100MB 可用空間

### 從原始碼執行

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd P_MP3_Downloader
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **準備 FFmpeg**
   - 下載 [FFmpeg Windows Essentials](https://www.gyan.dev/ffmpeg/builds/)
   - 解壓縮後，將 `bin` 資料夾內的檔案放到專案根目錄：
     - `ffmpeg.exe`
     - `ffprobe.exe`

4. **執行程式**
   ```bash
   python Mp3_D.py
   ```

### 打包成 EXE

使用 PyInstaller 配置檔：

```bash
pyinstaller Mp3_D.spec
```

打包完成後，執行檔位於 `dist/Mp3_D.exe`

### 專案結構

```
P_MP3_Downloader/
├── Mp3_D.py                 # 主程式
├── Mp3_D.spec              # PyInstaller 配置
├── requirements.txt         # Python 依賴
├── Readme.md               # 說明文檔
├── ffmpeg.exe              # 媒體處理工具 (需自行下載)
├── ffprobe.exe             # 媒體資訊工具 (需自行下載)
├── aria2-1.37.0.../        # Aria2 備用檔案
└── build/                  # 編譯暫存目錄
```


---

## 🔧 常見問題 (FAQ)

### Q1: 程式啟動後卡住不動？
**A:** 首次啟動需要下載 yt-dlp 核心 (~10MB)，請等待約 5-10 秒。如果網路較慢，可能需要更久。

### Q2: 下載失敗顯示「無法解析網址」？
**A:** 可能原因：
- 該網站不在支援清單內
- 影片為私人或需要登入
- 嘗試使用 F12 方法抓取直接串流網址（見上方教學）

### Q3: YouTube 下載失敗？
**A:** 解決方法：
1. 確保程式有自動更新 yt-dlp（啟動時會顯示訊息）
2. 檢查是否為地區限制影片
3. 嘗試開啟 VPN 後再下載
4. 確保已安裝 Chrome 瀏覽器（程式會讀取 Cookie）

### Q4: 下載速度很慢？
**A:** 優化建議：
- 確認 Aria2 是否已啟用（啟動時會顯示「Aria2 配置成功」）
- 檢查網路連線狀況
- 某些網站限制下載速度，屬正常現象

### Q5: 影片有畫面但沒聲音？
**A:** 這是因為 FFmpeg 合併失敗，通常發生在：
- 來源影片本身就無音訊
- FFmpeg 檔案損壞或缺失
- 重新下載程式或檢查 ffmpeg.exe 是否存在

### Q6: 可以下載 Netflix / Disney+ 嗎？
**A:** **不行**。這些平台使用 Widevine DRM 加密，下載行為違反使用條款且觸犯法律。

### Q7: 下載的檔案在哪裡？
**A:** 預設儲存在程式執行目錄，或是您在介面中自訂的資料夾。

---

## ⚖️ 法律聲明與免責條款

### 使用限制

本工具僅供**個人學習**與**技術研究**使用。使用者應遵守：

1. **著作權法**：不得下載受版權保護的商業內容
2. **平台服務條款**：遵守各影音平台的使用規範
3. **合理使用原則**：不得用於商業目的或大規模散布

### 免責聲明

- 本工具開發者不對使用者的下載行為負責
- 使用者應自行承擔使用本工具所產生的法律責任
- 本工具不提供破解 DRM 或規避技術保護措施的功能
- 請支持正版內容創作者

---

## 📄 授權條款

本專案採用 **MIT License** 授權。

```
MIT License

Copyright (c) 2026 P_MP3_Downloader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

完整授權內容請參閱 [LICENSE](LICENSE) 檔案。

---