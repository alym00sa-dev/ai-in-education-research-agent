'use client';

import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { BubbleData } from '@/lib/types';

interface BubbleDialogProps {
  bubble: BubbleData | null;
  isOpen: boolean;
  onClose: () => void;
  level: 1 | 2;
}

export default function BubbleDialog({ bubble, isOpen, onClose, level }: BubbleDialogProps) {
  if (!bubble) return null;

  const { breakdown } = bubble;

  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-start justify-between mb-4">
            <Dialog.Title className="text-2xl font-bold text-gray-900 pr-8">
              {bubble.label}
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-gray-400 hover:text-gray-600 transition-colors">
                <X size={24} />
              </button>
            </Dialog.Close>
          </div>

          <div className="space-y-6">
            {/* Paper Count */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Papers Analyzed</p>
              <p className="text-3xl font-bold text-blue-600">{bubble.paper_count}</p>
            </div>

            {/* Level 2 Investment (if applicable) */}
            {level === 2 && breakdown.investment && (
              <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                <p className="text-sm text-gray-600 mb-1">R&D Investment Already Allocated</p>
                <p className="text-3xl font-bold text-green-700">{breakdown.investment.formatted}</p>
                <p className="text-xs text-gray-500 mt-2">{breakdown.investment.description}</p>
              </div>
            )}

            {/* X-Axis: Evidence Maturity */}
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Evidence Maturity (X-axis)
              </h3>
              <p className="text-sm text-gray-600 mb-2">{breakdown.evidence_maturity.description}</p>
              <div className="bg-purple-50 p-3 rounded-lg mb-3">
                <p className="text-2xl font-bold text-purple-600">
                  {breakdown.evidence_maturity.score.toFixed(1)} / {breakdown.evidence_maturity.max}
                </p>
              </div>

              {/* Components */}
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(breakdown.evidence_maturity.components).map(([key, component]) => (
                  <div key={key} className="bg-gray-50 p-3 rounded">
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-1">
                      {key.replace('_', ' ')}
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {component.score.toFixed(1)} / {component.max}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{component.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Y-Axis: Problem Scale (Level 1) OR Potential Impact (Level 2) */}
            {level === 1 && breakdown.problem_scale && (
              <div className="border-l-4 border-orange-500 pl-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Problem Burden Scale (Y-axis)
                </h3>
                <p className="text-sm text-gray-600 mb-2">{breakdown.problem_scale.description}</p>
                <div className="bg-orange-50 p-3 rounded-lg mb-3">
                  <p className="text-2xl font-bold text-orange-600">
                    {breakdown.problem_scale.score.toFixed(2)} / {breakdown.problem_scale.max}
                  </p>
                </div>

                {/* Distribution */}
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm font-semibold text-gray-700 mb-2">User Type Distribution</p>
                  <div className="space-y-1">
                    {Object.entries(breakdown.problem_scale.distribution).map(([type, count]) => (
                      <div key={type} className="flex justify-between text-sm">
                        <span className="text-gray-600">{type}</span>
                        <span className="font-semibold text-gray-900">{count} papers</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {level === 2 && breakdown.potential_impact && (
              <div className="border-l-4 border-orange-500 pl-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Potential Impact (Y-axis)
                </h3>
                <p className="text-sm text-gray-600 mb-2">{breakdown.potential_impact.description}</p>
                <div className="bg-orange-50 p-3 rounded-lg mb-3">
                  <p className="text-2xl font-bold text-orange-600">
                    {breakdown.potential_impact.score.toFixed(1)}
                  </p>
                </div>

                {/* Outcomes Targeted */}
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm font-semibold text-gray-700 mb-2">
                    Outcomes Targeted ({breakdown.potential_impact.outcomes_targeted.length})
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {breakdown.potential_impact.outcomes_targeted.map((outcome, idx) => (
                      <span key={idx} className="text-xs bg-white px-2 py-1 rounded border border-gray-200">
                        {outcome}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Bubble Size: Effort Required (Level 1) OR R&D Required (Level 2) */}
            {level === 1 && breakdown.effort_required && (
              <div className="border-l-4 border-red-500 pl-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Effort Required (Bubble Size)
                </h3>
                <p className="text-sm text-gray-600 mb-2">{breakdown.effort_required.description}</p>
                <div className="bg-red-50 p-3 rounded-lg mb-3">
                  <p className="text-2xl font-bold text-red-600">
                    {breakdown.effort_required.score.toFixed(2)}
                  </p>
                </div>

                {/* Components */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-1">
                      System Impact
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {breakdown.effort_required.components.system_impact.score.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {breakdown.effort_required.components.system_impact.description}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-1">
                      Decision Complexity
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {breakdown.effort_required.components.decision_complexity.score.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {breakdown.effort_required.components.decision_complexity.description}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {level === 2 && breakdown.r_and_d_required && (
              <div className="border-l-4 border-red-500 pl-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  R&D Investment Required (Bubble Size)
                </h3>
                <p className="text-sm text-gray-600 mb-2">{breakdown.r_and_d_required.description}</p>
                <div className="bg-red-50 p-3 rounded-lg mb-3">
                  <p className="text-2xl font-bold text-red-600">
                    {breakdown.r_and_d_required.score.toFixed(2)}
                  </p>
                </div>

                {/* Components */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-1">
                      Evidence Maturity Gap
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {breakdown.r_and_d_required.components.evidence_maturity_gap.score.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {breakdown.r_and_d_required.components.evidence_maturity_gap.description}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-1">
                      Evaluation Burden
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      {breakdown.r_and_d_required.components.evaluation_burden.score.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {breakdown.r_and_d_required.components.evaluation_burden.description}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <Dialog.Close asChild>
            <button className="mt-6 w-full bg-gray-900 text-white py-3 rounded-lg hover:bg-gray-700 transition-colors font-semibold">
              Close
            </button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
