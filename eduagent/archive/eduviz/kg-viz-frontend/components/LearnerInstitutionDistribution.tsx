'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

interface DemographicDataPoint {
  state: string;
  category: string;
  student_count: number;
  percentage: number;
}

interface InstitutionDataPoint {
  state: string;
  institution_type: string;
  count: number;
  percentage: number;
}

interface GradeLevelDataPoint {
  state: string;
  grade_level: string;
  student_count: number;
  percentage: number;
}

interface TimeSlice {
  year: number;
  demographic_data: DemographicDataPoint[];
  institution_data: InstitutionDataPoint[];
  grade_level_data: GradeLevelDataPoint[];
  total_students: number;
  total_studies: number;
}

interface LearnerInstitutionDistributionProps {
  timeSlices: TimeSlice[];
  allYears: number[];
}

type ViewMode = 'learner-types' | 'institution-characteristics' | 'grade-levels';

const LEARNER_COLORS: { [key: string]: string } = {
  'FRPL': '#f59e0b', // amber - low-income
  'ELL': '#10b981', // green - English language learners
  'IEP': '#8b5cf6', // purple - special education
  'Minority': '#ef4444' // red - minority students
};

const INSTITUTION_COLORS: { [key: string]: string } = {
  'Public': '#3b82f6', // blue
  'Charter': '#10b981', // green
  'Private': '#f59e0b', // amber
  'Parochial': '#8b5cf6' // purple
};

const GRADE_LEVEL_COLORS: { [key: string]: string } = {
  'PK': '#ec4899', // pink - early childhood
  'K-5': '#3b82f6', // blue - elementary
  '6-8': '#10b981', // green - middle school
  '9-12': '#f59e0b' // amber - high school
};

export default function LearnerInstitutionDistribution({ timeSlices, allYears }: LearnerInstitutionDistributionProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1000, height: 600 });
  const [selectedYear, setSelectedYear] = useState(allYears[allYears.length - 1] || 2023);
  const [viewMode, setViewMode] = useState<ViewMode>('learner-types');
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
    const margin = { top: 40, right: 40, bottom: 40, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Draw US map background
    const projection = d3.geoAlbersUsa()
      .scale(innerWidth * 1.2)
      .translate([innerWidth / 2, innerHeight / 2]);

    const path = d3.geoPath().projection(projection);
    const states: any = topojson.feature(usTopology, usTopology.objects.states);

    // Draw states as light background with hover functionality
    g.selectAll('path.state-bg')
      .data(states.features)
      .join('path')
      .attr('class', 'state-bg')
      .attr('d', (d: any) => path(d) || '')
      .attr('fill', '#f8fafc')
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 1)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d: any) {
        const stateName = d.properties.name;

        d3.select(this)
          .attr('stroke', '#94a3b8')
          .attr('stroke-width', 2);

        // Show tooltip based on view mode
        if (viewMode === 'learner-types') {
          const stateDataMap = new Map<string, DemographicDataPoint[]>();
          currentTimeSlice.demographic_data.forEach(dp => {
            if (!stateDataMap.has(dp.state)) {
              stateDataMap.set(dp.state, []);
            }
            stateDataMap.get(dp.state)!.push(dp);
          });

          const stateData = stateDataMap.get(stateName);
          if (stateData && stateData.length > 0) {
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${x},${y - 10})`);

            const totalStudents = stateData.reduce((sum, d) => sum + d.student_count, 0);
            const text = [
              stateName,
              `~${totalStudents.toLocaleString()} students`,
              '---',
              ...stateData.map(d => `${d.category}: ${d.student_count.toLocaleString()} (${d.percentage.toFixed(1)}%)`)
            ];

            const boxWidth = 240;
            const lineHeight = 16;
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
                .style('font-size', i === 0 ? '13px' : i === 1 ? '11px' : i === 2 ? '10px' : '10px')
                .style('font-weight', i === 0 ? '600' : 'normal')
                .style('fill', i === 2 ? '#cbd5e1' : '#1e293b')
                .text(line);
            });
          }
        } else if (viewMode === 'institution-characteristics') {
          const stateDataMap = new Map<string, InstitutionDataPoint[]>();
          currentTimeSlice.institution_data.forEach(dp => {
            if (!stateDataMap.has(dp.state)) {
              stateDataMap.set(dp.state, []);
            }
            stateDataMap.get(dp.state)!.push(dp);
          });

          const stateData = stateDataMap.get(stateName);
          if (stateData && stateData.length > 0) {
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${x},${y - 10})`);

            const totalInstitutions = stateData.reduce((sum, d) => sum + d.count, 0);
            const text = [
              stateName,
              `${totalInstitutions.toFixed(1)} institutions`,
              '---',
              ...stateData.map(d => `${d.institution_type}: ${d.count.toFixed(1)} (${d.percentage.toFixed(1)}%)`)
            ];

            const boxWidth = 240;
            const lineHeight = 16;
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
                .style('font-size', i === 0 ? '13px' : i === 1 ? '11px' : i === 2 ? '10px' : '10px')
                .style('font-weight', i === 0 ? '600' : 'normal')
                .style('fill', i === 2 ? '#cbd5e1' : '#1e293b')
                .text(line);
            });
          }
        } else if (viewMode === 'grade-levels') {
          const stateDataMap = new Map<string, GradeLevelDataPoint[]>();
          currentTimeSlice.grade_level_data.forEach(dp => {
            if (!stateDataMap.has(dp.state)) {
              stateDataMap.set(dp.state, []);
            }
            stateDataMap.get(dp.state)!.push(dp);
          });

          const stateData = stateDataMap.get(stateName);
          if (stateData && stateData.length > 0) {
            const [x, y] = d3.pointer(event, svg.node());
            const tooltip = svg.append('g')
              .attr('class', 'tooltip')
              .attr('transform', `translate(${x},${y - 10})`);

            const totalStudents = stateData.reduce((sum, d) => sum + d.student_count, 0);
            const text = [
              stateName,
              `~${totalStudents.toLocaleString()} students`,
              '---',
              ...stateData.map(d => {
                const label = d.grade_level === 'PK' ? 'Early Childhood (PK)' :
                             d.grade_level === 'K-5' ? 'Elementary (K-5)' :
                             d.grade_level === '6-8' ? 'Middle School (6-8)' :
                             'High School (9-12)';
                return `${label}: ${d.student_count.toLocaleString()} (${d.percentage.toFixed(1)}%)`;
              })
            ];

            const boxWidth = 260;
            const lineHeight = 16;
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
                .style('font-size', i === 0 ? '13px' : i === 1 ? '11px' : i === 2 ? '10px' : '10px')
                .style('font-weight', i === 0 ? '600' : 'normal')
                .style('fill', i === 2 ? '#cbd5e1' : '#1e293b')
                .text(line);
            });
          }
        }
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', '#e2e8f0')
          .attr('stroke-width', 1);
        svg.selectAll('.tooltip').remove();
      });

    if (viewMode === 'learner-types') {
      // View 1: Learner Types (person icons) - distributed by state
      // Group data by state
      const stateDataMap = new Map<string, DemographicDataPoint[]>();
      currentTimeSlice.demographic_data.forEach(d => {
        if (!stateDataMap.has(d.state)) {
          stateDataMap.set(d.state, []);
        }
        stateDataMap.get(d.state)!.push(d);
      });

      // Draw icons for each state
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const stateData = stateDataMap.get(stateName);
        if (!stateData || stateData.length === 0) return;

        const centroid = path.centroid(feature);
        if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

        // Calculate state bounds for icon positioning
        const bounds = path.bounds(feature);
        const stateWidth = bounds[1][0] - bounds[0][0];
        const stateHeight = bounds[1][1] - bounds[0][1];
        const maxRadius = Math.min(stateWidth, stateHeight) * 0.15; // Use 15% for tighter clustering

        // Create icons for each demographic category in this state
        let iconIndex = 0;
        stateData.forEach(demo => {
          const numIcons = Math.max(1, Math.min(Math.ceil(demo.student_count / 100), 10)); // 1 icon = 100 students, cap at 10

          for (let i = 0; i < numIcons; i++) {
            const angle = (iconIndex / 20) * Math.PI * 2; // Distribute around circle
            const ringRadius = Math.min(5 + (iconIndex % 3) * 4, maxRadius);
            const x = centroid[0] + Math.cos(angle) * ringRadius;
            const y = centroid[1] + Math.sin(angle) * ringRadius;

            const personGroup = g.append('g')
              .attr('transform', `translate(${x},${y})`)
              .style('pointer-events', 'none');

            const color = LEARNER_COLORS[demo.category] || '#94a3b8';

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

            iconIndex++;
          }
        });
      });


    } else if (viewMode === 'institution-characteristics') {
      // View 2: Institution Characteristics (building icons) - distributed by state
      // Group data by state
      const stateDataMap = new Map<string, InstitutionDataPoint[]>();
      currentTimeSlice.institution_data.forEach(d => {
        if (!stateDataMap.has(d.state)) {
          stateDataMap.set(d.state, []);
        }
        stateDataMap.get(d.state)!.push(d);
      });

      // Draw icons for each state
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const stateData = stateDataMap.get(stateName);
        if (!stateData || stateData.length === 0) return;

        const centroid = path.centroid(feature);
        if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

        // Calculate state bounds for icon positioning
        const bounds = path.bounds(feature);
        const stateWidth = bounds[1][0] - bounds[0][0];
        const stateHeight = bounds[1][1] - bounds[0][1];
        const maxRadius = Math.min(stateWidth, stateHeight) * 0.15; // Use 15% for tighter clustering

        // Create icons for each institution type in this state
        let iconIndex = 0;
        stateData.forEach(inst => {
          const numIcons = Math.max(1, Math.min(Math.ceil(inst.count), 15)); // Cap at 15 per type

          for (let i = 0; i < numIcons; i++) {
            const angle = (iconIndex / 30) * Math.PI * 2; // Distribute around circle
            const ringRadius = Math.min(5 + (iconIndex % 3) * 4, maxRadius);
            const x = centroid[0] + Math.cos(angle) * ringRadius;
            const y = centroid[1] + Math.sin(angle) * ringRadius;

            const buildingGroup = g.append('g')
              .attr('transform', `translate(${x},${y})`)
              .style('pointer-events', 'none');

            const color = INSTITUTION_COLORS[inst.institution_type] || '#94a3b8';

            // Building rectangle
            buildingGroup.append('rect')
              .attr('x', -3)
              .attr('y', -6)
              .attr('width', 6)
              .attr('height', 8)
              .attr('fill', color)
              .attr('stroke', 'white')
              .attr('stroke-width', 0.5);

            // Roof
            buildingGroup.append('polygon')
              .attr('points', '-4,-6 0,-9 4,-6')
              .attr('fill', color)
              .attr('stroke', 'white')
              .attr('stroke-width', 0.5);

            iconIndex++;
          }
        });
      });


    } else {
      // View 3: Grade Levels (person icons, color-coded by level) - distributed by state
      // Group data by state
      const stateDataMap = new Map<string, GradeLevelDataPoint[]>();
      currentTimeSlice.grade_level_data.forEach(d => {
        if (!stateDataMap.has(d.state)) {
          stateDataMap.set(d.state, []);
        }
        stateDataMap.get(d.state)!.push(d);
      });

      // Draw icons for each state
      states.features.forEach((feature: any) => {
        const stateName = feature.properties.name;
        const stateData = stateDataMap.get(stateName);
        if (!stateData || stateData.length === 0) return;

        const centroid = path.centroid(feature);
        if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) return;

        // Calculate state bounds for icon positioning
        const bounds = path.bounds(feature);
        const stateWidth = bounds[1][0] - bounds[0][0];
        const stateHeight = bounds[1][1] - bounds[0][1];
        const maxRadius = Math.min(stateWidth, stateHeight) * 0.15; // Use 15% for tighter clustering

        // Create icons for each grade level in this state
        let iconIndex = 0;
        stateData.forEach(grade => {
          const numIcons = Math.max(1, Math.min(Math.ceil(grade.student_count / 100), 10)); // 1 icon = 100 students, cap at 10

          for (let i = 0; i < numIcons; i++) {
            const angle = (iconIndex / 20) * Math.PI * 2; // Distribute around circle
            const ringRadius = Math.min(5 + (iconIndex % 3) * 4, maxRadius);
            const x = centroid[0] + Math.cos(angle) * ringRadius;
            const y = centroid[1] + Math.sin(angle) * ringRadius;

            const personGroup = g.append('g')
              .attr('transform', `translate(${x},${y})`)
              .style('pointer-events', 'none');

            const color = GRADE_LEVEL_COLORS[grade.grade_level] || '#94a3b8';

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

            iconIndex++;
          }
        });
      });

    }

  }, [timeSlices, selectedYear, viewMode, dimensions, usTopology]);

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col">
      {/* Legend and Controls */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
        <div className="flex items-center gap-6">
          {viewMode === 'learner-types' && (
            <>
              <div className="text-sm font-medium text-slate-700">1 person = 100 students</div>
              {Object.entries(LEARNER_COLORS).map(([category, color]) => (
                <div key={category} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                  <span className="text-sm text-slate-600">{category}</span>
                </div>
              ))}
            </>
          )}
          {viewMode === 'institution-characteristics' && (
            <>
              <div className="text-sm font-medium text-slate-700">1 building = 1 institution</div>
              {Object.entries(INSTITUTION_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center gap-2">
                  <div className="w-3 h-3" style={{ backgroundColor: color }}></div>
                  <span className="text-sm text-slate-600">{type}</span>
                </div>
              ))}
            </>
          )}
          {viewMode === 'grade-levels' && (
            <>
              <div className="text-sm font-medium text-slate-700">1 person = 100 students</div>
              {Object.entries(GRADE_LEVEL_COLORS).map(([level, color]) => (
                <div key={level} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                  <span className="text-sm text-slate-600">
                    {level === 'PK' ? 'Early Childhood' : level === 'K-5' ? 'Elementary' : level === '6-8' ? 'Middle' : 'High School'}
                  </span>
                </div>
              ))}
            </>
          )}
        </div>

        {/* View Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('learner-types')}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              viewMode === 'learner-types'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Learner Types
          </button>
          <button
            onClick={() => setViewMode('institution-characteristics')}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              viewMode === 'institution-characteristics'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Institution Types
          </button>
          <button
            onClick={() => setViewMode('grade-levels')}
            className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
              viewMode === 'grade-levels'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Grade Levels
          </button>
        </div>
      </div>

      {/* Visualization */}
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
