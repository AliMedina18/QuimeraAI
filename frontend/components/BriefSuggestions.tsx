'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import type {
  SuggestResponse,
  MissingElement,
  StyleSuggestion,
  TemplateSuggestion,
  ColorPalette,
} from '@/types/pipeline';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';

function IconSparkle({ size = 11 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 0l1.8 5.2L15.2 7 10 8.8 8 14 6 8.8.8 7 6.2 5.2z" />
    </svg>
  );
}

function IconCheck({ size = 10 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none"
      stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 6l3 3 5-5" />
    </svg>
  );
}

function ColorDot({ color, title }: { color: string; title?: string }) {
  return (
    <span
      title={title ?? color}
      style={{ backgroundColor: color }}
      className="inline-block w-3 h-3 rounded-full border border-black/10 flex-shrink-0"
    />
  );
}

type ChipColor = 'orange' | 'indigo' | 'violet' | 'emerald';

interface ToggleChipProps {
  label: string;
  title?: string;
  color?: ChipColor;
  selected: boolean;
  disabled?: boolean;
  onClick: () => void;
}

function ToggleChip({ label, title, color = 'indigo', selected, disabled, onClick }: ToggleChipProps) {
  const base = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all duration-100 cursor-pointer select-none disabled:opacity-40 disabled:cursor-not-allowed';
  const unselected: Record<ChipColor, string> = {
    orange:  'bg-white border-orange-200 text-orange-700 hover:bg-orange-50',
    indigo:  'bg-white border-gray-200 text-gray-600 hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-700',
    violet:  'bg-white border-gray-200 text-gray-600 hover:bg-violet-50 hover:border-violet-300 hover:text-violet-700',
    emerald: 'bg-white border-gray-200 text-gray-600 hover:bg-emerald-50 hover:border-emerald-300 hover:text-emerald-700',
  };
  const sel: Record<ChipColor, string> = {
    orange:  'bg-orange-100 border-orange-400 text-orange-800',
    indigo:  'bg-indigo-100 border-indigo-400 text-indigo-800',
    violet:  'bg-violet-100 border-violet-400 text-violet-800',
    emerald: 'bg-emerald-100 border-emerald-400 text-emerald-800',
  };
  return (
    <button type="button" title={title} disabled={disabled} onClick={onClick}
      className={`${base} ${selected ? sel[color] : unselected[color]}`}>
      {selected && <IconCheck size={10} />}
      {label}
    </button>
  );
}

function PaletteChip({ palette, selected, disabled, onClick }: {
  palette: ColorPalette; selected: boolean; disabled?: boolean; onClick: () => void;
}) {
  return (
    <button type="button" disabled={disabled} onClick={onClick}
      className={`flex items-center gap-2.5 w-full px-2.5 py-1.5 rounded-lg text-left border transition-all duration-100 text-[11px] font-medium disabled:opacity-40 disabled:cursor-not-allowed ${
        selected
          ? 'bg-emerald-50 border-emerald-400 text-emerald-800'
          : 'bg-white border-gray-200 text-gray-600 hover:bg-emerald-50 hover:border-emerald-300'
      }`}>
      <div className="flex items-center gap-1 flex-shrink-0">
        <ColorDot color={palette.primary} title="Primario" />
        <ColorDot color={palette.secondary} title="Secundario" />
        <ColorDot color={palette.accent} title="Acento" />
        <ColorDot color={palette.surface} title="Fondo" />
      </div>
      <span className="flex-1">{palette.name}</span>
      {selected && <span className="text-emerald-500 flex-shrink-0"><IconCheck size={10} /></span>}
    </button>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1.5">
      {children}
    </p>
  );
}

export interface SelectedChip {
  key: string;
  text: string;
  label: string;
}

interface Props {
  brief: string;
  selectedKeys: string[];
  onToggle: (chip: SelectedChip) => void;
  disabled?: boolean;
}

export default function BriefSuggestions({ brief, selectedKeys, onToggle, disabled }: Props) {
  const [data, setData] = useState<SuggestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef    = useRef<AbortController | null>(null);

  const fetchSuggestions = useCallback(async (text: string) => {
    if (text.trim().length < 8) { setData(null); return; }
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/sugerir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brief: text }),
        signal: abortRef.current.signal,
      });
      if (!res.ok) throw new Error('Error en /sugerir');
      setData(await res.json());
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return;
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (disabled) return;
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(brief), 700);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [brief, disabled, fetchSuggestions]);

  if (!data && !loading) return null;

  const selectedCount = selectedKeys.length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2 bg-gradient-to-r from-indigo-50 to-violet-50 border-b border-gray-100">
        <div className="flex items-center gap-2 text-indigo-700">
          <IconSparkle size={11} />
          <span className="text-[11px] font-semibold uppercase tracking-widest">Sugerencias</span>
          {data?.industry && (
            <span className="text-[10px] bg-indigo-100 text-indigo-600 rounded-full px-2 py-0.5 font-medium capitalize">
              {data.industry}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {selectedCount > 0 && (
            <span className="text-[10px] bg-indigo-600 text-white rounded-full px-2 py-0.5 font-semibold">
              {selectedCount} seleccionado{selectedCount > 1 ? 's' : ''}
            </span>
          )}
          {loading && (
            <span className="inline-block w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
      </div>

      {loading && !data ? (
        <div className="px-4 py-4 text-center text-[11px] text-gray-400">Analizando brief…</div>
      ) : data ? (
        <div className="divide-y divide-gray-100">

          {/* Elementos faltantes */}
          {data.missing.length > 0 && (
            <div className="px-3.5 pt-2.5 pb-3">
              <SectionLabel>Completar brief</SectionLabel>
              <div className="flex flex-wrap gap-1.5">
                {data.missing.map((m: MissingElement) => (
                  <ToggleChip
                    key={m.key}
                    label={m.label}
                    title={m.hint}
                    color="orange"
                    selected={selectedKeys.includes(m.key)}
                    disabled={disabled}
                    onClick={() => onToggle({ key: m.key, text: m.chip_text, label: m.label })}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Estilos */}
          <div className="px-3.5 pt-2.5 pb-3">
            <SectionLabel>Estilo visual</SectionLabel>
            <div className="flex flex-wrap gap-1.5">
              {data.styles.map((s: StyleSuggestion) => (
                <ToggleChip
                  key={s.id}
                  label={s.emoji + ' ' + s.label}
                  title={s.description}
                  color="indigo"
                  selected={selectedKeys.includes(s.id)}
                  disabled={disabled}
                  onClick={() => onToggle({ key: s.id, text: s.chip_text, label: s.label })}
                />
              ))}
            </div>
          </div>

          {/* Templates */}
          <div className="px-3.5 pt-2.5 pb-3">
            <SectionLabel>Referencia de diseño</SectionLabel>
            <div className="flex flex-wrap gap-1.5">
              {data.templates.map((t: TemplateSuggestion) => (
                <ToggleChip
                  key={t.slug}
                  label={t.label}
                  title={t.mood}
                  color="violet"
                  selected={selectedKeys.includes(t.slug)}
                  disabled={disabled}
                  onClick={() => onToggle({ key: t.slug, text: t.chip_text, label: t.label })}
                />
              ))}
            </div>
          </div>

          {/* Paletas */}
          <div className="px-3.5 pt-2.5 pb-3">
            <SectionLabel>Paleta de colores</SectionLabel>
            <div className="flex flex-col gap-1.5">
              {data.palettes.map((p: ColorPalette) => (
                <PaletteChip
                  key={p.name}
                  palette={p}
                  selected={selectedKeys.includes(p.name)}
                  disabled={disabled}
                  onClick={() => onToggle({ key: p.name, text: p.chip_text, label: p.name })}
                />
              ))}
            </div>
          </div>

          {/* Tip */}
          <div className="px-3.5 py-2 bg-gray-50">
            <p className="text-[10px] text-gray-400">
              Selecciona lo que quieras incluir — tu texto original no se modifica
            </p>
          </div>

        </div>
      ) : null}
    </div>
  );
}
