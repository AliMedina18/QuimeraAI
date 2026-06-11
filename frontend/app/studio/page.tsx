'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useStudio } from '@/hooks/useStudio';
import type { HistoryEntry } from '@/hooks/useStudio';
import { useLibrary } from '@/hooks/useLibrary';
import { useUser } from '@/hooks/useUser';
import RatingModal from '@/components/RatingModal';
import PreviewWindow from '@/components/PreviewWindow';
import ColorPicker from '@/components/ColorPicker';
import { extractColorsFromHtml } from '@/utils/colorUtils';
import { IconCheck, IconExpand, IconDownload, IconX } from '@/components/Icons';
import type { SelectedElement } from '@/types/pipeline';

// ─── SVG Icons ────────────────────────────────────────────────────────────────

const IconUndo = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M3 7v6h6"/><path d="M3 13A9 9 0 1 0 5.6 6.5L3 13"/>
  </svg>
);
const IconRedo = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M21 7v6h-6"/><path d="M21 13A9 9 0 1 1 18.4 6.5L21 13"/>
  </svg>
);
const IconAI = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    {/* Sparkles — ícono de IA */}
    <path d="M9.5 2l.8 2.2L12.5 5l-2.2.8L9.5 8l-.8-2.2L6.5 5l2.2-.8z" fill="currentColor" stroke="none"/>
    <path d="M16 8l.6 1.4 1.4.6-1.4.6L16 12l-.6-1.4L14 10l1.4-.6z" fill="currentColor" stroke="none"/>
    <path d="M5 14l.5 1.5L7 16l-1.5.5L5 18l-.5-1.5L3 16l1.5-.5z" fill="currentColor" stroke="none"/>
    <circle cx="12" cy="16" r="3" strokeWidth={1.75}/>
    <path d="M12 13v-2M12 19v2M9 16H7M17 16h-2" strokeWidth={1.5}/>
  </svg>
);
const IconCursor = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M4 4l8 20 2.5-7L22 14.5z"/>
  </svg>
);
const IconClock = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
  </svg>
);
const IconArrow = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>
  </svg>
);
const IconPanelRight = ({ size = 15 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M15 3v18"/>
  </svg>
);
const IconBookmark = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
  </svg>
);
const IconLibrary = ({ size = 13 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
  </svg>
);
const IconPalette = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>
    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>
  </svg>
);

// ─── Helpers ──────────────────────────────────────────────────────────────────

function timeAgo(ts: number): string {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'ahora mismo';
  if (m < 60) return 'hace ' + m + 'm';
  return 'hace ' + Math.floor(m / 60) + 'h';
}

// ─── Tool button ──────────────────────────────────────────────────────────────

function ToolBtn({
  icon, label, active, onClick, disabled,
}: {
  icon: React.ReactNode; label: string; active?: boolean; onClick: () => void; disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      disabled={disabled}
      className={[
        'w-9 h-9 flex items-center justify-center rounded-lg transition-all duration-150',
        active
          ? 'bg-white/12 text-white'
          : 'text-white/40 hover:bg-white/7 hover:text-white/80',
        disabled ? 'opacity-30 cursor-not-allowed' : '',
      ].join(' ')}
    >
      {icon}
    </button>
  );
}

// ─── Right panel: Element tab ─────────────────────────────────────────────────

function ElementTab({
  selectedElement, textColor, setTextColor,
  bgColor, setBgColor, onApplyColor, onClear,
}: {
  selectedElement: SelectedElement | null;
  textColor: string; setTextColor: (c: string) => void;
  bgColor: string; setBgColor: (c: string) => void;
  onApplyColor: (prop: 'color' | 'background-color', color: string) => void;
  onClear: () => void;
}) {
  if (!selectedElement) {
    return (
      <div className="flex flex-col items-center justify-center h-52 text-center p-6 gap-4">
        <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-gray-300">
          <IconCursor size={18}/>
        </div>
        <div>
          <p className="text-[13px] font-medium text-gray-600">Sin elemento</p>
          <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
            Haz clic en el preview<br/>para seleccionar
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-5">
      {/* Element info */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <code className="text-[12px] font-mono font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
              &lt;{selectedElement.tag}&gt;
            </code>
            {selectedElement.id && (
              <code className="text-[11px] font-mono text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded border border-gray-100">
                #{selectedElement.id}
              </code>
            )}
          </div>
          {selectedElement.text && (
            <p className="text-[11px] text-gray-400 mt-2 bg-gray-50 rounded-lg px-2.5 py-1.5 truncate border border-gray-100 italic">
              &quot;{selectedElement.text}&quot;
            </p>
          )}
        </div>
        <button
          onClick={onClear}
          className="shrink-0 w-6 h-6 flex items-center justify-center text-gray-300 hover:text-gray-500 hover:bg-gray-100 rounded-md transition-all"
          title="Quitar selección"
        >
          <IconX size={12}/>
        </button>
      </div>

      <div className="h-px bg-gray-100"/>

      {/* Text color */}
      <div className="space-y-2.5">
        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-[0.06em]">
          Color de texto
        </p>
        <ColorPicker value={textColor} onChange={setTextColor}/>
        <button
          onClick={() => onApplyColor('color', textColor)}
          className="w-full py-1.5 text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors"
        >
          Aplicar al texto
        </button>
      </div>

      <div className="h-px bg-gray-100"/>

      {/* Background color */}
      <div className="space-y-2.5">
        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-[0.06em]">
          Color de fondo
        </p>
        <ColorPicker value={bgColor} onChange={setBgColor}/>
        <button
          onClick={() => onApplyColor('background-color', bgColor)}
          className="w-full py-1.5 text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors"
        >
          Aplicar al fondo
        </button>
      </div>
    </div>
  );
}

// ─── Right panel: Colors tab ──────────────────────────────────────────────────

function ColorsTab({
  siteColors, onReplaceGlobal,
}: {
  siteColors: string[];
  onReplaceGlobal: (oldColor: string, newColor: string) => void;
}) {
  const [replacingColor, setReplacingColor] = useState<string | null>(null);
  const [replacementColor, setReplacementColor] = useState('#000000');

  if (siteColors.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-52 text-center p-6 gap-4">
        <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-gray-300">
          <IconPalette size={18}/>
        </div>
        <p className="text-[11px] text-gray-400 leading-relaxed">
          No se detectaron<br/>colores en el HTML
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-[0.06em]">
        Paleta del sitio — {siteColors.length} colores
      </p>

      <div className="grid grid-cols-5 gap-2">
        {siteColors.map(color => (
          <button
            key={color}
            title={color}
            onClick={() => {
              setReplacingColor(prev => prev === color ? null : color);
              setReplacementColor(color);
            }}
            className={[
              'aspect-square rounded-lg border-2 transition-all duration-150',
              replacingColor === color
                ? 'border-indigo-500 scale-110 shadow-md shadow-indigo-200'
                : 'border-transparent hover:border-gray-300 hover:scale-105',
            ].join(' ')}
            style={{ backgroundColor: color }}
          />
        ))}
      </div>

      {replacingColor && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-3.5 space-y-3">
          <div className="flex items-center gap-2">
            <span
              className="w-4 h-4 rounded border border-gray-300 shrink-0"
              style={{ backgroundColor: replacingColor }}
            />
            <p className="text-[11px] text-gray-600">
              Reemplazar <code className="font-mono font-semibold">{replacingColor}</code>
            </p>
          </div>
          <ColorPicker value={replacementColor} onChange={setReplacementColor}/>
          <div className="flex gap-2">
            <button
              onClick={() => { onReplaceGlobal(replacingColor, replacementColor); setReplacingColor(null); }}
              className="flex-1 text-[11px] py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-colors"
            >
              Reemplazar global
            </button>
            <button
              onClick={() => setReplacingColor(null)}
              className="text-[11px] py-1.5 px-2.5 bg-white hover:bg-gray-100 text-gray-600 rounded-lg font-medium border border-gray-200 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {!replacingColor && (
        <p className="text-[10px] text-gray-400 text-center">
          Toca un color para reemplazarlo en todo el sitio
        </p>
      )}
    </div>
  );
}

// ─── Right panel: History tab ─────────────────────────────────────────────────

function HistoryTab({
  history, onLoad,
}: {
  history: HistoryEntry[];
  onLoad: (entry: HistoryEntry) => void;
}) {
  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-52 text-center p-6 gap-4">
        <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-gray-300">
          <IconClock size={18}/>
        </div>
        <div>
          <p className="text-[13px] font-medium text-gray-600">Sin versiones</p>
          <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
            Usa &quot;Guardar&quot; para crear<br/>puntos de restauración
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-2 space-y-0.5">
      {history.map((entry, i) => (
        <button
          key={i}
          onClick={() => onLoad(entry)}
          className="w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-all text-left group"
        >
          <div className="flex-1 min-w-0">
            <p className="text-[12px] font-medium text-gray-700 truncate">{entry.label}</p>
            <p className="text-[10px] text-gray-400 mt-0.5">{timeAgo(entry.savedAt)}</p>
          </div>
          <span className="text-[10px] text-indigo-500 font-semibold shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            Restaurar
          </span>
        </button>
      ))}
    </div>
  );
}

// ─── Empty state ──────────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-[#131315] text-white gap-6">
      <div className="w-14 h-14 rounded-2xl bg-indigo-600 flex items-center justify-center text-xl font-bold tracking-tight">
        Q
      </div>
      <div className="text-center">
        <p className="text-[15px] font-semibold text-white/90">No hay diseño abierto</p>
        <p className="text-[13px] text-white/40 mt-1">Genera un diseño desde la pantalla principal</p>
      </div>
      <Link
        href="/"
        className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-[13px] font-semibold rounded-xl transition-colors"
      >
        <IconArrow size={13}/> Volver a Quimera AI
      </Link>
    </div>
  );
}

// ─── Studio page ──────────────────────────────────────────────────────────────

type RightTab = 'props' | 'colors' | 'history';

const RIGHT_TABS: { id: RightTab; label: string }[] = [
  { id: 'props',   label: 'Elemento' },
  { id: 'colors',  label: 'Colores' },
  { id: 'history', label: 'Historial' },
];

export default function StudioPage() {
  const studio = useStudio();
  const { state, canUndo, canRedo } = studio;

  const library = useLibrary();
  const { user, markFirstProjectRated } = useUser();

  const [showAI, setShowAI] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveNameInput, setSaveNameInput] = useState('');
  const [saveFlashMsg, setSaveFlashMsg] = useState('');
  const [aiInstruction, setAiInstruction] = useState('');
  const [rightTab, setRightTab] = useState<RightTab>('props');
  const [textColor, setTextColor] = useState('#000000');
  const [bgColor, setBgColor] = useState('#ffffff');
  const [savedFlash, setSavedFlash] = useState(false);
  const [showRating, setShowRating] = useState(false);

  // Auto-popular colores cuando se selecciona un elemento
  useEffect(() => {
    if (!state.selectedElement) return;
    const styleAttr = state.selectedElement.outerHTML.match(/style\s*=\s*["']([^"']*)["']/i)?.[1] ?? '';

    const colorMatch = styleAttr.match(/(?<![a-z-])color\s*:\s*(#[0-9a-fA-F]{3,8})/i);
    if (colorMatch) setTextColor(colorMatch[1].toLowerCase());

    const bgMatch = styleAttr.match(/background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8})/i);
    if (bgMatch) setBgColor(bgMatch[1].toLowerCase());
  }, [state.selectedElement?.outerHTML]);

  if (!state.isLoaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#131315]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-7 h-7 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"/>
          <p className="text-[12px] text-white/30">Cargando studio…</p>
        </div>
      </div>
    );
  }

  if (!state.htmlOutput) return <EmptyState/>;

  const siteColors = extractColorsFromHtml(state.htmlOutput).slice(0, 20);

  function handleSave() {
    studio.saveVersion();
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 2200);
  }

  function handleExpand() {
    const blob = new Blob([state.htmlOutput], { type: 'text/html' });
    window.open(URL.createObjectURL(blob), '_blank');
  }

  function handleDownload() {
    const blob = new Blob([state.htmlOutput], { type: 'text/html' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (state.name || 'diseno') + '.html';
    a.click();
  }

  function openSaveModal() {
    setSaveNameInput(state.name || 'Diseño sin título');
    setShowSaveModal(true);
  }

  async function handleSaveToLibrary() {
    if (!saveNameInput.trim()) return;
    const id = await library.saveDesign(
      saveNameInput.trim(),
      state.htmlOutput,
      state.designMarkdown,
    );
    setShowSaveModal(false);
    if (id) {
      setSaveFlashMsg('¡Guardado en biblioteca!');
      setTimeout(() => setSaveFlashMsg(''), 2500);
      // Mostrar rating si el usuario aún no ha calificado
      if (user && !user.firstProjectRated) {
        setTimeout(() => setShowRating(true), 1200);
      }
    }
  }

  async function handleAIEdit() {
    if (!aiInstruction.trim() || state.isEditingAI) return;
    await studio.editWithAI(
      aiInstruction.trim(),
      state.htmlOutput,
      state.designMarkdown,
      state.selectedElement,
    );
    setAiInstruction('');
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#131315]">

      {/* ── Top bar ─────────────────────────────────────────────────────────── */}
      <header className="h-11 flex items-center justify-between px-3 bg-[#1C1C1F] border-b border-white/[0.06] shrink-0">

        {/* Left: back + name */}
        <div className="flex items-center gap-2.5 min-w-0">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-white/40 hover:text-white/80 text-[12px] transition-colors shrink-0 py-1 px-1.5 rounded-md hover:bg-white/5"
          >
            <IconArrow size={12}/>
            <span className="hidden sm:inline">Quimera</span>
          </Link>
          <div className="h-3.5 w-px bg-white/10 shrink-0"/>
          <input
            value={state.name}
            onChange={e => studio.setName(e.target.value)}
            className="bg-transparent text-[13px] font-medium text-white/80 placeholder-white/20 outline-none hover:bg-white/5 focus:bg-white/5 rounded-md px-2 py-0.5 min-w-0 max-w-[180px] transition-colors"
            title="Nombre del diseño"
          />
        </div>

        {/* Center: undo/redo */}
        <div className="flex items-center gap-0.5 absolute left-1/2 -translate-x-1/2">
          <button
            onClick={studio.undo}
            disabled={!canUndo}
            title="Deshacer (Ctrl+Z)"
            className="p-1.5 rounded-md text-white/40 hover:text-white/80 hover:bg-white/7 disabled:opacity-25 disabled:cursor-not-allowed transition-all"
          >
            <IconUndo size={15}/>
          </button>
          <button
            onClick={studio.redo}
            disabled={!canRedo}
            title="Rehacer"
            className="p-1.5 rounded-md text-white/40 hover:text-white/80 hover:bg-white/7 disabled:opacity-25 disabled:cursor-not-allowed transition-all"
          >
            <IconRedo size={15}/>
          </button>
        </div>

        {/* Right: actions */}
        <div className="flex items-center gap-1 shrink-0">
          {saveFlashMsg && (
            <span className="text-[11px] text-emerald-400 font-medium mr-1 animate-pulse">
              {saveFlashMsg}
            </span>
          )}
          <button
            onClick={openSaveModal}
            title="Guardar en biblioteca"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-semibold text-white/50 hover:text-white/80 hover:bg-white/7 transition-all border border-white/10"
          >
            <IconBookmark size={12}/>
            <span className="hidden sm:inline">Biblioteca</span>
          </button>
          <Link
            href="/biblioteca"
            title="Ver todos mis diseños"
            className="p-1.5 rounded-md text-white/30 hover:text-white/70 hover:bg-white/7 transition-all"
          >
            <IconLibrary size={13}/>
          </Link>
          <div className="h-3.5 w-px bg-white/10 mx-0.5"/>
          <button
            onClick={handleSave}
            className={[
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold transition-all',
              savedFlash
                ? 'bg-emerald-600 text-white'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white',
            ].join(' ')}
          >
            {savedFlash ? <><IconCheck size={11}/> Guardado</> : 'Guardar'}
          </button>
          <button
            onClick={handleExpand}
            title="Ver en pantalla completa"
            className="p-1.5 rounded-md text-white/40 hover:text-white/80 hover:bg-white/7 transition-all"
          >
            <IconExpand size={15}/>
          </button>
          <button
            onClick={handleDownload}
            title="Descargar HTML"
            className="p-1.5 rounded-md text-white/40 hover:text-white/80 hover:bg-white/7 transition-all"
          >
            <IconDownload size={15}/>
          </button>
          <div className="h-3.5 w-px bg-white/10 mx-0.5"/>
          <button
            onClick={() => setShowRightPanel(v => !v)}
            title={showRightPanel ? 'Ocultar panel de propiedades' : 'Mostrar panel de propiedades'}
            className={[
              'p-1.5 rounded-md transition-all',
              showRightPanel
                ? 'text-white/70 bg-white/10 hover:bg-white/15'
                : 'text-white/30 hover:text-white/70 hover:bg-white/7',
            ].join(' ')}
          >
            <IconPanelRight size={15}/>
          </button>
        </div>
      </header>

      {/* ── Main area ───────────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Left toolbar + AI panel ─────────────────────────────────────── */}
        <div className="flex shrink-0">

          {/* Icon toolbar (always visible, 48px) */}
          <div className="w-12 flex flex-col items-center py-2.5 gap-1 bg-[#1C1C1F] border-r border-white/[0.06]">

            {/* Tool group: select + AI */}
            <ToolBtn
              icon={<IconCursor size={15}/>}
              label="Seleccionar (V)"
              active={!showAI}
              onClick={() => setShowAI(false)}
            />
            <ToolBtn
              icon={<IconAI size={15}/>}
              label="Editar con IA (A)"
              active={showAI}
              onClick={() => setShowAI(v => !v)}
            />

            <div className="h-px w-5 bg-white/10 my-1"/>

            {/* Undo / redo */}
            <ToolBtn
              icon={<IconUndo size={15}/>}
              label="Deshacer"
              active={false}
              disabled={!canUndo}
              onClick={studio.undo}
            />
            <ToolBtn
              icon={<IconRedo size={15}/>}
              label="Rehacer"
              active={false}
              disabled={!canRedo}
              onClick={studio.redo}
            />
          </div>

          {/* AI panel (slides in) */}
          {showAI && (
            <div className="w-68 bg-[#1C1C1F] border-r border-white/[0.06] flex flex-col overflow-hidden"
                 style={{ width: 272 }}>

              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06] shrink-0">
                <div>
                  <p className="text-[10px] font-semibold text-indigo-400 uppercase tracking-[0.08em]">
                    Editar con IA
                  </p>
                  <p className="text-[11px] text-white/30 mt-0.5">
                    Gemini Flash · 5-15s
                  </p>
                </div>
                <button
                  onClick={() => setShowAI(false)}
                  className="w-6 h-6 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-white/7 rounded-md transition-all"
                >
                  <IconX size={12}/>
                </button>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto p-3.5 flex flex-col gap-3">

                {/* Selected element context */}
                {state.selectedElement ? (
                  <div className="rounded-xl bg-white/5 border border-white/8 px-3 py-2.5">
                    <p className="text-[9px] text-white/30 uppercase tracking-[0.08em] mb-1.5">
                      Elemento seleccionado
                    </p>
                    <code className="text-[12px] text-indigo-400 font-mono">
                      &lt;{state.selectedElement.tag}&gt;
                    </code>
                    {state.selectedElement.text && (
                      <p className="text-[11px] text-white/30 truncate mt-1 italic">
                        &quot;{state.selectedElement.text}&quot;
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="rounded-xl border border-dashed border-white/10 px-3 py-2.5 text-center">
                    <p className="text-[11px] text-white/30 leading-relaxed">
                      Selecciona un elemento para cambios específicos, o edita todo el diseño
                    </p>
                  </div>
                )}

                {/* Instruction textarea */}
                <textarea
                  value={aiInstruction}
                  onChange={e => setAiInstruction(e.target.value)}
                  onKeyDown={e => {
                    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') handleAIEdit();
                  }}
                  placeholder={'Ej: cambia los colores a tonos verdes\nagranda el título del hero\nagrega una sección de FAQ…'}
                  disabled={state.isEditingAI}
                  rows={5}
                  className="w-full rounded-xl bg-white/5 border border-white/8 text-[12px] text-white/80 placeholder-white/25 px-3.5 py-3 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/20 resize-none disabled:opacity-40 transition-all leading-relaxed"
                />

                {state.aiError && (
                  <div className="text-[11px] text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-3 py-2.5">
                    {state.aiError}
                  </div>
                )}

                <button
                  onClick={handleAIEdit}
                  disabled={!aiInstruction.trim() || state.isEditingAI}
                  className="flex items-center justify-center gap-2 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed text-white text-[12px] font-semibold rounded-xl transition-all"
                >
                  {state.isEditingAI ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                      Aplicando…
                    </>
                  ) : (
                    'Aplicar cambio'
                  )}
                </button>

                <p className="text-[10px] text-white/20 text-center">⌘ Enter para enviar</p>
              </div>
            </div>
          )}
        </div>

        {/* ── Central canvas ──────────────────────────────────────────────── */}
        <div
          className="flex-1 overflow-auto flex flex-col"
          style={{
            backgroundColor: '#131315',
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.055) 1px, transparent 1px)',
            backgroundSize: '20px 20px',
          }}
        >
          {/* Status bar */}
          <div className="flex items-center gap-2 px-4 py-2.5 shrink-0">
            <div className={[
              'w-1.5 h-1.5 rounded-full shrink-0',
              state.isEditingAI ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400',
            ].join(' ')}/>
            <span className="text-[11px] text-white/30">
              {state.isEditingAI
                ? 'Aplicando edición…'
                : state.selectedElement
                  ? `<${state.selectedElement.tag}> seleccionado · Arrastra handles · Doble clic para editar texto`
                  : 'Haz clic en cualquier elemento para seleccionarlo'
              }
            </span>
          </div>

          {/* Floating preview card */}
          <div className="flex-1 overflow-hidden p-5">
            <div
              className="h-full bg-white rounded-xl overflow-hidden"
              style={{ boxShadow: '0 8px 48px rgba(0,0,0,0.55), 0 2px 8px rgba(0,0,0,0.3)' }}
            >
              <PreviewWindow
                htmlOutput={state.htmlOutput}
                studioMode={true}
                selectedElement={state.selectedElement}
                onElementSelected={studio.setSelectedElement}
                onElementEdited={studio.updateElementHtml}
              />
            </div>
          </div>
        </div>

        {/* ── Right properties panel ──────────────────────────────────────── */}
        {showRightPanel && <div className="w-64 shrink-0 flex flex-col bg-white border-l border-gray-200 overflow-hidden">

          {/* Pill tabs */}
          <div className="flex items-center gap-1 p-2.5 border-b border-gray-100 shrink-0">
            {RIGHT_TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setRightTab(tab.id)}
                className={[
                  'flex-1 py-1 text-[11px] font-medium rounded-md transition-all',
                  rightTab === tab.id
                    ? 'bg-gray-900 text-white shadow-sm'
                    : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100',
                ].join(' ')}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto">
            {rightTab === 'props' && (
              <ElementTab
                selectedElement={state.selectedElement}
                textColor={textColor}
                setTextColor={setTextColor}
                bgColor={bgColor}
                setBgColor={setBgColor}
                onApplyColor={studio.applyElementColor}
                onClear={() => studio.setSelectedElement(null)}
              />
            )}
            {rightTab === 'colors' && (
              <ColorsTab
                siteColors={siteColors}
                onReplaceGlobal={studio.replaceGlobalColor}
              />
            )}
            {rightTab === 'history' && (
              <HistoryTab
                history={state.history}
                onLoad={studio.loadVersion}
              />
            )}
          </div>

          {/* Footer: quick save */}
          <div className="shrink-0 p-2.5 border-t border-gray-100">
            <button
              onClick={handleSave}
              className={[
                'w-full flex items-center justify-center gap-1.5 py-2 text-[11px] font-semibold rounded-lg transition-all',
                savedFlash
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white',
              ].join(' ')}
            >
              {savedFlash ? <><IconCheck size={10}/> Versión guardada</> : 'Guardar versión'}
            </button>
          </div>
        </div>}

      </div>

      {/* ── Modal: Guardar en biblioteca ────────────────────────────────── */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-[#1C1C1F] border border-white/10 rounded-2xl shadow-2xl w-full max-w-sm p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[14px] font-semibold text-white/90">Guardar en biblioteca</p>
                <p className="text-[11px] text-white/30 mt-0.5">El diseño quedará guardado en Firestore</p>
              </div>
              <button
                onClick={() => setShowSaveModal(false)}
                className="w-7 h-7 flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-white/7 rounded-lg transition-all"
              >
                <IconX size={13}/>
              </button>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-semibold text-white/30 uppercase tracking-[0.08em]">
                Nombre del diseño
              </label>
              <input
                value={saveNameInput}
                onChange={e => setSaveNameInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSaveToLibrary()}
                autoFocus
                maxLength={100}
                className="w-full rounded-xl bg-white/5 border border-white/10 px-3.5 py-2.5 text-[13px] text-white/80 placeholder-white/20 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                placeholder="Ej: Landing agencia creativa"
              />
            </div>
            <div className="flex gap-2 mt-1">
              <button
                onClick={handleSaveToLibrary}
                disabled={!saveNameInput.trim() || library.state.isSaving}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 text-[13px] font-semibold text-white rounded-xl disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 2px 10px rgba(99,102,241,0.3)' }}
              >
                {library.state.isSaving
                  ? <><span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"/> Guardando…</>
                  : <><IconBookmark size={13}/> Guardar</>
                }
              </button>
              <button
                onClick={() => setShowSaveModal(false)}
                className="px-4 py-2.5 text-[13px] text-white/40 hover:text-white/70 border border-white/10 hover:bg-white/5 rounded-xl transition-all"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

            {/* ── Rating modal ─────────────────────────────────────────────────── */}
      {showRating && (
        <RatingModal
          userName={user?.name}
          onRate={(stars, comment) => {
            markFirstProjectRated();
            setShowRating(false);
            console.info('Rating Studio:', stars, comment);
          }}
          onDismiss={() => {
            markFirstProjectRated();
            setShowRating(false);
          }}
        />
      )}
    </div>
  );
}
