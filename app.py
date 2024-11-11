import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import os

def download_video():
    video_url = url_entry.get()
    if not video_url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL")
        return
    
    # 다운로드할 폴더 선택
    download_folder = filedialog.askdirectory()
    if not download_folder:
        return  # 폴더 선택 취소 시 함수 종료

    # 다운로드 옵션 설정
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
    }

    try:
        # yt-dlp로 영상 다운로드
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        messagebox.showinfo("Download Complete", "The video has been downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Download Error", f"An error occurred: {e}")

def reset_entry():
    url_entry.delete(0, tk.END)  # 입력 필드의 내용을 모두 삭제

def paste_from_clipboard():
    try:
        # 클립보드에서 텍스트 가져오기
        clipboard_text = app.clipboard_get()
        url_entry.delete(0, tk.END)  # 기존 내용을 삭제하여 중복 방지
        url_entry.insert(tk.INSERT, clipboard_text)
    except tk.TclError:
        pass  # 클립보드가 비어있을 경우 예외 처리

# GUI 생성
app = tk.Tk()
app.title("YouTube Video Downloader")
app.geometry("680x130")

# URL 입력 레이블과 입력 필드
url_label = tk.Label(app, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=10, pady=20, sticky="e")

url_entry = tk.Entry(app, width=40)
url_entry.grid(row=0, column=1, padx=10, pady=20)

# 붙여넣기 버튼
paste_button = tk.Button(app, text="Paste", command=paste_from_clipboard)
paste_button.grid(row=0, column=2, padx=5, pady=20)

# 리셋 버튼 (붙여넣기 버튼 옆에 배치)
reset_button = tk.Button(app, text="Reset", command=reset_entry)
reset_button.grid(row=0, column=3, padx=5, pady=20)

# 다운로드 버튼
download_button = tk.Button(app, text="Download", command=download_video)
download_button.grid(row=1, column=1, columnspan=2, pady=5)

# GUI 실행
app.mainloop()