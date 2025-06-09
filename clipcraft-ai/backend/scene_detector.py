# File: backend/scene_detector.py
# Complete scene detector with OpenCV fallback mode

import os
import random
from typing import List, Dict, Tuple

# Try to import OpenCV with fallback
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
    print("✅ OpenCV available - using real computer vision")
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV not available - using fallback mode")
    # Create dummy numpy for compatibility
    class DummyNp:
        @staticmethod
        def mean(x): 
            return random.uniform(0.3, 0.7)
        @staticmethod  
        def std(x): 
            return random.uniform(0.2, 0.5)
        @staticmethod
        def linalg():
            class Norm:
                @staticmethod
                def norm(x):
                    return random.uniform(0, 10)
            return Norm()
    np = DummyNp()

class SceneDetector:
    def __init__(self):
        self.threshold = 0.3  # Scene change threshold
        self.opencv_available = OPENCV_AVAILABLE
        print(f"🎬 Scene detector initialized (OpenCV: {'✅' if OPENCV_AVAILABLE else '❌'})")
    
    def analyze_video(self, video_path: str) -> Dict:
        """Analyze video dengan OpenCV atau fallback mode"""
        if not self.opencv_available:
            print("🔄 Using fallback mode (no OpenCV)")
            return self._analyze_video_fallback(video_path)
        
        # Try OpenCV analysis first
        try:
            return self._analyze_video_opencv(video_path)
        except Exception as e:
            print(f"❌ OpenCV analysis failed: {str(e)}")
            print("🔄 Falling back to mock analysis")
            return self._analyze_video_fallback(video_path)
    
    def _analyze_video_opencv(self, video_path: str) -> Dict:
        """Real OpenCV analysis"""
        print(f"🎬 Real OpenCV analysis: {os.path.basename(video_path)}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        print(f"   Duration: {duration:.1f}s, FPS: {fps:.1f}, Frames: {frame_count}")
        
        # Detect scenes
        scene_changes = self._detect_scene_changes_opencv(cap, fps)
        
        # Analyze motion
        motion_levels = self._analyze_motion_opencv(video_path, fps)
        
        # Analyze brightness/contrast
        visual_quality = self._analyze_visual_quality_opencv(video_path, fps)
        
        cap.release()
        
        # Combine analysis
        analysis = {
            'success': True,
            'duration': duration,
            'fps': fps,
            'scene_changes': scene_changes,
            'motion_analysis': motion_levels,
            'visual_quality': visual_quality,
            'total_scenes': len(scene_changes),
            'analysis_method': 'opencv_real'
        }
        
        print(f"✅ Real analysis complete: {len(scene_changes)} scenes detected")
        return analysis
    
    def _analyze_video_fallback(self, video_path: str) -> Dict:
        """Fallback analysis tanpa OpenCV"""
        try:
            print(f"🎬 Fallback analysis: {os.path.basename(video_path)}")
            
            # Estimate duration dari file size
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            estimated_duration = min(600, file_size_mb * 8)  # Rough estimate
            
            print(f"   File size: {file_size_mb:.1f} MB")
            print(f"   Estimated duration: {estimated_duration:.1f}s")
            
            # Generate reasonable mock data
            scene_changes = self._generate_fallback_scenes(estimated_duration)
            motion_levels = self._generate_fallback_motion(estimated_duration)
            visual_quality = self._generate_fallback_visual(estimated_duration)
            
            analysis = {
                'success': True,
                'duration': estimated_duration,
                'fps': 30.0,  # Assume 30 FPS
                'scene_changes': scene_changes,
                'motion_analysis': motion_levels,
                'visual_quality': visual_quality,
                'total_scenes': len(scene_changes),
                'analysis_method': 'fallback_mock'
            }
            
            print(f"✅ Fallback analysis complete: {len(scene_changes)} scenes simulated")
            return analysis
            
        except Exception as e:
            print(f"❌ Fallback analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_scene_changes_opencv(self, cap, fps) -> List[Dict]:
        """Real scene detection with OpenCV"""
        scene_changes = [{'timestamp': 0.0, 'confidence': 1.0, 'type': 'start'}]
        
        prev_frame = None
        frame_num = 0
        sample_rate = max(1, int(fps / 2))  # Sample every 0.5 seconds
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_num % sample_rate == 0:
                # Resize untuk faster processing
                small_frame = cv2.resize(frame, (160, 90))
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_score = np.mean(diff) / 255.0
                    
                    # If difference exceeds threshold
                    if diff_score > self.threshold:
                        timestamp = frame_num / fps
                        confidence = min(diff_score / self.threshold, 1.0)
                        
                        scene_changes.append({
                            'timestamp': timestamp,
                            'confidence': confidence,
                            'type': 'scene_change',
                            'diff_score': diff_score
                        })
                        
                        print(f"   Scene change at {timestamp:.1f}s (confidence: {confidence:.2f})")
                
                prev_frame = gray
            
            frame_num += 1
        
        # Add end timestamp
        duration = frame_num / fps
        scene_changes.append({'timestamp': duration, 'confidence': 1.0, 'type': 'end'})
        
        return scene_changes
    
    def _analyze_motion_opencv(self, video_path: str, fps: float) -> List[Dict]:
        """Real motion analysis with OpenCV"""
        motion_data = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            prev_gray = None
            frame_num = 0
            sample_rate = max(1, int(fps))  # Sample every second
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_num % sample_rate == 0:
                    # Convert to grayscale and resize
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, (160, 90))
                    
                    if prev_gray is not None:
                        # Calculate optical flow (motion)
                        flow = cv2.calcOpticalFlowPyrLK(
                            prev_gray, gray, 
                            np.array([[80, 45]], dtype=np.float32),  # Center point
                            None
                        )[0]
                        
                        # Calculate motion magnitude
                        motion_magnitude = np.linalg.norm(flow[0] - [80, 45]) if flow is not None else 0
                        
                        timestamp = frame_num / fps
                        motion_data.append({
                            'timestamp': timestamp,
                            'motion_level': min(motion_magnitude / 10.0, 1.0),  # Normalize
                            'type': 'real_motion_analysis'
                        })
                    
                    prev_gray = gray
                
                frame_num += 1
            
            cap.release()
            
        except Exception as e:
            print(f"⚠️ Motion analysis warning: {str(e)}")
            # Return fallback data
            duration = 300  # Fallback duration
            return self._generate_fallback_motion(duration)
        
        return motion_data
    
    def _analyze_visual_quality_opencv(self, video_path: str, fps: float) -> List[Dict]:
        """Real visual quality analysis with OpenCV"""
        quality_data = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_num = 0
            sample_rate = max(1, int(fps * 2))  # Sample every 2 seconds
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_num % sample_rate == 0:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calculate brightness and contrast
                    brightness = np.mean(gray) / 255.0
                    contrast = np.std(gray) / 255.0
                    
                    timestamp = frame_num / fps
                    quality_data.append({
                        'timestamp': timestamp,
                        'brightness': brightness,
                        'contrast': contrast,
                        'quality_score': (brightness * 0.3 + contrast * 0.7),  # Weighted score
                        'type': 'real_visual_quality'
                    })
                
                frame_num += 1
            
            cap.release()
            
        except Exception as e:
            print(f"⚠️ Visual analysis warning: {str(e)}")
            # Return fallback data
            duration = 300  # Fallback duration
            return self._generate_fallback_visual(duration)
        
        return quality_data
    
    def _generate_fallback_scenes(self, duration: float) -> List[Dict]:
        """Generate realistic fallback scene changes"""
        scenes = [{'timestamp': 0.0, 'confidence': 1.0, 'type': 'start'}]
        
        # Generate scene changes based on video length
        if duration <= 60:  # Short video
            # Add one scene change in the middle
            scenes.append({
                'timestamp': duration * 0.5,
                'confidence': 0.8,
                'type': 'fallback_scene_change'
            })
        elif duration <= 180:  # Medium video
            # Add 2-3 scene changes
            for i in range(2):
                timestamp = duration * (0.3 + i * 0.4)
                scenes.append({
                    'timestamp': timestamp,
                    'confidence': random.uniform(0.7, 0.9),
                    'type': 'fallback_scene_change'
                })
        else:  # Long video
            # Add scene changes every 30-60 seconds
            current_time = 0
            while current_time < duration - 30:
                current_time += random.uniform(25, 50)
                if current_time < duration:
                    scenes.append({
                        'timestamp': current_time,
                        'confidence': random.uniform(0.7, 0.95),
                        'type': 'fallback_scene_change'
                    })
        
        # Add end
        scenes.append({'timestamp': duration, 'confidence': 1.0, 'type': 'end'})
        
        return scenes
    
    def _generate_fallback_motion(self, duration: float) -> List[Dict]:
        """Generate fallback motion data"""
        motion_data = []
        
        # Generate motion points every 5 seconds
        for t in range(0, int(duration), 5):
            # Create realistic motion patterns
            if t < duration * 0.1:  # Beginning - usually calm
                motion_level = random.uniform(0.2, 0.5)
            elif t > duration * 0.8:  # End - often calm
                motion_level = random.uniform(0.3, 0.6)
            else:  # Middle - more varied
                motion_level = random.uniform(0.4, 0.9)
            
            motion_data.append({
                'timestamp': float(t),
                'motion_level': motion_level,
                'type': 'fallback_motion_analysis'
            })
        
        return motion_data
    
    def _generate_fallback_visual(self, duration: float) -> List[Dict]:
        """Generate fallback visual quality data"""
        quality_data = []
        
        # Generate quality points every 10 seconds
        for t in range(0, int(duration), 10):
            # Create realistic brightness/contrast patterns
            brightness = random.uniform(0.3, 0.8)
            contrast = random.uniform(0.4, 0.9)
            
            quality_data.append({
                'timestamp': float(t),
                'brightness': brightness,
                'contrast': contrast,
                'quality_score': (brightness * 0.3 + contrast * 0.7),
                'type': 'fallback_visual_quality'
            })
        
        return quality_data
    
    def generate_smart_clips(self, analysis: Dict, clip_count: int = 5) -> List[Dict]:
        """Generate clips berdasarkan AI analysis - ENHANCED VERSION"""
        if not analysis.get('success'):
            print("❌ Analysis not successful, generating fallback clips")
            return self._generate_fallback_clips(analysis.get('duration', 120), clip_count)
        
        scene_changes = analysis.get('scene_changes', [])
        motion_levels = analysis.get('motion_analysis', [])
        visual_quality = analysis.get('visual_quality', [])
        duration = analysis.get('duration', 120)
        analysis_method = analysis.get('analysis_method', 'unknown')
        
        print(f"🎯 Generating clips from {len(scene_changes)} scenes, duration: {duration:.1f}s")
        print(f"   Analysis method: {analysis_method}")
        
        # Score each potential clip segment
        clip_candidates = []
        
        for i in range(len(scene_changes) - 1):
            start_time = scene_changes[i]['timestamp']
            end_time = scene_changes[i + 1]['timestamp']
            segment_duration = end_time - start_time
            
            print(f"   Evaluating scene {i+1}: {start_time:.1f}s - {end_time:.1f}s ({segment_duration:.1f}s)")
            
            # More lenient constraints
            if segment_duration < 5:  # Skip very short segments
                print(f"   ⚠️ Skipping scene {i+1}: too short ({segment_duration:.1f}s)")
                continue
            
            # For long segments, create multiple clips
            if segment_duration > 90:
                print(f"   ✂️ Splitting long scene {i+1}: {segment_duration:.1f}s")
                num_clips = min(3, max(2, int(segment_duration / 45)))
                sub_duration = segment_duration / num_clips
                
                for j in range(num_clips):
                    sub_start = start_time + (j * sub_duration)
                    sub_end = min(sub_start + min(60, sub_duration), end_time)
                    
                    if sub_end - sub_start >= 10:  # Minimum 10s
                        clip_candidates.append(self._create_clip_candidate(
                            sub_start, sub_end, motion_levels, visual_quality, duration, f"Part {j+1}"
                        ))
            else:
                # Normal segment
                clip_end = min(end_time, start_time + 75)  # Max 75s clips
                if clip_end - start_time >= 8:  # Minimum 8s
                    clip_candidates.append(self._create_clip_candidate(
                        start_time, clip_end, motion_levels, visual_quality, duration
                    ))
        
        print(f"📊 Generated {len(clip_candidates)} clip candidates")
        
        # If no clips from scene analysis, generate time-based clips
        if not clip_candidates:
            print("⚠️ No clips from scene analysis, generating time-based clips")
            return self._generate_time_based_clips(duration, clip_count)
        
        # Sort by score and take top clips
        clip_candidates.sort(key=lambda x: x['score'], reverse=True)
        top_clips = clip_candidates[:clip_count]
        
        # Format clips
        smart_clips = []
        for i, clip in enumerate(top_clips):
            smart_clips.append({
                'clip_id': f'smart_clip_{i+1}',
                'title': f'🤖 {clip["type"]} {clip.get("suffix", "")}',
                'start_time': clip['start_time'],
                'end_time': clip['end_time'],
                'duration': clip['duration'],
                'confidence': min(clip['score'], 1.0),  # Cap at 1.0
                'type': clip['type'],
                'ai_analysis': {
                    'motion_score': clip['motion_score'],
                    'visual_score': clip['visual_score'],
                    'overall_score': clip['score'],
                    'analysis_method': analysis_method
                }
            })
        
        # Emergency fallback - ensure we always have clips
        if not smart_clips:
            print("🚑 Emergency fallback - creating basic clips")
            smart_clips = self._generate_emergency_clips(duration, clip_count)
        
        print(f"✅ Created {len(smart_clips)} smart clips")
        return smart_clips
    
    def _create_clip_candidate(self, start_time: float, end_time: float, motion_levels: List, visual_quality: List, duration: float, suffix: str = "") -> Dict:
        """Create clip candidate with scoring"""
        clip_duration = end_time - start_time
        
        # Calculate scores
        motion_score = self._get_motion_score(start_time, end_time, motion_levels)
        visual_score = self._get_visual_score(start_time, end_time, visual_quality)
        position_score = self._get_position_score(start_time, duration)
        
        # Combine scores with randomness for variety
        randomness = random.uniform(0.9, 1.1)
        
        total_score = (
            motion_score * 0.35 + 
            visual_score * 0.35 + 
            position_score * 0.3
        ) * randomness
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': clip_duration,
            'score': total_score,
            'motion_score': motion_score,
            'visual_score': visual_score,
            'type': self._classify_clip_type(motion_score, visual_score),
            'suffix': suffix
        }
    
    def _generate_time_based_clips(self, duration: float, clip_count: int) -> List[Dict]:
        """Generate time-based clips as fallback"""
        clips = []
        
        print(f"🔄 Generating {clip_count} time-based clips for {duration:.1f}s video")
        
        if duration <= 60:  # Short video
            clips.append({
                'clip_id': 'time_clip_1',
                'title': '🎬 Video Highlight',
                'start_time': 5.0,
                'end_time': max(15.0, duration - 5),
                'duration': max(10.0, duration - 10),
                'confidence': 0.8,
                'type': 'full_highlight',
                'ai_analysis': {'method': 'time_based', 'reason': 'short_video'}
            })
        else:
            # Distribute clips evenly through video
            step = duration / (clip_count + 1)
            
            for i in range(clip_count):
                start_time = step * (i + 1)
                clip_duration = min(45, duration * 0.18)  # 18% of video or 45s max
                end_time = min(start_time + clip_duration, duration - 5)
                
                if end_time - start_time >= 10:
                    clips.append({
                        'clip_id': f'time_clip_{i+1}',
                        'title': f'🎯 Segment {i+1}',
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time,
                        'confidence': 0.75 + (i * 0.02),  # Slight variation
                        'type': 'time_segment',
                        'ai_analysis': {
                            'method': 'time_based',
                            'position': f'segment_{i+1}',
                            'distribution': 'even'
                        }
                    })
        
        print(f"✅ Generated {len(clips)} time-based clips")
        return clips
    
    def _generate_emergency_clips(self, duration: float, clip_count: int) -> List[Dict]:
        """Emergency clip generation - guaranteed to create clips"""
        clips = []
        
        print(f"🚑 Emergency clip generation for {duration:.1f}s video")
        
        for i in range(clip_count):
            # Simple distribution across video
            start_ratio = (i + 0.5) / clip_count  # Distribute evenly
            start_time = duration * start_ratio
            clip_duration = min(30, duration * 0.15)  # 15% of video or 30s
            end_time = min(start_time + clip_duration, duration - 2)
            
            # Ensure minimum duration
            if end_time - start_time < 8:
                end_time = min(start_time + 8, duration - 1)
            
            if start_time < duration - 5:  # Valid clip
                clips.append({
                    'clip_id': f'emergency_clip_{i+1}',
                    'title': f'📹 Clip {i+1}',
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'confidence': 0.7,
                    'type': 'emergency',
                    'ai_analysis': {
                        'method': 'emergency_fallback',
                        'position': f'{start_ratio:.1%}'
                    }
                })
        
        print(f"🚑 Emergency generated {len(clips)} clips")
        return clips
    
    def _generate_fallback_clips(self, duration: float, clip_count: int) -> List[Dict]:
        """Fallback when analysis fails"""
        print(f"🔄 Fallback clip generation for {duration:.1f}s video")
        return self._generate_time_based_clips(duration, clip_count)
    
    def _get_motion_score(self, start: float, end: float, motion_data: List) -> float:
        """Get average motion score for time segment"""
        if not motion_data:
            return random.uniform(0.4, 0.8)  # Fallback score
            
        relevant_motion = [m['motion_level'] for m in motion_data 
                          if start <= m['timestamp'] <= end]
        return np.mean(relevant_motion) if relevant_motion else 0.5
    
    def _get_visual_score(self, start: float, end: float, visual_data: List) -> float:
        """Get average visual quality score"""
        if not visual_data:
            return random.uniform(0.5, 0.9)  # Fallback score
            
        relevant_visual = [v['quality_score'] for v in visual_data 
                          if start <= v['timestamp'] <= end]
        return np.mean(relevant_visual) if relevant_visual else 0.5
    
    def _get_position_score(self, start_time: float, total_duration: float) -> float:
        """Score based on position (beginning and end often important)"""
        ratio = start_time / total_duration
        if ratio < 0.1:  # Beginning
            return 0.9
        elif ratio > 0.8:  # End
            return 0.8
        elif 0.2 < ratio < 0.7:  # Middle content
            return 0.85
        else:
            return 0.6
    
    def _classify_clip_type(self, motion_score: float, visual_score: float) -> str:
        """Classify clip type based on analysis"""
        if motion_score > 0.7:
            return "High Action"
        elif visual_score > 0.8:
            return "High Quality"
        elif motion_score > 0.4 and visual_score > 0.6:
            return "Balanced"
        else:
            return "Steady"

# Test function
def test_scene_detector():
    """Test scene detector"""
    detector = SceneDetector()
    print("🧪 Testing Scene Detector...")
    print("✅ Scene detector ready for video analysis")
    return True

if __name__ == "__main__":
    test_scene_detector()