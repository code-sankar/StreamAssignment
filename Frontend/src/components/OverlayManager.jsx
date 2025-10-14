import React, { useState } from 'react';

const OverlayManager = ({ 
  overlays, 
  activeOverlays, 
  onCreateOverlay, 
  onUpdateOverlay, 
  onDeleteOverlay, 
  onToggleOverlay 
}) => {
  const [showForm, setShowForm] = useState(false);
  const [editingOverlay, setEditingOverlay] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'text',
    content: '',
    position: { x: 50, y: 50 },
    size: { width: 200, height: 50 }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (editingOverlay) {
      onUpdateOverlay(editingOverlay._id, formData);
    } else {
      onCreateOverlay(formData);
    }
    
    resetForm();
  };

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'text',
      content: '',
      position: { x: 50, y: 50 },
      size: { width: 200, height: 50 }
    });
    setEditingOverlay(null);
    setShowForm(false);
  };

  const handleEdit = (overlay) => {
    setFormData({
      name: overlay.name,
      type: overlay.type,
      content: overlay.content,
      position: overlay.position,
      size: overlay.size
    });
    setEditingOverlay(overlay);
    setShowForm(true);
  };

  const handleToggle = (overlayId) => {
    onToggleOverlay(overlayId);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900">Overlay Manager</h2>
        <button 
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Add Overlay'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Enter overlay name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({...formData, type: e.target.value, content: ''})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="text">Text</option>
                <option value="image">Image</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {formData.type === 'text' ? 'Text Content' : 'Image URL'}
              </label>
              {formData.type === 'text' ? (
                <input
                  type="text"
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter text content"
                  required
                />
              ) : (
                <input
                  type="url"
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter image URL"
                  required
                />
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Position X: {formData.position.x}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.position.x}
                  onChange={(e) => setFormData({
                    ...formData, 
                    position: {...formData.position, x: parseInt(e.target.value)}
                  })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Position Y: {formData.position.y}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.position.y}
                  onChange={(e) => setFormData({
                    ...formData, 
                    position: {...formData.position, y: parseInt(e.target.value)}
                  })}
                  className="w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Width (px)</label>
                <input
                  type="number"
                  value={formData.size.width}
                  onChange={(e) => setFormData({
                    ...formData, 
                    size: {...formData.size, width: parseInt(e.target.value)}
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="10"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Height (px)</label>
                <input
                  type="number"
                  value={formData.size.height}
                  onChange={(e) => setFormData({
                    ...formData, 
                    size: {...formData.size, height: parseInt(e.target.value)}
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="10"
                  required
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button 
                type="submit" 
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                {editingOverlay ? 'Update' : 'Create'} Overlay
              </button>
              <button 
                type="button" 
                onClick={resetForm}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      <div className="space-y-3">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Saved Overlays ({overlays.length})</h3>
        {overlays.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No overlays created yet</p>
        ) : (
          overlays.map(overlay => (
            <div 
              key={overlay._id} 
              className="overlay-item p-4 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="font-medium text-gray-900">{overlay.name}</h4>
                  <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full capitalize">
                    {overlay.type}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleToggle(overlay._id)}
                    className={`px-3 py-1 text-xs rounded-md ${
                      activeOverlays.includes(overlay._id)
                        ? 'bg-green-100 text-green-800 hover:bg-green-200'
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                    }`}
                  >
                    {activeOverlays.includes(overlay._id) ? 'Active' : 'Show'}
                  </button>
                  <button
                    onClick={() => handleEdit(overlay)}
                    className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDeleteOverlay(overlay._id)}
                    className="px-3 py-1 text-xs bg-red-100 text-red-800 rounded-md hover:bg-red-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                {overlay.type === 'text' ? (
                  <span>Text: "{overlay.content}"</span>
                ) : (
                  <span>Image URL: {overlay.content.substring(0, 30)}...</span>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Position: ({overlay.position.x}%, {overlay.position.y}%) | 
                Size: {overlay.size.width}×{overlay.size.height}px
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default OverlayManager;