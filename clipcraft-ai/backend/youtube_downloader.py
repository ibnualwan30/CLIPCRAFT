# File: backend/youtube_downloader.py
# Buat file baru untuk test YouTube download

import yt_dlp
import os
import tempfile
from typing import Dict

class SimpleYouTubeDownloader:
    def __init__(self):
        # Buat folder temporary untuk download
        self.temp_dir = tempfile.mkdtemp(prefix="clipcraft_")
        print(f"📁 Download folder: {self.temp_dir}")
    
    def get_video_info(self, youtube_url: str) -> Dict:
        """Get video information without downloading"""
        try:
            print(f"📋 Getting info for: {youtube_url}")
            
            # Configure yt-dlp untuk info saja
            ydl_opts = {
                'quiet': True,  # Tidak terlalu banyak output
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info tanpa download
                info = ydl.extract_info(youtube_url, download=False)
                
                # Ambil info penting
                video_info = {
                    'success': True,
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:200],  # 200 karakter pertama
                    'thumbnail': info.get('thumbnail', ''),
                    'is_live': info.get('is_live', False)
                }
                
                print(f"✅ Video info retrieved: {video_info['title']}")
                print(f"   Duration: {video_info['duration']} seconds")
                print(f"   Views: {video_info['view_count']:,}")
                
                return video_info
                
        except Exception as e:
            print(f"❌ Error getting video info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_video(self, youtube_url: str) -> Dict:
        """Download video from YouTube"""
        try:
            print(f"📥 Starting download: {youtube_url}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=480]',  # Download kualitas sedang (480p)
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': True,  # Jangan download playlist
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download video
                ydl.download([youtube_url])
                
                # Cari file yang sudah didownload
                downloaded_files = []
                for file in os.listdir(self.temp_dir):
                    if file.endswith(('.mp4', '.webm', '.mkv')):
                        downloaded_files.append(file)
                
                if not downloaded_files:
                    raise Exception("No video file found after download")
                
                video_file = downloaded_files[0]
                video_path = os.path.join(self.temp_dir, video_file)
                
                # Get file size
                file_size = os.path.getsize(video_path)
                file_size_mb = file_size / (1024 * 1024)
                
                print(f"✅ Download complete!")
                print(f"   File: {video_file}")
                print(f"   Size: {file_size_mb:.1f} MB")
                print(f"   Path: {video_path}")
                
                return {
                    'success': True,
                    'video_path': video_path,
                    'file_name': video_file,
                    'file_size_mb': file_size_mb,
                    'temp_dir': self.temp_dir
                }
                
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Hapus file temporary"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleanup complete: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")

# Test function
def test_downloader():
    """Test YouTube downloader dengan video pendek"""
    downloader = SimpleYouTubeDownloader()
    
    try:
        # Test dengan video pendek
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print("🧪 Testing YouTube downloader...")
        print("=" * 50)
        
        # Step 1: Get video info
        print("\n1️⃣ Getting video information...")
        info = downloader.get_video_info(test_url)
        
        if not info['success']:
            print(f"❌ Failed to get info: {info['error']}")
            return
        
        print(f"✅ Video found: {info['title']}")
        
        # Check duration
        if info['duration'] > 300:  # 5 menit
            print(f"⚠️ Video is long ({info['duration']}s), skipping download for test")
            return
        
        # Step 2: Download video
        print("\n2️⃣ Downloading video...")
        result = downloader.download_video(test_url)
        
        if result['success']:
            print("✅ Test passed! YouTube downloader working.")
        else:
            print(f"❌ Test failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    finally:
        print("\n3️⃣ Cleaning up...")
        downloader.cleanup()

if __name__ == "__main__":
    test_downloader()