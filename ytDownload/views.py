from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import yt_dlp
import json
import os

def index(request):
    return render(request, 'index.html')

class ProgressHook:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel_layer = get_channel_layer()

    def __call__(self, d):
        if d['status'] == 'downloading':
            # 计算下载进度
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            if total > 0:
                progress = (downloaded / total) * 100
                # 发送进度更新
                async_to_sync(self.channel_layer.send)(
                    self.channel_name,
                    {
                        'type': 'download_progress',
                        'progress': progress,
                        'status': f'下载中... {progress:.1f}%'
                    }
                )

def download_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        
        if not video_url:
            return JsonResponse({
                'error': True,
                'message': '请输入视频链接！'
            })
        
        try:
            temp_dir = 'temp_downloads'
            os.makedirs(temp_dir, exist_ok=True)
            
            # 创建进度钩子
            progress_hook = ProgressHook(request.channel_name)
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'cookiefile': 'cookies.txt',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info)
            
            file = open(file_path, 'rb')
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            
            # 清理临时文件
            os.remove(file_path)
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
                
            return response
            
        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'下载失败：{str(e)}'
            })
    
    return render(request, 'index.html')