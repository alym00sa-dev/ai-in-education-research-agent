'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { TimeSeriesData, TimeSeriesDataPoint } from '@/lib/types';

interface LineChartProps {
  timeSeries: TimeSeriesData[];
  onPointClick?: (series: TimeSeriesData, point: TimeSeriesDataPoint) => void;
}

export default function LineChart({ timeSeries, onPointClick }: LineChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

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
    if (!svgRef.current || !containerRef.current || !timeSeries || !timeSeries.length) return;

    // Validate timeSeries structure
    const validSeries = timeSeries.filter(series =>
      series &&
      series.id &&
      series.label &&
      series.color &&
      Array.isArray(series.data_points)
    );

    if (validSeries.length === 0) {
      console.error('No valid series data');
      return;
    }

    const { width, height } = dimensions;
    const margin = { top: 40, right: 280, bottom: 80, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Get all data points for scales (only from valid series)
    const allPoints = validSeries.flatMap(series => series.data_points || []);

    if (allPoints.length === 0) {
      console.warn('No data points found in time series');
      return;
    }

    // X scale (time periods)
    const allYears = allPoints.map(d => d.year_midpoint);
    const minYear = Math.min(...allYears);
    const maxYear = Math.max(...allYears);

    const xScale = d3.scaleLinear()
      .domain([minYear - 1, maxYear + 1])
      .range([0, innerWidth]);

    // Y scale (generalizability score 0-100)
    const maxScore = d3.max(allPoints, d => d.generalizability_score) || 100;
    const yScale = d3.scaleLinear()
      .domain([0, Math.max(maxScore * 1.1, 100)])
      .range([innerHeight, 0]);

    // Size scale for bubbles (cumulative students)
    const maxStudents = d3.max(allPoints, d => d.cumulative_students) || 1;
    const sizeScale = d3.scaleSqrt()
      .domain([0, maxStudents])
      .range([3, 20]);

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
        .ticks(8));

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
      .text('Generalizability Score (Context Diversity)');

    // Line generator
    const line = d3.line<TimeSeriesDataPoint>()
      .x(d => xScale(d.year_midpoint))
      .y(d => yScale(d.generalizability_score))
      .curve(d3.curveMonotoneX);

    // Draw lines for each series
    validSeries.forEach((series, seriesIndex) => {
      // Create a safe ID for CSS selectors (remove special characters)
      const safeId = `series-${seriesIndex}`;

      // Filter out points with 0 values for cleaner visualization
      const validPoints = (series.data_points || []).filter(d =>
        d.generalizability_score > 0 || d.cumulative_students > 0
      );

      if (validPoints.length === 0) return;

      // Line path
      g.append('path')
        .datum(validPoints)
        .attr('fill', 'none')
        .attr('stroke', series.color)
        .attr('stroke-width', 2.5)
        .attr('d', line)
        .style('opacity', 0.8);

      // Bubbles at each data point
      g.selectAll(`.bubble-${safeId}`)
        .data(validPoints)
        .join('circle')
        .attr('class', `bubble-${safeId}`)
        .attr('cx', d => xScale(d.year_midpoint))
        .attr('cy', d => yScale(d.generalizability_score))
        .attr('r', d => sizeScale(d.cumulative_students))
        .attr('fill', series.color)
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
        .style('opacity', 0.9)
        .style('cursor', onPointClick ? 'pointer' : 'default')
        .on('mouseover', function(_event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('r', sizeScale(d.cumulative_students) * 1.5)
            .style('opacity', 1);

          // Tooltip
          const tooltip = g.append('g')
            .attr('class', 'tooltip')
            .attr('transform', `translate(${xScale(d.year_midpoint)},${yScale(d.generalizability_score) - 20})`);

          const tooltipText = [
            d.period,
            `Generalizability: ${d.generalizability_score.toFixed(1)}`,
            `Students: ${d.cumulative_students.toLocaleString()}`,
            `Effect Size: ${d.avg_effect_size.toFixed(2)}`,
            `Studies: ${d.num_studies}`
          ];

          const boxHeight = tooltipText.length * 15 + 15;
          const boxWidth = 220;

          tooltip.append('rect')
            .attr('x', -boxWidth / 2)
            .attr('y', -boxHeight)
            .attr('width', boxWidth)
            .attr('height', boxHeight)
            .attr('fill', 'white')
            .attr('stroke', series.color)
            .attr('stroke-width', 2)
            .attr('rx', 4);

          tooltipText.forEach((text, i) => {
            tooltip.append('text')
              .attr('text-anchor', 'middle')
              .attr('y', -boxHeight + 15 + i * 15)
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
            .attr('r', sizeScale(d.cumulative_students))
            .style('opacity', 0.9);

          g.selectAll('.tooltip').remove();
        })
        .on('click', function(_event, d) {
          if (onPointClick) {
            onPointClick(series, d);
          }
        });
    });

    // Legend
    const legend = g.append('g')
      .attr('transform', `translate(${innerWidth + 15}, 0)`);

    validSeries.forEach((series, i) => {
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
        .text(series.label.length > 40 ? series.label.substring(0, 40) + '...' : series.label);
    });

  }, [timeSeries, onPointClick, dimensions]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <svg ref={svgRef}></svg>
    </div>
  );
}
