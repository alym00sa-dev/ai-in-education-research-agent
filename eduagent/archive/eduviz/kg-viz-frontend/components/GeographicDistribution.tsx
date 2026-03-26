'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

interface GeographicDataPoint {
  state: string;
  student_count: number;
  study_count: number;
  interventions?: { [key: string]: number };
}

interface TimeSlice {
  year: number;
  geographic_data: GeographicDataPoint[];
  total_students: number;
  total_studies: number;
}

interface GeographicDistributionProps {
  timeSlices: TimeSlice[];
  allYears: number[];
  onInterventionColorsUpdate?: (colors: Map<string, string>) => void;
}

export default function GeographicDistribution({ timeSlices, allYears, onInterventionColorsUpdate }: GeographicDistributionProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 600 });
  const [selectedYear, setSelectedYear] = useState(allYears[allYears.length - 1] || 2023);
  const [viewMode, setViewMode] = useState<'overall' | 'by-intervention'>('overall');
  const [usTopology, setUsTopology] = useState<any>(null);
  const [interventionColors, setInterventionColors] = useState<Map<string, string>>(new Map());

  // Load US TopoJSON
  useEffect(() => {
    async function loadMap() {
      try {
        // Use a public CDN for US states TopoJSON
        const response = await fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json');
        const topology = await response.json();
        setUsTopology(topology);
      } catch (error) {
        console.error('Failed to load US map:', error);
      }
    }
    loadMap();
  }, []);

  // Clear intervention colors when switching to overall view
  useEffect(() => {
    if (viewMode === 'overall') {
      setInterventionColors(new Map());
      if (onInterventionColorsUpdate) {
        onInterventionColorsUpdate(new Map());
      }
    }
  }, [viewMode, onInterventionColorsUpdate]);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const containerHeight = containerRef.current.clientHeight - 120;

        // Maintain aspect ratio for US map (roughly 1.6:1)
        const mapAspectRatio = 1.6;
        let width = containerWidth;
        let height = containerHeight;

        if (width / height > mapAspectRatio) {
          // Container is too wide, constrain by height
          width = height * mapAspectRatio;
        } else {
          // Container is too tall, constrain by width
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
    if (!svgRef.current || !containerRef.current || !usTopology) return;

    const currentTimeSlice = timeSlices.find(ts => ts.year === selectedYear);
    if (!currentTimeSlice) return;

    const { width, height } = dimensions;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Set up projection - adjust scale to fit nicely without squishing
    const projection = d3.geoAlbersUsa()
      .scale(width * 1.2)
      .translate([width / 2, height / 2]);

    const path = d3.geoPath().projection(projection);

    // Convert TopoJSON to GeoJSON
    const states: any = topojson.feature(usTopology, usTopology.objects.states);

    // Create a map of state data by name
    const stateDataMap = new Map<string, GeographicDataPoint>();
    currentTimeSlice.geographic_data.forEach(d => {
      stateDataMap.set(d.state, d);
    });

    // Get max student count for color scale
    const maxStudents = d3.max(currentTimeSlice.geographic_data, d => d.student_count) || 1;

    // Create study-to-states mapping for icon placement
    const studiesByState = new Map<string, Set<string>>(); // state -> Set of study_ids

    // We need to track which studies are in which states
    // For now, we'll use a simplified approach: count distinct interventions per state as proxy for studies
    currentTimeSlice.geographic_data.forEach(stateData => {
      if (stateData.interventions) {
        studiesByState.set(stateData.state, new Set(Object.keys(stateData.interventions)));
      }
    });

    if (viewMode === 'overall') {
      // View 1: State colored by student density, icons = studies
      const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([0, maxStudents]);

      // Draw states
      g.selectAll('path')
        .data(states.features)
        .join('path')
        .attr('d', (d: any) => path(d) || '')
        .attr('fill', (d: any) => {
          const stateName = d.properties.name;
          const stateData = stateDataMap.get(stateName);
          return stateData ? colorScale(stateData.student_count) : '#f1f5f9';
        })
        .attr('stroke', '#cbd5e1')
        .attr('stroke-width', 1)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d: any) {
          const stateName = d.properties.name;
          const stateData = stateDataMap.get(stateName);

          d3.select(this)
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 2);

          if (stateData) {
            // Show tooltip
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${x},${y - 10})`);

            const numStudies = studiesByState.get(stateName)?.size || 0;
            const text = [
              stateName,
              `~${Math.round(stateData.student_count).toLocaleString()} students (est.)`,
              `${numStudies} studies`
            ];

            const boxWidth = 200;
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
          }
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('stroke', '#cbd5e1')
            .attr('stroke-width', 1);
          svg.selectAll('.tooltip').remove();
        });

      // Add study icons (1 icon = 1 study)
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const studies = studiesByState.get(stateName);
        if (!studies || studies.size === 0) return;

        const centroid = path.centroid(feature);
        if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

        const numIcons = studies.size;
        const iconsToShow = Math.min(numIcons, 20); // Cap at 20 icons per state

        // Calculate appropriate radius based on state size
        const bounds = path.bounds(feature);
        const stateWidth = bounds[1][0] - bounds[0][0];
        const stateHeight = bounds[1][1] - bounds[0][1];
        const maxRadius = Math.min(stateWidth, stateHeight) * 0.15; // Use 15% of smallest dimension for tighter clustering

        // Arrange icons in a compact circle
        for (let i = 0; i < iconsToShow; i++) {
          const angle = (i / iconsToShow) * Math.PI * 2;
          const ringRadius = Math.min(5 + (i % 3) * 4, maxRadius);
          const x = centroid[0] + Math.cos(angle) * ringRadius;
          const y = centroid[1] + Math.sin(angle) * ringRadius;

          const personGroup = g.append('g')
            .attr('transform', `translate(${x},${y})`)
            .style('pointer-events', 'none');

          // Head
          personGroup.append('circle')
            .attr('r', 2.5)
            .attr('fill', '#1e293b')
            .attr('stroke', 'white')
            .attr('stroke-width', 0.5);

          // Body
          personGroup.append('line')
            .attr('x1', 0)
            .attr('y1', 2.5)
            .attr('x2', 0)
            .attr('y2', 8)
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 1.2);
        }
      });


    } else {
      // View 2: By intervention - state colored by student density, icons by intervention
      const allInterventions = new Set<string>();
      currentTimeSlice.geographic_data.forEach(dp => {
        if (dp.interventions) {
          Object.keys(dp.interventions).forEach(int => allInterventions.add(int));
        }
      });

      const interventionColorScale = d3.scaleOrdinal(d3.schemeCategory10)
        .domain(Array.from(allInterventions));

      // Update intervention colors map and notify parent
      const colorsMap = new Map<string, string>();
      allInterventions.forEach(int => {
        colorsMap.set(int, interventionColorScale(int));
      });
      setInterventionColors(colorsMap);
      if (onInterventionColorsUpdate) {
        onInterventionColorsUpdate(colorsMap);
      }

      // Same color scale as overall view
      const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([0, maxStudents]);

      // Draw states (same as overall view - colored by student density)
      g.selectAll('path')
        .data(states.features)
        .join('path')
        .attr('d', (d: any) => path(d) || '')
        .attr('fill', (d: any) => {
          const stateName = d.properties.name;
          const stateData = stateDataMap.get(stateName);
          return stateData ? colorScale(stateData.student_count) : '#f1f5f9';
        })
        .attr('stroke', '#cbd5e1')
        .attr('stroke-width', 1)
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d: any) {
          const stateName = d.properties.name;
          const stateData = stateDataMap.get(stateName);

          d3.select(this)
            .attr('stroke', '#1e293b')
            .attr('stroke-width', 2);

          if (stateData && stateData.interventions) {
            // Show tooltip with interventions
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${x},${y - 10})`);

            const interventionList = Object.entries(stateData.interventions)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 3); // Show top 3

            const numStudies = studiesByState.get(stateName)?.size || 0;
            const totalInterventions = Object.keys(stateData.interventions).length;
            const topCount = Math.min(3, interventionList.length);

            const text = [
              stateName,
              `~${Math.round(stateData.student_count).toLocaleString()} students`,
              `${numStudies} studies`,
              `${totalInterventions} unique intervention${totalInterventions !== 1 ? 's' : ''}`,
              '---',
              `Top ${topCount}:`,
              ...interventionList.map(([name]) =>
                (name.length > 32 ? name.substring(0, 32) + '...' : name)
              )
            ];

            const boxWidth = 280;
            const lineHeight = 17;
            const padding = 14;
            const boxHeight = text.length * lineHeight + padding;

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
                .attr('y', -boxHeight + padding + 2 + i * lineHeight)
                .style('font-size', i === 0 ? '13px' : i < 4 ? '11px' : i === 5 ? '10px' : '10px')
                .style('font-weight', i === 0 ? '600' : i === 5 ? '600' : 'normal')
                .style('fill', i === 4 ? '#cbd5e1' : i === 5 ? '#64748b' : '#1e293b')
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

      // Add study icons colored by intervention (1 icon = 1 study)
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const stateData = stateDataMap.get(stateName);
        if (!stateData || !stateData.interventions) return;

        const centroid = path.centroid(feature);
        if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

        // Each intervention represents a study
        const interventionList = Object.keys(stateData.interventions);
        const iconsToShow = Math.min(interventionList.length, 20);

        // Calculate appropriate radius based on state size
        const bounds = path.bounds(feature);
        const stateWidth = bounds[1][0] - bounds[0][0];
        const stateHeight = bounds[1][1] - bounds[0][1];
        const maxRadius = Math.min(stateWidth, stateHeight) * 0.15; // Use 15% of smallest dimension for tighter clustering

        interventionList.slice(0, iconsToShow).forEach((intervention, iconIndex) => {
          const angle = (iconIndex / iconsToShow) * Math.PI * 2;
          const ringRadius = Math.min(5 + (iconIndex % 3) * 4, maxRadius);
          const x = centroid[0] + Math.cos(angle) * ringRadius;
          const y = centroid[1] + Math.sin(angle) * ringRadius;

          const personGroup = g.append('g')
            .attr('transform', `translate(${x},${y})`)
            .style('pointer-events', 'none');

          const color = interventionColorScale(intervention);

          // Head
          personGroup.append('circle')
            .attr('r', 2.5)
            .attr('fill', color)
            .attr('stroke', 'white')
            .attr('stroke-width', 0.5);

          // Body
          personGroup.append('line')
            .attr('x1', 0)
            .attr('y1', 2.5)
            .attr('x2', 0)
            .attr('y2', 8)
            .attr('stroke', color)
            .attr('stroke-width', 1.2);
        });
      });

    }

  }, [timeSlices, selectedYear, viewMode, dimensions, usTopology]);

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col">
      {/* Legend and Controls */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="text-sm font-medium text-slate-700">Map Color:</div>
            <div className="w-20 h-4 bg-gradient-to-r from-blue-100 to-blue-700 rounded"></div>
            <span className="text-xs text-slate-600">Est. Student Density</span>
          </div>
          <div className="flex items-center gap-2 border-l pl-6 border-slate-300">
            <div className="text-sm font-medium text-slate-700">Icons:</div>
            {viewMode === 'overall' ? (
              <span className="text-xs text-slate-600">1 icon = 1 study (max 20 per state)</span>
            ) : (
              <span className="text-xs text-slate-600">1 icon = 1 study, colored by intervention (see sidebar)</span>
            )}
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overall')}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              viewMode === 'overall'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Overall Distribution
          </button>
          <button
            onClick={() => setViewMode('by-intervention')}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              viewMode === 'by-intervention'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            By Intervention
          </button>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative flex items-center justify-center bg-slate-50">
        {!usTopology && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-500">
            Loading map...
          </div>
        )}
        <svg ref={svgRef}></svg>
      </div>

      {/* Time Slider */}
      <div className="px-6 py-4 border-t border-slate-200">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-slate-700 min-w-[60px]">
            Year: {selectedYear}
          </label>
          <input
            type="range"
            min={allYears[0]}
            max={allYears[allYears.length - 1]}
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="flex-1"
            step="1"
          />
          <div className="text-sm text-slate-500 min-w-[100px] text-right">
            {timeSlices.find(ts => ts.year === selectedYear)?.total_students.toLocaleString() || 0} students
          </div>
        </div>
      </div>
    </div>
  );
}
