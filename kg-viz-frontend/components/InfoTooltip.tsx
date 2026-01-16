'use client';

import { useState, useRef, useEffect } from 'react';
import { Info } from 'lucide-react';

interface InfoTooltipProps {
  content: string;
  className?: string;
}

export default function InfoTooltip({ content, className = '' }: InfoTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState<{ left?: number; right?: number; top: number }>({ top: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isVisible && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      const tooltipWidth = 320; // 80 * 4 (w-80)

      // Estimate tooltip height based on content length (rough approximation)
      // Average ~40 characters per line, ~20px per line, plus padding
      const estimatedHeight = Math.ceil(content.length / 40) * 20 + 32;

      // Calculate position
      const newPosition: { left?: number; right?: number; top: number } = {
        top: rect.top
      };

      // Check if tooltip would overflow bottom of viewport
      if (rect.top + estimatedHeight + 16 > viewportHeight) {
        // Position above the icon
        newPosition.top = rect.top - estimatedHeight - 8;
        // Ensure it doesn't go off the top
        if (newPosition.top < 8) {
          newPosition.top = 8;
        }
      }

      // If tooltip would go off right side of screen, show on left
      if (rect.right + tooltipWidth + 24 > viewportWidth) {
        newPosition.right = viewportWidth - rect.left + 8;
      } else {
        newPosition.left = rect.right + 8;
      }

      setPosition(newPosition);
    }
  }, [isVisible, content]);

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        ref={buttonRef}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="text-slate-500 hover:text-slate-700 transition-colors focus:outline-none"
        type="button"
      >
        <Info className="w-4 h-4" />
      </button>

      {isVisible && (
        <div
          className="fixed w-80 p-4 bg-slate-900 text-white text-sm rounded-lg shadow-2xl pointer-events-none"
          style={{
            zIndex: 9999,
            top: `${position.top}px`,
            left: position.left !== undefined ? `${position.left}px` : undefined,
            right: position.right !== undefined ? `${position.right}px` : undefined
          }}
        >
          <div className="relative leading-relaxed">
            {content}
          </div>
        </div>
      )}
    </div>
  );
}
