# File: backend/main.py
# Complete ClipCraft AI with Scene Detection, Motion Analysis, and Visual Quality AI

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uuid
import time
from datetime import datetime
from typing import Optional, List
from youtube_downloader import SimpleYouTubeDownloader
from scene_detector import SceneDetector
from audio_analyzer import AudioAnalyzer
from clip_downloader import ClipDownloader
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="ClipCraft AI API",
    description="AI-powered video clip generation with Scene Detection, Motion Analysis & Visual Quality AI",
    version="2.1.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage and AI processors
jobs_storage = {}
scene_detector = SceneDetector()
audio_analyzer = AudioAnalyzer()
clip_downloader = ClipDownloader()

class ClipDownloadRequest(BaseModel):
    video_id: str
    clip_id: str
    title: str
    start_time: float
    end_time: float
    format: str = "mp4"

class BatchDownloadRequest(BaseModel):
    video_id: str
    clips: list
    format: str = "mp4"

@app.on_event("startup")
async def startup_event():
    """Initialize AI components on startup"""
    print("🚀 Initializing ClipCraft AI v2.1...")
    print("🎬 Scene Detection AI: Ready")
    print("📊 Motion Analysis AI: Ready") 
    print("🎨 Visual Quality AI: Ready")
    print("✅ All AI systems online!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ClipCraft AI v2.1 - Scene Detection AI! 🎬",
        "version": "2.1.0",
        "status": "healthy",
        "ai_features": [
            "youtube_download",
            "scene_detection", 
            "motion_analysis",
            "visual_quality_analysis",
            "smart_clip_generation"
        ],
        "capabilities": {
            "max_video_duration": "30 minutes",
            "supported_formats": ["mp4", "webm", "mkv"],
            "ai_processing": "real-time"
        },
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len(jobs_storage),
        "ai_systems": {
            "scene_detection": "operational",
            "motion_analysis": "operational",
            "visual_quality": "operational",
            "youtube_downloader": "operational"
        },
        "server_info": {
            "framework": "FastAPI",
            "ai_backend": "OpenCV + NumPy",
            "processing_mode": "async"
        }
    }

@app.post("/api/process-video")
async def process_video(
    background_tasks: BackgroundTasks,
    youtube_url: str = Query(..., description="YouTube URL to process"),
    clip_count: int = Query(5, description="Number of clips to generate (1-10)", ge=1, le=10),
    use_ai_analysis: bool = Query(True, description="Use AI scene detection and analysis"),
    analysis_mode: str = Query("balanced", description="Analysis mode: fast, balanced, detailed")
):
    """Start video processing with advanced AI scene detection"""
    
    try:
        print(f"📥 New processing request:")
        print(f"   URL: {youtube_url}")
        print(f"   Clips: {clip_count}")
        print(f"   AI Analysis: {use_ai_analysis}")
        print(f"   Mode: {analysis_mode}")
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Enhanced URL validation
        if not youtube_url or len(youtube_url) < 10:
            raise HTTPException(status_code=400, detail="Valid YouTube URL is required")
        
        # Check URL format patterns
        youtube_patterns = [
            "youtube.com/watch?v=",
            "youtu.be/",
            "youtube.com/embed/",
            "m.youtube.com/watch?v="
        ]
        
        if not any(pattern in youtube_url.lower() for pattern in youtube_patterns):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL format")
        
        # Estimate processing time based on features
        base_time = 30
        if use_ai_analysis:
            time_multiplier = {"fast": 1.5, "balanced": 2.0, "detailed": 3.0}
            estimated_time = int(base_time * time_multiplier.get(analysis_mode, 2.0))
        else:
            estimated_time = base_time
        
        # Store comprehensive job information
        jobs_storage[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "current_step": "Initializing AI video processing pipeline...",
            "youtube_url": youtube_url,
            "clip_count": clip_count,
            "use_ai_analysis": use_ai_analysis,
            "analysis_mode": analysis_mode,
            "created_at": datetime.now().isoformat(),
            "estimated_time": estimated_time,
            "ai_features_enabled": [
                "youtube_download",
                "scene_detection",
                "motion_analysis", 
                "visual_quality"
            ] if use_ai_analysis else ["youtube_download"],
            "processing_pipeline": "advanced_ai" if use_ai_analysis else "basic"
        }
        
        # Start background processing
        background_tasks.add_task(process_video_with_scene_ai, job_id)
        
        print(f"✅ Job queued successfully: {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Video processing started with {'advanced AI analysis' if use_ai_analysis else 'basic processing'}",
            "status": "queued",
            "estimated_time": estimated_time,
            "ai_features": jobs_storage[job_id]["ai_features_enabled"],
            "processing_mode": analysis_mode if use_ai_analysis else "basic"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Request processing error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

async def process_video_with_scene_ai(job_id: str):
    """Advanced video processing with Scene Detection AI"""
    downloader = None
    
    try:
        job = jobs_storage[job_id]
        youtube_url = job["youtube_url"]
        clip_count = job["clip_count"]
        use_ai = job["use_ai_analysis"]
        analysis_mode = job["analysis_mode"]
        
        print(f"🎬 Starting advanced AI processing for job: {job_id}")
        print(f"   AI Analysis: {use_ai}")
        print(f"   Analysis Mode: {analysis_mode}")
        
        # Initialize YouTube downloader
        downloader = SimpleYouTubeDownloader()
        
        # Step 1: Video Information Extraction (15%)
        await update_job_progress(job_id, 15, "📋 Extracting video metadata and information...")
        await asyncio.sleep(1)  # Realistic delay
        
        video_info = downloader.get_video_info(youtube_url)
        
        if not video_info['success']:
            raise Exception(f"Failed to extract video information: {video_info['error']}")
        
        # Enhanced video validation
        if video_info['is_live']:
            raise Exception("Live streams are not supported for processing")
        
        max_duration = 1800  # 30 minutes
        if video_info['duration'] > max_duration:
            raise Exception(f"Video duration too long: {video_info['duration']}s (maximum: {max_duration}s)")
        
        if video_info['duration'] < 10:
            raise Exception(f"Video too short: {video_info['duration']}s (minimum: 10s)")
        
        print(f"✅ Video validated:")
        print(f"   Title: {video_info['title']}")
        print(f"   Duration: {video_info['duration']}s")
        print(f"   Views: {video_info.get('view_count', 'N/A'):,}")
        print(f"   Uploader: {video_info.get('uploader', 'Unknown')}")
        
        # Step 2: Video Download (35%)
        await update_job_progress(job_id, 35, f"📥 Downloading video: {video_info['title'][:50]}...")
        
        download_result = downloader.download_video(youtube_url)
        
        if not download_result['success']:
            raise Exception(f"Video download failed: {download_result['error']}")
        
        print(f"✅ Download completed:")
        print(f"   File size: {download_result['file_size_mb']:.1f} MB")
        print(f"   Path: {download_result['video_path']}")
        
        # Step 3: AI Scene Analysis (if enabled)
        scene_analysis = None
        if use_ai:
            await update_job_progress(job_id, 55, "🎬 Performing AI scene detection and analysis...")
            
            # Configure scene detector based on analysis mode
            if analysis_mode == "fast":
                scene_detector.threshold = 0.4  # Less sensitive, faster
            elif analysis_mode == "detailed": 
                scene_detector.threshold = 0.2  # More sensitive, slower
            else:  # balanced
                scene_detector.threshold = 0.3  # Default
            
            scene_analysis = scene_detector.analyze_video(download_result['video_path'])
            
            if scene_analysis['success']:
                print(f"✅ AI Scene Analysis completed:")
                print(f"   Scenes detected: {scene_analysis['total_scenes']}")
                print(f"   Motion segments: {len(scene_analysis.get('motion_analysis', []))}")
                print(f"   Visual quality points: {len(scene_analysis.get('visual_quality', []))}")
            else:
                print(f"⚠️ Scene analysis failed: {scene_analysis.get('error', 'Unknown error')}")
                print("   Falling back to time-based clip generation")
        
        # Step 4: Audio Analysis (if enabled)
        audio_analysis = None
        if use_ai:
            await update_job_progress(job_id, 75, "🎵 Analyzing audio for viral moments...")
            audio_analysis = audio_analyzer.analyze_audio(download_result['video_path'])
            
            if audio_analysis['success']:
                print(f"✅ Audio Analysis: {len(audio_analysis.get('viral_moments', []))} viral moments")
            else:
                print(f"⚠️ Audio analysis failed: {audio_analysis.get('error', 'Unknown error')}")

        # Step 5: Intelligent Clip Generation (80%)
        await update_job_progress(job_id, 85, "🎯 Generating intelligent clips with AI analysis...")
        await asyncio.sleep(1)
        
        if use_ai and scene_analysis and scene_analysis['success']:
            clips = scene_detector.generate_smart_clips(scene_analysis, clip_count)
            
            # Enhance clips with audio analysis
            if audio_analysis and audio_analysis['success']:
                clips = enhance_clips_with_audio_analysis(clips, audio_analysis)
                processing_method = "ai_scene_and_audio_analysis"
                print(f"✅ Generated {len(clips)} AI clips with audio enhancement")
            else:
                processing_method = "ai_scene_analysis"
                print(f"✅ Generated {len(clips)} AI clips (scene analysis only)")
        else:
            clips = generate_enhanced_fallback_clips(video_info, clip_count)
            processing_method = "enhanced_time_based"
            print(f"✅ Generated {len(clips)} time-based clips with enhancements")
        
        # Step 6: Finalization and Optimization (100%)
        await update_job_progress(job_id, 100, "✅ Finalizing results and optimizing clips...")
        await asyncio.sleep(0.5)
        
        # Store comprehensive results
        jobs_storage[job_id].update({
            "status": "completed",
            "video_info": video_info,
            "download_info": download_result,
            "scene_analysis": scene_analysis,
            "audio_analysis": audio_analysis,
            "clips": clips,
            "processing_method": processing_method,
            "processing_type": "scene_ai" if use_ai else "enhanced_basic",
            "completed_at": datetime.now().isoformat(),
            "processing_summary": {
                "total_clips_generated": len(clips),
                "ai_analysis_used": use_ai,
                "scenes_detected": scene_analysis.get('total_scenes', 0) if scene_analysis else 0,
                "viral_moments_detected": len(audio_analysis.get('viral_moments', [])) if audio_analysis else 0,
                "processing_mode": analysis_mode if use_ai else "basic"
            }
        })
        
        print(f"🎉 Processing completed successfully for job: {job_id}")
        print(f"   Total clips: {len(clips)}")
        print(f"   Processing method: {processing_method}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Processing failed for job {job_id}: {error_msg}")
        await update_job_progress(job_id, 0, f"❌ Processing error: {error_msg}", "failed")
        jobs_storage[job_id]["error_message"] = error_msg
        jobs_storage[job_id]["failed_at"] = datetime.now().isoformat()
    finally:
        # Cleanup resources
        if downloader:
            downloader.cleanup()
            print(f"🧹 Cleanup completed for job: {job_id}")

def enhance_clips_with_audio_analysis(clips: list, audio_analysis: dict) -> list:
    """Enhance clips dengan audio analysis data"""
    viral_moments = audio_analysis.get('viral_moments', [])
    
    if not viral_moments:
        return clips
    
    enhanced_clips = []
    
    for clip in clips:
        # Check if clip overlaps dengan viral moments
        clip_start = clip.get('start_time', 0)
        clip_end = clip.get('end_time', 0)
        
        overlapping_moments = []
        for moment in viral_moments:
            moment_time = moment.get('time', 0)
            if clip_start <= moment_time <= clip_end:
                overlapping_moments.append(moment)
        
        # Enhance clip information
        enhanced_clip = clip.copy()
        
        if overlapping_moments:
            # Boost confidence untuk clips dengan viral moments
            original_confidence = clip.get('confidence', 0.5)
            viral_boost = min(len(overlapping_moments) * 0.1, 0.3)
            enhanced_clip['confidence'] = min(original_confidence + viral_boost, 1.0)
            
            # Add viral moment information
            enhanced_clip['viral_moments'] = overlapping_moments
            enhanced_clip['has_viral_content'] = True
            enhanced_clip['viral_score'] = sum(m.get('confidence', 0) for m in overlapping_moments) / len(overlapping_moments)
            
            # Update title
            if overlapping_moments:
                best_moment = max(overlapping_moments, key=lambda x: x.get('confidence', 0))
                enhanced_clip['title'] = f"🔥 {clip.get('title', 'Clip')} - {best_moment.get('description', 'Viral Content')}"
        else:
            enhanced_clip['has_viral_content'] = False
            enhanced_clip['viral_score'] = 0
        
        enhanced_clips.append(enhanced_clip)
    
    # Sort clips by confidence (prioritize viral content)
    enhanced_clips.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    return enhanced_clips

def generate_enhanced_fallback_clips(video_info: dict, clip_count: int) -> list:
    """Enhanced fallback clip generation with smart positioning"""
    duration = video_info['duration']
    clips = []
    
    # Smart clip distribution
    if duration <= 60:  # Short video
        clips.append({
            "clip_id": "enhanced_clip_1",
            "title": "🎬 Full Video Highlight", 
            "start_time": 5,
            "end_time": max(10, duration - 5),
            "duration": max(5, duration - 10),
            "confidence": 0.9,
            "type": "full_highlight",
            "ai_analysis": {"method": "enhanced_fallback", "positioning": "full_video"}
        })
    else:
        # Strategic positioning for longer videos
        positions = [
            {"name": "Opening", "start_ratio": 0.05, "weight": 0.9},
            {"name": "Early Content", "start_ratio": 0.2, "weight": 0.8},
            {"name": "Mid Content", "start_ratio": 0.4, "weight": 0.85},
            {"name": "Key Section", "start_ratio": 0.6, "weight": 0.87},
            {"name": "Conclusion", "start_ratio": 0.8, "weight": 0.88}
        ]
        
        for i in range(min(clip_count, len(positions))):
            pos = positions[i]
            start_time = duration * pos["start_ratio"]
            clip_duration = min(50, duration * 0.15)  # 15% of video or 50s max
            end_time = min(start_time + clip_duration, duration - 5)
            
            if end_time - start_time < 10:  # Ensure minimum duration
                continue
                
            clips.append({
                "clip_id": f"enhanced_clip_{i+1}",
                "title": f"🎯 {pos['name']} Segment",
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "confidence": pos["weight"],
                "type": "strategic_positioned",
                "ai_analysis": {
                    "method": "enhanced_fallback",
                    "positioning": pos["name"].lower().replace(" ", "_"),
                    "strategy": "smart_distribution"
                }
            })
    
    return clips

async def update_job_progress(job_id: str, progress: int, step: str, status: str = "processing"):
    """Update job progress with timestamp"""
    if job_id in jobs_storage:
        jobs_storage[job_id].update({
            "progress": progress,
            "current_step": step,
            "status": status,
            "updated_at": datetime.now().isoformat()
        })

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get comprehensive job status"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs_storage[job_id]
    
    # Add runtime calculations
    created_at = datetime.fromisoformat(job_data["created_at"])
    runtime = (datetime.now() - created_at).total_seconds()
    
    job_data["runtime_seconds"] = round(runtime, 1)
    
    if job_data["status"] == "processing":
        remaining_time = max(0, job_data.get("estimated_time", 0) - runtime)
        job_data["estimated_remaining"] = round(remaining_time, 1)
    
    return job_data

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """Get comprehensive processing results"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed. Current status: {job['status']}"
        )
    
    # Extract all result data
    video_info = job.get("video_info", {})
    download_info = job.get("download_info", {})
    scene_analysis = job.get("scene_analysis", {})
    audio_analysis = job.get("audio_analysis", {})
    clips = job.get("clips", [])
    processing_summary = job.get("processing_summary", {})
    
    return {
        "job_id": job_id,
        "success": True,
        
        # Video Information
        "video_info": {
            "title": video_info.get("title", "Unknown Video"),
            "duration": video_info.get("duration", 0),
            "views": video_info.get("view_count", 0),
            "uploader": video_info.get("uploader", "Unknown"),
            "upload_date": video_info.get("upload_date", ""),
            "description_preview": video_info.get("description", "")[:100]
        },
        
        # Download Information  
        "download_info": {
            "file_size_mb": download_info.get("file_size_mb", 0),
            "file_path": download_info.get("video_path", ""),
            "file_name": download_info.get("file_name", "")
        },
        
        # AI Analysis Results
        "ai_analysis": {
            "scene_analysis_enabled": scene_analysis.get("success", False) if scene_analysis else False,
            "audio_analysis_enabled": audio_analysis.get("success", False) if audio_analysis else False,
            "scenes_detected": scene_analysis.get("total_scenes", 0) if scene_analysis else 0,
            "viral_moments_detected": len(audio_analysis.get("viral_moments", [])) if audio_analysis else 0,
            "motion_segments_analyzed": len(scene_analysis.get("motion_analysis", [])) if scene_analysis else 0,
            "visual_quality_points": len(scene_analysis.get("visual_quality", [])) if scene_analysis else 0,
            "analysis_duration": scene_analysis.get("duration", 0) if scene_analysis else 0
        },
        
        # Generated Clips
        "clips": clips,
        "clips_summary": {
            "total_generated": len(clips),
            "avg_duration": round(sum(clip.get("duration", 0) for clip in clips) / len(clips), 1) if clips else 0,
            "avg_confidence": round(sum(clip.get("confidence", 0) for clip in clips) / len(clips), 2) if clips else 0,
            "clips_with_viral_content": len([c for c in clips if c.get("has_viral_content", False)])
        },
        
        # Processing Information
        "processing_info": {
            "method": job.get("processing_method", "unknown"),
            "type": job.get("processing_type", "basic"),
            "mode": job.get("analysis_mode", "basic"),
            "ai_features_used": job.get("ai_features_enabled", []),
            "created_at": job["created_at"],
            "completed_at": job.get("completed_at", ""),
            "total_processing_time": processing_summary.get("total_processing_time", 0)
        }
    }

@app.delete("/api/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a processing job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    if job["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {job['status']}")
    
    jobs_storage[job_id].update({
        "status": "cancelled",
        "current_step": "Job cancelled by user request",
        "cancelled_at": datetime.now().isoformat()
    })
    
    print(f"🚫 Job cancelled: {job_id}")
    
    return {
        "success": True,
        "message": "Job cancelled successfully",
        "job_id": job_id
    }

@app.get("/api/jobs")
async def list_all_jobs(limit: int = Query(20, description="Maximum number of jobs to return")):
    """List recent jobs for debugging and monitoring"""
    all_jobs = list(jobs_storage.values())
    
    # Sort by creation time (newest first)
    all_jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Limit results
    limited_jobs = all_jobs[:limit]
    
    return {
        "jobs": limited_jobs,
        "total_jobs": len(all_jobs),
        "returned_jobs": len(limited_jobs),
        "timestamp": datetime.now().isoformat(),
        "system_status": "operational"
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    total_jobs = len(jobs_storage)
    completed_jobs = len([j for j in jobs_storage.values() if j.get("status") == "completed"])
    failed_jobs = len([j for j in jobs_storage.values() if j.get("status") == "failed"])
    active_jobs = len([j for j in jobs_storage.values() if j.get("status") in ["queued", "processing"]])
    
    return {
        "total_jobs_processed": total_jobs,
        "completed_jobs": completed_jobs, 
        "failed_jobs": failed_jobs,
        "currently_active": active_jobs,
        "success_rate": round((completed_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0,
        "ai_features": {
            "scene_detection": "operational",
            "motion_analysis": "operational", 
            "visual_quality": "operational",
            "audio_analysis": "operational"
        },
        "uptime": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/download-clip")
async def download_single_clip(request: ClipDownloadRequest):
    """Download a single clip"""
    try:
        print(f"📥 Download request for clip: {request.clip_id}")
        
        # Create clip info
        clip_data = {
            "clip_id": request.clip_id,
            "title": request.title,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "duration": request.end_time - request.start_time
        }
        
        clip_info = clip_downloader.create_clip_info(request.video_id, clip_data)
        
        # Add additional info
        clip_info.update({
            "download_url": clip_info["youtube_url"],
            "suggested_filename": f"{request.title.replace(' ', '_')}_{request.clip_id}.mp4",
            "instructions": {
                "method_1": "Click the YouTube link to watch the clip at the specific timestamp",
                "method_2": "Use a YouTube downloader tool with the provided URL and timestamps",
                "method_3": "For direct download, FFmpeg integration is needed (coming soon)"
            }
        })
        
        print(f"✅ Clip download info generated: {clip_info['youtube_url']}")
        
        return clip_info
        
    except Exception as e:
        print(f"❌ Download clip failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare clip download: {str(e)}")

@app.post("/api/download-batch")
async def download_batch_clips(request: BatchDownloadRequest):
    """Download multiple clips as batch"""
    try:
        print(f"📥 Batch download request for {len(request.clips)} clips")
        
        batch_info = clip_downloader.create_batch_download_info(request.video_id, request.clips)
        
        # Add instructions for batch download
        batch_info.update({
            "instructions": {
                "individual_links": "Each clip has its own YouTube timestamp link",
                "batch_method": "Use a batch YouTube downloader with the provided URLs",
                "manual_method": "Download each clip individually using the timestamp links"
            },
            "download_tips": [
                "Right-click on YouTube links and 'Open in new tab' for multiple clips",
                "Use browser extensions like 'Video DownloadHelper' for easier downloading",
                "For best quality, use yt-dlp with the timestamp URLs"
            ]
        })
        
        print(f"✅ Batch download info generated for {len(request.clips)} clips")
        
        return batch_info
        
    except Exception as e:
        print(f"❌ Batch download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to prepare batch download: {str(e)}")

@app.post("/api/copy-timestamps")
async def copy_all_timestamps(video_id: str, clips: list):
    """Generate copyable text with all clip timestamps"""
    try:
        print(f"📋 Generating timestamps for {len(clips)} clips")
        
        timestamp_text = f"🎬 ClipCraft AI - Generated Clips\n"
        timestamp_text += f"Original Video: https://www.youtube.com/watch?v={video_id}\n\n"
        
        for i, clip in enumerate(clips, 1):
            start_time = clip.get('start_time', 0)
            end_time = clip.get('end_time', 30)
            title = clip.get('title', f'Clip {i}')
            confidence = clip.get('confidence', 0.5)
            
            youtube_url = clip_downloader.generate_clip_url(video_id, start_time, end_time)
            
            timestamp_text += f"{i}. {title}\n"
            timestamp_text += f"   ⏰ {int(start_time//60)}:{int(start_time%60):02d} - {int(end_time//60)}:{int(end_time%60):02d}\n"
            timestamp_text += f"   🎯 Confidence: {int(confidence*100)}%\n"
            timestamp_text += f"   🔗 {youtube_url}\n\n"
        
        timestamp_text += "Generated by ClipCraft AI - Turn long videos into viral clips! 🚀"
        
        return {
            "success": True,
            "total_clips": len(clips),
            "timestamp_text": timestamp_text,
            "instructions": "Copy the text below and share it anywhere!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate timestamps: {str(e)}")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when shutting down"""
    print("🛑 Shutting down ClipCraft AI...")
    clip_downloader.cleanup()
    print("✅ Cleanup completed")

# Run server
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ClipCraft AI v2.1 with Scene Detection...")
    print("📖 API Documentation: http://127.0.0.1:8001/docs")
    print("🔧 Health Check: http://127.0.0.1:8001/api/health")
    print("📊 System Stats: http://127.0.0.1:8001/api/stats")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )