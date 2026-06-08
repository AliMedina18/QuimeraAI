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

  const isRunning = state.status === 'running';
  const isCompleted = state.status === 'completed';
  const hasError = state.status === 'error';
  const canSubmit = brief.trim().length > 10 && !isRunning;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onGenerate(brief.trim());
  }

  const stepLabels: Record<string, { label: string; icon: string }> = {
    analyzing: { label: 'Analizando...', icon: '✨' },
    generating: { label: 'Generando...', icon: '⚡' },
    completed: { label: 'Completado', icon: '✓' },
  };

  const currentStepInfo = state.currentStep ? stepLabels[state.currentStep] : null;

  return (
    <div className="flex flex-col gap-4 p-6 h-full bg-white">
      {/* Formulario */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="text-xs font-semibold text-gray-900 uppercase tracking-wide block mb-2">
            Descripción del diseño
          </label>
          <textarea
            value={brief}
            onChange={e => setBrief(e.target.value)}
            placeholder="Ej: Restaurante de sushi premium. Colores: negro, rojo, dorado. Hero, menú, testimonios, reservas…"
            disabled={isRunning}
            rows={6}
            className="
              w-full rounded-lg border border-gray-200 bg-white px-4 py-3
              text-sm text-gray-800 placeholder-gray-400 resize-none
              focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400
              disabled:bg-gray-50 disabled:text-gray-400 
              transition-all duration-150
            "
          />
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="
            w-full rounded-lg py-3 px-4 text-sm font-semibold
            bg-blue-600 text-white hover:bg-blue-700 
            active:bg-blue-800
            disabled:opacity-50 disabled:cursor-not-allowed
            shadow-sm hover:shadow-md
            transition-all duration-150
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

      {/* Status indicator */}
      {isRunning && currentStepInfo && (
        <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-100 rounded-lg mt-2">
          <span className="text-lg animate-pulse">{currentStepInfo.icon}</span>
          <span className="text-sm font-medium text-blue-900">{currentStepInfo.label}</span>
        </div>
      )}

      {/* Error display */}
      {hasError && (
        <div className="flex flex-col gap-2 p-4 bg-red-50 border border-red-100 rounded-lg mt-2">
          <p className="text-xs font-semibold text-red-900">⚠ Error</p>
          <p className="text-xs text-red-700">{state.error}</p>
        </div>
      )}

      {/* Completed summary */}
      {isCompleted && (
        <div className="flex flex-col gap-3 p-4 bg-green-50 border border-green-100 rounded-lg mt-2">
          <p className="text-xs font-semibold text-green-900">✓ Diseño generado</p>
          <div className="text-xs text-green-700 space-y-1">
            {state.designMarkdown && (
              <p>• Sistema de diseño creado</p>
            )}
            {state.htmlOutput && (
              <p>• Sitio web generado</p>
            )}
            {state.elapsedMs && (
              <p>• Tiempo: {(state.elapsedMs / 1000).toFixed(2)}s</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
