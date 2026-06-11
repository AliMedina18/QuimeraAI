'use client';

import { useMemo } from 'react';
import type { FC } from 'react';
import Markdown from 'react-markdown';
import { IconPalette, IconTypography, IconLayout } from './Icons';

interface DesignPreviewProps {
  designMarkdown: string;
}

interface ParsedDesign {
  name?: string;
  description?: string;
  industry?: string;
  style?: string;
  colors: Record<string, string>;
  typography: { heading?: string; body?: string; accent?: string };
}

const ROLE_LABELS: Record<string, string> = {
  primary: 'Principal',
  secondary: 'Secundario',
  accent: 'Acento',
  background: 'Fondo',
  surface: 'Superficie',
  text: 'Texto',
  muted: 'Atenuado',
  neutral: 'Neutro',
  error: 'Error',
  success: 'Éxito',
  warning: 'Advertencia',
};

function label(key: string): string {
  return ROLE_LABELS[key.toLowerCase()] ?? key;
}

function usesDarkText(hex: string): boolean {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
  return luminance > 0.45;
}

function parseDesign(raw: string): ParsedDesign {
  const nameMatch   = raw.match(/^name:\s*(.+)$/m);
  const descMatch   = raw.match(/^description:\s*['"]?(.+?)['"]?\s*$/m);
  const indMatch    = raw.match(/^industry:\s*(.+)$/m);
  const styleMatch  = raw.match(/^style:\s*(.+)$/m);

  const colors: Record<string, string> = {};
  const colorsBlock = raw.match(/^colors:\s*\n((?:[ \t]+\S[^\n]*\n?)*)/m);
  if (colorsBlock) {
    const re = /^\s{2,4}(\w[\w-]*):\s*['"]?(#[0-9a-fA-F]{6})['"]?/gm;
    let m;
    while ((m = re.exec(colorsBlock[1])) !== null) colors[m[1]] = m[2];
  }

  const typography: ParsedDesign['typography'] = {};
  const typBlock = raw.match(/^typography:\s*\n((?:[ \t]+\S[^\n]*\n?)*)/m);
  if (typBlock) {
    const rh = /heading:\s*['"]?([^'"#\n]+?)['"]?\s*$/m;
    const rb = /body:\s*['"]?([^'"#\n]+?)['"]?\s*$/m;
    const ra = /accent:\s*['"]?([^'"#\n]+?)['"]?\s*$/m;
    const mh = typBlock[1].match(rh);
    const mb = typBlock[1].match(rb);
    const ma = typBlock[1].match(ra);
    if (mh) typography.heading = mh[1].trim();
    if (mb) typography.body    = mb[1].trim();
    if (ma) typography.accent  = ma[1].trim();
  }

  return {
    name:        nameMatch?.[1]?.trim(),
    description: descMatch?.[1]?.trim(),
    industry:    indMatch?.[1]?.trim(),
    style:       styleMatch?.[1]?.trim(),
    colors,
    typography,
  };
}

// ── Sub-components ────────────────────────────────────────────────

const SectionHeader: FC<{ icon: React.ReactNode; title: string }> = ({ icon, title }) => (
  <div className="flex items-center gap-2 mb-3">
    <span className="text-gray-400">{icon}</span>
    <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-widest">{title}</h4>
  </div>
);

const ColorSwatch: FC<{ name: string; hex: string }> = ({ name, hex }) => {
  const dark = usesDarkText(hex);
  return (
    <div className="group relative rounded-lg overflow-hidden border border-black/8 shadow-sm">
      <div
        className="h-20 flex items-end p-2 transition-all"
        style={{ backgroundColor: hex }}
      >
        <span
          className="text-[10px] font-mono opacity-0 group-hover:opacity-100 transition-opacity font-semibold"
          style={{ color: dark ? '#111' : '#fff' }}
        >
          {hex.toUpperCase()}
        </span>
      </div>
      <div className="px-2 py-1.5 bg-white border-t border-black/5">
        <p className="text-[11px] font-medium text-gray-700 truncate">{label(name)}</p>
        <p className="text-[10px] text-gray-400 font-mono truncate">{hex.toUpperCase()}</p>
      </div>
    </div>
  );
};

const PaletteBar: FC<{ colors: Record<string, string> }> = ({ colors }) => {
  const entries = Object.entries(colors);
  if (!entries.length) return null;
  return (
    <div className="flex h-3 rounded-full overflow-hidden border border-black/8 shadow-inner mb-4">
      {entries.map(([k, hex]) => (
        <div key={k} className="flex-1 transition-all hover:flex-[2]" style={{ backgroundColor: hex }} title={`${label(k)}: ${hex}`}/>
      ))}
    </div>
  );
};

const TypographyChip: FC<{ role: string; font?: string }> = ({ role, font }) => {
  if (!font) return null;
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-xs text-gray-500 capitalize">{role}</span>
      <span className="text-sm font-medium text-gray-800" style={{ fontFamily: font }}>
        {font}
      </span>
    </div>
  );
};

// ── Main component ────────────────────────────────────────────────

const DesignPreview: FC<DesignPreviewProps> = ({ designMarkdown }) => {
  const match = designMarkdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  const design = match ? parseDesign(match[1]) : { colors: {}, typography: {} };
  const body = match ? match[2] : designMarkdown;

  const colorEntries = Object.entries(design.colors);
  const hasTypography = !!(design.typography.heading || design.typography.body || design.typography.accent);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Header */}
      <div className="border-b border-gray-100 bg-white px-5 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">
              {design.name ?? 'Sistema de diseño'}
            </h3>
            {design.description && (
              <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{design.description}</p>
            )}
          </div>
          <div className="flex gap-1.5 flex-shrink-0 mt-0.5">
            {design.industry && (
              <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[11px] font-medium rounded-full border border-indigo-100">
                {design.industry}
              </span>
            )}
            {design.style && (
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-[11px] font-medium rounded-full">
                {design.style}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-6">
        {/* Paleta */}
        {colorEntries.length > 0 && (
          <section>
            <SectionHeader icon={<IconPalette size={14}/>} title="Paleta de colores"/>
            <PaletteBar colors={design.colors}/>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {colorEntries.map(([k, hex]) => (
                <ColorSwatch key={k} name={k} hex={hex}/>
              ))}
            </div>
          </section>
        )}

        {/* Tipografía */}
        {hasTypography && (
          <section>
            <SectionHeader icon={<IconTypography size={14}/>} title="Tipografía"/>
            <div className="bg-gray-50 rounded-lg border border-gray-100 px-3 divide-y divide-gray-100">
              <TypographyChip role="Encabezados" font={design.typography.heading}/>
              <TypographyChip role="Cuerpo"      font={design.typography.body}/>
              <TypographyChip role="Acento"      font={design.typography.accent}/>
            </div>
          </section>
        )}

        {/* Especificación completa */}
        <section>
          <SectionHeader icon={<IconLayout size={14}/>} title="Especificación"/>
          <div className="prose prose-sm max-w-none
            prose-headings:text-gray-900 prose-headings:font-semibold prose-headings:mt-4
            prose-p:text-gray-700 prose-p:leading-relaxed
            prose-li:text-gray-700 prose-li:leading-relaxed
            prose-code:text-indigo-700 prose-code:bg-indigo-50
            prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-[11px]
            prose-strong:text-gray-900">
            <Markdown>{body}</Markdown>
          </div>
        </section>
      </div>
    </div>
  );
};

export default DesignPreview;
