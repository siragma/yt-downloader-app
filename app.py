from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import uuid

app = Flask(__name__)

# 다운로드 폴더 설정
DOWNLOAD_FOLDER = "/app/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 다운로드 상태를 저장할 딕셔너리
download_status = {}

def progress_hook(d):
    download_id = d['download_id']
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        if total > 0:
            percentage = (downloaded / total) * 100
            download_status[download_id] = {
                'status': 'downloading',
                'percentage': round(percentage, 1),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
    elif d['status'] == 'finished':
        download_status[download_id] = {
            'status': 'finished',
            'percentage': 100
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download-video', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'highest')
        
        if not url:
            return jsonify({'error': 'URL을 입력해주세요.'}), 400
        
        temp_id = str(uuid.uuid4())
        download_status[temp_id] = {'status': 'starting'}
        
        format_opt = {
            'highest': 'bestvideo[ext=mp4]+bestaudio/best',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio/best[height<=360]'
        }
        
        ydl_opts = {
            'format': format_opt[quality],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{temp_id}/%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4',
            'progress_hooks': [lambda d: progress_hook({**d, 'download_id': temp_id})]
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        return jsonify({
            'success': True,
            'message': '다운로드가 완료되었습니다!',
            'filename': os.path.basename(filename),
            'download_id': temp_id
        })
    except Exception as e:
        print(f"Error in download_video: {str(e)}")
        download_status[temp_id] = {'status': 'error', 'error': str(e)}
        return jsonify({'error': f"다운로드 중 오류 발생: {str(e)}"}), 500

@app.route('/download-status/<download_id>')
def get_download_status(download_id):
    return jsonify(download_status.get(download_id, {'status': 'not_found'}))

@app.route('/download-audio', methods=['POST'])
def download_audio():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL을 입력해주세요.'}), 400
        
        temp_id = str(uuid.uuid4())
        
        # 먼저 정보 추출
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            # 아티스트와 제목 정보 추출
            artist = info.get('artist', '')
            title = info.get('title', '')
            
            if not artist:
                # 아티스트 정보가 없을 경우 채널명을 사용
                artist = info.get('channel', 'Unknown Artist')
            
            # 파일명에 사용할 수 없는 문자 제거
            artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_'))
            title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{temp_id}/{artist} - {title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            filename = f"{artist} - {title}.mp3"
            
        return jsonify({
            'success': True,
            'message': '다운로드가 완료되었습니다!',
            'filename': filename,
            'download_id': temp_id
        })
    except Exception as e:
        print(f"Error in download_audio: {str(e)}")
        return jsonify({'error': f"다운로드 중 오류 발생: {str(e)}"}), 500

@app.route('/download/<download_id>/<filename>')
def serve_file(download_id, filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, download_id, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)