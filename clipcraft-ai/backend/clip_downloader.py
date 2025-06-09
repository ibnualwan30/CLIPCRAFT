# File: backend/clip_downloader.py
# STEP 1: Buat file ini sebagai file baru di folder backend

import os
import tempfile
from typing import Dict
import uuid

class ClipDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="clipcraft_downloads_")
        print(f"📁 Download temp directory: {self.temp_dir}")
    
    def generate_clip_url(self, video_id: str, start_time: float, end_time: float) -> str:
        """Generate YouTube URL with timestamp"""
        base_url = f"https://www.youtube.com/watch?v={video_id}"
        start_seconds = int(start_time)
        
        # YouTube URL with start time
        url_with_time = f"{base_url}&t={start_seconds}s"
        
        return url_with_time
    
    def create_clip_info(self, video_id: str, clip_data: Dict) -> Dict:
        """Create clip information for download"""
        clip_info = {
            "success": True,
            "clip_id": clip_data.get("clip_id"),
            "title": clip_data.get("title", "Untitled Clip"),
            "start_time": clip_data.get("start_time", 0),
            "end_time": clip_data.get("end_time", 30),
            "duration": clip_data.get("duration", 30),
            "youtube_url": self.generate_clip_url(
                video_id, 
                clip_data.get("start_time", 0), 
                clip_data.get("end_time", 30)
            ),
            "download_method": "youtube_link",
            "format": "mp4"
        }
        
        return clip_info
    
    def create_batch_download_info(self, video_id: str, clips: list) -> Dict:
        """Create batch download information"""
        batch_info = {
            "success": True,
            "total_clips": len(clips),
            "clips": [],
            "batch_id": str(uuid.uuid4()),
            "download_method": "youtube_links"
        }
        
        for clip in clips:
            clip_info = self.create_clip_info(video_id, clip)
            batch_info["clips"].append(clip_info)
        
        return batch_info
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up download directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")

# Test function
def test_clip_downloader():
    """Test clip downloader"""
    downloader = ClipDownloader()
    
    print("🧪 Testing Clip Downloader...")
    print(f"   Temp directory: {downloader.temp_dir}")
    
    # Test clip info generation
    test_clip = {
        "clip_id": "test_001",
        "title": "Test Clip",
        "start_time": 30,
        "end_time": 60,
        "duration": 30
    }
    
    clip_info = downloader.create_clip_info("dQw4w9WgXcQ", test_clip)
    print(f"   Generated clip info: {clip_info}")
    
    downloader.cleanup()
    print("✅ Clip downloader test completed!")

if __name__ == "__main__":
    test_clip_downloader()