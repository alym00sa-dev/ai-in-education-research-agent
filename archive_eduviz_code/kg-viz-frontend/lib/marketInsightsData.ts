// Market Insights Data extracted from market_demo.html

export const marketInsightsData = {
  // Memory Growth By Year
  memoryGrowthByYear: {
    2023: {
      total: 3,
      byProvider: {
        Google: 2,
        Microsoft: 1,
        OpenAI: 0,
        Anthropic: 0,
        Meta: 0
      }
    },
    2024: {
      total: 16,
      byProvider: {
        Google: 5,
        Microsoft: 6,
        OpenAI: 3,
        Anthropic: 2,
        Meta: 0
      }
    },
    2025: {
      total: 14,
      byProvider: {
        Google: 4,
        Microsoft: 3,
        OpenAI: 2,
        Anthropic: 1,
        Meta: 4
      }
    }
  },

  // Non-Hyperscaler Memory Products
  nonHyperscalerMemoryData: [
    { year: 2023, provider: 'Rewind', product: 'Rewind AI', count: 1 },
    { year: 2023, provider: 'Notion', product: 'Notion AI', count: 1 },
    { year: 2023, provider: 'Mem', product: 'Mem AI', count: 1 },
    { year: 2023, provider: 'Otter', product: 'Otter.ai', count: 1 },
    { year: 2024, provider: 'Limitless', product: 'Limitless AI', count: 1 },
    { year: 2024, provider: 'Perplexity', product: 'Perplexity Pro', count: 1 },
    { year: 2024, provider: 'Arc', product: 'Arc Browser AI', count: 1 },
    { year: 2024, provider: 'Dropbox', product: 'Dropbox Dash', count: 1 },
    { year: 2024, provider: 'Typeface', product: 'Typeface Enterprise', count: 1 },
    { year: 2024, provider: 'Cody', product: 'Sourcegraph Cody', count: 1 },
    { year: 2024, provider: 'Readwise', product: 'Readwise Reader 2.0', count: 1 },
    { year: 2024, provider: 'Glean', product: 'Glean Enterprise', count: 1 },
    { year: 2025, provider: 'Adept', product: 'ACT Agents', count: 1 },
    { year: 2025, provider: 'Inflection', product: 'Pi 2', count: 1 },
    { year: 2025, provider: 'Notion', product: 'Memory Blocks', count: 1 },
    { year: 2025, provider: 'Descript', product: 'Descript AI', count: 1 }
  ],

  // Agent Features (Cumulative)
  agentFeatures: [
    { provider: 'Google', '2023': 2, '2024': 6, '2025': 10 },
    { provider: 'Microsoft', '2023': 1, '2024': 3, '2025': 10 },
    { provider: 'OpenAI', '2023': 3, '2024': 5, '2025': 10 },
    { provider: 'Anthropic', '2023': 3, '2024': 5, '2025': 8 },
    { provider: 'Meta', '2023': 3, '2024': 6, '2025': 10 }
  ],

  // Memory Openness vs Lock-In Matrix
  opennessMatrix: [
    {
      name: 'Google',
      openness: 2.5,  // Low openness (0-10 scale)
      lockIn: 7.5,    // High lock-in (0-10 scale)
      color: '#4285f4',
      description: 'Gemini + Workspace memory features tightly bound to Google identity. Lowest openness, highest lock-in.'
    },
    {
      name: 'Microsoft',
      openness: 6.0,  // Medium-high openness
      lockIn: 5.0,    // Medium lock-in
      color: '#00a4ef',
      description: 'Microsoft Graph identity system integrated with Copilot memory. Medium-high openness, medium lock-in.'
    },
    {
      name: 'OpenAI',
      openness: 4.5,  // Medium openness
      lockIn: 6.0,    // High-ish lock-in
      color: '#ff6b35',
      description: 'Memory features tied to ChatGPT account/workspace. Medium openness, high-ish lock-in.'
    },
    {
      name: 'Anthropic',
      openness: 7.0,  // High openness
      lockIn: 3.5,    // Low lock-in
      color: '#d4a574',
      description: 'Claude organizational workspaces with comparatively lower identity binding. High openness, low lock-in.'
    },
    {
      name: 'Meta',
      openness: 8.5,  // Highest openness
      lockIn: 2.5,    // Lowest lock-in
      color: '#00d4aa',
      description: 'Open-source models with developer-managed memory infrastructure. Highest openness, low lock-in.'
    }
  ],

  // Recall Depth History (Context Window Growth)
  recallDepthHistory: [
    // 2023 Q1
    { date: '2023-03', provider: 'OpenAI', model: 'GPT-3.5 Turbo', depth: 10000 },
    { date: '2023-03', provider: 'OpenAI', model: 'GPT-4', depth: 25000 },
    { date: '2023-07', provider: 'OpenAI', model: 'Claude 2', depth: 90000 },
    { date: '2023-07', provider: 'Meta', model: 'Llama 2', depth: 4000 },
    // 2023 Q4
    { date: '2023-11', provider: 'OpenAI', model: 'GPT-4 Turbo', depth: 75000 },
    { date: '2023-11', provider: 'Anthropic', model: 'Claude 2.1', depth: 135000 },
    { date: '2023-12', provider: 'Google', model: 'Gemini Pro 1.0', depth: 25000 },
    { date: '2023-12', provider: 'Microsoft', model: 'Copilot (GPT-4 Turbo)', depth: 75000 },
    // 2024 Q1
    { date: '2024-02', provider: 'Google', model: 'Gemini 1.5 Flash', depth: 300000 },
    { date: '2024-02', provider: 'Google', model: 'Gemini 1.5 Pro', depth: 650000 },
    { date: '2024-03', provider: 'Anthropic', model: 'Claude 3 Opus', depth: 190000 },
    { date: '2024-03', provider: 'Anthropic', model: 'Claude 3 Sonnet', depth: 165000 },
    // 2024 Q2
    { date: '2024-04', provider: 'Meta', model: 'Llama 3 8B', depth: 6000 },
    { date: '2024-04', provider: 'Meta', model: 'Llama 3 70B', depth: 50000 },
    { date: '2024-04', provider: 'Microsoft', model: 'Phi-3 Medium', depth: 45000 },
    { date: '2024-04', provider: 'Microsoft', model: 'Phi-3 Mini', depth: 30000 },
    { date: '2024-05', provider: 'OpenAI', model: 'GPT-4o', depth: 90000 },
    { date: '2024-05', provider: 'Microsoft', model: 'Copilot (GPT-4o)', depth: 90000 },
    // 2024 Q3
    { date: '2024-07', provider: 'Meta', model: 'Llama 3.1 70B', depth: 70000 },
    { date: '2024-07', provider: 'Meta', model: 'Llama 3.1 405B', depth: 90000 },
    // 2025 Q1
    { date: '2025-01', provider: 'Meta', model: 'Llama 4 (Preview)', depth: 160000 }
  ]
};

// Helper to calculate cumulative agent features by quarter
export function getAgentFeaturesTimeline() {
  return [
    { date: '2024-01', Google: 2, Microsoft: 1, OpenAI: 1, Anthropic: 0 },
    { date: '2024-04', Google: 4, Microsoft: 3, OpenAI: 2, Anthropic: 1 },
    { date: '2024-07', Google: 6, Microsoft: 5, OpenAI: 4, Anthropic: 2 },
    { date: '2024-10', Google: 8, Microsoft: 8, OpenAI: 5, Anthropic: 3 },
    { date: '2025-01', Google: 9, Microsoft: 10, OpenAI: 6, Anthropic: 4 },
  ];
}

// Helper to get non-hyperscaler counts by year
export function getNonHyperscalerCounts() {
  return {
    2023: 4,
    2024: 8,
    2025: 4
  };
}
