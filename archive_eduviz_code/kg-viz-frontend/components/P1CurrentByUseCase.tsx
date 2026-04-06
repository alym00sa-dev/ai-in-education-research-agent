'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { P1CurrentByCaseResponse, P1CurrentUseCaseLadder } from '@/lib/types';

interface P1CurrentByUseCaseProps {
  data: P1CurrentByCaseResponse;
  onUseCaseClick?: (useCase: P1CurrentUseCaseLadder) => void;
}

export default function P1CurrentByUseCase({ data, onUseCaseClick }: P1CurrentByUseCaseProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1400, height: 600 });

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
    const margin = { top: 30, right: 40, bottom: 60, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const useCases = data.use_case_ladders;
    const ladderWidth = innerWidth / useCases.length;
    const rungHeight = innerHeight / 6; // 6 rungs

    // Color scale for rungs
    const colorScale = d3.scaleSequential()
      .domain([1, 6])
      .interpolator(d3.interpolateViridis);

    // Size scale for bubbles
    const maxPapers = d3.max(useCases.flatMap(uc => uc.rungs.map(r => r.paper_count))) || 1;
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxPapers])
      .range([0, Math.min(ladderWidth * 0.3, 40)]);

    // Draw each use case ladder
    useCases.forEach((useCase, useCaseIndex) => {
      const xOffset = useCaseIndex * ladderWidth;
      const ladderCenterX = xOffset + ladderWidth / 2;

      // Use case label at bottom
      g.append('text')
        .attr('x', ladderCenterX)
        .attr('y', innerHeight + 30)
        .attr('text-anchor', 'middle')
        .style('font-size', '13px')
        .style('font-weight', '700')
        .style('fill', '#1e293b')
        .text(useCase.use_case_label);

      // Draw rungs from top (6) to bottom (1)
      const reversedRungs = [...useCase.rungs].reverse();

      reversedRungs.forEach((rung, rungIndex) => {
        const yPos = rungIndex * rungHeight + rungHeight / 2;
        const rungColor = colorScale(rung.rung_number);

        // Rung bar
        g.append('rect')
          .attr('x', xOffset + ladderWidth * 0.2)
          .attr('y', yPos - 2)
          .attr('width', ladderWidth * 0.6)
          .attr('height', 4)
          .attr('fill', '#cbd5e1')
          .attr('opacity', 0.3)
          .attr('rx', 2);

        // Bubble for paper count
        if (rung.paper_count > 0) {
          const bubbleRadius = sizeScale(rung.paper_count);

          const bubble = g.append('g')
            .attr('transform', `translate(${ladderCenterX},${yPos})`)
            .style('cursor', 'pointer')
            .on('click', () => {
              if (onUseCaseClick) {
                onUseCaseClick(useCase);
              }
            });

          bubble.append('circle')
            .attr('r', bubbleRadius)
            .attr('fill', rungColor)
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 1.5)
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
            .style('font-size', bubbleRadius > 15 ? '12px' : '10px')
            .style('font-weight', '700')
            .style('fill', 'white')
            .style('pointer-events', 'none')
            .text(rung.paper_count);
        } else {
          // Show 0 for empty rungs
          g.append('text')
            .attr('x', ladderCenterX)
            .attr('y', yPos)
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('font-size', '10px')
            .style('fill', '#cbd5e1')
            .text('0');
        }
      });

      // Vertical rail (light connecting line)
      g.append('line')
        .attr('x1', ladderCenterX)
        .attr('x2', ladderCenterX)
        .attr('y1', rungHeight / 2)
        .attr('y2', innerHeight - rungHeight / 2)
        .attr('stroke', '#e2e8f0')
        .attr('stroke-width', 2)
        .attr('opacity', 0.4);
    });

    // Rung labels on the left
    const rungLabels = ['R6', 'R5', 'R4', 'R3', 'R2', 'R1'];
    rungLabels.forEach((label, i) => {
      const yPos = i * rungHeight + rungHeight / 2;
      g.append('text')
        .attr('x', -10)
        .attr('y', yPos)
        .attr('text-anchor', 'end')
        .attr('dy', '0.35em')
        .style('font-size', '11px')
        .style('font-weight', '600')
        .style('fill', '#64748b')
        .text(label);
    });

  }, [data, dimensions, onUseCaseClick]);

  return (
    <div className="flex flex-col w-full h-full">
      {/* Visualization */}
      <div ref={containerRef} className="flex-1 w-full">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
