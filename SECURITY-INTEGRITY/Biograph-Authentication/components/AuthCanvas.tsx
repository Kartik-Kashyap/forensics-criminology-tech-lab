// components/AuthCanvas.tsx


import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ClickData, Point } from '../types';

interface AuthCanvasProps {
  mode: 'register' | 'login';
  gridSize: number; // e.g., 4 means 4x4 grid
  onComplete: (clicks: ClickData[], trajectory: Point[], totalTime: number) => void;
  imageUrl: string;
}

const AuthCanvas: React.FC<AuthCanvasProps> = ({ mode, gridSize, onComplete, imageUrl }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [clicks, setClicks] = useState<ClickData[]>([]);
  const [trajectory, setTrajectory] = useState<Point[]>([]);
  const [startTime, setStartTime] = useState<number | null>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  // Load image
  useEffect(() => {
    const img = new Image();
    img.src = imageUrl;
    img.crossOrigin = "Anonymous";
    img.onload = () => setImage(img);
  }, [imageUrl]);

  // Draw Canvas
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !image) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Image
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

    // Draw Grid Overlay
    const cellW = canvas.width / gridSize;
    const cellH = canvas.height / gridSize;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;

    for (let i = 1; i < gridSize; i++) {
      // Vertical
      ctx.beginPath();
      ctx.moveTo(i * cellW, 0);
      ctx.lineTo(i * cellW, canvas.height);
      ctx.stroke();

      // Horizontal
      ctx.beginPath();
      ctx.moveTo(0, i * cellH);
      ctx.lineTo(canvas.width, i * cellH);
      ctx.stroke();
    }

    // Visual Feedback (Only in Register mode or for debug)
    if (mode === 'register') {
      ctx.font = '20px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      clicks.forEach((click, index) => {
        // Draw circle
        ctx.fillStyle = 'rgba(16, 185, 129, 0.8)'; // Emerald 500
        ctx.beginPath();
        ctx.arc(click.x, click.y, 15, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw number
        ctx.fillStyle = 'white';
        ctx.fillText((index + 1).toString(), click.x, click.y);

        // Draw connecting lines
        if (index > 0) {
            const prev = clicks[index - 1];
            ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(click.x, click.y);
            ctx.stroke();
        }
      });
    } else {
        // Login mode - maybe show a fleeting ripple?
        // For security, strict graphical passwords often don't show markers to prevent shoulder surfing
        // But for UX, a tiny flash is helpful.
        // We will leave it blank for strict security simulation, or just render the last click briefly.
        if (clicks.length > 0) {
            const lastClick = clicks[clicks.length - 1];
            ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.beginPath();
            ctx.arc(lastClick.x, lastClick.y, 10, 0, Math.PI * 2);
            ctx.fill();
        }
    }

  }, [image, gridSize, clicks, mode]);

  useEffect(() => {
    draw();
  }, [draw]);

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!startTime) setStartTime(Date.now());
    
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const t = Date.now();

    const cellW = canvas.width / gridSize;
    const cellH = canvas.height / gridSize;

    const col = Math.floor(x / cellW);
    const row = Math.floor(y / cellH);
    const gridIndex = row * gridSize + col;

    const newClick: ClickData = {
      seqIndex: clicks.length,
      gridIndex,
      x,
      y,
      t
    };

    const newClicks = [...clicks, newClick];
    setClicks(newClicks);

    // Auto-submit after sequence length of 4 (configurable, but hardcoded for demo simplicity)
    if (newClicks.length === 4) {
      const finalTime = t - (startTime || t);
      // Small delay to let user see the last click
      setTimeout(() => {
          onComplete(newClicks, trajectory, finalTime);
      }, 300);
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!startTime) return; // Don't track if not started authentication

    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    
    setTrajectory(prev => [
      ...prev,
      {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        t: Date.now()
      }
    ]);
  };

  const reset = () => {
    setClicks([]);
    setTrajectory([]);
    setStartTime(null);
    draw();
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="relative rounded-xl overflow-hidden shadow-2xl border-4 border-slate-700 bg-slate-800">
        <canvas
          ref={canvasRef}
          width={500}
          height={500}
          className="cursor-crosshair active:cursor-grabbing touch-none"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
        />
        {/* Loading Overlay */}
        {!image && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-900 text-white">
                Loading Image...
            </div>
        )}
      </div>
      
      <div className="flex space-x-4">
        <button 
            onClick={reset}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-md font-mono text-sm transition-colors"
        >
            RESET SEQUENCE
        </button>
      </div>

      <p className="text-slate-400 text-sm font-mono mt-2">
        {mode === 'register' ? 'Click 4 points to set your pattern.' : 'Replicate your pattern.'}
        {clicks.length > 0 && ` (${clicks.length}/4)`}
      </p>
    </div>
  );
};

export default AuthCanvas;