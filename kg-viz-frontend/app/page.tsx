'use client';

import { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import BubbleChart from '@/components/BubbleChart';
import InfoTooltip from '@/components/InfoTooltip';
import { fetchLevel1Data, fetchLevel2Data, fetchLevel3Data } from '@/lib/api';
import { BubbleData, VisualizationResponse } from '@/lib/types';

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

type ViewType = 'intro' | 'level1' | 'level2' | 'level3';

export default function Home() {
  const [level1Data, setLevel1Data] = useState<VisualizationResponse | null>(null);
  const [level2Data, setLevel2Data] = useState<VisualizationResponse | null>(null);
  const [level3Data, setLevel3Data] = useState<VisualizationResponse | null>(null);
  const [selectedBubble, setSelectedBubble] = useState<BubbleData | null>(null);
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
        const [l1, l2, l3] = await Promise.all([
          fetchLevel1Data(),
          fetchLevel2Data(),
          fetchLevel3Data()
        ]);
        setLevel1Data(l1);
        setLevel2Data(l2);
        setLevel3Data(l3);
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

  // Calculate x-axis domain from Level 1 data and use for both levels
  const level1XValues = level1Data?.bubbles.map(b => b.x) || [];
  const xMin = level1XValues.length > 0 ? Math.min(...level1XValues) : 0;
  const xMax = level1XValues.length > 0 ? Math.max(...level1XValues) : 100;
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
                setShowOutcomesTargeted(false);
              }}
              className="appearance-none bg-white text-slate-900 px-6 py-2 pr-10 rounded-lg font-medium shadow-md border-2 border-slate-200 focus:outline-none focus:ring-2 focus:ring-slate-400 cursor-pointer"
            >
              <option value="intro">Introduction</option>
              <option value="level1">Level 1: Problem Burden Map</option>
              <option value="level2">Level 2: Intervention Evidence Map</option>
              <option value="level3">Level 3: Evidence-Based Interventions (RCT)</option>
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

              {/* Database Status Note */}
              <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-900">
                      Pilot Version - Living Database
                    </p>
                    <p className="text-sm text-blue-800 mt-1">
                      This is a pilot version of the dashboard based on a limited initial dataset. The visualizations reflect data from our actively expanding research database. New studies and evidence are continuously being added to provide the most current view of the field.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Two-Level Framework */}
            <div className="grid grid-cols-2 gap-8 mb-16">
              {/* Level 1 */}
              <div className="border-l-4 border-slate-900 pl-6">
                <div className="mb-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Level 1</span>
                  <h3 className="text-2xl font-semibold text-slate-900 mt-1">Problem Burden Map</h3>
                </div>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  Identifies which educational challenges have sufficient evidence to inform action and which require further research investment.
                </p>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">Evidence Maturity</p>
                      <p className="text-slate-500">Composite score of study design, consistency, and external validity</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">Problem Burden Scale</p>
                      <p className="text-slate-500">Scope of systemic impact from classroom to policy level</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">Effort Required</p>
                      <p className="text-slate-500">Coordination complexity and system-level changes needed</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Level 2 */}
              <div className="border-l-4 border-slate-900 pl-6">
                <div className="mb-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Level 2</span>
                  <h3 className="text-2xl font-semibold text-slate-900 mt-1">Intervention Evidence Map</h3>
                </div>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  Evaluates intervention readiness by mapping evidence maturity against alignment to high-burden educational challenges.
                </p>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">Evidence Maturity</p>
                      <p className="text-slate-500">Same composite scoring as Level 1 for consistency</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">Potential Impact</p>
                      <p className="text-slate-500">Cumulative burden of problems addressed by intervention</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-1 h-1 bg-slate-400 rounded-full mt-2"></div>
                    <div>
                      <p className="font-medium text-slate-900">R&D Investment</p>
                      <p className="text-slate-500">Gap to field readiness and evaluation requirements</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Priority Classification */}
            <div className="bg-slate-50 border border-slate-200 p-8 mb-16">
              <h4 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-6">Priority Classification</h4>
              <div className="grid grid-cols-3 gap-6">
                <div className="flex items-start gap-3">
                  <div className="w-3 h-3 rounded-full bg-green-500 mt-1 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold text-slate-900 mb-1">High Priority</p>
                    <p className="text-sm text-slate-600">High evidence maturity and high burden/impact. Ready for scaled action.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-3 h-3 rounded-full bg-yellow-500 mt-1 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold text-slate-900 mb-1">On Watch</p>
                    <p className="text-sm text-slate-600">Either high burden/impact with insufficient evidence, or high evidence with lower burden. Proceed with caution.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-3 h-3 rounded-full bg-pink-500 mt-1 flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold text-slate-900 mb-1">Research Gap</p>
                    <p className="text-sm text-slate-600">Below median threshold. Requires foundational research investment.</p>
                  </div>
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
          {/* Left Sidebar - Legend & Controls */}
          <aside className="w-80 border-r border-slate-200 bg-gradient-to-b from-slate-50 to-white p-6 overflow-y-auto relative z-20">
            {/* Legend */}
            <div className="mb-7 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-wide">Visualization Guide</h3>

            <div className="space-y-4 text-sm">
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
            </div>
          </div>

          {/* Priority Filter */}
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

        {/* Center - Bubble Chart */}
        <main className="flex-1 p-8 overflow-hidden bg-slate-50 relative z-10">
          <div className="h-full bg-white border border-slate-200 rounded-xl shadow-md flex flex-col">
            <div className="flex-1 min-h-0">
              {currentData && (
                <BubbleChart
                  data={visibleBubbles}
                  allData={currentData.bubbles}
                  xLabel={currentData.metadata.x_axis.label}
                  yLabel={currentData.metadata.y_axis.label}
                  onBubbleClick={handleBubbleClick}
                  selectedBubbleId={selectedBubble?.id || null}
                  xDomain={xDomain}
                  yMedian={currentData.metadata.y_axis.median}
                />
              )}
            </div>
            {/* So-What Blurb */}
            {currentData && (
              <div className="border-t border-slate-200 px-6 py-4 bg-slate-50">
                {activeView === 'level1' ? (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map helps us prioritize where to invest by combining problem burden with evidence readiness—so we focus on high-impact learning challenges that are both important and actionable.
                  </p>
                ) : activeView === 'level2' ? (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map evaluates intervention readiness by showing which AI-enabled approaches have both strong evidence and clear alignment to urgent educational problems as outlined in Level 1.
                  </p>
                ) : (
                  <p className="text-sm text-slate-700 leading-relaxed">
                    <strong className="text-slate-900">Strategic Insight:</strong> This map showcases proven interventions from rigorous RCTs (What Works Clearinghouse), highlighting which tech-compatible approaches have strong evidence AND generalize across diverse contexts—representing millions of students already impacted.
                  </p>
                )}
              </div>
            )}
          </div>
        </main>

        {/* Right Sidebar - Detail Panel */}
        <aside className="w-96 border-l border-slate-200 bg-white overflow-y-auto relative z-20">
          {selectedBubble ? (
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

                  {/* Study Design Breakdown */}
                  {selectedBubble.breakdown.study_design_distribution && Object.keys(selectedBubble.breakdown.study_design_distribution).length > 0 && (
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

                {/* Implication Panel */}
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

                {/* Evidence Maturity */}
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
