'use client';

import { useState } from 'react';
import type { PipelineState } from '@/types/pipeline';
import { IconSend, IconCheck, IconAlertCircle } from './Icons';
import BriefSuggestions, { type SelectedChip } from './BriefSuggestions';

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
  const [selectedSuggestions, setSelectedSuggestions] = useState<SelectedChip[]>([]);

  const isRunning   = state.status === 'running';
  const isCompleted = state.status === 'completed';
  const hasError    = state.status === 'error';
  const charCount   = brief.trim().length;
  const canSubmit   = charCount > 10 && !isRunning;

  /** Toggle de un chip: añade si no estaba, quita si estaba */
  function handleToggle(chip: SelectedChip) {
    setSelectedSuggestions(prev => {
      const exists = prev.find(s => s.key === chip.key);
      return exists ? prev.filter(s => s.key !== chip.key) : [...prev, chip];
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;

    // Combinar el brief del usuario con el contexto seleccionado
    const context = selectedSuggestions.map(s => s.text).join(' ');
    const fullBrief = context
      ? brief.trim() + '\n\n' + context
      : brief.trim();

    setSelectedSuggestions([]); // limpiar tras enviar
    onGenerate(fullBrief);
  }

  return (
    <div className="flex flex-col gap-4 p-5 bg-white">
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
            rows={5}
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

        {/* ── Tags de sugerencias seleccionadas ─────────────────────────── */}
        {selectedSuggestions.length > 0 && (
          <div className="flex flex-wrap gap-1.5 p-2.5 bg-indigo-50 rounded-xl border border-indigo-100">
            <span className="text-[10px] text-indigo-500 font-semibold self-center mr-0.5 uppercase tracking-wider">
              Contexto:
            </span>
            {selectedSuggestions.map(s => (
              <span
                key={s.key}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-white border border-indigo-200 text-indigo-700 rounded-full text-[11px] font-medium shadow-sm"
              >
                {s.label}
                <button
                  type="button"
                  onClick={() => handleToggle(s)}
                  className="text-indigo-300 hover:text-indigo-600 leading-none ml-0.5 transition-colors"
                  aria-label={"Quitar " + s.label}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}

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
              {selectedSuggestions.length > 0
                ? "Generar con " + selectedSuggestions.length + " contexto" + (selectedSuggestions.length > 1 ? "s" : "")
                : "Generar interfaz"}
            </>
          )}
        </button>
      </form>

      {/* ── Panel de sugerencias inteligentes ─────────────────────────── */}
      {!isRunning && !isCompleted && (
        <BriefSuggestions
          brief={brief}
          selectedKeys={selectedSuggestions.map(s => s.key)}
          onToggle={handleToggle}
          disabled={isRunning}
        />
      )}

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
