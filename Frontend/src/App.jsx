import React, { useState, useEffect } from 'react';
import axios from 'axios';
import VideoPlayer from './components/VideoPlayer';
import OverlayManager from './components/OverlayManager';

const API_BASE = 'https://streamassignment.onrender.com/api';

function App() {
  const [overlays, setOverlays] = useState([]);
  const [rtspUrl, setRtspUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeOverlays, setActiveOverlays] = useState([]);

  // Load overlays from backend
  const loadOverlays = async () => {
    try {
      const response = await axios.get(`${API_BASE}overlays`);
      setOverlays(response.data);
    } catch (error) {
      console.error('Error loading overlays:', error);
    }
  };

  useEffect(() => {
    loadOverlays();
  }, []);

  const handleCreateOverlay = async (overlayData) => {
    try {
      await axios.post(`${API_BASE}/overlays`, overlayData);
      loadOverlays();
    } catch (error) {
      console.error('Error creating overlay:', error);
      alert('Error creating overlay: ' + error.response?.data?.error || error.message);
    }
  };

  const handleUpdateOverlay = async (id, overlayData) => {
    try {
      await axios.put(`${API_BASE}/overlays/${id}`, overlayData);
      loadOverlays();
    } catch (error) {
      console.error('Error updating overlay:', error);
      alert('Error updating overlay: ' + error.response?.data?.error || error.message);
    }
  };

  const handleDeleteOverlay = async (id) => {
    try {
      await axios.delete(`${API_BASE}/overlays/${id}`);
      loadOverlays();
      // Remove from active overlays if it was active
      setActiveOverlays(prev => prev.filter(overlayId => overlayId !== id));
    } catch (error) {
      console.error('Error deleting overlay:', error);
      alert('Error deleting overlay: ' + error.response?.data?.error || error.message);
    }
  };

  const toggleOverlay = (overlayId) => {
    setActiveOverlays(prev => 
      prev.includes(overlayId) 
        ? prev.filter(id => id !== overlayId)
        : [...prev, overlayId]
    );
  };

  const getActiveOverlaysData = () => {
    return overlays.filter(overlay => activeOverlays.includes(overlay._id));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">Livestream Video Player</h1>
            <div className="text-sm text-gray-500">
              Stream and manage overlays in real-time
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Video Section - 2/3 width on large screens */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              {/* URL Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RTSP Stream URL
                </label>
                <div className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Enter RTSP URL (e.g., rtsp://your-stream-url)"
                    value={rtspUrl}
                    onChange={(e) => setRtspUrl(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button 
                    onClick={() => rtspUrl && setIsPlaying(true)}
                    disabled={!rtspUrl}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    Load Stream
                  </button>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  For testing, you can use: <code className="bg-gray-100 px-1 rounded">rtsp://your-test-stream</code>
                </p>
              </div>
              
              {/* Video Player */}
              <VideoPlayer
                rtspUrl={rtspUrl}
                overlays={getActiveOverlaysData()}
                isPlaying={isPlaying}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              />

              {/* Active Overlays */}
              {activeOverlays.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Active Overlays</h3>
                  <div className="flex flex-wrap gap-2">
                    {getActiveOverlaysData().map(overlay => (
                      <span
                        key={overlay._id}
                        className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        {overlay.name}
                        <button
                          onClick={() => toggleOverlay(overlay._id)}
                          className="ml-2 text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Overlay Manager Section - 1/3 width on large screens */}
          <div className="lg:col-span-1">
            <OverlayManager
              overlays={overlays}
              activeOverlays={activeOverlays}
              onCreateOverlay={handleCreateOverlay}
              onUpdateOverlay={handleUpdateOverlay}
              onDeleteOverlay={handleDeleteOverlay}
              onToggleOverlay={toggleOverlay}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;