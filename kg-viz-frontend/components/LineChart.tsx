'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TimeSeriesDataPoint {
  period: string;
  year_midpoint: number;
  implementation_reach: number;
  cumulative_students: number;
  num_contexts: number;
  avg_effect_size: number;
  num_studies: number;
  new_students_this_period: number;
}

interface TimeSeriesData {
  id: string;
  label: string;
  color: string;
  data_points: TimeSeriesDataPoint[];
}

interface LineChartProps {
  timeSeries: TimeSeriesData[];
  onPointClick?: (series: TimeSeriesData, point: TimeSeriesDataPoint) => void;
}

export default function LineChart({ timeSeries, onPointClick }: LineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !timeSeries.length) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;
    const margin = { top: 40, right: 120, bottom: 80, left: 80 };
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
    const allPoints = timeSeries.flatMap(series => series.data_points);

    // X scale (time periods)
    const xScale = d3.scaleLinear()
      .domain([1995, 2025])
      .range([0, innerWidth]);

    // Y scale (implementation reach)
    const maxReach = d3.max(allPoints, d => d.implementation_reach) || 1;
    const yScale = d3.scaleLinear()
      .domain([0, maxReach * 1.1])
      .range([innerHeight, 0]);

    // Size scale for bubbles (effect size)
    const maxEffectSize = d3.max(allPoints, d => d.avg_effect_size) || 1;
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxEffectSize])
      .range([3, 15]);

    // Add gridlines
    g.append('g')
      .attr('class', 'grid')
      .selectAll('line')
      .data(yScale.ticks(8))
      .join('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', d => yScale(d))
      .attr('y2', d => yScale(d))
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,2');

    // X axis
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale)
        .tickValues([1995, 2000, 2005, 2010, 2015, 2020, 2025])
        .tickFormat(d => d.toString()));

    xAxis.selectAll('text')
      .style('font-size', '12px')
      .style('fill', '#475569');

    xAxis.select('.domain')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 2);

    // Y axis
    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale)
        .ticks(8)
        .tickFormat(d => d3.format('.2s')(d)));

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
      .text('Time Period');

    // Y axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -55)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('fill', '#334155')
      .text('Implementation Reach (Students × Contexts)');

    // Line generator
    const line = d3.line<TimeSeriesDataPoint>()
      .x(d => xScale(d.year_midpoint))
      .y(d => yScale(d.implementation_reach))
      .curve(d3.curveMonotoneX);

    // Draw lines for each series
    timeSeries.forEach(series => {
      // Line path
      g.append('path')
        .datum(series.data_points)
        .attr('fill', 'none')
        .attr('stroke', series.color)
        .attr('stroke-width', 2.5)
        .attr('d', line)
        .style('opacity', 0.8);

      // Bubbles at each data point
      g.selectAll(`.bubble-${series.id}`)
        .data(series.data_points)
        .join('circle')
        .attr('class', `bubble-${series.id}`)
        .attr('cx', d => xScale(d.year_midpoint))
        .attr('cy', d => yScale(d.implementation_reach))
        .attr('r', d => sizeScale(d.avg_effect_size))
        .attr('fill', series.color)
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
        .style('opacity', 0.9)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', sizeScale(d.avg_effect_size) * 1.5)
            .style('opacity', 1);

          // Tooltip
          const tooltip = g.append('g')
            .attr('class', 'tooltip')
            .attr('transform', `translate(${xScale(d.year_midpoint)},${yScale(d.implementation_reach) - 20})`);

          tooltip.append('rect')
            .attr('x', -100)
            .attr('y', -60)
            .attr('width', 200)
            .attr('height', 55)
            .attr('fill', 'white')
            .attr('stroke', series.color)
            .attr('stroke-width', 2)
            .attr('rx', 4);

          tooltip.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', -40)
            .style('font-size', '11px')
            .style('font-weight', '600')
            .style('fill', '#1e293b')
            .text(d.period);

          tooltip.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', -25)
            .style('font-size', '10px')
            .style('fill', '#475569')
            .text(`Reach: ${d3.format('.2s')(d.implementation_reach)}`);

          tooltip.append('text')
            .attr('text-anchor', 'middle')
            .attr('y', -12)
            .style('font-size', '10px')
            .style('fill', '#475569')
            .text(`Effect: ${d.avg_effect_size.toFixed(2)}`);
        })
        .on('mouseout', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', sizeScale(d.avg_effect_size))
            .style('opacity', 0.9);

          g.selectAll('.tooltip').remove();
        })
        .on('click', function(event, d) {
          if (onPointClick) {
            onPointClick(series, d);
          }
        });
    });

    // Legend
    const legend = g.append('g')
      .attr('transform', `translate(${innerWidth + 15}, 0)`);

    timeSeries.forEach((series, i) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${i * 25})`);

      legendRow.append('circle')
        .attr('r', 5)
        .attr('fill', series.color);

      legendRow.append('text')
        .attr('x', 12)
        .attr('y', 4)
        .style('font-size', '11px')
        .style('fill', '#334155')
        .text(series.label);
    });

  }, [timeSeries, onPointClick]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <svg ref={svgRef}></svg>
    </div>
  );
}
