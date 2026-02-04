'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { P1CurrentResponse, P1CurrentRung } from '@/lib/types';

interface P1CurrentEvidenceLadderProps {
  data: P1CurrentResponse;
  onRungClick?: (rung: P1CurrentRung) => void;
}

export default function P1CurrentEvidenceLadder({ data, onRungClick }: P1CurrentEvidenceLadderProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1200, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !data) return;

    const { width, height } = dimensions;
    const margin = { top: 30, right: 200, bottom: 40, left: 200 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Define ladder rungs (top to bottom: Rung 6 → Rung 1)
    const rungs = [...data.rungs].reverse(); // Display from top (6) to bottom (1)

    const rungHeight = innerHeight / rungs.length;

    // Y positions for each rung
    const yScale = d3.scaleLinear()
      .domain([0, rungs.length - 1])
      .range([0, innerHeight - rungHeight]);

    // Size scale for bubbles (based on paper count)
    const maxPapers = d3.max(rungs, r => r.paper_count) || 1;
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxPapers])
      .range([0, 60]);

    // Color scale for rungs
    const colorScale = d3.scaleSequential()
      .domain([1, 6])
      .interpolator(d3.interpolateViridis);

    // Draw vertical ladder rails
    const railWidth = 4;
    const railX1 = innerWidth * 0.45;
    const railX2 = innerWidth * 0.55;

    g.append('rect')
      .attr('x', railX1)
      .attr('y', 0)
      .attr('width', railWidth)
      .attr('height', innerHeight)
      .attr('fill', '#cbd5e1')
      .attr('opacity', 0.5);

    g.append('rect')
      .attr('x', railX2)
      .attr('y', 0)
      .attr('width', railWidth)
      .attr('height', innerHeight)
      .attr('fill', '#cbd5e1')
      .attr('opacity', 0.5);

    // Draw rungs
    rungs.forEach((rung, i) => {
      const yPos = yScale(i) + rungHeight / 2;
      const rungColor = colorScale(rung.rung_number);

      // Horizontal rung bar
      g.append('rect')
        .attr('x', railX1)
        .attr('y', yPos - 3)
        .attr('width', railX2 - railX1 + railWidth)
        .attr('height', 6)
        .attr('fill', '#94a3b8')
        .attr('rx', 3);

      // Rung label on the left
      const rungLabel = g.append('g')
        .attr('transform', `translate(${railX1 - 20},${yPos})`);

      rungLabel.append('text')
        .attr('text-anchor', 'end')
        .attr('dy', '0.35em')
        .style('font-size', '18px')
        .style('font-weight', '700')
        .style('fill', '#1e293b')
        .text(`Rung ${rung.rung_number}`);

      rungLabel.append('text')
        .attr('text-anchor', 'end')
        .attr('y', 18)
        .style('font-size', '14px')
        .style('font-weight', '600')
        .style('fill', '#475569')
        .text(rung.rung_name);

      // Description on the right
      const descWords = rung.description.split(' ');
      const maxWordsPerLine = 10;
      const lines = [];
      for (let j = 0; j < descWords.length; j += maxWordsPerLine) {
        lines.push(descWords.slice(j, j + maxWordsPerLine).join(' '));
      }

      const descGroup = g.append('g')
        .attr('transform', `translate(${railX2 + railWidth + 20},${yPos - (lines.length * 6)})`);

      lines.forEach((line, lineIndex) => {
        descGroup.append('text')
          .attr('text-anchor', 'start')
          .attr('y', lineIndex * 12)
          .style('font-size', '11px')
          .style('fill', '#64748b')
          .text(line);
      });

      // Bubble for paper count
      if (rung.paper_count > 0) {
        const bubbleRadius = sizeScale(rung.paper_count);

        const bubble = g.append('g')
          .attr('transform', `translate(${innerWidth / 2},${yPos})`)
          .style('cursor', 'pointer')
          .on('click', () => {
            if (onRungClick) {
              onRungClick(rung);
            }
          });

        bubble.append('circle')
          .attr('r', bubbleRadius)
          .attr('fill', rungColor)
          .attr('stroke', '#1e293b')
          .attr('stroke-width', 2)
          .style('opacity', 0.85)
          .on('mouseover', function() {
            d3.select(this)
              .transition()
              .duration(200)
              .attr('r', bubbleRadius * 1.2)
              .style('opacity', 1);
          })
          .on('mouseout', function() {
            d3.select(this)
              .transition()
              .duration(200)
              .attr('r', bubbleRadius)
              .style('opacity', 0.85);
          });

        // Paper count inside bubble
        bubble.append('text')
          .attr('text-anchor', 'middle')
          .attr('dy', '0.35em')
          .style('font-size', bubbleRadius > 25 ? '16px' : '12px')
          .style('font-weight', '700')
          .style('fill', 'white')
          .style('pointer-events', 'none')
          .text(rung.paper_count);
      } else {
        // Show "0" for empty rungs
        g.append('text')
          .attr('x', innerWidth / 2)
          .attr('y', yPos)
          .attr('text-anchor', 'middle')
          .attr('dy', '0.35em')
          .style('font-size', '14px')
          .style('fill', '#94a3b8')
          .text('0');
      }
    });

    // No title needed

  }, [data, dimensions, onRungClick]);

  return (
    <div className="flex flex-col w-full h-full">
      {/* Visualization */}
      <div ref={containerRef} className="flex-1 w-full">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
