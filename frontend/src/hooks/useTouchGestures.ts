/**
 * Touch Gestures Hook
 * Requirements: 21.6
 * 
 * Implements touch gestures for image zoom and pan on mobile devices
 */

import { useState, useEffect, useRef, TouchEvent } from 'react';

interface TouchGestureState {
  scale: number;
  positionX: number;
  positionY: number;
  isDragging: boolean;
}

interface UseTouchGesturesOptions {
  minScale?: number;
  maxScale?: number;
  onZoomChange?: (scale: number) => void;
}

export const useTouchGestures = (options: UseTouchGesturesOptions = {}) => {
  const {
    minScale = 1,
    maxScale = 4,
    onZoomChange
  } = options;

  const [gestureState, setGestureState] = useState<TouchGestureState>({
    scale: 1,
    positionX: 0,
    positionY: 0,
    isDragging: false
  });

  const lastTouchDistance = useRef<number>(0);
  const lastTouchCenter = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const lastPosition = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  /**
   * Calculate distance between two touch points
   */
  const getTouchDistance = (touch1: Touch, touch2: Touch): number => {
    const dx = touch1.clientX - touch2.clientX;
    const dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  };

  /**
   * Calculate center point between two touches
   */
  const getTouchCenter = (touch1: Touch, touch2: Touch): { x: number; y: number } => {
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  };

  /**
   * Handle touch start
   */
  const handleTouchStart = (e: TouchEvent) => {
    if (e.touches.length === 2) {
      // Pinch zoom start
      const distance = getTouchDistance(e.touches[0], e.touches[1]);
      lastTouchDistance.current = distance;
      lastTouchCenter.current = getTouchCenter(e.touches[0], e.touches[1]);
    } else if (e.touches.length === 1 && gestureState.scale > 1) {
      // Pan start (only when zoomed in)
      setGestureState(prev => ({ ...prev, isDragging: true }));
      lastPosition.current = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY
      };
    }
  };

  /**
   * Handle touch move
   */
  const handleTouchMove = (e: TouchEvent) => {
    if (e.touches.length === 2) {
      // Pinch zoom
      e.preventDefault();
      
      const distance = getTouchDistance(e.touches[0], e.touches[1]);
      const center = getTouchCenter(e.touches[0], e.touches[1]);
      
      if (lastTouchDistance.current > 0) {
        const scaleChange = distance / lastTouchDistance.current;
        const newScale = Math.max(minScale, Math.min(maxScale, gestureState.scale * scaleChange));
        
        setGestureState(prev => ({
          ...prev,
          scale: newScale
        }));

        if (onZoomChange) {
          onZoomChange(newScale);
        }
      }
      
      lastTouchDistance.current = distance;
      lastTouchCenter.current = center;
    } else if (e.touches.length === 1 && gestureState.isDragging && gestureState.scale > 1) {
      // Pan
      e.preventDefault();
      
      const deltaX = e.touches[0].clientX - lastPosition.current.x;
      const deltaY = e.touches[0].clientY - lastPosition.current.y;
      
      setGestureState(prev => ({
        ...prev,
        positionX: prev.positionX + deltaX,
        positionY: prev.positionY + deltaY
      }));
      
      lastPosition.current = {
        x: e.touches[0].clientX,
        y: e.touches[0].clientY
      };
    }
  };

  /**
   * Handle touch end
   */
  const handleTouchEnd = (e: TouchEvent) => {
    if (e.touches.length < 2) {
      lastTouchDistance.current = 0;
    }
    
    if (e.touches.length === 0) {
      setGestureState(prev => ({ ...prev, isDragging: false }));
      
      // Reset position if zoomed out
      if (gestureState.scale === 1) {
        setGestureState(prev => ({
          ...prev,
          positionX: 0,
          positionY: 0
        }));
      }
    }
  };

  /**
   * Reset gesture state
   */
  const resetGestures = () => {
    setGestureState({
      scale: 1,
      positionX: 0,
      positionY: 0,
      isDragging: false
    });
    lastTouchDistance.current = 0;
  };

  /**
   * Get transform style for the element
   */
  const getTransformStyle = (): React.CSSProperties => {
    return {
      transform: `translate(${gestureState.positionX}px, ${gestureState.positionY}px) scale(${gestureState.scale})`,
      transition: gestureState.isDragging ? 'none' : 'transform 0.2s ease-out',
      touchAction: 'none'
    };
  };

  return {
    gestureState,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd
    },
    getTransformStyle,
    resetGestures
  };
};
