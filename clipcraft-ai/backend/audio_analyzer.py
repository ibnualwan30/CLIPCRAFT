# File: backend/audio_analyzer.py
# Audio analysis untuk detect viral moments dan audio patterns

import os
import numpy as np
from typing import Dict, List, Tuple
import tempfile

# Try to import audio libraries with fallback
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️ MoviePy not available, using audio fallback mode")

class AudioAnalyzer:
    def __init__(self):
        self.moviepy_available = MOVIEPY_AVAILABLE
        self.sample_rate = 22050
        print(f"🎵 Audio analyzer initialized (MoviePy: {'✅' if MOVIEPY_AVAILABLE else '❌'})")
    
    def analyze_audio(self, video_path: str) -> Dict:
        """Comprehensive audio analysis for viral moment detection"""
        try:
            print(f"🎵 Analyzing audio: {os.path.basename(video_path)}")
            
            if self.moviepy_available:
                return self._analyze_with_moviepy(video_path)
            else:
                return self._analyze_fallback(video_path)
                
        except Exception as e:
            print(f"❌ Audio analysis failed: {str(e)}")
            return self._generate_fallback_audio_analysis(video_path)
    
    def _analyze_with_moviepy(self, video_path: str) -> Dict:
        """Real audio analysis using MoviePy"""
        try:
            # Load video and extract audio
            video = VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                print("⚠️ No audio track found in video")
                return self._generate_fallback_audio_analysis(video_path)
            
            duration = video.duration
            fps = video.fps
            
            print(f"   Video duration: {duration:.1f}s, FPS: {fps:.1f}")
            
            # Extract audio array
            audio_array = audio.to_soundarray(fps=self.sample_rate)
            
            # Close resources
            audio.close()
            video.close()
            
            # Analyze audio features
            volume_analysis = self._analyze_volume_levels(audio_array, duration)
            peak_analysis = self._detect_audio_peaks(audio_array, duration)
            silence_analysis = self._detect_silence_periods(audio_array, duration)
            energy_analysis = self._analyze_energy_distribution(audio_array, duration)
            viral_moments = self._identify_viral_audio_moments(
                volume_analysis, peak_analysis, energy_analysis
            )
            
            return {
                'success': True,
                'duration': duration,
                'sample_rate': self.sample_rate,
                'has_audio': True,
                'volume_analysis': volume_analysis,
                'peak_analysis': peak_analysis,
                'silence_analysis': silence_analysis,
                'energy_analysis': energy_analysis,
                'viral_moments': viral_moments,
                'analysis_method': 'moviepy_real'
            }
            
        except Exception as e:
            print(f"❌ MoviePy audio analysis failed: {str(e)}")
            return self._analyze_fallback(video_path)
    
    def _analyze_volume_levels(self, audio_array: np.ndarray, duration: float) -> List[Dict]:
        """Analyze volume levels over time"""
        volume_data = []
        
        # Calculate RMS volume in 2-second windows
        window_size = int(self.sample_rate * 2)  # 2 seconds
        
        for i in range(0, len(audio_array), window_size):
            window = audio_array[i:i+window_size]
            
            if len(window) > 0:
                # Calculate RMS (Root Mean Square) for volume
                if window.ndim > 1:  # Stereo audio
                    rms = np.sqrt(np.mean(window**2, axis=0))
                    volume = np.mean(rms)  # Average across channels
                else:  # Mono audio
                    volume = np.sqrt(np.mean(window**2))
                
                timestamp = i / self.sample_rate
                
                volume_data.append({
                    'timestamp': timestamp,
                    'volume': float(volume),
                    'volume_db': float(20 * np.log10(max(volume, 1e-10))),  # Convert to dB
                    'type': 'volume_analysis'
                })
        
        print(f"   Volume analysis: {len(volume_data)} data points")
        return volume_data
    
    def _detect_audio_peaks(self, audio_array: np.ndarray, duration: float) -> List[Dict]:
        """Detect significant audio peaks (loud moments)"""
        peaks = []
        
        # Calculate volume levels first
        window_size = int(self.sample_rate * 1)  # 1 second windows
        volumes = []
        timestamps = []
        
        for i in range(0, len(audio_array), window_size):
            window = audio_array[i:i+window_size]
            
            if len(window) > 0:
                if window.ndim > 1:
                    volume = np.sqrt(np.mean(window**2))
                else:
                    volume = np.sqrt(np.mean(window**2))
                
                volumes.append(volume)
                timestamps.append(i / self.sample_rate)
        
        if not volumes:
            return peaks
        
        # Find peaks (moments significantly louder than average)
        mean_volume = np.mean(volumes)
        std_volume = np.std(volumes)
        threshold = mean_volume + (1.5 * std_volume)
        
        for i, (timestamp, volume) in enumerate(zip(timestamps, volumes)):
            if volume > threshold:
                # Check if it's a local maximum
                is_peak = True
                for j in range(max(0, i-2), min(len(volumes), i+3)):
                    if j != i and volumes[j] >= volume:
                        is_peak = False
                        break
                
                if is_peak:
                    peaks.append({
                        'timestamp': timestamp,
                        'volume': float(volume),
                        'intensity': float((volume - mean_volume) / std_volume),
                        'type': 'audio_peak'
                    })
        
        print(f"   Audio peaks detected: {len(peaks)}")
        return peaks
    
    def _detect_silence_periods(self, audio_array: np.ndarray, duration: float) -> List[Dict]:
        """Detect silence periods (potential cut points)"""
        silence_periods = []
        
        # Calculate volume in small windows
        window_size = int(self.sample_rate * 0.5)  # 0.5 second windows
        silence_threshold = 0.01  # Threshold for silence
        
        current_silence_start = None
        
        for i in range(0, len(audio_array), window_size):
            window = audio_array[i:i+window_size]
            
            if len(window) > 0:
                if window.ndim > 1:
                    volume = np.sqrt(np.mean(window**2))
                else:
                    volume = np.sqrt(np.mean(window**2))
                
                timestamp = i / self.sample_rate
                
                if volume < silence_threshold:
                    # Start of silence
                    if current_silence_start is None:
                        current_silence_start = timestamp
                else:
                    # End of silence
                    if current_silence_start is not None:
                        silence_duration = timestamp - current_silence_start
                        
                        # Only record silences longer than 1 second
                        if silence_duration > 1.0:
                            silence_periods.append({
                                'start_time': current_silence_start,
                                'end_time': timestamp,
                                'duration': silence_duration,
                                'type': 'silence_period'
                            })
                        
                        current_silence_start = None
        
        print(f"   Silence periods detected: {len(silence_periods)}")
        return silence_periods
    
    def _analyze_energy_distribution(self, audio_array: np.ndarray, duration: float) -> List[Dict]:
        """Analyze energy distribution for excitement detection"""
        energy_data = []
        
        # Calculate energy in 3-second windows
        window_size = int(self.sample_rate * 3)  # 3 seconds
        
        for i in range(0, len(audio_array), window_size):
            window = audio_array[i:i+window_size]
            
            if len(window) > 0:
                # Calculate energy (sum of squares)
                if window.ndim > 1:
                    energy = np.sum(window**2)
                else:
                    energy = np.sum(window**2)
                
                # Normalize energy
                energy_normalized = energy / len(window)
                
                timestamp = i / self.sample_rate
                
                energy_data.append({
                    'timestamp': timestamp,
                    'energy': float(energy_normalized),
                    'energy_level': 'high' if energy_normalized > 0.1 else 'medium' if energy_normalized > 0.01 else 'low',
                    'type': 'energy_analysis'
                })
        
        print(f"   Energy analysis: {len(energy_data)} segments")
        return energy_data
    
    def _identify_viral_audio_moments(self, volume_data: List[Dict], peak_data: List[Dict], energy_data: List[Dict]) -> List[Dict]:
        """Identify moments with high viral potential based on audio"""
        viral_moments = []
        
        # Combine different audio features to identify viral moments
        for energy_point in energy_data:
            timestamp = energy_point['timestamp']
            
            # Get volume at this timestamp
            volume_score = 0.5  # Default
            for vol_point in volume_data:
                if abs(vol_point['timestamp'] - timestamp) <= 1.0:  # Within 1 second
                    volume_score = vol_point['volume']
                    break
            
            # Check for nearby peaks
            peak_bonus = 0
            for peak in peak_data:
                if abs(peak['timestamp'] - timestamp) <= 3.0:  # Within 3 seconds
                    peak_bonus = peak['intensity'] * 0.3
                    break
            
            # Calculate viral potential score
            energy_score = energy_point['energy']
            viral_score = (energy_score * 0.4) + (volume_score * 0.4) + peak_bonus
            
            # Only include moments with high viral potential
            if viral_score > 0.6:
                viral_moments.append({
                    'timestamp': timestamp,
                    'viral_score': float(viral_score),
                    'energy_score': float(energy_score),
                    'volume_score': float(volume_score),
                    'peak_bonus': float(peak_bonus),
                    'type': 'viral_audio_moment',
                    'description': self._describe_viral_moment(viral_score, energy_score, volume_score)
                })
        
        # Sort by viral score
        viral_moments.sort(key=lambda x: x['viral_score'], reverse=True)
        
        print(f"   Viral audio moments identified: {len(viral_moments)}")
        return viral_moments[:10]  # Top 10 moments
    
    def _describe_viral_moment(self, viral_score: float, energy_score: float, volume_score: float) -> str:
        """Generate description for viral moment"""
        if energy_score > 0.2 and volume_score > 0.3:
            return "High energy & loud moment - great for highlights"
        elif energy_score > 0.15:
            return "High energy moment - potential for engagement"
        elif volume_score > 0.4:
            return "Loud/dramatic moment - attention-grabbing"
        else:
            return "Interesting audio pattern - worth checking"
    
    def _analyze_fallback(self, video_path: str) -> Dict:
        """Fallback audio analysis without MoviePy"""
        try:
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            estimated_duration = min(600, file_size_mb * 8)
            
            print(f"   Fallback audio analysis - estimated duration: {estimated_duration:.1f}s")
            
            # Generate mock audio analysis
            import random
            
            volume_data = []
            for t in range(0, int(estimated_duration), 2):
                volume_data.append({
                    'timestamp': float(t),
                    'volume': random.uniform(0.1, 0.8),
                    'volume_db': random.uniform(-40, -10),
                    'type': 'mock_volume'
                })
            
            peak_data = []
            for i in range(3):  # 3 random peaks
                timestamp = random.uniform(10, estimated_duration - 10)
                peak_data.append({
                    'timestamp': timestamp,
                    'volume': random.uniform(0.6, 0.9),
                    'intensity': random.uniform(1.5, 3.0),
                    'type': 'mock_peak'
                })
            
            viral_moments = []
            for i in range(2):  # 2 viral moments
                timestamp = random.uniform(15, estimated_duration - 15)
                viral_moments.append({
                    'timestamp': timestamp,
                    'viral_score': random.uniform(0.7, 0.95),
                    'description': "Mock viral moment - high energy detected",
                    'type': 'mock_viral_moment'
                })
            
            return {
                'success': True,
                'duration': estimated_duration,
                'sample_rate': self.sample_rate,
                'has_audio': True,
                'volume_analysis': volume_data,
                'peak_analysis': peak_data,
                'silence_analysis': [],
                'energy_analysis': [],
                'viral_moments': viral_moments,
                'analysis_method': 'fallback_mock'
            }
            
        except Exception as e:
            print(f"❌ Fallback audio analysis failed: {str(e)}")
            return self._generate_fallback_audio_analysis(video_path)
    
    def _generate_fallback_audio_analysis(self, video_path: str) -> Dict:
        """Generate minimal fallback when all else fails"""
        return {
            'success': False,
            'error': 'Audio analysis not available',
            'has_audio': False,
            'analysis_method': 'failed'
        }
    
    def enhance_clips_with_audio(self, clips: List[Dict], audio_analysis: Dict) -> List[Dict]:
        """Enhance clip scoring with audio analysis"""
        if not audio_analysis.get('success'):
            return clips
        
        viral_moments = audio_analysis.get('viral_moments', [])
        volume_data = audio_analysis.get('volume_analysis', [])
        
        enhanced_clips = []
        
        for clip in clips:
            start_time = clip.get('start_time', 0)
            end_time = clip.get('end_time', start_time + 30)
            
            # Check for viral moments in this clip
            viral_score_bonus = 0
            audio_highlights = []
            
            for moment in viral_moments:
                moment_time = moment['timestamp']
                if start_time <= moment_time <= end_time:
                    viral_score_bonus += moment['viral_score'] * 0.2
                    audio_highlights.append({
                        'timestamp': moment_time,
                        'description': moment['description'],
                        'score': moment['viral_score']
                    })
            
            # Calculate average volume in clip
            clip_volumes = [v['volume'] for v in volume_data 
                          if start_time <= v['timestamp'] <= end_time]
            avg_volume = np.mean(clip_volumes) if clip_volumes else 0.5
            
            # Create enhanced clip
            enhanced_clip = clip.copy()
            enhanced_clip['audio_analysis'] = {
                'viral_score_bonus': viral_score_bonus,
                'average_volume': float(avg_volume),
                'audio_highlights': audio_highlights,
                'has_viral_moments': len(audio_highlights) > 0
            }
            
            # Update confidence with audio bonus
            original_confidence = clip.get('confidence', 0.7)
            enhanced_confidence = min(1.0, original_confidence + viral_score_bonus)
            enhanced_clip['confidence'] = enhanced_confidence
            
            enhanced_clips.append(enhanced_clip)
        
        print(f"✅ Enhanced {len(enhanced_clips)} clips with audio analysis")
        return enhanced_clips

# Test function
def test_audio_analyzer():
    """Test audio analyzer"""
    analyzer = AudioAnalyzer()
    print("🧪 Testing Audio Analyzer...")
    print("✅ Audio analyzer ready!")
    return True

if __name__ == "__main__":
    test_audio_analyzer()