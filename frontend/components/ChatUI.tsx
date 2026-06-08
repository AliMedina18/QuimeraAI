'use client';

import { useState } from 'react';
import type { PipelineState } from '@/types/pipeline';

interface Props {
  state: PipelineState;
  onGenerate: (brief: string, projectType?: string) => void;
}

/**
 * ChatUI - Componente para ingresar brief y disparar el pipeline
 * Pipeline: 2 pasos (analyzing → generating)
 */
export default function ChatUI({ state, onGenerate }: Props) {
  const [brief, setBrief] = useState('');
  const [projectType, setProjectType] = useState('');

  const isRunning = state.status === 'running';
  const isCompleted = state.status === 'completed';
  const hasError = state.status === 'error';
  const canSubmit = brief.trim().length > 10 && !isRunning;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onGenerate(brief.trim(), projectType.trim() || undefined);
  }

  const stepLabels: Record<string, { label: string; icon: string }> = {
    analyzing: { label: 'Analizando diseño...', icon: '🎨' },
    generating: { label: 'Generando React...', icon: '⚛' },
    completed: { label: 'Completado', icon: '✅' },
  };

  const currentStepInfo = state.currentStep ? stepLabels[state.currentStep] : null;

  return (
    <div className="flex flex-col gap-4 p-5 h-full">
      {/* Formulario */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          Brief de diseño
        </label>
        <textarea
          value={brief}
          onChange={e => setBrief(e.target.value)}
          placeholder="Ej: Dashboard de analytics para startup SaaS, estilo minimalista, colores corporativos azul y blanco, público tech…"
          disabled={isRunning}
          rows={5}
          className="
            w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5
            text-sm text-gray-800 placeholder-gray-400 resize-none
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:bg-gray-50 disabled:text-gray-400 transition-colors
          "
        />

        <div className="flex gap-2">
          <input
            type="text"
            value={projectType}
            onChange={e => setProjectType(e.target.value)}
            placeholder="Tipo (opcional): dashboard, landing, app…"
            disabled={isRunning}
            className="
              flex-1 rounded-lg border border-gray-200 bg-white px-3 py-2
              text-sm text-gray-800 placeholder-gray-400
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              disabled:bg-gray-50 disabled:text-gray-400 transition-colors
            "
          />
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="
            w-full rounded-lg py-2.5 px-4 text-sm font-semibold
            bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-colors duration-150
          "
        >
          {isRunning ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generando…
            </span>
          ) : (
            '✦ Generar'
          )}
        </button>
      </form>

      {/* Status indicator */}
      {isRunning && currentStepInfo && (
        <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <span className="text-lg animate-pulse">{currentStepInfo.icon}</span>
          <span className="text-sm font-medium text-blue-700">{currentStepInfo.label}</span>
        </div>
      )}

      {/* Error display */}
      {hasError && (
        <div className="flex flex-col gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs font-semibold text-red-700">Error</p>
          <p className="text-xs text-red-600">{state.error}</p>
        </div>
      )}

      {/* Completed summary */}
      {isCompleted && (
        <div className="flex flex-col gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-xs font-semibold text-green-700">✅ Completado</p>
          <div className="text-xs text-green-600 space-y-1">
            <p>• DESIGN.md generado ({state.designMarkdown.length} caracteres)</p>
            <p>• HTML generado ({state.htmlOutput.length} caracteres)</p>
            {state.elapsedMs && (
              <p>• Tiempo: {(state.elapsedMs / 1000).toFixed(2)}s</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
