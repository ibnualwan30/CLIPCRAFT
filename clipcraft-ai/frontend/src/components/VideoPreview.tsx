// File: frontend/src/components/VideoPreview.tsx
// UPDATE: Tambahkan video player functionality

import React, { useState } from 'react';
import { Play, Download, Clock, TrendingUp, Star, Grid, List, ExternalLink, Youtube, Copy, FileDown, Loader2 } from 'lucide-react';

interface ClipData {
  clip_id: string;
  title: string;
  start_time: number;
  end_time: number;
  duration: number;
  confidence: number;
  type: string;
  ai_analysis?: {
    motion_score?: number;
    visual_score?: number;
    overall_score?: number;
  };
}

interface VideoInfo {
  title: string;
  duration: number;
  views: number;
  uploader: string;
}

interface VideoPreviewProps {
  videoInfo: VideoInfo;
  clips: ClipData[];
  youtubeUrl: string;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({ videoInfo, clips, youtubeUrl }) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedClip, setSelectedClip] = useState<ClipData | null>(null);
  const [isPlayerVisible, setIsPlayerVisible] = useState(false);
  const [downloadingClips, setDownloadingClips] = useState<Set<string>>(new Set());
  const [batchDownloading, setBatchDownloading] = useState(false);
  const [copyingTimestamps, setCopyingTimestamps] = useState(false);

  // Extract YouTube video ID
  const getYouTubeId = (url: string) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    return match ? match[1] : null;
  };

  const videoId = getYouTubeId(youtubeUrl);

  // Format time helper
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Generate YouTube embed URL with start time
  const getEmbedUrl = (startTime?: number) => {
    if (!videoId) return '';
    const baseUrl = `https://www.youtube.com/embed/${videoId}`;
    const params = new URLSearchParams({
      autoplay: '1',
      controls: '1',
      rel: '0',
      modestbranding: '1',
      ...(startTime && { start: Math.floor(startTime).toString() })
    });
    return `${baseUrl}?${params.toString()}`;
  };

  // Generate YouTube link with timestamp
  const getYouTubeLink = (startTime?: number) => {
    if (!videoId) return youtubeUrl;
    const baseUrl = `https://www.youtube.com/watch?v=${videoId}`;
    return startTime ? `${baseUrl}&t=${Math.floor(startTime)}s` : baseUrl;
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'text-green-400 bg-green-400/20';
    if (confidence > 0.6) return 'text-yellow-400 bg-yellow-400/20';
    return 'text-red-400 bg-red-400/20';
  };

  // Get type emoji
  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'high action': return '⚡';
      case 'high quality': return '✨';
      case 'balanced': return '🎯';
      case 'steady': return '📹';
      default: return '🎬';
    }
  };

  // Calculate viral potential
  const getViralPotential = (clip: ClipData) => {
    const baseScore = clip.confidence;
    const motionBonus = (clip.ai_analysis?.motion_score || 0.5) * 0.3;
    const visualBonus = (clip.ai_analysis?.visual_score || 0.5) * 0.2;
    const typeBonus = clip.type === 'High Action' ? 0.2 : 0.1;
    const downloadClip = async (clip: ClipData) => {
  if (!videoId) {
    alert('Video ID not available');
    return;
  }

  setDownloadingClips(prev => new Set(prev).add(clip.clip_id));

  try {
    const response = await fetch('http://localhost:8001/api/download-clip', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        clip_id: clip.clip_id,
        title: clip.title,
        start_time: clip.start_time,
        end_time: clip.end_time,
        format: 'mp4'
      }),
    });

    const result = await response.json();

    if (result.success) {
      // Open YouTube link with timestamp
      window.open(result.youtube_url, '_blank');
      
      // Show success message with instructions
      const instructions = result.instructions;
      alert(`✅ Clip download prepared!

📱 Quick Options:
1. ${instructions.method_1}
2. ${instructions.method_2}

🔗 Link: ${result.youtube_url}`);
    } else {
      throw new Error(result.error || 'Download preparation failed');
    }
  } catch (error) {
    console.error('Download failed:', error);
    alert(`❌ Download failed: ${error}`);
  } finally {
    setDownloadingClips(prev => {
      const newSet = new Set(prev);
      newSet.delete(clip.clip_id);
      return newSet;
    });
  }
};

  // Download all clips - NEW FUNCTION
const downloadAllClips = async () => {
  if (!videoId || clips.length === 0) {
    alert('No clips available for download');
    return;
  }

  setBatchDownloading(true);

  try {
    const response = await fetch('http://localhost:8001/api/download-batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        clips: clips,
        format: 'mp4'
      }),
    });

    const result = await response.json();

    if (result.success) {
      // Open each clip link in new tab
      result.clips.forEach((clipInfo: any, index: number) => {
        setTimeout(() => {
          window.open(clipInfo.youtube_url, '_blank');
        }, index * 1000); // Delay to avoid popup blocking
      });

      alert(`✅ Batch download prepared!

📊 ${result.total_clips} clips ready
🔗 Opening each clip in new tabs...

💡 Tip: ${result.download_tips[0]}`);
    } else {
      throw new Error('Batch download preparation failed');
    }
  } catch (error) {
    console.error('Batch download failed:', error);
    alert(`❌ Batch download failed: ${error}`);
  } finally {
    setBatchDownloading(false);
  }
};

// Copy timestamps to clipboard - ENHANCED FUNCTION
const copyTimestamps = async () => {
  if (!videoId) {
    alert('Video ID not available');
    return;
  }

  setCopyingTimestamps(true);

  try {
    const response = await fetch('http://localhost:8001/api/copy-timestamps', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        clips: clips
      }),
    });

    const result = await response.json();

    if (result.success) {
      await navigator.clipboard.writeText(result.timestamp_text);
      alert(`✅ Timestamps copied to clipboard!

📋 ${result.total_clips} clips included
📤 Ready to paste and share!`);
    } else {
      throw new Error('Failed to generate timestamps');
    }
  } catch (error) {
    console.error('Copy timestamps failed:', error);
    
    // Fallback: manual copy
    const fallbackText = clips.map((clip, index) => 
      `${index + 1}. ${clip.title}
   ⏰ ${formatTime(clip.start_time)} - ${formatTime(clip.end_time)}
   🔗 ${getYouTubeLink(clip.start_time)}
`
    ).join('\n');
    
    try {
      await navigator.clipboard.writeText(fallbackText);
      alert('✅ Timestamps copied (fallback method)');
    } catch {
      alert(`❌ Copy failed. Please copy manually:

${fallbackText.slice(0, 200)}...`);
    }
  } finally {
    setCopyingTimestamps(false);
  }
};

    return Math.min(1.0, baseScore + motionBonus + visualBonus + typeBonus);
  };

  // Handle clip selection for preview
  const handleClipPreview = (clip: ClipData) => {
    setSelectedClip(clip);
    setIsPlayerVisible(true);
  };

  // Copy timestamp links to clipboard
  const copyTimestamps = () => {
    const timestamps = clips.map(clip => 
      `${clip.title}\n${getYouTubeLink(clip.start_time)}\nDuration: ${formatTime(clip.duration)} | Confidence: ${Math.round(clip.confidence * 100)}%\n`
    ).join('\n');
    
    navigator.clipboard.writeText(timestamps).then(() => {
      alert('Timestamps copied to clipboard!');
    });
  };

  return (
    <div className="space-y-6">
      {/* Success Header */}
      <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 backdrop-blur-sm border border-green-500/30 rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white mb-3 flex items-center">
              🎉 Processing Complete! 
              <span className="ml-2 text-green-400">✓</span>
            </h2>
            <h3 className="text-xl text-slate-200 mb-3">{videoInfo.title}</h3>
            
            <div className="flex items-center space-x-6 text-slate-400">
              <span className="flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                {formatTime(videoInfo.duration)}
              </span>
              <span className="flex items-center">
                <TrendingUp className="w-4 h-4 mr-2" />
                {videoInfo.views?.toLocaleString()} views
              </span>
              <span className="text-slate-300">by {videoInfo.uploader}</span>
            </div>
          </div>
          
          {/* Original Video Thumbnail */}
          {videoId && (
            <div className="ml-6">
              <div className="w-48 h-28 bg-slate-700 rounded-lg overflow-hidden border border-slate-600 cursor-pointer hover:border-blue-500 transition-colors"
                   onClick={() => window.open(youtubeUrl, '_blank')}>
                <img
                  src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                  alt="Video thumbnail"
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-xs text-slate-400 mt-2 text-center">Click to open original</p>
            </div>
          )}
        </div>
      </div>

      {/* Video Player Section */}
      {isPlayerVisible && selectedClip && videoId && (
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center">
                  🎬 Video Player - {selectedClip.title}
                </h3>
                <p className="text-sm text-slate-400">
                  Playing from {formatTime(selectedClip.start_time)} to {formatTime(selectedClip.end_time)}
                </p>
              </div>
              <button
                onClick={() => setIsPlayerVisible(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
          
          {/* YouTube Embed Player */}
          <div className="aspect-video bg-black">
            <iframe
              src={getEmbedUrl(selectedClip.start_time)}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={`Clip: ${selectedClip.title}`}
            />
          </div>
          
          {/* Player Controls */}
          <div className="p-4 bg-slate-900/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 text-sm text-slate-300">
                <span>⏱️ Duration: {formatTime(selectedClip.duration)}</span>
                <span>🎯 Confidence: {Math.round(selectedClip.confidence * 100)}%</span>
                <span>📊 Type: {selectedClip.type}</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => window.open(getYouTubeLink(selectedClip.start_time), '_blank')}
                  className="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-1 text-sm"
                >
                  <Youtube className="w-4 h-4" />
                  <span>Open in YouTube</span>
                </button>
                
                <button
                  onClick={() => navigator.clipboard.writeText(getYouTubeLink(selectedClip.start_time))}
                  className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-1 text-sm"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Copy Link</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clips Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center">
            🤖 AI Generated Clips ({clips.length})
          </h3>
          <p className="text-slate-400 text-sm mt-1">
            Smart clips generated using AI scene detection and analysis
          </p>
        </div>
        
        {/* View Toggle & Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={copyTimestamps}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all flex items-center space-x-2 text-sm"
          >
            <Clock className="w-4 h-4" />
            <span>Copy All Timestamps</span>
          </button>
          
          <div className="flex items-center space-x-2 bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-all ${
                viewMode === 'grid' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-all ${
                viewMode === 'list' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Clips Display */}
      <div className={
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
      }>
        {clips.map((clip, index) => {
          const viralPotential = getViralPotential(clip);
          const isSelected = selectedClip?.clip_id === clip.clip_id;
          
          return (
            <div
              key={clip.clip_id}
              className={`group bg-slate-800/50 backdrop-blur-sm border rounded-xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 transform hover:-translate-y-1 ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-500/20' : 'border-slate-700'
              }`}
            >
              {/* Clip Thumbnail/Preview */}
              <div className="relative cursor-pointer" onClick={() => handleClipPreview(clip)}>
                <div className="aspect-video bg-slate-700 flex items-center justify-center relative">
                  {videoId ? (
                    <img
                      src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                      alt={clip.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <Play className="w-12 h-12 text-slate-500" />
                  )}
                  
                  {/* Duration Badge */}
                  <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                    {formatTime(clip.duration)}
                  </div>
                  
                  {/* Viral Potential Badge */}
                  {viralPotential > 0.75 && (
                    <div className="absolute top-2 left-2 bg-gradient-to-r from-pink-500 to-orange-500 text-white text-xs px-2 py-1 rounded-full flex items-center">
                      <Star className="w-3 h-3 mr-1" />
                      Viral
                    </div>
                  )}
                  
                  {/* Play Overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <div className="bg-white/20 backdrop-blur-sm rounded-full p-4">
                      <Play className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  
                  {/* Selected Indicator */}
                  {isSelected && (
                    <div className="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                      Playing
                    </div>
                  )}
                </div>
              </div>

              {/* Clip Info */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-white text-sm leading-tight flex items-center">
                    <span className="mr-2">{getTypeIcon(clip.type)}</span>
                    {clip.title}
                  </h4>
                </div>

                {/* Timing Info */}
                <div className="text-xs text-slate-400 mb-3 flex items-center justify-between">
                  <span>
                    {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                  </span>
                  <span className="text-slate-500 bg-slate-700 px-2 py-1 rounded">
                    {clip.type}
                  </span>
                </div>

                {/* AI Scores */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">AI Confidence</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(clip.confidence)}`}>
                      {Math.round(clip.confidence * 100)}%
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">Viral Potential</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(viralPotential)}`}>
                      {Math.round(viralPotential * 100)}%
                    </span>
                  </div>

                  {/* AI Analysis Bars */}
                  {clip.ai_analysis && (
                    <div className="space-y-2 pt-2 border-t border-slate-700">
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>Motion</span>
                        <span>{Math.round((clip.ai_analysis.motion_score || 0.5) * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-1.5">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-cyan-500 h-1.5 rounded-full transition-all duration-700"
                          style={{ width: `${(clip.ai_analysis.motion_score || 0.5) * 100}%` }}
                        />
                      </div>
                      
                      <div className="flex justify-between text-xs text-slate-500">
                        <span>Visual Quality</span>
                        <span>{Math.round((clip.ai_analysis.visual_score || 0.5) * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-1.5">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-1.5 rounded-full transition-all duration-700"
                          style={{ width: `${(clip.ai_analysis.visual_score || 0.5) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons - UPDATED */}
<div className="flex space-x-2">
  <button 
    onClick={() => handleClipPreview(clip)}
    className={`flex-1 text-xs py-2.5 px-3 rounded-lg transition-all flex items-center justify-center space-x-1 ${
      isSelected 
        ? 'bg-blue-600 text-white' 
        : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700'
    }`}
  >
    <Play className="w-3 h-3" />
    <span>{isSelected ? 'Playing' : 'Preview'}</span>
  </button>
  
  <button 
    onClick={() => downloadClip(clip)}
    disabled={downloadingClips.has(clip.clip_id)}
    className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white text-xs py-2.5 px-3 rounded-lg hover:from-green-600 hover:to-green-700 disabled:opacity-50 transition-all flex items-center justify-center space-x-1"
  >
    {downloadingClips.has(clip.clip_id) ? (
      <Loader2 className="w-3 h-3 animate-spin" />
    ) : (
      <Download className="w-3 h-3" />
    )}
                      <span>Download</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

          <div className="bg-slate-800/50 rounded-xl p-6">
  <h4 className="text-lg font-semibold text-white mb-4">📥 Download Actions</h4>
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    <button
      onClick={downloadAllClips}
      disabled={batchDownloading}
      className="p-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
    >
      {batchDownloading ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <Download className="w-5 h-5" />
      )}
      <span>{batchDownloading ? 'Preparing...' : 'Download All Clips'}</span>
    </button>
    
    <button
      onClick={() => window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank')}
      className="p-4 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-lg hover:from-red-700 hover:to-pink-700 transition-all flex items-center justify-center space-x-2"
    >
      <ExternalLink className="w-5 h-5" />
      <span>Original Video</span>
    </button>
    
    <button
      onClick={copyTimestamps}
      disabled={copyingTimestamps}
      className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
    >
      {copyingTimestamps ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <Copy className="w-5 h-5" />
      )}
      <span>{copyingTimestamps ? 'Copying...' : 'Copy Timestamps'}</span>
    </button>
  </div>
  
  <div className="mt-4 p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
    <p className="text-sm text-slate-300">
      💡 <strong>Download Instructions:</strong> Clips will open as YouTube links with timestamps. 
      Use YouTube downloaders like yt-dlp or browser extensions to save them locally.
    </p>
  </div>
</div>

      {/* AI Recommendations Panel */}
      <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
        <h4 className="text-lg font-bold text-white mb-4 flex items-center">
          <Star className="w-5 h-5 mr-2 text-yellow-400" />
          🤖 AI Recommendations for Maximum Virality
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h5 className="font-semibold text-purple-300 flex items-center">
              📱 Best for TikTok/Shorts:
            </h5>
            {clips
              .filter(clip => clip.duration <= 60)
              .sort((a, b) => getViralPotential(b) - getViralPotential(a))
              .slice(0, 2)
              .map(clip => (
                <div 
                  key={clip.clip_id} 
                  className="flex items-center space-x-3 bg-purple-500/10 rounded-lg p-3 cursor-pointer hover:bg-purple-500/20 transition-colors"
                  onClick={() => handleClipPreview(clip)}
                >
                  <div className="w-3 h-3 bg-purple-400 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{clip.title}</div>
                    <div className="text-xs text-purple-300">
                      {Math.round(getViralPotential(clip) * 100)}% viral potential • {formatTime(clip.duration)}
                    </div>
                  </div>
                  <Play className="w-4 h-4 text-purple-400" />
                </div>
              ))}
          </div>
          
          <div className="space-y-3">
            <h5 className="font-semibold text-pink-300 flex items-center">
              🚀 Highest Engagement Potential:
            </h5>
            {clips
              .sort((a, b) => getViralPotential(b) - getViralPotential(a))
              .slice(0, 2)
              .map(clip => (
                <div 
                  key={clip.clip_id} 
                  className="flex items-center space-x-3 bg-pink-500/10 rounded-lg p-3 cursor-pointer hover:bg-pink-500/20 transition-colors"
                  onClick={() => handleClipPreview(clip)}
                >
                  <div className="w-3 h-3 bg-pink-400 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{clip.title}</div>
                    <div className="text-xs text-pink-300">
                      {Math.round(getViralPotential(clip) * 100)}% overall score • {clip.type}
                    </div>
                  </div>
                  <Play className="w-4 h-4 text-pink-400" />
                </div>
              ))}
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
          <p className="text-sm text-slate-300">
            💡 <strong>Pro tip:</strong> Click on any clip card to preview it in the video player above. 
            Use "Copy All Timestamps" to get shareable links for all clips!
          </p>
        </div>
      </div>
    </div>
  );
};

export default VideoPreview;