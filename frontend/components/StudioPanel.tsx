'use client';

import { useState } from 'react';
import type { PipelineState, SavedDesign } from '@/types/pipeline';
import { IconSend, IconCheck } from './Icons';

interface Props {
  state: PipelineState;
  onEdit: (instruccion: string) => void;
  onLoadDesign: (id: string) => void;
  onClearElement: () => void;
  onExitStudio: () => void;
}

function timeAgo(ts: number): string {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'ahora mismo';
  if (mins < 60) return `hace ${mins}m`;
  const hrs = Math.floor(mins / 60);
  return `hace ${hrs}h`;
}

function SavedDesignCard({
  design,
  isActive,
  onLoad,
}: {
  design: SavedDesign;
  isActive: boolean;
  onLoad: () => void;
}) {
  return (
    <button
      onClick={onLoad}
      className={`
        w-full text-left px-3 py-2.5 rounded-xl border transition-all
        ${isActive
          ? 'border-indigo-300 bg-indigo-50 ring-1 ring-indigo-200'
          : 'border-gray-100 bg-white hover:border-indigo-200 hover:bg-indigo-50/40'
        }
      `}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[13px] font-medium text-gray-800 truncate">{design.name}</span>
        {isActive && <IconCheck size={12} className="text-indigo-500 shrink-0"/>}
      </div>
      <span className="text-[11px] text-gray-400">{timeAgo(design.savedAt)}</span>
    </button>
  );
}

export default function StudioPanel({ state, onEdit, onLoadDesign, onClearElement, onExitStudio }: Props) {
  const [instruccion, setInstruccion] = useState('');

  const isRunning = state.status === 'running';
  const canSubmit = instruccion.trim().length > 3 && !isRunning;
  const { selectedElement, savedDesigns, htmlOutput } = state;

  // Detectar el diseño activo (el que coincide con el htmlOutput actual)
  const activeDesignId = savedDesigns.find(d => d.htmlOutput === htmlOutput)?.id ?? null;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    onEdit(instruccion.trim());
    setInstruccion('');
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">

      {/* Header del estudio */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-indigo-600 uppercase tracking-widest">
              Modo estudio
            </p>
            <p className="text-[12px] text-gray-400 mt-0.5">
              Edita el diseño con instrucciones
            </p>
          </div>
          <button
            onClick={onExitStudio}
            className="text-[11px] text-gray-400 hover:text-gray-600 px-2.5 py-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            ← Volver
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto flex flex-col gap-5 p-5">

        {/* Elemento seleccionado */}
        {selectedElement ? (
          <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-3.5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-indigo-600 uppercase tracking-widest">
                Elemento seleccionado
              </span>
              <button
                onClick={onClearElement}
                className="text-[11px] text-indigo-400 hover:text-indigo-600 transition-colors"
              >
                Quitar
              </button>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <code className="text-[11px] bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded font-mono">
                &lt;{selectedElement.tag}&gt;
              </code>
              {selectedElement.id && (
                <code className="text-[11px] bg-white text-gray-500 px-2 py-0.5 rounded border border-gray-200 font-mono">
                  #{selectedElement.id}
                </code>
              )}
            </div>
            {selectedElement.text && (
              <p className="text-[12px] text-indigo-700 mt-2 truncate opacity-70">
                &quot;{selectedElement.text}&quot;
              </p>
            )}
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-gray-200 p-3.5 text-center">
            <p className="text-[12px] text-gray-400 leading-relaxed">
              Haz clic en cualquier elemento del{' '}
              <span className="font-medium text-gray-500">preview</span>{' '}
              para seleccionarlo y editar solo esa parte
            </p>
          </div>
        )}

        {/* Prompt de edición */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
            {selectedElement
              ? `Cambiar ${selectedElement.tag}`
              : 'Instrucción de edición'}
          </label>
          <textarea
            value={instruccion}
            onChange={e => setInstruccion(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit(e as unknown as React.FormEvent);
            }}
            placeholder={selectedElement
              ? `Ej: "cambia el color a rojo", "agranda el texto", "añade una sombra"…`
              : `Ej: "cambia la paleta a tonos verdes", "añade una sección de FAQ"…`
            }
            disabled={isRunning}
            rows={4}
            className="
              w-full rounded-xl border border-gray-200 bg-white px-4 py-3
              text-sm text-gray-800 placeholder-gray-400 resize-none
              focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100
              disabled:bg-gray-50 disabled:text-gray-400
              transition-all duration-150
            "
          />
          <button
            type="submit"
            disabled={!canSubmit}
            className="
              flex items-center justify-center gap-2 w-full px-4 py-2.5
              bg-indigo-600 text-white text-sm font-semibold rounded-xl
              hover:bg-indigo-700 active:scale-[0.98]
              disabled:opacity-40 disabled:cursor-not-allowed
              transition-all duration-150
            "
          >
            {isRunning ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                Aplicando cambio…
              </>
            ) : (
              <>
                <IconSend size={14}/>
                Aplicar cambio
              </>
            )}
          </button>
          <p className="text-[11px] text-gray-400 text-center">⌘ + Enter para enviar</p>
        </form>

        {/* Diseños guardados */}
        {savedDesigns.length > 0 && (
          <div className="flex flex-col gap-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
              Diseños guardados
            </p>
            <div className="flex flex-col gap-1.5">
              {savedDesigns.map(design => (
                <SavedDesignCard
                  key={design.id}
                  design={design}
                  isActive={design.id === activeDesignId}
                  onLoad={() => onLoadDesign(design.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
