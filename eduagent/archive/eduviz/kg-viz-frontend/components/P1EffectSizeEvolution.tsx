'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { P1Response, P1Series, P1DataPoint } from '@/lib/types';

interface P1EffectSizeEvolutionProps {
  data: P1Response;
  onPointClick?: (series: P1Series, point: P1DataPoint) => void;
  onViewModeChange?: (mode: 'interventions' | 'usecases') => void;
}

type ViewMode = 'interventions' | 'usecases';

export default function P1EffectSizeEvolution({ data, onPointClick, onViewModeChange }: P1EffectSizeEvolutionProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1400, height: 700 });
  const [viewMode, setViewMode] = useState<ViewMode>('usecases');

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
    if (onViewModeChange) {
      onViewModeChange(viewMode);
    }
  }, [viewMode, onViewModeChange]);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !data) return;

    const series = viewMode === 'interventions' ? data.intervention_series : data.usecase_series;

    if (!series || series.length === 0) return;

    const { width, height } = dimensions;
    const margin = { top: 40, right: 20, bottom: 100, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Get all data points for scales
    const allPoints = series.flatMap(s => s.data_points || []);

    if (allPoints.length === 0) {
      g.append('text')
        .attr('x', innerWidth / 2)
        .attr('y', innerHeight / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('fill', '#64748b')
        .text('No data available');
      return;
    }

    // X scale (years)
    const allYears = allPoints.map(d => d.year);
    const minYear = Math.min(...allYears);
    const maxYear = Math.max(...allYears);

    const xScale = d3.scaleLinear()
      .domain([minYear - 1, maxYear + 1])
      .range([0, innerWidth]);

    // Y scale (effect size)
    const allEffects = allPoints.map(d => d.effect_size);
    const minEffect = Math.min(...allEffects);
    const maxEffect = Math.max(...allEffects);
    const effectPadding = (maxEffect - minEffect) * 0.1 || 0.5;

    const yScale = d3.scaleLinear()
      .domain([minEffect - effectPadding, maxEffect + effectPadding])
      .range([innerHeight, 0]);

    // Size scale for bubbles (students)
    const maxStudents = d3.max(allPoints, d => d.new_students) || 1;
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxStudents])
      .range([4, 25]);

    // Add gridlines
    g.append('g')
      .attr('class', 'grid')
      .selectAll('line')
      .data(yScale.ticks(10))
      .join('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', d => yScale(d))
      .attr('y2', d => yScale(d))
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2');

    // Add zero line if in range
    if (minEffect < 0 && maxEffect > 0) {
      g.append('line')
        .attr('x1', 0)
        .attr('x2', innerWidth)
        .attr('y1', yScale(0))
        .attr('y2', yScale(0))
        .attr('stroke', '#94a3b8')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');
    }

    // X axis
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => d.toString())
        .ticks(Math.min(maxYear - minYear + 1, 20)));

    xAxis.selectAll('text')
      .style('font-size', '11px')
      .style('fill', '#475569');

    xAxis.select('.domain')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 2);

    // Y axis
    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale).ticks(10));

    yAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#475569');

    yAxis.select('.domain')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 2);

    // X axis label
    g.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 50)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#334155')
      .text('Year');

    // Y axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -55)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#334155')
      .text('Effect Size (WWC)');

    // Line generator
    const line = d3.line<P1DataPoint>()
      .x(d => xScale(d.year))
      .y(d => yScale(d.effect_size))
      .curve(d3.curveMonotoneX);

    // Helper function to get bubble color based on direction
    const getBubbleColor = (direction: string) => {
      if (direction === 'Favorable') return '#10b981'; // green
      if (direction === 'Unfavorable') return '#ef4444'; // red
      return '#9ca3af'; // grey
    };

    // Draw lines and bubbles for each series
    series.forEach((seriesItem, seriesIndex) => {
      const safeId = `series-${seriesIndex}`;
      const validPoints = (seriesItem.data_points || []).filter(d => d.effect_size !== null);

      if (validPoints.length === 0) return;

      // Line path (use series color for the line)
      g.append('path')
        .datum(validPoints)
        .attr('fill', 'none')
        .attr('stroke', seriesItem.color)
        .attr('stroke-width', 2.5)
        .attr('d', line)
        .style('opacity', 0.8);

      // Bubbles at each data point
      g.selectAll(`.bubble-${safeId}`)
        .data(validPoints)
        .join('circle')
        .attr('class', `bubble-${safeId}`)
        .attr('cx', d => xScale(d.year))
        .attr('cy', d => yScale(d.effect_size))
        .attr('r', d => sizeScale(d.new_students))
        .attr('fill', d => getBubbleColor(d.dominant_direction))
        .attr('stroke', seriesItem.color)
        .attr('stroke-width', 2)
        .style('opacity', 0.9)
        .style('cursor', 'pointer')
        .on('mouseover', function(_event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', sizeScale(d.new_students) * 1.5)
            .style('opacity', 1);

          // Tooltip
          const tooltip = g.append('g')
            .attr('class', 'tooltip')
            .attr('transform', `translate(${xScale(d.year)},${yScale(d.effect_size) - 20})`);

          const tooltipText = [
            `${seriesItem.label} - ${d.year}`,
            `Effect Size: ${d.effect_size.toFixed(3)}`,
            `Students: ${d.new_students.toLocaleString()}`,
            `Studies: ${d.num_studies}`,
            `Direction: ${d.dominant_direction}`
          ];

          const boxHeight = tooltipText.length * 16 + 16;
          const boxWidth = 250;

          tooltip.append('rect')
            .attr('x', -boxWidth / 2)
            .attr('y', -boxHeight)
            .attr('width', boxWidth)
            .attr('height', boxHeight)
            .attr('fill', 'white')
            .attr('stroke', seriesItem.color)
            .attr('stroke-width', 2)
            .attr('rx', 4);

          tooltipText.forEach((text, i) => {
            tooltip.append('text')
              .attr('text-anchor', 'middle')
              .attr('y', -boxHeight + 16 + i * 16)
              .style('font-size', i === 0 ? '11px' : '10px')
              .style('font-weight', i === 0 ? '600' : 'normal')
              .style('fill', '#1e293b')
              .text(text);
          });
        })
        .on('mouseout', function(_event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', sizeScale(d.new_students))
            .style('opacity', 0.9);

          g.selectAll('.tooltip').remove();
        })
        .on('click', function(_event, d) {
          if (onPointClick) {
            onPointClick(seriesItem, d);
          }
        });
    });


  }, [data, viewMode, dimensions, onPointClick]);

  return (
    <div className="flex flex-col w-full h-full">
      {/* Legend Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
        <div className="text-sm font-medium text-slate-700">
          Viewing by Use Case
        </div>

        {/* Line Color Legend for Use Cases */}
        {data.usecase_series && (
          <div className="flex gap-3 text-xs">
            {data.usecase_series.map((useCaseSeries) => (
              <div key={useCaseSeries.id} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: useCaseSeries.color }}
                ></div>
                <span className="text-slate-700">{useCaseSeries.label}</span>
              </div>
            ))}
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full flex-shrink-0 bg-slate-300"></div>
              <span className="text-slate-500 italic">Automated Grading</span>
            </div>
          </div>
        )}
      </div>


      {/* Chart */}
      <div ref={containerRef} className="flex-1 w-full min-h-[700px]">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
