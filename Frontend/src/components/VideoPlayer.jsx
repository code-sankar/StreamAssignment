import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const VideoPlayer = ({ rtspUrl, overlays, isPlaying, onPlay, onPause }) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const videoNode = useRef(null);

  useEffect(() => {
    // Initialize Video.js player
    if (videoNode.current && !playerRef.current) {
      playerRef.current = videojs(videoNode.current, {
        controls: true,
        responsive: true,
        fluid: true,
        liveui: true,
        preload: 'auto'
      });

      playerRef.current.on('play', onPlay);
      playerRef.current.on('pause', onPause);
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (playerRef.current && rtspUrl && isPlaying) {
      // Convert RTSP to a format that browsers can play
      // Note: In production, you need a server to convert RTSP to HLS/DASH
      const playableUrl = convertToPlayableUrl(rtspUrl);
      
      playerRef.current.src({
        src: playableUrl,
        type: getStreamType(playableUrl)
      });
      
      playerRef.current.play().catch(error => {
        console.error('Error playing video:', error);
      });
    }
  }, [rtspUrl, isPlaying]);

  const convertToPlayableUrl = (url) => {
    // For demo purposes, using a test HLS stream
    // In production, implement RTSP to HLS conversion on the server
    if (url.includes('rtsp://')) {
      // Return a test HLS stream for demonstration
      return 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8';
    }
    return url;
  };

  const getStreamType = (url) => {
    if (url.includes('.m3u8')) return 'application/x-mpegURL';
    if (url.includes('.mpd')) return 'application/dash+xml';
    if (url.includes('.mp4')) return 'video/mp4';
    return 'video/mp4';
  };

  return (
    <div className="relative">
      <div data-vjs-player>
        <video
          ref={videoNode}
          className="video-js vjs-default-skin vjs-big-play-centered"
          playsInline
        />
      </div>
      
      {/* Overlays */}
      <div className="absolute inset-0 pointer-events-none">
        {overlays.map(overlay => (
          <div
            key={overlay._id}
            className="absolute pointer-events-none"
            style={{
              left: `${overlay.position.x}%`,
              top: `${overlay.position.y}%`,
              width: `${overlay.size.width}px`,
              height: `${overlay.size.height}px`,
              transform: 'translate(-50%, -50%)'
            }}
          >
            {overlay.type === 'text' ? (
              <div 
                className="text-overlay w-full h-full flex items-center justify-center bg-black bg-opacity-50 text-white p-2 rounded"
                style={{
                  fontSize: Math.min(overlay.size.width / 10, 24) + 'px',
                  fontWeight: 'bold'
                }}
              >
                {overlay.content}
              </div>
            ) : (
              <img 
                src={overlay.content} 
                alt="Overlay" 
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VideoPlayer;