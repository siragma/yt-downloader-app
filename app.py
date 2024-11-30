from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
from pathlib import Path
import uuid

app = Flask(__name__)

# 다운로드 폴더 설정
DOWNLOAD_FOLDER = "/app/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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
            'merge_output_format': 'mp4'
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
        return jsonify({'error': f"다운로드 중 오류 발생: {str(e)}"}), 500

@app.route('/download-audio', methods=['POST'])
def download_audio():
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL을 입력해주세요.'}), 400
        
        temp_id = str(uuid.uuid4())
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{temp_id}/%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit('.', 1)[0] + '.mp3'
            
        return jsonify({
            'success': True,
            'message': '다운로드가 완료되었습니다!',
            'filename': os.path.basename(filename),
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
    app.run(host='0.0.0.0', port=5000, debug=True)