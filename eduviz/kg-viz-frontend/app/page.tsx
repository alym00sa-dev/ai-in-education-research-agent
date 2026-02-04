'use client';

import { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import BubbleChart from '@/components/BubbleChart';
import LineChart from '@/components/LineChart';
import InfoTooltip from '@/components/InfoTooltip';
import { fetchLevel1Data, fetchLevel2Data, fetchLevel3Data, fetchLevel5Data, fetchP5Data, fetchP1Data, /* fetchGatesInvestmentData, */ fetchP1CurrentData, fetchP1CurrentByCaseData } from '@/lib/api';
import { BubbleData, VisualizationResponse, Level5Response, P5Response, P1Response, P1Series, P1DataPoint, TimeSeriesData, TimeSeriesDataPoint, /* GatesInvestmentResponse, */ P1CurrentResponse, P1CurrentRung, P1CurrentByCaseResponse, P1CurrentUseCaseLadder } from '@/lib/types';
import GeographicDistribution from '@/components/GeographicDistribution';
import LearnerInstitutionDistribution from '@/components/LearnerInstitutionDistribution';
import P1EffectSizeEvolution from '@/components/P1EffectSizeEvolution';
// import GatesInvestmentMap from '@/components/GatesInvestmentMap';
import P1CurrentEvidenceLadder from '@/components/P1CurrentEvidenceLadder';
import P1CurrentByUseCase from '@/components/P1CurrentByUseCase';

// Helper to capitalize labels properly
function capitalizeLabel(label: string): string {
  const smallWords = new Set(['and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with']);

  // Special case fixes for known patterns
  const specialCases: Record<string, string> = {
    'ai-enable': 'AI-Enabled',
    'ai-enabled': 'AI-Enabled',
  };

  return label
    .split(' - ')
    .map(part =>
      part.split(' ')
        .map((word, index) => {
          const lowerWord = word.toLowerCase();

          // Check for special case patterns
          if (specialCases[lowerWord]) {
            return specialCases[lowerWord];
          }

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

type ViewType = 'intro' | 'level1' | 'level2' | 'level3' | 'level5' | 'p1' | 'p1-current' | 'p5-geographic' | 'p5-learner'; // | 'gates-investment';

export default function Home() {
  const [level1Data, setLevel1Data] = useState<VisualizationResponse | null>(null);
  const [level2Data, setLevel2Data] = useState<VisualizationResponse | null>(null);
  const [level3Data, setLevel3Data] = useState<VisualizationResponse | null>(null);
  const [level5Data, setLevel5Data] = useState<Level5Response | null>(null);
  const [p1Data, setP1Data] = useState<P1Response | null>(null);
  const [p1CurrentData, setP1CurrentData] = useState<P1CurrentResponse | null>(null);
  const [p1CurrentByCaseData, setP1CurrentByCaseData] = useState<P1CurrentByCaseResponse | null>(null);
  const [p5Data, setP5Data] = useState<P5Response | null>(null);
  // const [gatesInvestmentData, setGatesInvestmentData] = useState<GatesInvestmentResponse | null>(null);
  const [p5InterventionColors, setP5InterventionColors] = useState<Map<string, string>>(new Map());
  const [selectedBubble, setSelectedBubble] = useState<BubbleData | null>(null);
  const [selectedTimePoint, setSelectedTimePoint] = useState<{series: TimeSeriesData, point: TimeSeriesDataPoint} | null>(null);
  const [selectedP1Point, setSelectedP1Point] = useState<{series: P1Series, point: P1DataPoint} | null>(null);
  const [selectedP1CurrentRung, setSelectedP1CurrentRung] = useState<P1CurrentRung | null>(null);
  const [selectedP1CurrentUseCase, setSelectedP1CurrentUseCase] = useState<P1CurrentUseCaseLadder | null>(null);
  const [p1ViewMode, setP1ViewMode] = useState<'interventions' | 'usecases'>('usecases');
  const [p1CurrentViewMode, setP1CurrentViewMode] = useState<'overall' | 'by-usecase'>('overall');
  const [activeView, setActiveView] = useState<ViewType>('intro');
  const [hiddenBubbles, setHiddenBubbles] = useState<Set<string>>(new Set());
  const [hiddenPriorities, setHiddenPriorities] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showOutcomesTargeted, setShowOutcomesTargeted] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [l1, l2, l3, l5, p1, p1Current, p1CurrentByCase, p5] = await Promise.all([
          fetchLevel1Data(),
          fetchLevel2Data(),
          fetchLevel3Data(),
          fetchLevel5Data(),
          fetchP1Data(),
          fetchP1CurrentData('Intelligent Tutoring and Instruction'),
          fetchP1CurrentByCaseData('Intelligent Tutoring and Instruction'),
          fetchP5Data(),
          // fetchGatesInvestmentData()
        ]);
        setLevel1Data(l1);
        setLevel2Data(l2);
        setLevel3Data(l3);
        setLevel5Data(l5);
        setP1Data(p1);
        setP1CurrentData(p1Current);
        setP1CurrentByCaseData(p1CurrentByCase);
        setP5Data(p5);
        // setGatesInvestmentData(gatesInv);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const handleBubbleClick = (bubble: BubbleData) => {
    setSelectedBubble(bubble);
  };

  const toggleBubbleVisibility = (bubbleId: string) => {
    setHiddenBubbles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(bubbleId)) {
        newSet.delete(bubbleId);
      } else {
        newSet.add(bubbleId);
      }
      return newSet;
    });
  };

  const togglePriorityVisibility = (priority: string) => {
    setHiddenPriorities(prev => {
      const newSet = new Set(prev);
      if (newSet.has(priority)) {
        newSet.delete(priority);
      } else {
        newSet.add(priority);
      }
      return newSet;
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-slate-700 mx-auto mb-5"></div>
          <p className="text-slate-700 text-lg font-medium">Loading research data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="bg-red-50 border-l-4 border-red-700 p-8 max-w-lg shadow-lg rounded-r-lg">
          <h2 className="text-red-900 font-semibold text-2xl mb-3">Unable to Load Data</h2>
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  const currentData = activeView === 'level1' ? level1Data : activeView === 'level2' ? level2Data : activeView === 'level3' ? level3Data : null;
  const visibleBubbles = currentData?.bubbles.filter(b =>
    !hiddenBubbles.has(b.id) && !hiddenPriorities.has(b.priority)
  ) || [];

  // Calculate x-axis domain from current level's data
  const currentXValues = currentData?.bubbles.map(b => b.x) || [];
  const xMin = currentXValues.length > 0 ? Math.min(...currentXValues) : 0;
  const xMax = currentXValues.length > 0 ? Math.max(...currentXValues) : 100;
  const xPadding = (xMax - xMin) * 0.15;
  const xDomain: [number, number] = [
    Math.max(0, xMin - xPadding),
    Math.min(100, xMax + xPadding)
  ];

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <header className="border-b border-slate-300 bg-gradient-to-r from-slate-800 to-slate-700 px-8 py-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-white tracking-tight">
            AI in Education Research Evidence Dashboard
          </h1>

          {/* View Selector Dropdown */}
          <div className="relative">
            <select
              value={activeView}
              onChange={(e) => {
                setActiveView(e.target.value as ViewType);
                setSelectedBubble(null);
                setSelectedTimePoint(null);
                setSelectedP1Point(null);
                setShowOutcomesTargeted(false);
              }}
              className="appearance-none bg-white text-slate-900 px-6 py-2 pr-10 rounded-lg font-medium shadow-md border-2 border-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-400 cursor-pointer"
            >
              <option value="intro">Introduction</option>
              <optgroup label="WWC Retrospective">
                <option value="level5">Evidence Evolution Over Time</option>
              </optgroup>
              <optgroup label="P1: Core Instruction & Tutoring">
                <option value="p1">Effect Size Evolution Over Time</option>
                <option value="p1-current">Current Evidence Landscape</option>
              </optgroup>
              <optgroup label="P5: Delivery (WIP)">
                <option value="p5-geographic">Pillar and Intervention Distribution</option>
                <option value="p5-learner">Learner Type and Institution Distribution</option>
              </optgroup>
              <optgroup label="Current Landscape">
                <option value="level1">Problem Burden Map</option>
                <option value="level2">Intervention Evidence Map</option>
              </optgroup>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-700">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
              </svg>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      {activeView === 'intro' ? (
        /* Introduction Page */
        <div className="flex-1 overflow-y-auto bg-white">
          <div className="max-w-5xl mx-auto px-12 py-16">
            {/* Header Section */}
            <div className="mb-16">
              <h2 className="text-4xl font-light text-slate-900 mb-4 tracking-tight">
                AI in Education Research Evidence Dashboard
              </h2>
              <p className="text-lg text-slate-600 leading-relaxed max-w-3xl mb-4">
                A strategic framework for navigating research evidence and investment priorities across AI-enabled educational interventions.
              </p>

              {/* Current Status Notice */}
              <div className="mt-6 bg-amber-50 border-l-4 border-amber-500 p-4">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-amber-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-amber-900 mb-1">
                      Current Data Availability
                    </p>
                    <p className="text-sm text-amber-800">
                      The current visualizations reflect evidence currently available in our research database. <strong>P1 (Core Instruction & Tutoring) and P5 (Delivery)</strong> will be the first pillars to be added as we continue expanding the database.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Five Pillars Framework */}
            <div className="mb-12">
              <h3 className="text-2xl font-semibold text-slate-900 mb-4">Five Strategic Pillars</h3>
              <p className="text-slate-600 mb-8 leading-relaxed">
                This dashboard will eventually showcase evidence across five strategic priorities for AI in education. Each pillar will be evaluated through three distinct layers of evidence, providing a comprehensive view of what we know, what we're learning, and what we need to discover.
              </p>

              <div className="grid grid-cols-1 gap-4 mb-12">
                <div className="border-l-4 border-blue-500 pl-6 py-3">
                  <h4 className="font-semibold text-slate-900">P1: Core Instruction & Tutoring</h4>
                  <p className="text-sm text-slate-600">Enhancing direct learning experiences through AI-supported instruction and personalized tutoring</p>
                </div>
                <div className="border-l-4 border-purple-500 pl-6 py-3">
                  <h4 className="font-semibold text-slate-900">P2: Gateway Math</h4>
                  <p className="text-sm text-slate-600">Addressing critical barriers in mathematics education that impact student progression</p>
                </div>
                <div className="border-l-4 border-green-500 pl-6 py-3">
                  <h4 className="font-semibold text-slate-900">P3: Personalized Advising</h4>
                  <p className="text-sm text-slate-600">Supporting student decision-making and pathways through intelligent guidance systems</p>
                </div>
                <div className="border-l-4 border-orange-500 pl-6 py-3">
                  <h4 className="font-semibold text-slate-900">P4: Credit Mobility</h4>
                  <p className="text-sm text-slate-600">Facilitating transfer and recognition of learning across institutions and contexts</p>
                </div>
                <div className="border-l-4 border-red-500 pl-6 py-3">
                  <h4 className="font-semibold text-slate-900">P5: Delivery</h4>
                  <p className="text-sm text-slate-600">Optimizing infrastructure and systems for effective educational delivery at scale</p>
                </div>
              </div>
            </div>

            {/* Three Evidence Layers */}
            <div className="mb-12">
              <h3 className="text-2xl font-semibold text-slate-900 mb-4">Three Layers of Evidence</h3>
              <p className="text-slate-600 mb-8 leading-relaxed">
                Each pillar is examined through three complementary evidence layers that span historical insights, current developments, and forward-looking indicators.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-slate-50 to-white border border-slate-200 p-6 rounded-lg">
                  <h4 className="font-semibold text-slate-900 mb-2">WWC Retrospective</h4>
                  <p className="text-sm text-slate-600 mb-3">
                    Historical evidence from rigorous randomized controlled trials, providing foundational insights from past research.
                  </p>
                  <div className="text-xs text-slate-500 font-medium">Historical Context</div>
                </div>

                <div className="bg-gradient-to-br from-blue-50 to-white border border-blue-200 p-6 rounded-lg">
                  <h4 className="font-semibold text-slate-900 mb-2">Current Landscape</h4>
                  <p className="text-sm text-slate-600 mb-3">
                    Ongoing and recent evidence from diverse study designs, capturing the present state of research and practice.
                  </p>
                  <div className="text-xs text-blue-600 font-medium">Present Evidence</div>
                </div>

                <div className="bg-gradient-to-br from-purple-50 to-white border border-purple-200 p-6 rounded-lg">
                  <h4 className="font-semibold text-slate-900 mb-2">Prophetic Layer</h4>
                  <p className="text-sm text-slate-600 mb-3">
                    Forward-looking indicators and emerging patterns that signal future developments and research needs.
                  </p>
                  <div className="text-xs text-purple-600 font-medium">Future Signals</div>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="flex justify-center pt-8 border-t border-slate-200">
              <button
                onClick={() => setActiveView('level1')}
                className="bg-slate-900 hover:bg-slate-800 text-white font-medium px-8 py-3 transition-colors"
              >
                Begin Analysis
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Visualization Dashboard */
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar - Legend & Controls (Hidden for Level 5, P1, P1Current, and P5) */}
          {activeView !== 'level5' && activeView !== 'p1' && activeView !== 'p1-current' && !activeView.startsWith('p5-') && (
            <aside className="w-80 border-r border-slate-200 bg-gradient-to-b from-slate-50 to-white p-6 overflow-y-auto relative z-20">
            {/* Legend */}
            <div className="mb-7 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">Visualization Guide</h3>

              <div className="space-y-4 text-sm">
                {currentData && (
                  <>
                  <div className="flex items-start">
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800">X-Axis: {currentData?.metadata.x_axis.label}</p>
                      <p className="text-slate-600 text-xs mt-1 leading-relaxed">{currentData?.metadata.x_axis.description}</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800">Y-Axis: {currentData?.metadata.y_axis.label}</p>
                      <p className="text-slate-600 text-xs mt-1 leading-relaxed">{currentData?.metadata.y_axis.description}</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="flex-1">
                      <p className="font-semibold text-slate-800">Bubble Size: {currentData?.metadata.bubble_size.label}</p>
                      <p className="text-slate-600 text-xs mt-1 leading-relaxed">{currentData?.metadata.bubble_size.description}</p>
                    </div>
                  </div>

                  {(activeView === 'level1' || activeView === 'level2') && (
                    <div className="flex items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-slate-800">Bubble Color: Priority Tag</p>
                        <div className="space-y-2 mt-2">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-green-500 flex-shrink-0"></div>
                            <p className="text-xs text-slate-600"><strong>High Priority:</strong> High evidence & high burden/impact</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-yellow-500 flex-shrink-0"></div>
                            <p className="text-xs text-slate-600">
                              <strong>On Watch:</strong> {activeView === 'level1' ? 'Either high burden with low evidence OR high evidence with low burden' : 'High burden/impact, low evidence'}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-pink-500 flex-shrink-0"></div>
                            <p className="text-xs text-slate-600"><strong>Research Gap:</strong> Below median threshold</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Remove bubble color legend for Level 3 */}
                  {/* {activeView === 'level3' && (
                    <div className="flex items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-slate-800">Bubble Color: Unique per Objective</p>
                        <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                          Each bubble has a distinct color for easy identification
                        </p>
                      </div>
                    </div>
                  )} */}
                  {/* {(activeView === 'level3' || activeView === 'level4') && (
                    <div className="flex items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-slate-800">Bubble Color: {activeView === 'level3' ? 'Unique per Objective' : 'Implementation Objective'}</p>
                        <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                          {activeView === 'level3' ? 'Each bubble has a distinct color for easy identification' : 'Color-coded by the four Implementation Objectives'}
                        </p>
                      </div>
                    </div>
                  )} */}
                  </>
                )}
              </div>
            </div>

          {/* Priority Filter - Only for Level 1 & 2 */}
          {(activeView === 'level1' || activeView === 'level2') && (
            <div className="mb-7 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">Filter by Priority</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-all group">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-sm text-slate-700 font-medium">High Priority</span>
                  </div>
                  <button
                    onClick={() => togglePriorityVisibility('high_priority')}
                    className="text-slate-500 hover:text-slate-900 transition-colors p-1"
                    title={hiddenPriorities.has('high_priority') ? 'Show bubbles' : 'Hide bubbles'}
                  >
                    {hiddenPriorities.has('high_priority') ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-all group">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="text-sm text-slate-700 font-medium">On Watch</span>
                  </div>
                  <button
                    onClick={() => togglePriorityVisibility('on_watch')}
                    className="text-slate-500 hover:text-slate-900 transition-colors p-1"
                    title={hiddenPriorities.has('on_watch') ? 'Show bubbles' : 'Hide bubbles'}
                  >
                    {hiddenPriorities.has('on_watch') ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-all group">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-pink-500"></div>
                    <span className="text-sm text-slate-700 font-medium">Research Gap</span>
                  </div>
                  <button
                    onClick={() => togglePriorityVisibility('research_gap')}
                    className="text-slate-500 hover:text-slate-900 transition-colors p-1"
                    title={hiddenPriorities.has('research_gap') ? 'Show bubbles' : 'Hide bubbles'}
                  >
                    {hiddenPriorities.has('research_gap') ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Bubble Visibility Controls */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">Categories</h3>
              <div className="space-y-1 max-h-96 overflow-y-auto pr-2">
                {currentData?.bubbles.map((bubble) => (
                  <div
                    key={bubble.id}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-all group"
                  >
                    <button
                      onClick={() => setSelectedBubble(bubble)}
                      className="flex-1 text-left text-sm text-slate-700 hover:text-slate-900 font-medium"
                    >
                      {capitalizeLabel(bubble.label)}
                    </button>
                    <button
                      onClick={() => toggleBubbleVisibility(bubble.id)}
                      className="text-slate-500 hover:text-slate-900 transition-colors p-1"
                      title={hiddenBubbles.has(bubble.id) ? 'Show bubble' : 'Hide bubble'}
                    >
                      {hiddenBubbles.has(bubble.id) ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
        </aside>
          )}

        {/* Center - Bubble Chart or Line Chart */}
        <main className="flex-1 p-8 overflow-hidden bg-slate-50 relative z-10">
          <div className="h-full bg-white border border-slate-200 rounded-xl shadow-md flex flex-col">
            {/* Level 5 Horizontal Metadata Guide */}
            {activeView === 'level5' && level5Data && (
              <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                <div className="grid grid-cols-4 gap-6 text-sm items-start">
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">X-Axis: {level5Data.metadata.x_axis.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">Publication year (5-year buckets)</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Y-Axis: {level5Data.metadata.y_axis.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">{level5Data.metadata.y_axis.description}</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Bubble Size: {level5Data.metadata.bubble_size.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">{level5Data.metadata.bubble_size.description}</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Line Color: Implementation Objective</p>
                    <p className="text-slate-600 text-xs leading-relaxed">Each line represents one of the four tech-compatible implementation objectives</p>
                  </div>
                </div>
              </div>
            )}

            {/* P1 Horizontal Metadata Guide */}
            {activeView === 'p1' && p1Data && (
              <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
                <div className="grid grid-cols-4 gap-6 text-sm items-start">
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">X-Axis: {p1Data.metadata.x_axis.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">{p1Data.metadata.x_axis.description}</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Y-Axis: {p1Data.metadata.y_axis.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">{p1Data.metadata.y_axis.description}</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Bubble Size: {p1Data.metadata.bubble_size.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed">{p1Data.metadata.bubble_size.description}</p>
                  </div>
                  <div className="flex flex-col">
                    <p className="font-semibold text-slate-800 mb-1.5">Bubble Color: {p1Data.metadata.bubble_color.label}</p>
                    <p className="text-slate-600 text-xs leading-relaxed mb-2">{p1Data.metadata.bubble_color.description}</p>
                    <div className="flex gap-4 text-xs">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-green-500"></div>
                        <span className="text-slate-600">Favorable</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <span className="text-slate-600">Unfavorable</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                        <span className="text-slate-600">Mixed/Neutral</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex-1 min-h-0">
              {activeView === 'level5' && level5Data ? (
                <LineChart
                  timeSeries={level5Data.time_series}
                  onPointClick={(series, point) => setSelectedTimePoint({series, point})}
                />
              ) : activeView === 'p1' && p1Data ? (
                <P1EffectSizeEvolution
                  data={p1Data}
                  onPointClick={(series, point) => setSelectedP1Point({series, point})}
                  onViewModeChange={(mode) => setP1ViewMode(mode)}
                />
              ) : activeView === 'p1-current' && p1CurrentData && p1CurrentByCaseData ? (
                <div className="flex flex-col w-full h-full">
                  {/* Combined Header: Description + Toggle Buttons */}
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
                    <div className="text-sm font-medium text-slate-700">
                      Distribution of research evidence across 6 rungs from monitoring to personalized effectiveness
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setP1CurrentViewMode('overall')}
                        className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                          p1CurrentViewMode === 'overall'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-300'
                        }`}
                      >
                        Overall Ladder
                      </button>
                      <button
                        onClick={() => setP1CurrentViewMode('by-usecase')}
                        className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                          p1CurrentViewMode === 'by-usecase'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-300'
                        }`}
                      >
                        By Use Case
                      </button>
                    </div>
                  </div>

                  {/* Visualization */}
                  <div className="flex-1 overflow-hidden">
                    {p1CurrentViewMode === 'overall' ? (
                      <P1CurrentEvidenceLadder
                        data={p1CurrentData}
                        onRungClick={(rung) => setSelectedP1CurrentRung(rung)}
                      />
                    ) : (
                      <P1CurrentByUseCase
                        data={p1CurrentByCaseData}
                        onUseCaseClick={(useCase) => setSelectedP1CurrentUseCase(useCase)}
                      />
                    )}
                  </div>
                </div>
              ) : activeView === 'p5-geographic' && p5Data ? (
                <GeographicDistribution
                  timeSlices={p5Data.time_slices}
                  allYears={p5Data.all_years}
                  onInterventionColorsUpdate={setP5InterventionColors}
                />
              ) : activeView === 'p5-learner' && p5Data ? (
                <LearnerInstitutionDistribution
                  timeSlices={p5Data.time_slices}
                  allYears={p5Data.all_years}
                />
              ) : /* activeView === 'gates-investment' && gatesInvestmentData ? (
                <GatesInvestmentMap
                  data={gatesInvestmentData}
                />
              ) : */ currentData && (
                <BubbleChart
                  data={visibleBubbles}
                  allData={currentData.bubbles}
                  xLabel={currentData.metadata.x_axis.label}
                  yLabel={currentData.metadata.y_axis.label}
                  onBubbleClick={handleBubbleClick}
                  selectedBubbleId={selectedBubble?.id || null}
                  xDomain={xDomain}
                  yMedian={activeView !== 'level3' ? currentData.metadata.y_axis.median : undefined}
                />
              )}
            </div>
            {/* So-What Blurb - Not shown for Level 5, P1, P1Current, or P5 */}
            {(currentData || level5Data) && activeView !== 'level5' && activeView !== 'p1' && activeView !== 'p1-current' && !activeView.startsWith('p5-') && (
              <div className="border-t border-slate-200 px-6 py-4 bg-slate-50">
                {activeView === 'level1' ? (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map helps us prioritize where to invest by combining problem burden with evidence readiness—so we focus on high-impact learning challenges that are both important and actionable.
                  </p>
                ) : activeView === 'level2' ? (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map evaluates intervention readiness by showing which AI-enabled approaches have both strong evidence and clear alignment to urgent educational problems as outlined in Level 1.
                  </p>
                ) : activeView === 'level3' ? (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map showcases proven interventions from rigorous RCTs (What Works Clearinghouse), highlighting which tech-compatible approaches have strong evidence AND generalize across diverse contexts—representing millions of students already impacted.
                  </p>
                ) : null}
              </div>
            )}
          </div>
        </main>

        {/* Right Sidebar - Detail Panel */}
        <aside className="w-96 border-l border-slate-200 bg-white overflow-y-auto relative z-20">
          {activeView === 'level5' && selectedTimePoint ? (
            <div className="p-7">
              <button
                onClick={() => setSelectedTimePoint(null)}
                className="text-slate-600 hover:text-slate-900 mb-5 text-sm font-medium transition-colors"
              >
                ← Return to Overview
              </button>

              <h2 className="text-2xl font-medium text-slate-900 mb-4 leading-tight">
                {selectedTimePoint.series.label}
              </h2>
              <p className="text-lg text-slate-600 mb-6">{selectedTimePoint.point.period}</p>

              <div className="space-y-6">
                {/* Students Impacted */}
                <div className="bg-slate-100 p-5 rounded-lg border border-slate-300">
                  <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">New Students This Period</p>
                  <p className="text-4xl font-bold text-slate-900 mt-2">
                    {selectedTimePoint.point.new_students_this_period.toLocaleString()}
                  </p>
                </div>

                <div className="bg-slate-100 p-5 rounded-lg border border-slate-300">
                  <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">Cumulative Students</p>
                  <p className="text-4xl font-bold text-slate-900 mt-2">
                    {selectedTimePoint.point.cumulative_students.toLocaleString()}
                  </p>
                </div>

                {/* Generalizability Score */}
                <div className="border-l-4 border-slate-700 pl-5">
                  <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide mb-3">
                    Generalizability Score
                  </h3>
                  <div className="bg-slate-100 p-4 rounded-lg border border-slate-300">
                    <p className="text-3xl font-bold text-slate-900">
                      {selectedTimePoint.point.generalizability_score.toFixed(1)}
                      <span className="text-lg text-slate-600"> / 100</span>
                    </p>
                  </div>
                  <p className="text-sm text-slate-600 mt-3 leading-relaxed">
                    <strong>Cumulative context diversity</strong> across all studies up to this period:
                  </p>
                  <div className="mt-3 space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Geographic regions:</span>
                      <span className="font-semibold text-slate-900">{selectedTimePoint.point.contexts.regions.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">School types:</span>
                      <span className="font-semibold text-slate-900">{selectedTimePoint.point.contexts.school_types.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-600">Grade levels/populations:</span>
                      <span className="font-semibold text-slate-900">{selectedTimePoint.point.contexts.populations.length}</span>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-200">
                    <p className="text-xs text-slate-500 leading-relaxed">
                      <strong>Calculation:</strong> Weighted score based on cumulative diversity.
                      Geographic regions (max 40 pts: 2 pts × unique regions),
                      school types (max 30 pts: 10 pts × type),
                      grade levels (max 30 pts: 5 pts × level).
                      Higher scores indicate interventions tested across more varied educational contexts.
                    </p>
                  </div>
                </div>

                {/* Effect Size */}
                <div className="border-l-4 border-slate-700 pl-5">
                  <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide mb-3">
                    Average Effect Size
                  </h3>
                  <div className="bg-slate-100 p-4 rounded-lg border border-slate-300">
                    <p className="text-3xl font-bold text-slate-900">
                      {selectedTimePoint.point.avg_effect_size.toFixed(3)}
                    </p>
                    <p className="text-sm text-slate-600 mt-1">Cohen's d</p>
                  </div>
                  <p className="text-sm text-slate-600 mt-3 leading-relaxed">
                    Based on {selectedTimePoint.point.num_studies} {selectedTimePoint.point.num_studies === 1 ? 'study' : 'studies'} in this period
                  </p>
                </div>

              </div>
            </div>
          ) : selectedP1Point ? (
            <div className="p-7">
              <button
                onClick={() => setSelectedP1Point(null)}
                className="text-slate-600 hover:text-slate-900 mb-5 text-sm font-medium transition-colors"
              >
                ← Return to Overview
              </button>

              <h2 className="text-2xl font-medium text-slate-900 mb-4 leading-tight">
                {selectedP1Point.series.label}
              </h2>
              <p className="text-lg text-slate-600 mb-6">{selectedP1Point.point.year}</p>

              <div className="space-y-6">
                {/* Effect Size */}
                <div className="border-l-4 border-slate-700 pl-5">
                  <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide mb-3">
                    Effect Size
                  </h3>
                  <div className="bg-slate-100 p-4 rounded-lg border border-slate-300">
                    <p className="text-3xl font-bold text-slate-900">
                      {selectedP1Point.point.effect_size.toFixed(3)}
                    </p>
                    <p className="text-sm text-slate-600 mt-1">Cohen's d (WWC)</p>
                  </div>
                </div>

                {/* Students Impacted */}
                <div className="bg-slate-100 p-5 rounded-lg border border-slate-300">
                  <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">New Students This Year</p>
                  <p className="text-4xl font-bold text-slate-900 mt-2">
                    {selectedP1Point.point.new_students.toLocaleString()}
                  </p>
                </div>

                <div className="bg-slate-100 p-5 rounded-lg border border-slate-300">
                  <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">Cumulative Students</p>
                  <p className="text-4xl font-bold text-slate-900 mt-2">
                    {selectedP1Point.point.cumulative_students.toLocaleString()}
                  </p>
                </div>

                {/* Finding Direction */}
                <div className="border-l-4 border-slate-700 pl-5">
                  <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide mb-3">
                    Dominant Finding Direction
                  </h3>
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${
                      selectedP1Point.point.dominant_direction === 'Favorable' ? 'bg-green-500' :
                      selectedP1Point.point.dominant_direction === 'Unfavorable' ? 'bg-red-500' :
                      'bg-gray-400'
                    }`}></div>
                    <span className="text-lg font-semibold text-slate-900">
                      {selectedP1Point.point.dominant_direction}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-3">
                    Based on {selectedP1Point.point.num_findings} finding{selectedP1Point.point.num_findings !== 1 ? 's' : ''} from {selectedP1Point.point.num_studies} {selectedP1Point.point.num_studies === 1 ? 'study' : 'studies'}
                  </p>
                </div>

                {/* Studies List */}
                <div className="border-l-4 border-slate-700 pl-5">
                  <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide mb-3">
                    Studies ({selectedP1Point.point.studies.length})
                  </h3>
                  <div className="space-y-4">
                    {selectedP1Point.point.studies.map((study, idx) => {
                      // Get unique outcome measures to summarize what was tested
                      const uniqueOutcomes = [...new Set(study.findings.map(f => f.outcome_measure))];
                      const avgEffectSize = study.findings.reduce((sum, f) => sum + f.effect_size, 0) / study.findings.length;

                      return (
                        <div key={idx} className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <div className="text-xs text-slate-500 mb-1">Study ID: {study.study_id}</div>
                              <div className="text-sm text-slate-700 italic">{study.citation}</div>
                            </div>
                            <div className="ml-4 text-right flex-shrink-0">
                              <div className="text-xs text-slate-600 mb-1">Sample Size</div>
                              <div className="text-xl font-bold text-slate-900">
                                {study.sample_size.toLocaleString()}
                              </div>
                            </div>
                          </div>

                          {/* Study Summary */}
                          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 mb-3">
                            <div className="text-xs font-semibold text-blue-900 mb-1">Study Summary</div>
                            <div className="text-xs text-blue-800">
                              This study tested <strong>{study.intervention_name || selectedP1Point.series.label}</strong>
                              {study.intervention_name && (
                                <span> (use case: <strong>{selectedP1Point.series.label}</strong>)</span>
                              )}{' '}
                              measuring {uniqueOutcomes.length} outcome{uniqueOutcomes.length !== 1 ? 's' : ''}: {uniqueOutcomes.slice(0, 2).join(', ')}
                              {uniqueOutcomes.length > 2 && ` and ${uniqueOutcomes.length - 2} more`}.
                              Average effect size: <strong>{avgEffectSize.toFixed(3)}</strong>
                            </div>
                          </div>

                          {/* Findings */}
                          <div className="text-xs font-semibold text-slate-700 mb-2">
                            Individual Findings ({study.findings.length}):
                          </div>
                        <div className="space-y-3">
                          {study.findings.map((finding, fidx) => {
                            // Interpret effect size magnitude
                            const absEffectSize = Math.abs(finding.effect_size);
                            let magnitude = 'Negligible';
                            if (absEffectSize >= 0.8) magnitude = 'Large';
                            else if (absEffectSize >= 0.5) magnitude = 'Medium';
                            else if (absEffectSize >= 0.2) magnitude = 'Small';

                            // Create impact description
                            const impactText = finding.direction === 'Favorable'
                              ? `Students who received this intervention performed ${magnitude.toLowerCase()} better than the control group.`
                              : finding.direction === 'Unfavorable'
                              ? `Students who received this intervention performed ${magnitude.toLowerCase()} worse than the control group.`
                              : `The intervention showed no clear positive or negative effect on student outcomes.`;

                            return (
                              <div key={fidx} className="bg-white p-3 rounded border border-slate-200 shadow-sm">
                                {/* Measurement */}
                                <div className="mb-2">
                                  <div className="text-xs font-semibold text-slate-700 mb-1">What Was Measured:</div>
                                  <div className="text-xs text-slate-900">{finding.outcome_measure}</div>
                                </div>

                                {/* Additional Context - Domain, Period, Sample */}
                                {(finding.outcome_domain || finding.period || finding.sample_description || finding.is_subgroup) && (
                                  <div className="mb-2 space-y-1">
                                    {finding.outcome_domain && (
                                      <div className="text-xs text-slate-600">
                                        <span className="font-semibold">Domain:</span> {finding.outcome_domain}
                                      </div>
                                    )}
                                    {finding.period && (
                                      <div className="text-xs text-slate-600">
                                        <span className="font-semibold">Timing:</span> {finding.period}
                                      </div>
                                    )}
                                    {finding.sample_description && (
                                      <div className="text-xs text-slate-600">
                                        <span className="font-semibold">Sample:</span> {finding.sample_description}
                                      </div>
                                    )}
                                    {finding.is_subgroup && (
                                      <div className="inline-block px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded">
                                        Subgroup Analysis
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* Effect Size & Direction */}
                                <div className="flex items-center gap-3 mb-2">
                                  <div>
                                    <div className="text-xs text-slate-600">Effect Size</div>
                                    <div className="text-sm font-bold text-slate-900">
                                      {finding.effect_size.toFixed(3)}
                                      {finding.is_significant && <span className="text-blue-600 ml-1">*</span>}
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${
                                      finding.direction === 'Favorable' ? 'bg-green-500' :
                                      finding.direction === 'Unfavorable' ? 'bg-red-500' :
                                      'bg-gray-400'
                                    }`}></div>
                                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                      finding.direction === 'Favorable' ? 'bg-green-100 text-green-700' :
                                      finding.direction === 'Unfavorable' ? 'bg-red-100 text-red-700' :
                                      'bg-gray-100 text-gray-700'
                                    }`}>
                                      {finding.direction}
                                    </span>
                                  </div>
                                  <div className="text-xs px-2 py-0.5 bg-slate-100 text-slate-700 rounded">
                                    {magnitude} Effect
                                  </div>
                                </div>

                                {/* Comparison: Intervention vs Control Scores */}
                                {(finding.intervention_mean !== null && finding.comparison_mean !== null) && (
                                  <div className="mb-2 bg-blue-50 border border-blue-200 p-2 rounded">
                                    <div className="text-xs font-semibold text-blue-900 mb-1">
                                      Score Comparison:
                                      {finding.comparison_clusters && (
                                        <span className="font-normal ml-1 text-blue-700">
                                          (Control: {finding.comparison_clusters} schools)
                                        </span>
                                      )}
                                    </div>
                                    <div className="flex items-center gap-2 text-xs">
                                      <span className="text-blue-900">
                                        <span className="font-semibold">Intervention:</span> {finding.intervention_mean.toFixed(2)}
                                      </span>
                                      <span className="text-slate-400">vs</span>
                                      <span className="text-blue-900">
                                        <span className="font-semibold">Control:</span> {finding.comparison_mean.toFixed(2)}
                                      </span>
                                    </div>
                                    <div className="text-xs text-blue-700 mt-1 italic">
                                      {finding.intervention_mean > finding.comparison_mean
                                        ? `Intervention scored ${(finding.intervention_mean - finding.comparison_mean).toFixed(2)} points higher`
                                        : finding.intervention_mean < finding.comparison_mean
                                        ? `Control scored ${(finding.comparison_mean - finding.intervention_mean).toFixed(2)} points higher`
                                        : 'Both groups scored equally'}
                                      {finding.comparison_clusters && ` (compared to ${finding.comparison_clusters} control schools)`}
                                    </div>
                                  </div>
                                )}

                                {/* Impact Description */}
                                <div className="bg-slate-50 p-2 rounded">
                                  <div className="text-xs font-semibold text-slate-700 mb-1">Impact:</div>
                                  <div className="text-xs text-slate-700 leading-relaxed">{impactText}</div>
                                </div>

                                {finding.is_significant && (
                                  <div className="text-xs text-blue-600 mt-2">* Statistically significant finding</div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                    })}
                  </div>
                </div>
              </div>
            </div>
          ) : selectedBubble ? (
            <div className="p-7">
              <button
                onClick={() => setSelectedBubble(null)}
                className="text-slate-600 hover:text-slate-900 mb-5 text-sm font-medium transition-colors"
              >
                ← Return to Overview
              </button>

              <h2 className="text-3xl font-medium text-slate-900 mb-6 leading-tight">
                {capitalizeLabel(selectedBubble.label)}
              </h2>

              <div className="space-y-6">
                {/* Paper Count with Study Design Breakdown */}
                <div className="bg-slate-100 p-5 rounded-lg border border-slate-300">
                  <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">Studies Analyzed</p>
                  <p className="text-4xl font-bold text-slate-900 mt-2">{selectedBubble.paper_count}</p>

                  {/* Study Design Breakdown - Only for Level 1 & 2 */}
                  {(activeView === 'level1' || activeView === 'level2') && selectedBubble.breakdown.study_design_distribution && Object.keys(selectedBubble.breakdown.study_design_distribution).length > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-300">
                      <p className="text-xs font-bold text-slate-700 uppercase mb-3 tracking-wide">Study Design Breakdown</p>
                      <div className="space-y-2">
                        {Object.entries(selectedBubble.breakdown.study_design_distribution).map(([design, count]) => (
                          <div key={design} className="flex justify-between text-sm items-center bg-white p-2 rounded border border-slate-200">
                            <span className="text-slate-700">{design}</span>
                            <span className="font-semibold text-slate-900 bg-slate-100 px-2 py-1 rounded">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Implication Panel - Only for Level 1 & 2 */}
                {(activeView === 'level1' || activeView === 'level2') && (
                  <div className="bg-slate-900 text-white p-5 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                        selectedBubble.priority === 'high_priority' ? 'bg-green-500' :
                        selectedBubble.priority === 'on_watch' ? 'bg-yellow-500' :
                        'bg-pink-500'
                      }`}></div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                        {selectedBubble.priority === 'high_priority' ? 'High Priority' :
                         selectedBubble.priority === 'on_watch' ? 'On Watch' :
                         'Research Gap'}
                      </p>
                    </div>
                    <p className="text-sm leading-relaxed mb-4">
                      {selectedBubble.priority === 'high_priority' ? (
                        <><strong>Ready for scaled action.</strong> High evidence maturity with {activeView === 'level1' ? 'high systemic burden' : 'strong alignment to urgent problems'}.</>
                      ) : selectedBubble.priority === 'on_watch' ? (
                        <><strong>Proceed with caution.</strong> {activeView === 'level1' ? 'Either high-burden problems lacking evidence or well-understood problems with lower systemic impact.' : 'High potential impact but needs additional validation before deployment.'}</>
                      ) : (
                        <><strong>Requires foundational research.</strong> Below median threshold—{activeView === 'level1' ? 'lower systemic priority or insufficient evidence base' : 'narrow scope or limited evidence of effectiveness'}.</>
                      )}
                    </p>
                    <div className="pt-3 border-t border-slate-700">
                      <p className="text-xs text-slate-400 leading-relaxed">
                        <strong>How it's calculated:</strong> {activeView === 'level1' ? 'Position based on Evidence Maturity (X-axis) > 65 and Problem Burden Scale (Y-axis) > median. High Priority = both conditions met. On Watch = one condition met (either high burden with low evidence OR high evidence with low burden). Research Gap = neither condition met.' : 'Position based on Evidence Maturity (X-axis) > 65 and Potential Impact (Y-axis) > median. Interventions with strong evidence AND high alignment to urgent problems are prioritized.'}
                      </p>
                    </div>
                  </div>
                )}

                {/* Evidence Maturity - Only for Level 1 & 2 */}
                {(activeView === 'level1' || activeView === 'level2') && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Evidence Maturity
                      </h3>
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.evidence_maturity.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.evidence_maturity.score.toFixed(1)} <span className="text-lg text-slate-600">/ {selectedBubble.breakdown.evidence_maturity.max}</span>
                      </p>
                    </div>

                    {/* Components */}
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedBubble.breakdown.evidence_maturity.components).map(([key, component]) => {
                        // Define detailed tooltip content for each component
                        const tooltipContent: { [key: string]: string } = {
                          'design_strength': 'CALCULATION: For each paper, assign points based on study_design field: RCT=25pts, Meta-analysis=22pts, Quasi-experimental=18pts, Pre-post=15pts, Case study=10pts, Literature review=8pts, Commentary=5pts. Final score = average across all papers in this cell. CONTEXT: Higher scores indicate more rigorous experimental designs with stronger causal inference. RCTs and meta-analyses provide the most reliable evidence for intervention effectiveness.',
                          'consistency': 'CALCULATION: Count papers by finding_direction (Positive, Negative, Mixed, Neutral). Calculate directional stability = (count of most common direction / total papers) × 25. Example: If 8 of 10 papers show Positive results, score = (8/10) × 25 = 20 points. CONTEXT: Higher scores mean findings consistently point in the same direction across studies, indicating reliable and replicable effects. Low scores suggest conflicting evidence requiring further investigation.',
                          'external_validity': 'CALCULATION: Count unique values across three diversity dimensions for all papers: (1) unique settings (classroom, online, after-school, etc.), (2) unique geographic regions (North America, Europe, Asia, etc.), (3) unique populations (K-12, higher ed, adult learners, etc.). Score = (total unique contexts / theoretical maximum) × 25. CONTEXT: Higher scores indicate findings generalize across diverse educational contexts, suggesting broader applicability and real-world relevance.',
                          'quality': 'CALCULATION: For each paper, use evidence_type_strength field (0=best, 4=worst quality). Invert scale: Quality score = 25 - (avg evidence_type_strength × 6.25). Lower evidence_type_strength = higher quality score. CONTEXT: Measures risk of bias based on peer review status, methodology transparency, sample size, conflict of interest, and replication potential. Higher scores indicate more trustworthy, rigorous research.'
                        };

                        return (
                          <div key={key} className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-1.5 mb-1.5">
                              <p className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                                {key.replace(/_/g, ' ')}
                              </p>
                              <InfoTooltip content={tooltipContent[key] || component.description} />
                            </div>
                            <p className="text-lg font-bold text-slate-900">
                              {component.score.toFixed(1)} <span className="text-sm text-slate-600">/ {component.max}</span>
                            </p>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">{component.description}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Y-Axis: Problem Scale (Level 1) OR Potential Impact (Level 2) */}
                {activeView === 'level1' && selectedBubble.breakdown.problem_scale && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Problem Burden Scale
                      </h3>
                      <InfoTooltip content="CALCULATION: Extract user_type field from each paper in this cell. Count unique user types (e.g., 'K-12 students', 'Teachers', 'Higher Ed students', 'Adult learners', 'Administrators'). Score = total count of unique user types. Example: If papers mention Teachers, K-12 students, and Administrators, score = 3. CONTEXT: Higher scores indicate the problem affects a broader range of educational stakeholders across different roles and contexts, suggesting wider systemic impact and greater urgency for scalable solutions." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.problem_scale.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.problem_scale.score.toFixed(2)} <span className="text-lg text-slate-600">/ {selectedBubble.breakdown.problem_scale.max}</span>
                      </p>
                    </div>

                    {/* Distribution */}
                    <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                      <p className="text-xs font-bold text-slate-700 mb-3 uppercase tracking-wide">User Type Distribution</p>
                      <div className="space-y-2">
                        {Object.entries(selectedBubble.breakdown.problem_scale.distribution).map(([type, count]) => (
                          <div key={type} className="flex justify-between text-sm items-center">
                            <span className="text-slate-700">{type}</span>
                            <span className="font-semibold text-slate-900 bg-slate-100 px-2 py-1 rounded">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeView === 'level2' && selectedBubble.breakdown.potential_impact && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Potential Impact
                      </h3>
                      <InfoTooltip content="CALCULATION: For each unique outcome this intervention targets, get the Problem Burden Scale (Y-axis) value from Level 1, then sum all those values. Example: If targeting 6 outcomes with Level 1 burden scales of 2.1, 1.8, 2.4, 1.7, 2.2, and 2.2, the score = 12.4. CONTEXT: Higher scores indicate interventions addressing multiple high-burden educational problems from Level 1, suggesting broader systemic impact and transformative potential across urgent educational challenges." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.potential_impact.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.potential_impact.score.toFixed(1)}
                      </p>
                    </div>

                    {/* Outcomes Targeted - Collapsible */}
                    <div className="bg-slate-50 rounded-lg border border-slate-200">
                      <button
                        onClick={() => setShowOutcomesTargeted(!showOutcomesTargeted)}
                        className="w-full p-4 flex items-center justify-between hover:bg-slate-100 transition-colors"
                      >
                        <p className="text-sm font-bold text-slate-700 uppercase tracking-wide">
                          Outcomes Targeted ({selectedBubble.breakdown.potential_impact.outcomes_targeted.length})
                        </p>
                        <span className="text-slate-600">{showOutcomesTargeted ? '−' : '+'}</span>
                      </button>
                      {showOutcomesTargeted && (
                        <div className="px-4 pb-4">
                          <div className="flex flex-wrap gap-2">
                            {selectedBubble.breakdown.potential_impact.outcomes_targeted.map((outcome, idx) => (
                              <span key={idx} className="text-xs bg-white px-3 py-1.5 rounded-md border border-slate-300 text-slate-700">
                                {outcome}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Bubble Size: Effort Required (Level 1) OR R&D Required (Level 2) */}
                {activeView === 'level1' && selectedBubble.breakdown.effort_required && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Effort Required
                      </h3>
                      <InfoTooltip content="CALCULATION: Two components averaged together: (1) System Impact = Count of system coordination indicators per paper (curriculum_alignment_needed, pd_training_needed, infrastructure_changes_needed, policy_changes_needed, assessment_changes_needed), averaged across all papers. (2) Decision Complexity = For each paper: (count of stakeholder_groups × avg_decisions_per_stakeholder), then averaged across papers. Final score = (System Impact + Decision Complexity) / 2. CONTEXT: Higher scores indicate more complex implementations requiring extensive coordination, stakeholder buy-in, and organizational change management." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.effort_required.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.effort_required.score.toFixed(2)}
                      </p>
                    </div>

                    {/* Components */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                        <p className="text-xs font-bold text-slate-700 uppercase mb-1.5 tracking-wide">
                          System Impact
                        </p>
                        <p className="text-lg font-bold text-slate-900">
                          {selectedBubble.breakdown.effort_required.components.system_impact.score.toFixed(2)}
                        </p>
                        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                          {selectedBubble.breakdown.effort_required.components.system_impact.description}
                        </p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                        <p className="text-xs font-bold text-slate-700 uppercase mb-1.5 tracking-wide">
                          Decision Complexity
                        </p>
                        <p className="text-lg font-bold text-slate-900">
                          {selectedBubble.breakdown.effort_required.components.decision_complexity.score.toFixed(2)}
                        </p>
                        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                          {selectedBubble.breakdown.effort_required.components.decision_complexity.description}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {activeView === 'level2' && selectedBubble.breakdown.r_and_d_required && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        R&D Investment Required
                      </h3>
                      <InfoTooltip content="CALCULATION: Two components averaged together: (1) Evidence Maturity Gap = 100 - Evidence Maturity score (max 100 pts). Example: If Evidence Maturity = 65, gap = 35 points. (2) Evaluation Burden = For each paper: (count unique outcomes via FOCUSES_ON_OUTCOME relationships × count unique population values), then averaged across papers. Final score = (Evidence Maturity Gap + Evaluation Burden) / 2. CONTEXT: Higher scores indicate areas needing more research investment. Large maturity gaps require foundational studies. High evaluation burden means complex multi-outcome, multi-population research designs needed to generate robust, generalizable evidence." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.r_and_d_required.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.r_and_d_required.score.toFixed(2)}
                      </p>
                    </div>

                    {/* Components */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                        <p className="text-xs font-bold text-slate-700 uppercase mb-1.5 tracking-wide">
                          Evidence Maturity Gap
                        </p>
                        <p className="text-lg font-bold text-slate-900">
                          {selectedBubble.breakdown.r_and_d_required.components.evidence_maturity_gap.score.toFixed(2)}
                        </p>
                        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                          {selectedBubble.breakdown.r_and_d_required.components.evidence_maturity_gap.description}
                        </p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                        <p className="text-xs font-bold text-slate-700 uppercase mb-1.5 tracking-wide">
                          Evaluation Burden
                        </p>
                        <p className="text-lg font-bold text-slate-900">
                          {selectedBubble.breakdown.r_and_d_required.components.evaluation_burden.score.toFixed(2)}
                        </p>
                        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                          {selectedBubble.breakdown.r_and_d_required.components.evaluation_burden.description}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Level 3 Specific Sections */}
                {activeView === 'level3' && selectedBubble.breakdown.evidence_maturity && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Evidence Base Quality
                      </h3>
                      <InfoTooltip content="CALCULATION: 4-component composite score (25 points each): (1) Study Design Quality - WWC ratings (Meets standards without/with reservations), (2) Replication Strength - Number of independent RCT studies, (3) Sample Adequacy - Total students studied (1,000+ = 25 pts), (4) Effect Consistency - Standard deviation of effect sizes (0.0 = 25 pts, 0.6+ = 0 pts). CONTEXT: Measures rigor and replication of RCT evidence from What Works Clearinghouse. Higher scores indicate more reliable, well-replicated interventions." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.evidence_maturity.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.evidence_maturity.score.toFixed(1)} <span className="text-lg text-slate-600">/ {selectedBubble.breakdown.evidence_maturity.max}</span>
                      </p>
                    </div>

                    {/* Components */}
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedBubble.breakdown.evidence_maturity.components).map(([key, component]) => {
                        const tooltipContent: { [key: string]: string } = {
                          'study_design_quality': 'CALCULATION: Average score across all studies based on WWC ratings - Meets standards without reservations = 25 pts, Meets with reservations = 15 pts, Does not meet = 5 pts. CONTEXT: Higher scores indicate more rigorous experimental designs meeting What Works Clearinghouse standards for causal inference.',
                          'replication_strength': 'CALCULATION: Based on number of independent RCT studies - 10+ studies = 25 pts, 7-9 studies = 22 pts, 5-6 studies = 20 pts, 3-4 studies = 15 pts, 2 studies = 10 pts, 1 study = 5 pts. CONTEXT: More replications provide stronger evidence that effects are reliable and not due to chance.',
                          'sample_adequacy': 'CALCULATION: Linear scale based on total students - 1,000+ students = 25 pts, proportionally less for fewer students. CONTEXT: Larger samples provide more statistical power and precision, reducing risk of false positives/negatives.',
                          'effect_consistency': 'CALCULATION: Based on standard deviation of effect sizes - 0.0 std dev = 25 pts, 0.6+ std dev = 0 pts, linear scale between. CONTEXT: Lower variance indicates effects are stable across studies/contexts. High variance suggests intervention effectiveness may depend on implementation conditions.'
                        };
                        return (
                          <div key={key} className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-1.5 mb-1.5">
                              <p className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                                {key.replace(/_/g, ' ')}
                              </p>
                              <InfoTooltip content={tooltipContent[key] || component.description} />
                            </div>
                            <p className="text-lg font-bold text-slate-900">
                              {component.score.toFixed(1)} <span className="text-sm text-slate-600">/ {component.max}</span>
                            </p>
                            <p className="text-xs text-slate-600 mt-2 leading-relaxed">{component.description}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {activeView === 'level3' && selectedBubble.breakdown.external_validity && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        External Validity Score
                      </h3>
                      <InfoTooltip content="CALCULATION: Diversity across contexts (out of 50 total): (1) Geographic regions - 2 points per unique state/region (max 20 pts for 10+ regions), (2) School types - 5 points per type: Public/Private/Charter (max 15 pts), (3) Grade levels/populations - 3 points per level: Elementary/Middle/High School/Undergraduate (max 15 pts). CONTEXT: Measures generalizability across diverse educational contexts. Higher scores indicate findings replicate across many settings, suggesting broader real-world applicability." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.external_validity.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg mb-4 border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.external_validity.score.toFixed(1)} <span className="text-lg text-slate-600">/ {selectedBubble.breakdown.external_validity.max}</span>
                      </p>
                    </div>

                  </div>
                )}

                {activeView === 'level3' && selectedBubble.breakdown.students_impacted && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Students Impacted
                      </h3>
                      <InfoTooltip content="CALCULATION: Sum of unique study sample sizes. For each study, we take the maximum sample size reported across all outcome findings to avoid double-counting students. Example: Study with 3 findings of sizes 1,000, 950, 1,050 counts as 1,050 students. CONTEXT: Represents actual scale of evidence - total number of unique students who participated in RCTs for this intervention. Higher numbers indicate more extensive real-world testing." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.students_impacted.description}</p>
                    <div className="bg-slate-100 p-4 rounded-lg border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.students_impacted.score.toLocaleString()}
                      </p>
                      <p className="text-sm text-slate-600 mt-1">students studied across RCTs</p>
                    </div>
                  </div>
                )}

                {activeView === 'level3' && selectedBubble.breakdown.effect_summary && (
                  <div className="border-l-4 border-slate-700 pl-5">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-lg font-bold text-slate-900 uppercase tracking-wide">
                        Average Effect Size
                      </h3>
                      <InfoTooltip content="CALCULATION: Mean of all Cohen's d values across findings. CONTEXT: Summarizes intervention effectiveness. Cohen's d interpretation: 0.2 = small, 0.5 = medium, 0.8 = large effect." />
                    </div>
                    <p className="text-sm text-slate-600 mb-3 leading-relaxed">{selectedBubble.breakdown.effect_summary.description}</p>

                    <div className="bg-slate-100 p-4 rounded-lg border border-slate-300">
                      <p className="text-3xl font-bold text-slate-900">
                        {selectedBubble.breakdown.effect_summary.average_effect_size}
                      </p>
                      <p className="text-sm text-slate-600 mt-1">Cohen's d across {selectedBubble.breakdown.effect_summary.num_findings} findings</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : activeView === 'level5' ? (
            <div className="p-7">
              <h2 className="text-2xl font-semibold text-slate-900 mb-6">Strategic Insights</h2>
              <div className="space-y-6">
                <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Early 2000s shift</h3>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    From roughly 2000–2010, evidence appears to become more generalizable, with interventions tested across a wider range of student populations, school contexts, and settings.
                  </p>
                </div>
                <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Scale outpaces learning</h3>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    Between about 2005–2015, areas like tutoring and adaptive instruction reach many more students, while newer areas (e.g., personalization and data-driven decision-making) begin to emerge but with a thinner evidence base.
                  </p>
                </div>
                <div className="mt-6 pt-6 border-t border-slate-200">
                  <p className="text-xs text-slate-500 leading-relaxed">
                    <strong>Tip:</strong> Click on any data point in the visualization to view detailed period analysis
                  </p>
                </div>
              </div>
            </div>
          ) : activeView.startsWith('p5-') && p5Data ? (
            <div className="p-7">
              <h2 className="text-2xl font-semibold text-slate-900 mb-6">P1: Core Instruction & Tutoring</h2>
              <div className="space-y-6">
                <div className="bg-blue-50 p-5 rounded-lg border border-blue-200">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">About This Pillar</h3>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {p5Data.metadata.description}
                  </p>
                </div>

                {activeView === 'p5-geographic' && p5InterventionColors.size > 0 && (
                  <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                    <h3 className="text-sm font-bold text-slate-900 mb-3">Intervention Colors</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {Array.from(p5InterventionColors.entries()).map(([intervention, color]) => (
                        <div key={intervention} className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: color }}></div>
                          <span className="text-xs text-slate-700 leading-tight">
                            {intervention.length > 35 ? intervention.substring(0, 35) + '...' : intervention}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Visualization Guide</h3>
                  <p className="text-sm text-slate-700 leading-relaxed mb-2">
                    <strong>Map Color:</strong> Estimated student density (total sample size divided by states covered)
                  </p>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong>Icons:</strong> 1 icon = 1 study (max 20 per state)
                  </p>
                </div>

                <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Filters Applied</h3>
                  <ul className="text-sm text-slate-700 leading-relaxed space-y-1">
                    {p5Data.metadata.filters_applied.map((filter, idx) => (
                      <li key={idx}>• {filter}</li>
                    ))}
                  </ul>
                </div>
                <div className="mt-6 pt-6 border-t border-slate-200">
                  <p className="text-xs text-slate-500 leading-relaxed">
                    <strong>Tip:</strong> Use the time slider to see how evidence distribution has evolved over time
                  </p>
                </div>
              </div>
            </div>
          ) : activeView === 'p1' && p1Data && p1ViewMode === 'interventions' ? (
            <div className="p-7">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Intervention Legend</h2>
              <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                Click on any data point in the visualization to view detailed study information and findings.
              </p>

              <div className="grid grid-cols-1 gap-2">
                {p1Data.intervention_series.map((series, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2 rounded hover:bg-slate-50 transition-colors">
                    <div
                      className="w-4 h-4 rounded-full flex-shrink-0"
                      style={{ backgroundColor: series.color }}
                    ></div>
                    <span className="text-sm text-slate-700">{series.label}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : activeView === 'p1' && p1Data && p1ViewMode === 'usecases' ? (
            <div className="p-7 overflow-y-auto">
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Strategic Context</h2>
              <p className="text-xs text-slate-500 mb-6 italic">
                Click on any data point to view detailed study information
              </p>

              {/* Context Section */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-blue-600 rounded"></div>
                  Context
                </h3>
                <p className="text-sm text-slate-700 leading-relaxed">
                  The What Works Clearinghouse (WWC) corpus of rigorous studies reveals how pre-LLM educational technology interventions were predominantly human-led, requiring significant teacher support and adaptation to reach effectiveness. We identified 20 unique interventions aligned with Core Instruction & Tutoring and mapped them to 5 use-cases. Notably, no WWC interventions mapped to Automated Grading—a capability now emerging with LLM technology.
                </p>
              </div>

              {/* Strategic Insights */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-green-600 rounded"></div>
                  Strategic Insights
                </h3>
                <div className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-lg border-l-4 border-green-500">
                    <p className="text-xs font-semibold text-slate-800 mb-2">Real-Time Feedback (65% of interventions)</p>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Most interventions require hybrid teacher-student approaches where teachers model the tool/system and students reciprocate behaviors. The high stability of favorable findings suggests these interventions depend heavily on proper modeling and consistent usage patterns.
                    </p>
                  </div>

                  <div className="bg-slate-50 p-4 rounded-lg border-l-4 border-yellow-500">
                    <p className="text-xs font-semibold text-slate-800 mb-2">Math Tutoring</p>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Math tutoring, particularly through intelligent tutoring systems and technology-enabled interventions, has shown consistent improvements in early learning outcomes throughout the years. However, these gains appear limited to immediate post-intervention assessments and are not indicative of long-term student outcomes in later grades. The advent of adaptive technologies has enhanced early math proficiency, but longitudinal effectiveness remains uncertain in pre-LLM systems.
                    </p>
                  </div>

                  <div className="bg-slate-50 p-4 rounded-lg border-l-4 border-blue-500">
                    <p className="text-xs font-semibold text-slate-800 mb-2">Instructional Planning & Teacher Coaching</p>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Pre-LLM interventions were more effective when targeted at teachers rather than students (evidenced by finding stability). This explains why hybrid teacher-student interventions showed the strongest favorable outcomes—teacher-mediated approaches were critical to success.
                    </p>
                  </div>
                </div>
              </div>

              {/* Points of Reflection */}
              <div>
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-purple-600 rounded"></div>
                  Points of Reflection: What to Look for Post-LLMs
                </h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      <strong>Direct comparison studies</strong> examining LLM-powered student tutoring in core subjects like Algebra 1, with attention to long-term math proficiency outcomes that WWC studies couldn't measure. Specifically, whether LLMs can replicate or exceed pre-LLM tutoring effects without intensive teacher mediation.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      <strong>Evidence of reduced teacher burden</strong> in instructional planning through LLM-assisted tools, exploring whether these technologies can shift the labor-intensive modeling requirements observed in pre-LLM Real-Time Feedback interventions.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      <strong>Autonomous student engagement patterns</strong> with LLM tutoring systems to assess whether the hybrid teacher-student modeling approach (critical to pre-LLM intervention success) remains necessary or if LLMs enable effective direct-to-student deployment.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      <strong>Rigorous evaluation of automated grading systems</strong> powered by LLMs, representing an entirely new intervention category absent from the WWC corpus. Particularly examining accuracy, fairness, and impact on learning outcomes across diverse student populations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : activeView === 'p1-current' && p1CurrentData ? (
            <div className="p-7 overflow-y-auto">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Current Evidence Landscape</h2>

              {/* Context Section */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-blue-600 rounded"></div>
                  Evidence Ladder Framework
                </h3>
                <p className="text-sm text-slate-700 leading-relaxed mb-4">
                  This visualization shows the current research landscape for <strong>{p1CurrentData.implementation_objective}</strong> using non-WWC studies from our knowledge graph. Papers are classified into 6 evidence rungs based on their study design and methodology.
                </p>
                <p className="text-sm text-slate-700 leading-relaxed">
                  <strong>Total Papers:</strong> {p1CurrentData.rungs.reduce((sum, r) => sum + r.paper_count, 0)} (Not Including {p1CurrentData.total_papers - p1CurrentData.rungs.reduce((sum, r) => sum + r.paper_count, 0)} Meta-Analyses)
                </p>
              </div>

              {/* Rung Descriptions */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-green-600 rounded"></div>
                  Evidence Rungs
                </h3>
                <div className="space-y-3">
                  {p1CurrentData.rungs.map((rung) => (
                    <div
                      key={rung.rung_number}
                      className="bg-slate-50 p-3 rounded-lg border-l-4"
                      style={{ borderColor: rung.paper_count > 0 ? '#3b82f6' : '#cbd5e1' }}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <p className="text-xs font-bold text-slate-800">
                          Rung {rung.rung_number}: {rung.rung_name}
                        </p>
                        <span className="text-xs font-semibold text-slate-600">
                          {rung.paper_count} papers
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {rung.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Insights */}
              <div>
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
                  <div className="w-1 h-4 bg-purple-600 rounded"></div>
                  Key Insights
                </h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Most evidence clusters at <strong>Rung 1 (Monitoring)</strong> and <strong>Rung 3 (Comparative)</strong>, indicating that much of the current research is exploratory or quasi-experimental.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      <strong>Rung 4 (Causal Effectiveness)</strong> shows {p1CurrentData.rungs.find(r => r.rung_number === 4)?.paper_count || 0} RCT studies, representing rigorous causal evidence.
                    </p>
                  </div>
                  <div className="flex gap-3">w
                    <div className="text-purple-600 font-bold text-sm flex-shrink-0">•</div>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Gaps at higher rungs (5-6) suggest opportunities for <strong>multi-site replication studies</strong> and <strong>personalized effectiveness research</strong> to understand who benefits most.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              <div className="text-center px-8">
                <p className="text-lg font-medium text-slate-700 mb-2">
                  Select a Category
                </p>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Click on any bubble in the visualization to view detailed analysis and evidence breakdown
                </p>
              </div>
            </div>
          )}
        </aside>
        </div>
      )}
    </div>
  );
}
