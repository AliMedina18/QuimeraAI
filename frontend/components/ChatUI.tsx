'use client';

import { useState, useEffect } from 'react';
import type { PipelineState } from '@/types/pipeline';
import { IconSend, IconCheck, IconAlertCircle } from './Icons';
import BriefSuggestions, { type SelectedChip } from './BriefSuggestions';

interface Props {
  state: PipelineState;
  onGenerate: (brief: string) => void;
  externalBrief?: string | null;
}

const STEP_LABELS: Record<string, string> = {
  analyzing:  'Analizando brief…',
  generating: 'Generando código…',
  completed:  'Completado',
};

export default function ChatUI({ state, onGenerate, externalBrief }: Props) {
  const [brief, setBrief] = useState('');
  const [selectedSuggestions, setSelectedSuggestions] = useState<SelectedChip[]>([]);

  useEffect(() => {
    if (externalBrief) setBrief(externalBrief);
  }, [externalBrief]);

  const isRunning   = state.status === 'running';
  const isCompleted = state.status === 'completed';
  const hasError    = state.status === 'error';
  const charCount   = brief.trim().length;
  const canSubmit   = charCount > 10 && !isRunning;

  function handleToggle(chip: SelectedChip) {
    setSelectedSuggestions(prev => {
      const exists = prev.find(s => s.key === chip.key);
      return exists ? prev.filter(s => s.key !== chip.key) : [...prev, chip];
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    const context   = selectedSuggestions.map(s => s.text).join(' ');
    const fullBrief = context ? brief.trim() + '\n\n' + context : brief.trim();
    setSelectedSuggestions([]);
    onGenerate(fullBrief);
  }

  return (
    <div className="flex flex-col gap-5 p-5">

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">

        <label className="text-[10px] font-semibold text-white/30 uppercase tracking-[0.08em]">
          Descripción del diseño
        </label>

        <div className="relative">
          <textarea
            value={brief}
            onChange={e => setBrief(e.target.value)}
            onKeyDown={e => {
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') handleSubmit(e as unknown as React.FormEvent);
            }}
            placeholder="Ej: Restaurante de sushi premium. Colores: negro, rojo, dorado. Hero con video, menú interactivo, reservas…"
            disabled={isRunning}
            rows={5}
            className="thin-scroll w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3.5 text-[13px] text-white/80 placeholder-white/20 resize-none focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/20 disabled:opacity-40 transition-all duration-150 leading-relaxed"
          />
          <span className="absolute bottom-3 right-3.5 text-[10px] text-white/20 tabular-nums pointer-events-none">
            {charCount}
          </span>
        </div>

        {selectedSuggestions.length > 0 && (
          <div className="flex flex-wrap gap-1.5 px-3 py-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
            <span className="text-[9px] text-indigo-400 font-semibold self-center mr-1 uppercase tracking-[0.08em]">
              Contexto:
            </span>
            {selectedSuggestions.map(s => (
              <span
                key={s.key}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-white/5 border border-indigo-500/30 text-indigo-300 rounded-full text-[11px] font-medium"
              >
                {s.label}
                <button
                  type="button"
                  onClick={() => handleToggle(s)}
                  className="text-indigo-400/60 hover:text-indigo-300 leading-none ml-0.5 transition-colors"
                  aria-label={'Quitar ' + s.label}
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
          className="w-full rounded-xl py-2.5 px-4 text-[13px] font-semibold text-white flex items-center justify-center gap-2 transition-all duration-150 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
          style={{ background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)', boxShadow: canSubmit ? '0 2px 12px rgba(99,102,241,0.3)' : 'none' }}
        >
          {isRunning ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin"/>
              Generando…
            </>
          ) : (
            <>
              <IconSend size={13}/>
              {selectedSuggestions.length > 0
                ? `Generar con ${selectedSuggestions.length} contexto${selectedSuggestions.length > 1 ? 's' : ''}`
                : 'Generar interfaz'
              }
            </>
          )}
        </button>

        <p className="text-[10px] text-white/20 text-center">⌘ Enter para enviar</p>
      </form>

      {!isRunning && !isCompleted && (
        <BriefSuggestions
          brief={brief}
          selectedKeys={selectedSuggestions.map(s => s.key)}
          onToggle={handleToggle}
          disabled={isRunning}
        />
      )}

      {isRunning && state.currentStep && (
        <div className="flex items-center gap-3 p-3.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
          <span className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin shrink-0"/>
          <span className="text-[12px] font-medium text-indigo-300">
            {STEP_LABELS[state.currentStep] ?? state.currentStep}
          </span>
        </div>
      )}

      {hasError && (
        <div className="flex items-start gap-3 p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl">
          <IconAlertCircle size={14} className="text-red-400 shrink-0 mt-0.5"/>
          <div>
            <p className="text-[11px] font-semibold text-red-300 mb-0.5">Error al generar</p>
            <p className="text-[11px] text-red-400/80 leading-relaxed">{state.error}</p>
          </div>
        </div>
      )}

      {isCompleted && (
        <div className="flex items-start gap-3 p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
          <IconCheck size={14} className="text-emerald-400 shrink-0 mt-0.5"/>
          <div className="space-y-0.5">
            <p className="text-[11px] font-semibold text-emerald-300">Diseño generado</p>
            {state.htmlOutput  && <p className="text-[11px] text-emerald-400/70">Sitio HTML listo</p>}
            {state.elapsedMs   && <p className="text-[11px] text-emerald-500/60">{(state.elapsedMs / 1000).toFixed(1)}s · Abre en Studio para editar</p>}
          </div>
        </div>
      )}
    </div>
  );
}
