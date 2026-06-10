'use client';

import { useState } from 'react';
import type { PipelineState } from '@/types/pipeline';
import { IconSend, IconCheck, IconAlertCircle } from './Icons';

interface Props {
  state: PipelineState;
  onGenerate: (brief: string, projectType?: string) => void;
}

const STEP_LABELS: Record<string, string> = {
  analyzing:  'Analizando brief…',
  generating: 'Generando código…',
  completed:  'Completado',
};

export default function ChatUI({ state, onGenerate }: Props) {
  const [brief, setBrief] = useState('');

  const isRunning   = state.status === 'running';
  const isCompleted = state.status === 'completed';
  const hasError    = state.status === 'error';
  const charCount   = brief.trim().length;
  const canSubmit   = charCount > 10 && !isRunning;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onGenerate(brief.trim());
  }

  return (
    <div className="flex flex-col gap-4 p-6 h-full bg-white">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-widest block mb-2">
            Descripción del diseño
          </label>
          <textarea
            value={brief}
            onChange={e => setBrief(e.target.value)}
            placeholder="Ej: Restaurante de sushi premium. Colores: negro, rojo, dorado. Hero, menú, testimonios, reservas…"
            disabled={isRunning}
            rows={6}
            className="
              w-full rounded-xl border border-gray-200 bg-white px-4 py-3
              text-sm text-gray-800 placeholder-gray-400 resize-none
              focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100
              disabled:bg-gray-50 disabled:text-gray-400
              transition-all duration-150
            "
          />
          <p className="text-[11px] text-gray-400 mt-1 text-right">
            {charCount} / mín. 10 caracteres
          </p>
        </div>

        <button
          type="submit"
          disabled={!canSubmit}
          className="
            w-full rounded-xl py-3 px-4 text-sm font-semibold
            bg-indigo-600 text-white hover:bg-indigo-700
            active:bg-indigo-800
            disabled:opacity-40 disabled:cursor-not-allowed
            shadow-sm hover:shadow-md
            transition-all duration-150
            flex items-center justify-center gap-2
          "
        >
          {isRunning ? (
            <>
              <span className="inline-block w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"/>
              Generando…
            </>
          ) : (
            <>
              <IconSend size={14}/>
              Generar interfaz
            </>
          )}
        </button>
      </form>

      {/* Estado de progreso */}
      {isRunning && state.currentStep && (
        <div className="flex items-center gap-3 p-3.5 bg-indigo-50 border border-indigo-100 rounded-xl">
          <span className="inline-block w-3.5 h-3.5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin flex-shrink-0"/>
          <span className="text-sm font-medium text-indigo-800">
            {STEP_LABELS[state.currentStep] ?? state.currentStep}
          </span>
        </div>
      )}

      {/* Error */}
      {hasError && (
        <div className="flex items-start gap-3 p-3.5 bg-red-50 border border-red-100 rounded-xl">
          <IconAlertCircle size={15} className="text-red-500 flex-shrink-0 mt-0.5"/>
          <div>
            <p className="text-xs font-semibold text-red-800 mb-0.5">Error al generar</p>
            <p className="text-xs text-red-700">{state.error}</p>
          </div>
        </div>
      )}

      {/* Completado */}
      {isCompleted && (
        <div className="flex items-start gap-3 p-3.5 bg-green-50 border border-green-100 rounded-xl">
          <IconCheck size={15} className="text-green-600 flex-shrink-0 mt-0.5"/>
          <div className="space-y-0.5">
            <p className="text-xs font-semibold text-green-800">Diseño generado</p>
            {state.designMarkdown && <p className="text-xs text-green-700">Sistema de diseño creado</p>}
            {state.htmlOutput     && <p className="text-xs text-green-700">Sitio web generado</p>}
            {state.elapsedMs      && <p className="text-xs text-green-600">Tiempo: {(state.elapsedMs / 1000).toFixed(2)}s</p>}
          </div>
        </div>
      )}
    </div>
  );
}
