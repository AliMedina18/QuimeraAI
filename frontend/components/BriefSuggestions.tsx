'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import type {
  SuggestResponse,
  MissingElement,
  StyleSuggestion,
  TemplateSuggestion,
  ColorPalette,
} from '@/types/pipeline';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';

function IconSparkle({ size = 10 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="currentColor" aria-hidden>
      <path d="M8 0l1.8 5.2L15.2 7 10 8.8 8 14 6 8.8.8 7 6.2 5.2z" />
    </svg>
  );
}

function IconCheck({ size = 9 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none"
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M2 6l3 3 5-5" />
    </svg>
  );
}

function ColorDot({ color, title }: { color: string; title?: string }) {
  return (
    <span
      title={title ?? color}
      style={{ backgroundColor: color }}
      className="inline-block w-3.5 h-3.5 rounded-full border border-white/20 flex-shrink-0"
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
  const base = 'inline-flex items-center gap-1 px-2.5 py-[5px] rounded-full text-[11px] font-medium border transition-all duration-100 select-none disabled:opacity-30 disabled:cursor-not-allowed';
  const unselected: Record<ChipColor, string> = {
    orange:  'bg-white/5 border-orange-500/30 text-orange-400/80 hover:bg-orange-500/10 hover:border-orange-400/50 hover:text-orange-300',
    indigo:  'bg-white/5 border-white/10 text-white/40 hover:bg-indigo-500/10 hover:border-indigo-500/30 hover:text-indigo-300',
    violet:  'bg-white/5 border-white/10 text-white/40 hover:bg-violet-500/10 hover:border-violet-500/30 hover:text-violet-300',
    emerald: 'bg-white/5 border-white/10 text-white/40 hover:bg-emerald-500/10 hover:border-emerald-500/30 hover:text-emerald-300',
  };
  const sel: Record<ChipColor, string> = {
    orange:  'bg-orange-500/15 border-orange-400/50 text-orange-300',
    indigo:  'bg-indigo-500/15 border-indigo-400/50 text-indigo-300',
    violet:  'bg-violet-500/15 border-violet-400/50 text-violet-300',
    emerald: 'bg-emerald-500/15 border-emerald-400/50 text-emerald-300',
  };
  return (
    <button type="button" title={title} disabled={disabled} onClick={onClick}
      className={`${base} ${selected ? sel[color] : unselected[color]}`}>
      {selected && <IconCheck size={9} />}
      {label}
    </button>
  );
}

function PaletteChip({ palette, selected, disabled, onClick }: {
  palette: ColorPalette; selected: boolean; disabled?: boolean; onClick: () => void;
}) {
  return (
    <button type="button" disabled={disabled} onClick={onClick}
      className={`flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-left border transition-all duration-100 text-[11px] font-medium disabled:opacity-30 disabled:cursor-not-allowed ${
        selected
          ? 'bg-emerald-500/15 border-emerald-400/40 text-emerald-300'
          : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20 hover:bg-white/8 hover:text-white/70'
      }`}>
      <div className="flex items-center gap-1 flex-shrink-0">
        <ColorDot color={palette.primary} title="Primario" />
        <ColorDot color={palette.secondary} title="Secundario" />
        <ColorDot color={palette.accent} title="Acento" />
        <ColorDot color={palette.surface} title="Fondo" />
      </div>
      <span className="flex-1 text-[11px]">{palette.name}</span>
      {selected && <span className="text-emerald-400 flex-shrink-0"><IconCheck size={9} /></span>}
    </button>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[9px] font-semibold text-white/25 uppercase tracking-[0.1em] mb-2">
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
    <div className="rounded-xl border border-white/10 bg-white/[0.04] overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-white/[0.06] bg-white/[0.03]">
        <div className="flex items-center gap-1.5 text-indigo-400">
          <IconSparkle size={10} />
          <span className="text-[10px] font-semibold uppercase tracking-[0.08em]">Sugerencias IA</span>
          {data?.industry && (
            <span className="text-[9px] bg-indigo-500/15 text-indigo-300 rounded-full px-2 py-0.5 font-semibold capitalize">
              {data.industry}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {selectedCount > 0 && (
            <span className="text-[9px] bg-indigo-600 text-white rounded-full px-2 py-0.5 font-semibold">
              {selectedCount} activo{selectedCount > 1 ? 's' : ''}
            </span>
          )}
          {loading && (
            <span className="w-3 h-3 border-2 border-indigo-400/60 border-t-indigo-400 rounded-full animate-spin inline-block" />
          )}
        </div>
      </div>

      {loading && !data ? (
        <div className="px-4 py-5 text-center text-[11px] text-white/30">Analizando brief…</div>
      ) : data ? (
        <div className="divide-y divide-white/[0.06]">

          {data.missing.length > 0 && (
            <div className="px-3.5 pt-3 pb-3">
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

          <div className="px-3.5 pt-3 pb-3">
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

          <div className="px-3.5 pt-3 pb-3">
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

          <div className="px-3.5 pt-3 pb-3">
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

          <div className="px-3.5 py-2.5 bg-white/[0.02]">
            <p className="text-[9px] text-white/20 leading-relaxed">
              Selecciona contexto adicional — tu brief original no se modifica
            </p>
          </div>

        </div>
      ) : null}
    </div>
  );
}
