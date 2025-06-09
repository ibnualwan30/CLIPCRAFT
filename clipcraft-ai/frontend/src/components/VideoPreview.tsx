// File: frontend/src/components/VideoPreview.tsx
// Buat file baru untuk video preview

import React, { useState } from 'react';
import { Play, Download, Clock, TrendingUp, Star, Grid, List } from 'lucide-react';

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
    
    return Math.min(1.0, baseScore + motionBonus + visualBonus + typeBonus);
  };

  return (
    <div className="space-y-6">
      {/* Video Info Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white mb-3">
              🎉 Processing Complete!
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
              <div className="w-48 h-28 bg-slate-700 rounded-lg overflow-hidden border border-slate-600">
                <img
                  src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                  alt="Video thumbnail"
                  className="w-full h-full object-cover"
                />
              </div>
              <p className="text-xs text-slate-400 mt-2 text-center">Original Video</p>
            </div>
          )}
        </div>
      </div>

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
        
        {/* View Toggle */}
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

      {/* Clips Display */}
      <div className={
        viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
      }>
        {clips.map((clip, index) => {
          const viralPotential = getViralPotential(clip);
          
          return (
            <div
              key={clip.clip_id}
              className="group bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 transform hover:-translate-y-1"
            >
              {/* Clip Thumbnail/Preview */}
              <div className="relative">
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
                  <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
                      <Play className="w-6 h-6 text-white" />
                    </div>
                  </div>
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

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <button className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs py-2.5 px-3 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all flex items-center justify-center space-x-1">
                    <Play className="w-3 h-3" />
                    <span>Preview</span>
                  </button>
                  <button className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white text-xs py-2.5 px-3 rounded-lg hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center space-x-1">
                    <Download className="w-3 h-3" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
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
                <div key={clip.clip_id} className="flex items-center space-x-3 bg-purple-500/10 rounded-lg p-3">
                  <div className="w-3 h-3 bg-purple-400 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{clip.title}</div>
                    <div className="text-xs text-purple-300">
                      {Math.round(getViralPotential(clip) * 100)}% viral potential • {formatTime(clip.duration)}
                    </div>
                  </div>
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
                <div key={clip.clip_id} className="flex items-center space-x-3 bg-pink-500/10 rounded-lg p-3">
                  <div className="w-3 h-3 bg-pink-400 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{clip.title}</div>
                    <div className="text-xs text-pink-300">
                      {Math.round(getViralPotential(clip) * 100)}% overall score • {clip.type}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20">
          <p className="text-sm text-slate-300">
            💡 <strong>Pro tip:</strong> Clips with high motion scores and short duration (&lt;60s) tend to perform best on social media platforms.
          </p>
        </div>
      </div>
    </div>
  );
};

export default VideoPreview;