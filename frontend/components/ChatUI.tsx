'use client';

import { useState } from 'react';
import type { PipelineState, PipelineStep } from '@/types/pipeline';

interface Props {
  state: PipelineState;
  onGenerate: (brief: string, projectType: string) => void;
}

const STEPS: { id: PipelineStep; label: string; icon: string }[] = [
  { id: 'analisis',    label: 'Analizando diseño',   icon: '🔍' },
  { id: 'evaluacion',  label: 'Evaluando criterios',  icon: '📊' },
  { id: 'correccion',  label: 'Refinando diseño',     icon: '✏️' },
  { id: 'generacion',  label: 'Generando código',     icon: '⚡' },
  { id: 'guardando',   label: 'Guardando resultado',  icon: '💾' },
  { id: 'completado',  label: 'Completado',           icon: '✅' },
];

const STEP_ORDER: PipelineStep[] = STEPS.map(s => s.id);

function stepIndex(step: PipelineStep | null) {
  if (!step) return -1;
  return STEP_ORDER.indexOf(step);
}

export default function ChatUI({ state, onGenerate }: Props) {
  const [brief, setBrief] = useState('');
  const [projectType, setProjectType] = useState('');

  const isRunning = state.status === 'running';
  const canSubmit = brief.trim().length > 10 && !isRunning;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onGenerate(brief.trim(), projectType.trim());
  }

  const activeIdx = stepIndex(state.currentStep);

  return (
    <div className="flex flex-col gap-4 p-5 h-full">
      {/* Formulario siempre visible */}
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
            placeholder="Tipo (opcional): dashboard, landing, e-commerce…"
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
            '✦ Generar interfaz'
          )}
        </button>
      </form>

      {/* Pipeline progress */}
      {state.status !== 'idle' && (
        <div className="flex flex-col gap-1 mt-2">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">
            Progreso del pipeline
          </p>

          {STEPS.map((step, i) => {
            const isDone    = i < activeIdx;
            const isActive  = i === activeIdx;
            const isPending = i > activeIdx;

            return (
              <div
                key={step.id}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                  ${isActive  ? 'bg-blue-50 border border-blue-200' : ''}
                  ${isDone    ? 'opacity-60' : ''}
                  ${isPending ? 'opacity-30' : ''}
                `}
              >
                <span className={`text-base ${isActive ? 'animate-pulse' : ''}`}>
                  {isDone ? '✅' : step.icon}
                </span>
                <span className={`flex-1 ${isActive ? 'font-semibold text-blue-700' : 'text-gray-600'}`}>
                  {step.label}
                </span>
                {isActive && isRunning && (
                  <span className="inline-block w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Iteración actual */}
      {state.currentIteration > 0 && state.status === 'running' && (
        <p className="text-xs text-gray-400 text-center">
          Iteración {state.currentIteration} / 3
        </p>
      )}

      {/* Critique preview cuando está en corrección */}
      {state.currentStep === 'correccion' && state.critiquePreview && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
          <p className="font-semibold mb-1">🔧 Refinando:</p>
          <p>{state.critiquePreview}</p>
        </div>
      )}

      {/* Score interim durante evaluacion */}
      {state.overallScore !== null && state.status === 'running' && (
        <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
          <span className="text-xs text-gray-500">Score actual</span>
          <span
            className={`text-sm font-bold ${
              state.overallScore >= 85
                ? 'text-green-600'
                : state.overallScore >= 70
                ? 'text-yellow-600'
                : 'text-red-500'
            }`}
          >
            {state.overallScore.toFixed(1)}
          </span>
        </div>
      )}

      {/* Error */}
      {state.status === 'error' && state.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-xs text-red-700">
          <p className="font-semibold mb-1">❌ Error</p>
          <p>{state.error}</p>
        </div>
      )}

      {/* Completado */}
      {state.status === 'completed' && state.elapsedMs !== null && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-xs text-green-800">
          <p className="font-semibold">✅ Diseño generado</p>
          <p className="text-green-600 mt-0.5">
            {(state.elapsedMs / 1000).toFixed(1)}s · {state.currentIteration} iteración(es)
          </p>
          {state.projectId && (
            <p className="text-green-500 mt-0.5 font-mono truncate">
              ID: {state.projectId}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
