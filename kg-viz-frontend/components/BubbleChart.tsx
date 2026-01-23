'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { BubbleData } from '@/lib/types';

interface BubbleChartProps {
  data: BubbleData[];
  allData: BubbleData[];
  xLabel: string;
  yLabel: string;
  onBubbleClick: (bubble: BubbleData) => void;
  selectedBubbleId?: string | null;
  xDomain?: [number, number];
  yMedian?: number;
}

// Priority-based color mapping
const PRIORITY_COLORS = {
  high_priority: '#22c55e',  // Green
  on_watch: '#eab308',       // Yellow
  research_gap: '#ec4899'    // Pink
};

// Helper function to capitalize labels properly
function capitalizeLabel(label: string): string {
  const smallWords = new Set(['and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with']);

  return label
    .split(' - ')
    .map(part =>
      part.split(' ')
        .map((word, index) => {
          const lowerWord = word.toLowerCase();
          // Always capitalize first word, otherwise check if it's a small word
          if (index === 0 || !smallWords.has(lowerWord)) {
            return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
          }
          return lowerWord;
        })
        .join(' ')
    )
    .join(' - ');
}

export default function BubbleChart({ data, allData, xLabel, yLabel, onBubbleClick, selectedBubbleId, xDomain, yMedian }: BubbleChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const container = svgRef.current.parentElement;
        if (container) {
          setDimensions({
            width: container.clientWidth,
            height: Math.min(650, container.clientWidth * 0.8) // Increased height for more spacing
          });
        }
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return;

    const { width, height } = dimensions;
    const margin = { top: 40, right: 60, bottom: 100, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scales - use provided xDomain or calculate from data
    let xScaleDomain: [number, number];
    if (xDomain) {
      xScaleDomain = xDomain;
    } else {
      const xValues = data.map(d => d.x);
      const xMin = Math.min(...xValues);
      const xMax = Math.max(...xValues);
      const xPadding = (xMax - xMin) * 0.15;
      xScaleDomain = [Math.max(0, xMin - xPadding), Math.min(100, xMax + xPadding)];
    }

    const xScale = d3.scaleLinear()
      .domain(xScaleDomain)
      .range([0, innerWidth])
      .nice();

    const maxSize = Math.max(...data.map(d => d.size)) || 1;
    const minSize = Math.min(...data.filter(d => d.size > 0).map(d => d.size)) || 0;

    const sizeScale = d3.scaleSqrt()
      .domain([minSize, maxSize])
      .range([20, 80]);

    // Calculate y-axis domain with padding based on bubble sizes
    const yValues = data.map(d => d.y);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);

    // Find the largest bubble radius in pixels
    const maxRadius = sizeScale(maxSize);

    // Convert pixel radius to data units for y-axis padding
    // Using a rough approximation: radius in pixels / (innerHeight / data range)
    const yPadding = Math.max((yMax - yMin) * 0.2, 0.3); // At least 0.3 padding
    const bubblePadding = (maxRadius / innerHeight) * (yMax - yMin + yPadding * 2);

    const yScale = d3.scaleLinear()
      .domain([Math.max(0, yMin - yPadding - bubblePadding), yMax + yPadding])
      .range([innerHeight, 0])
      .nice();

    // Use priority-based colors for bubbles
    const getColorByPriority = (priority: string) => {
      return PRIORITY_COLORS[priority as keyof typeof PRIORITY_COLORS] || PRIORITY_COLORS.research_gap;
    };

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(5);
    const yAxis = d3.axisLeft(yScale).ticks(5);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#475569');

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis)
      .selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#475569');

    // Axis labels
    g.append('text')
      .attr('class', 'x-label')
      .attr('text-anchor', 'middle')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 50)
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#1e293b')
      .text(xLabel);

    g.append('text')
      .attr('class', 'y-label')
      .attr('text-anchor', 'middle')
      .attr('transform', `rotate(-90)`)
      .attr('x', -innerHeight / 2)
      .attr('y', -50)
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#1e293b')
      .text(yLabel);

    // Median threshold line (if provided)
    if (yMedian !== undefined) {
      g.append('line')
        .attr('class', 'median-line')
        .attr('x1', 0)
        .attr('x2', innerWidth)
        .attr('y1', yScale(yMedian))
        .attr('y2', yScale(yMedian))
        .attr('stroke', '#64748b')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.6);

      // Median label
      g.append('text')
        .attr('x', innerWidth + 5)
        .attr('y', yScale(yMedian))
        .attr('dy', '0.35em')
        .style('font-size', '11px')
        .style('fill', '#64748b')
        .style('font-weight', '600')
        .text('Median');
    }

    // Bubbles
    const bubbleGroups = g.selectAll('.bubble')
      .data(data.filter(d => d.size > 0), (d: any) => d.id)
      .enter()
      .append('g')
      .attr('class', 'bubble')
      .attr('transform', d => `translate(${xScale(d.x)},${yScale(d.y)})`)
      .style('cursor', 'pointer');

    // Circles
    bubbleGroups.append('circle')
      .attr('r', d => sizeScale(d.size))
      .attr('fill', d => d.color || getColorByPriority(d.priority))
      .attr('opacity', d => {
        if (!selectedBubbleId) return 0.75;
        return d.id === selectedBubbleId ? 0.95 : 0.2;
      })
      .attr('stroke', d => selectedBubbleId === d.id ? '#1e293b' : '#64748b')
      .attr('stroke-width', d => selectedBubbleId === d.id ? 3 : 1)
      .on('click', (_event, d) => onBubbleClick(d))
      .on('mouseenter', function(_event, d) {
        if (!selectedBubbleId || d.id === selectedBubbleId) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('opacity', 1)
            .attr('stroke-width', 4);
        }
      })
      .on('mouseleave', function(_event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('opacity', () => {
            if (!selectedBubbleId) return 0.75;
            return d.id === selectedBubbleId ? 0.95 : 0.2;
          })
          .attr('stroke-width', d.id === selectedBubbleId ? 3 : 1);
      });

    // Labels below bubbles
    bubbleGroups.append('text')
      .attr('class', 'bubble-label')
      .attr('text-anchor', 'middle')
      .attr('y', d => sizeScale(d.size) + 20)
      .style('font-size', '11px')
      .style('font-weight', '600')
      .style('fill', '#1e293b')
      .style('pointer-events', 'none')
      .text(d => {
        const parts = d.label.split(' - ');
        const shortLabel = parts.length > 1 ? parts[1] : d.label;
        return capitalizeLabel(shortLabel);
      })
      .attr('opacity', d => {
        if (!selectedBubbleId) return 1;
        return d.id === selectedBubbleId ? 1 : 0.3;
      });

    // Tooltips
    bubbleGroups.append('title')
      .text(d => `${d.label}\n${d.paper_count} papers\nClick for details`);

  }, [data, dimensions, xLabel, yLabel, onBubbleClick, selectedBubbleId, xDomain, yMedian]);

  return (
    <div className="w-full h-full flex items-center justify-center">
      <svg ref={svgRef} className="w-full" />
    </div>
  );
}
