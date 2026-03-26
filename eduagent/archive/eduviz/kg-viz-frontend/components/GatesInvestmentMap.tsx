'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import { GatesInvestmentResponse } from '@/lib/types';

interface GatesInvestmentMapProps {
  data: GatesInvestmentResponse;
}

export default function GatesInvestmentMap({ data }: GatesInvestmentMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 600 });
  const [usTopology, setUsTopology] = useState<any>(null);

  // Load US TopoJSON
  useEffect(() => {
    async function loadMap() {
      try {
        const response = await fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json');
        const topology = await response.json();
        setUsTopology(topology);
      } catch (error) {
        console.error('Failed to load US map:', error);
      }
    }
    loadMap();
  }, []);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const containerHeight = containerRef.current.clientHeight - 100;

        // Maintain aspect ratio for US map (roughly 1.6:1)
        const mapAspectRatio = 1.6;
        let width = containerWidth;
        let height = containerHeight;

        if (width / height > mapAspectRatio) {
          width = height * mapAspectRatio;
        } else {
          height = width / mapAspectRatio;
        }

        setDimensions({ width, height });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !usTopology || !data) return;

    const { width, height } = dimensions;
    const margin = { top: 20, right: 20, bottom: 40, left: 20 };

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Set up projection - balanced scale for larger map while keeping all states visible
    const innerHeight = height - margin.top - margin.bottom;
    const projection = d3.geoAlbersUsa()
      .scale(width * 1.25)
      .translate([width / 2, innerHeight / 2 + margin.top]);

    const path = d3.geoPath().projection(projection);

    // Convert TopoJSON to GeoJSON
    const states: any = topojson.feature(usTopology, usTopology.objects.states);

    // Create investment lookup by state name
    const investmentByState = new Map(
      data.state_data.map(d => [d.state, d.investment_amount])
    );

    // Color scale (light green to dark green)
    const maxInvestment = d3.max(data.state_data, d => d.investment_amount) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateGreens)
      .domain([0, maxInvestment]);

    // Draw states with choropleth coloring
    g.selectAll('path')
      .data(states.features)
      .join('path')
      .attr('d', (d: any) => path(d) || '')
      .attr('fill', (d: any) => {
        const stateName = d.properties.name;
        const investment = investmentByState.get(stateName);
        return investment ? colorScale(investment) : '#f1f5f9';
      })
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 1)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d: any) {
        const stateName = d.properties.name;
        const investment = investmentByState.get(stateName);

        d3.select(this)
          .attr('stroke', '#1e293b')
          .attr('stroke-width', 2);

        if (investment) {
          // Show tooltip
          const [x, y] = d3.pointer(event, svg.node());
          const tooltip = svg.append('g')
            .attr('class', 'tooltip')
            .attr('transform', `translate(${x},${y - 10})`);

          const text = [
            stateName,
            `Investment: $${(investment / 1000000).toFixed(2)}M`
          ];

          const boxWidth = 200;
          const boxHeight = text.length * 18 + 10;

          tooltip.append('rect')
            .attr('x', -boxWidth / 2)
            .attr('y', -boxHeight)
            .attr('width', boxWidth)
            .attr('height', boxHeight)
            .attr('fill', 'white')
            .attr('stroke', '#10b981')
            .attr('stroke-width', 2)
            .attr('rx', 4);

          text.forEach((line, i) => {
            tooltip.append('text')
              .attr('text-anchor', 'middle')
              .attr('y', -boxHeight + 18 + i * 18)
              .style('font-size', i === 0 ? '12px' : '11px')
              .style('font-weight', i === 0 ? '600' : 'normal')
              .style('fill', '#1e293b')
              .text(line);
          });
        }
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', '#cbd5e1')
          .attr('stroke-width', 1);
        svg.selectAll('.tooltip').remove();
      });

    // Add blue bubbles for WWC study distribution
    if (data.wwc_distribution && data.wwc_distribution.length > 0) {
      // Create WWC data lookup by state name
      const wwcByState = new Map(
        data.wwc_distribution.map(d => [d.state, d])
      );

      // Size scale for bubbles based on student count
      const maxStudents = d3.max(data.wwc_distribution, d => d.student_count) || 1;
      const bubbleSizeScale = d3.scaleSqrt()
        .domain([0, maxStudents])
        .range([0, 30]);

      // Draw bubbles at state centroids
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const wwcData = wwcByState.get(stateName);

        if (wwcData && wwcData.student_count > 0) {
          const centroid = path.centroid(feature);
          if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

          const radius = bubbleSizeScale(wwcData.student_count);

          // Blue bubble
          const bubble = g.append('circle')
            .attr('cx', centroid[0])
            .attr('cy', centroid[1])
            .attr('r', radius)
            .attr('fill', '#3b82f6')
            .attr('stroke', '#1e3a8a')
            .attr('stroke-width', 2)
            .style('opacity', 0.7)
            .style('cursor', 'pointer');

          // Bubble hover
          bubble.on('mouseover', function(event) {
            d3.select(this)
              .transition()
              .duration(200)
              .style('opacity', 1)
              .attr('stroke-width', 3);

            // Show tooltip
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip-bubble')
              .attr('transform', `translate(${x},${y - 10})`);

            const text = [
              stateName,
              `WWC Students: ~${Math.round(wwcData.student_count).toLocaleString()}`,
              `Studies: ${Math.round(wwcData.study_count)}`
            ];

            const boxWidth = 220;
            const boxHeight = text.length * 18 + 10;

            tooltip.append('rect')
              .attr('x', -boxWidth / 2)
              .attr('y', -boxHeight)
              .attr('width', boxWidth)
              .attr('height', boxHeight)
              .attr('fill', 'white')
              .attr('stroke', '#3b82f6')
              .attr('stroke-width', 2)
              .attr('rx', 4);

            text.forEach((line, i) => {
              tooltip.append('text')
                .attr('text-anchor', 'middle')
                .attr('y', -boxHeight + 18 + i * 18)
                .style('font-size', i === 0 ? '12px' : '11px')
                .style('font-weight', i === 0 ? '600' : 'normal')
                .style('fill', '#1e293b')
                .text(line);
            });
          });

          bubble.on('mouseout', function() {
            d3.select(this)
              .transition()
              .duration(200)
              .style('opacity', 0.7)
              .attr('stroke-width', 2);
            svg.selectAll('.tooltip-bubble').remove();
          });
        }
      });
    }

  }, [data, dimensions, usTopology]);

  const maxInvestment = d3.max(data.state_data, d => d.investment_amount) || 1;

  return (
    <div className="flex flex-col w-full h-full">
      {/* Title */}
      <div className="px-4 py-3 border-b border-slate-200">
        <div className="flex items-start justify-between gap-6">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900">{data.metadata.title}</h3>
            <p className="text-xs text-slate-600 mt-1">{data.metadata.description}</p>
            <div className="flex gap-4 mt-2 text-xs text-slate-600">
              <span>Total Investment: <strong>${(data.total_investment / 1000000).toFixed(2)}M</strong></span>
              <span>State-Specific: <strong>${(data.state_allocated_investment / 1000000).toFixed(2)}M</strong></span>
              <span>US Unallocated: <strong>${(data.unallocated_investment / 1000000).toFixed(2)}M</strong></span>
              <span>States: <strong>{data.states_with_specific_investment}</strong></span>
            </div>
          </div>

          {/* Legend */}
          <div className="flex-shrink-0" style={{ width: '320px' }}>
            <div className="mb-3">
              <div className="text-xs font-semibold text-slate-800 mb-2">State-Specific Investment Amount</div>
              <div
                className="h-4 rounded"
                style={{
                  background: 'linear-gradient(to right, #f0fdf4, #166534)'
                }}
              ></div>
              <div className="flex justify-between mt-1 text-xs text-slate-600">
                <span>$0</span>
                <span>${(maxInvestment / 1000000).toFixed(1)}M</span>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-200">
              <div className="text-xs font-semibold text-slate-800 mb-2">WWC Study Distribution</div>
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <svg width="24" height="24">
                  <circle cx="12" cy="12" r="8" fill="#3b82f6" stroke="#1e3a8a" strokeWidth="2" opacity="0.7" />
                </svg>
                <span>Bubble size = Student count</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Map */}
      <div ref={containerRef} className="flex-1 w-full min-h-[600px] flex items-center justify-center">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
}
