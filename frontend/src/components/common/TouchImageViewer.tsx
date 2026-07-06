/**
 * Touch Image Viewer Component
 * Requirements: 21.6
 * 
 * Image viewer with touch gesture support for zoom and pan
 */

import React, { useRef } from 'react';
import { useTouchGestures } from '../../hooks/useTouchGestures';

interface TouchImageViewerProps {
  src: string;
  alt: string;
  className?: string;
  showControls?: boolean;
  onClose?: () => void;
}

export const TouchImageViewer: React.FC<TouchImageViewerProps> = ({
  src,
  alt,
  className = '',
  showControls = true,
  onClose
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  const {
    gestureState,
    handlers,
    getTransformStyle,
    resetGestures
  } = useTouchGestures({
    minScale: 1,
    maxScale: 4,
    onZoomChange: (scale) => {
      console.log('Zoom level:', scale);
    }
  });

  const handleReset = () => {
    resetGestures();
  };

  return (
    <div className={`relative ${className}`}>
      {/* Controls */}
      {showControls && (
        <div className="absolute top-4 right-4 z-10 flex gap-2">
          {gestureState.scale > 1 && (
            <button
              onClick={handleReset}
              className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Reset zoom"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
                />
              </svg>
            </button>
          )}
          
          {onClose && (
            <button
              onClick={onClose}
              className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Close viewer"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>
      )}

      {/* Zoom indicator */}
      {gestureState.scale > 1 && (
        <div className="absolute top-4 left-4 z-10 bg-black bg-opacity-50 text-white px-3 py-1 rounded-lg text-sm">
          {Math.round(gestureState.scale * 100)}%
        </div>
      )}

      {/* Image container */}
      <div
        ref={containerRef}
        className="overflow-hidden relative bg-gray-100 dark:bg-gray-900 rounded-lg"
        style={{ touchAction: 'none' }}
      >
        <img
          src={src}
          alt={alt}
          className="w-full h-auto select-none"
          style={getTransformStyle()}
          draggable={false}
          {...handlers}
        />
      </div>

      {/* Instructions */}
      {showControls && gestureState.scale === 1 && (
        <div className="mt-2 text-center text-sm text-gray-500 dark:text-gray-400">
          Pinch to zoom • Drag to pan
        </div>
      )}
    </div>
  );
};

export default TouchImageViewer;
