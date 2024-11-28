import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import os
from pathlib import Path

class YouTubeDownloader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YouTube Downloader")
        self.window.geometry("600x250")
        
        # 기본 다운로드 경로 설정
        self.download_path = str(Path.home() / "Downloads")
        
        self.create_widgets()
        
    def create_widgets(self):
        # URL 입력 프레임
        url_frame = tk.Frame(self.window)
        url_frame.pack(pady=20, padx=20, fill='x')
        
        tk.Label(url_frame, text="URL:").pack(side='left')
        self.url_entry = tk.Entry(url_frame)
        self.url_entry.pack(side='left', expand=True, fill='x', padx=10)
        
        # 붙여넣기 버튼
        tk.Button(url_frame, text="붙여넣기", command=self.paste_url).pack(side='left', padx=5)
        
        # 경로 선택 프레임
        path_frame = tk.Frame(self.window)
        path_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(path_frame, text="저장 경로:").pack(side='left')
        self.path_label = tk.Label(path_frame, text=self.download_path, wraplength=400)
        self.path_label.pack(side='left', padx=10)
        
        tk.Button(path_frame, text="경로 변경", command=self.change_path).pack(side='left')
        
        # 품질 선택 프레임
        quality_frame = tk.Frame(self.window)
        quality_frame.pack(pady=10, padx=20)
        
        tk.Label(quality_frame, text="품질:").pack(side='left')
        self.quality_var = tk.StringVar(value="highest")
        qualities = ["highest", "1080p", "720p", "480p", "360p"]
        
        for quality in qualities:
            tk.Radiobutton(quality_frame, text=quality, value=quality, 
                          variable=self.quality_var).pack(side='left', padx=10)
        
        # 다운로드 버튼
        tk.Button(self.window, text="다운로드", command=self.download_video,
                 width=20, height=2).pack(pady=20)
        
        # 상태 표시 레이블
        self.status_label = tk.Label(self.window, text="")
        self.status_label.pack(pady=10)
        
    def paste_url(self):
        try:
            clipboard_text = self.window.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except:
            pass
            
    def change_path(self):
        new_path = filedialog.askdirectory(initialdir=self.download_path)
        if new_path:
            self.download_path = new_path
            self.path_label.config(text=self.download_path)
            
    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("경고", "URL을 입력해주세요.")
            return
            
        quality = self.quality_var.get()
        format_opt = {
            'highest': 'best[ext=mp4]/best',
            '1080p': 'best[height<=1080][ext=mp4]/best[height<=1080]',
            '720p': 'best[height<=720][ext=mp4]/best[height<=720]',
            '480p': 'best[height<=480][ext=mp4]/best[height<=480]',
            '360p': 'best[height<=360][ext=mp4]/best[height<=360]'
        }
        
        ydl_opts = {
            'format': format_opt[quality],
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
            'cookiesfrombrowser': ('chrome',),
            'merge_output_format': 'mp4'
        }
        
        self.status_label.config(text="다운로드 중...")
        self.window.update()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            self.status_label.config(text=f"다운로드 완료!\n저장 위치: {filename}")
            messagebox.showinfo("완료", f"다운로드가 완료되었습니다!\n저장 위치: {filename}")
            
        except Exception as e:
            self.status_label.config(text="다운로드 실패")
            messagebox.showerror("오류", f"다운로드 중 오류가 발생했습니다:\n{str(e)}")
            
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress = d.get('_percent_str', '0%')
            self.status_label.config(text=f"다운로드 중... {progress}")
            self.window.update()
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()