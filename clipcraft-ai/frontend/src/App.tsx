// File: frontend/src/App.tsx
// UPDATE: Perbaikan kecil untuk integrasi dengan VideoPreview yang baru

import React, { useState, useEffect } from 'react';
import { Play, Sparkles, Brain, Scissors, Type, Smartphone, Zap, Palette, CheckCircle, XCircle, Clock } from 'lucide-react';
import VideoPreview from './components/VideoPreview';

const App: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [jobId, setJobId] = useState('');
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState<boolean | null>(null);

  // Handle scroll effect untuk navbar
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Test backend connection on mount - UPDATE: Lebih robust error handling
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('🔗 Testing backend connection...');
        const response = await fetch('http://localhost:8001/api/health');
        
        if (response.ok) {
          const data = await response.json();
          setIsConnected(true);
          console.log('✅ Backend connected successfully:', data.message);
        } else {
          setIsConnected(false);
          console.log('❌ Backend responded with error:', response.status);
        }
      } catch (error) {
        setIsConnected(false);
        console.error('❌ Backend connection failed:', error);
      }
    };
    
    testConnection();
    
    // Re-test connection every 30 seconds if disconnected
    const interval = setInterval(() => {
      if (isConnected === false) {
        testConnection();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Poll job status when processing - UPDATE: Better error handling
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (jobId && isProcessing) {
      console.log('📊 Starting status polling for job:', jobId);
      
      interval = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:8001/api/status/${jobId}`);
          const status = await response.json();
          setJobStatus(status);
          
          console.log(`📈 Job progress: ${status.progress}% - ${status.current_step}`);
          
          if (status.status === 'completed') {
            setIsProcessing(false);
            console.log('🎉 Processing completed successfully!');
            
            // Get final result
            try {
              const resultResponse = await fetch(`http://localhost:8001/api/result/${jobId}`);
              const finalResult = await resultResponse.json();
              setResult(finalResult);
              console.log('📊 Final results received:', finalResult);
              
              // Auto scroll to results after a short delay
              setTimeout(() => {
                const resultsElement = document.getElementById('results');
                if (resultsElement) {
                  resultsElement.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                  });
                }
              }, 1000);
              
            } catch (err) {
              console.error('❌ Failed to get final results:', err);
              setError('Failed to get processing results. Please try again.');
            }
          } else if (status.status === 'failed') {
            setIsProcessing(false);
            const errorMsg = status.error_message || 'Processing failed unexpectedly';
            setError(errorMsg);
            console.error('❌ Processing failed:', errorMsg);
          }
        } catch (err) {
          console.error('❌ Failed to get job status:', err);
          setError('Lost connection to server. Please check if backend is running.');
          setIsProcessing(false);
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
        console.log('🛑 Stopped status polling');
      }
    };
  }, [jobId, isProcessing]);

  // Validate YouTube URL - UPDATE: More comprehensive validation
  const isValidYouTubeUrl = (url: string): boolean => {
    const youtubePatterns = [
      /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
      /^https?:\/\/(www\.)?youtu\.be\/[\w-]+/,
      /^https?:\/\/(m\.)?youtube\.com\/watch\?v=[\w-]+/,
    ];
    return youtubePatterns.some(pattern => pattern.test(url));
  };

  // Handle form submission - UPDATE: Better validation and error messages
  const handleProcessVideo = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset previous state
    setError('');
    setResult(null);
    setJobStatus(null);
    
    // Validation
    if (!youtubeUrl.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }

    if (!isValidYouTubeUrl(youtubeUrl)) {
      setError('Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=...)');
      return;
    }

    if (isConnected === false) {
      setError('Backend server is not available. Please make sure the Python server is running on port 8001.');
      return;
    }

    setIsProcessing(true);
    console.log('🚀 Starting video processing for:', youtubeUrl);
    
    try {
      const response = await fetch(`http://localhost:8001/api/process-video?youtube_url=${encodeURIComponent(youtubeUrl)}&clip_count=5&use_ai_analysis=true&analysis_mode=balanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setJobId(data.job_id);
        console.log('✅ Processing started successfully with job ID:', data.job_id);
      } else {
        const errorMsg = data.detail || data.message || 'Failed to start processing';
        setError(errorMsg);
        setIsProcessing(false);
        console.error('❌ Failed to start processing:', errorMsg);
      }
    } catch (err: any) {
      const errorMsg = 'Failed to connect to server. Please check if the backend is running.';
      setError(errorMsg);
      setIsProcessing(false);
      console.error('❌ Network error:', err);
    }
  };

  // Reset form - UPDATE: Complete state reset
  const resetForm = () => {
    console.log('🔄 Resetting form');
    setYoutubeUrl('');
    setJobId('');
    setJobStatus(null);
    setResult(null);
    setError('');
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Navigation Bar - Tidak ada perubahan */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-slate-900/95 backdrop-blur-md border-b border-slate-800' 
          : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                ClipCraft AI
              </span>
            </div>
            
            {/* Connection Status - UPDATE: More detailed status */}
            <div className="hidden md:flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {isConnected === true ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-green-400">Backend Online</span>
                  </>
                ) : isConnected === false ? (
                  <>
                    <XCircle className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-red-400">Backend Offline</span>
                  </>
                ) : (
                  <>
                    <Clock className="w-4 h-4 text-yellow-400 animate-spin" />
                    <span className="text-sm text-yellow-400">Connecting...</span>
                  </>
                )}
              </div>
            </div>
            
            <button 
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
              onClick={() => window.open('http://localhost:8001/docs', '_blank')}
            >
              API Docs
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Tidak ada perubahan */}
      <section className="min-h-screen flex items-center justify-center px-4 pt-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20"></div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-2 mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-slate-300">Powered by Advanced AI</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
            <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Transform Videos
            </span>
            <br />
            <span className="text-white">into Viral Clips</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto leading-relaxed animate-slide-up">
            Revolutionary AI technology that automatically creates engaging short clips 
            from your YouTube videos. No editing skills required.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up mb-12">
            <button 
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 flex items-center space-x-2"
              onClick={() => document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <Sparkles className="w-5 h-5" />
              <span>Start Creating</span>
            </button>
            
            <button 
              className="border border-slate-600 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-slate-800 transition-all duration-200 flex items-center space-x-2"
              onClick={() => window.open('http://localhost:8001/docs', '_blank')}
            >
              <Play className="w-5 h-5" />
              <span>API Demo</span>
            </button>
          </div>

          <div className="grid grid-cols-3 gap-8 max-w-md mx-auto text-center">
            <div>
              <div className="text-2xl font-bold text-blue-400">Real</div>
              <div className="text-sm text-slate-400">AI Processing</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">Live</div>
              <div className="text-sm text-slate-400">API Backend</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-pink-400">Full</div>
              <div className="text-sm text-slate-400">Stack Demo</div>
            </div>
          </div>
        </div>
      </section>

      {/* Processing Section - UPDATE: Enhanced UI and validation */}
      <section className="py-16 px-4 bg-slate-800/50" id="demo">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent text-center">
            Try Real AI Processing
          </h2>
          
          {/* Connection Status Alert - UPDATE: More helpful messages */}
          {isConnected === false && (
            <div className="mb-6 p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-400 font-semibold">Backend server is not available</span>
              </div>
              <p className="text-sm text-red-300 mt-2">
                Please run: <code className="bg-red-800/30 px-2 py-1 rounded">python main.py</code> in the backend folder
              </p>
            </div>
          )}
          
          {/* Success Connection Message */}
          {isConnected === true && !isProcessing && !result && (
            <div className="mb-6 p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-green-400 font-semibold">Backend connected successfully!</span>
              </div>
              <p className="text-sm text-green-300 mt-2">
                Ready to process videos with AI analysis
              </p>
            </div>
          )}
          
          {/* Input Form - UPDATE: Better placeholder and validation */}
          <form onSubmit={handleProcessVideo} className="space-y-4">
            <div>
              <input
                type="url"
                placeholder="Paste YouTube URL here... (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                disabled={isProcessing || isConnected === false}
              />
              {youtubeUrl && !isValidYouTubeUrl(youtubeUrl) && (
                <p className="text-xs text-red-400 mt-2">
                  Please enter a valid YouTube URL
                </p>
              )}
            </div>
            
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={isProcessing || !youtubeUrl || isConnected === false || !isValidYouTubeUrl(youtubeUrl)}
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 flex items-center justify-center space-x-2"
              >
                {isProcessing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Clips</span>
                  </>
                )}
              </button>
              
              {(jobId || error || result) && (
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-3 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-700 transition-all"
                >
                  Reset
                </button>
              )}
            </div>
          </form>
          
          {/* Error Display - UPDATE: Better error styling */}
          {error && (
            <div className="mt-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="w-5 h-5 text-red-400" />
                <span className="text-red-400 font-semibold">Error</span>
              </div>
              <p className="text-red-300 mt-2">{error}</p>
            </div>
          )}
          
          {/* Job Status - UPDATE: Enhanced progress display */}
          {jobStatus && isProcessing && (
            <div className="mt-6 p-4 bg-slate-700/50 backdrop-blur-sm rounded-lg border border-slate-600">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white">Processing Status</h3>
                <span className="text-sm text-slate-400">Job: {jobStatus.job_id?.slice(0, 8)}...</span>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">{jobStatus.current_step}</span>
                  <span className="text-blue-400 font-semibold">{jobStatus.progress}%</span>
                </div>
                
                <div className="w-full bg-slate-600 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    style={{ width: `${jobStatus.progress}%` }}
                  >
                    {jobStatus.progress > 15 && (
                      <span className="text-xs text-white font-medium">
                        {jobStatus.progress}%
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="text-xs text-slate-400 flex items-center justify-between">
                  <span>Status: <span className={`font-medium ${
                    jobStatus.status === 'completed' ? 'text-green-400' :
                    jobStatus.status === 'failed' ? 'text-red-400' :
                    'text-yellow-400'
                  }`}>{jobStatus.status}</span></span>
                  
                  {jobStatus.estimated_remaining && jobStatus.estimated_remaining > 0 && (
                    <span>~{Math.round(jobStatus.estimated_remaining)}s remaining</span>
                  )}
                </div>

                {/* AI Features Used */}
                {jobStatus.ai_features_enabled && jobStatus.ai_features_enabled.length > 0 && (
                  <div className="text-xs text-slate-400 border-t border-slate-600 pt-2">
                    <div className="flex flex-wrap gap-1">
                      <span className="text-slate-500">AI Features:</span>
                      {jobStatus.ai_features_enabled.map((feature: string) => (
                        <span key={feature} className="bg-slate-600 px-2 py-1 rounded text-xs">
                          {feature.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <p className="text-sm text-slate-400 mt-4 text-center">
            {isConnected ? (
              <>✅ Connected to live backend API • Real AI processing with scene detection</>
            ) : (
              <>❌ Backend disconnected • Start Python server to test</>
            )}
          </p>
        </div>
      </section>

      {/* Results Section - UPDATE: Enhanced integration dengan VideoPreview */}
      {result && (
        <section className="py-16 px-4" id="results">
          <div className="max-w-7xl mx-auto">
            <VideoPreview
              videoInfo={{
                title: result.video_info?.title || "Processed Video",
                duration: result.video_info?.duration || 0,
                views: result.video_info?.views || 0,
                uploader: result.video_info?.uploader || "Unknown"
              }}
              clips={result.clips || []}
              youtubeUrl={youtubeUrl}
            />
          </div>
        </section>
      )}

      {/* Features Section - Tidak ada perubahan */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                Powerful AI Features
              </span>
            </h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Everything you need to create viral content with cutting-edge technology
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: <Brain className="w-12 h-12" />, title: "Smart AI Analysis", description: "Our AI analyzes your video content to identify the most engaging moments automatically." },
              { icon: <Scissors className="w-12 h-12" />, title: "Auto Clip Generation", description: "Generate multiple short clips with perfect timing and smooth transitions." },
              { icon: <Type className="w-12 h-12" />, title: "AI-Powered Subtitles", description: "Automatic subtitle generation with speaker recognition and perfect timing." },
              { icon: <Smartphone className="w-12 h-12" />, title: "Multi-Platform Export", description: "Export clips optimized for TikTok, Instagram Reels, YouTube Shorts." },
              { icon: <Zap className="w-12 h-12" />, title: "Lightning Fast", description: "Advanced cloud infrastructure ensures quick processing with real-time tracking." },
              { icon: <Palette className="w-12 h-12" />, title: "Custom Styling", description: "Customize colors, fonts, transitions to match your brand identity." }
            ].map((feature, index) => (
              <div key={index} className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-blue-500/50 transition-all duration-300 transform hover:-translate-y-2">
                <div className="text-blue-400 mb-4 group-hover:text-blue-300 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3 text-white">{feature.title}</h3>
                <p className="text-slate-300 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer - Tidak ada perubahan */}
      <footer className="border-t border-slate-800 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              ClipCraft AI
            </span>
          </div>
          <p className="text-slate-400">
            &copy; 2025 ClipCraft AI. Made with ❤️ for content creators.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;