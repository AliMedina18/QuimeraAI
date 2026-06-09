/**
 * DesignPreview.tsx — Muestra el DESIGN.md generado
 *
 * Parsea el YAML frontmatter para extraer la paleta de colores,
 * y renderiza el cuerpo Markdown con react-markdown.
 */

'use client';

import { useMemo } from 'react';
import type { FC } from 'react';
import Markdown from 'react-markdown';

interface DesignPreviewProps {
  designMarkdown: string;
}

interface ParsedFrontmatter {
  colors: Record<string, string>;
  name?: string;
  description?: string;
}

/**
 * Extrae colores HEX del bloque YAML del frontmatter.
 * Busca líneas de la forma:   clave: "#RRGGBB"
 */
function parseFrontmatterColors(yamlBlock: string): Record<string, string> {
  const colors: Record<string, string> = {};
  const colorRegex = /^\s{2,4}(\w[\w-]*):\s*['"]?(#[0-9a-fA-F]{6})['"]?/gm;
  let match;
  while ((match = colorRegex.exec(yamlBlock)) !== null) {
    colors[match[1]] = match[2];
  }
  return colors;
}

function parseFrontmatter(raw: string): ParsedFrontmatter {
  const nameMatch = raw.match(/^name:\s*(.+)$/m);
  const descMatch = raw.match(/^description:\s*['"]?(.+?)['"]?\s*$/m);

  // Extraer solo la subsección colors:
  const colorsSection = raw.match(/^colors:\s*\n((?:\s{2,4}\S.*\n?)*)/m);
  const colors = colorsSection ? parseFrontmatterColors(colorsSection[1]) : {};

  return {
    colors,
    name: nameMatch?.[1]?.trim(),
    description: descMatch?.[1]?.trim(),
  };
}

/** Contraste perceptual simple para decidir texto claro u oscuro sobre el color. */
function usesDarkText(hex: string): boolean {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 > 128;
}

const DesignPreview: FC<DesignPreviewProps> = ({ designMarkdown }) => {
  const { frontmatter, body } = useMemo(() => {
    const match = designMarkdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
    if (!match) return { frontmatter: { colors: {} }, body: designMarkdown };
    return {
      frontmatter: parseFrontmatter(match[1]),
      body: match[2],
    };
  }, [designMarkdown]);

  const colorEntries = Object.entries(frontmatter.colors);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-5 py-3.5">
        <h3 className="text-sm font-semibold text-gray-900">
          {frontmatter.name ?? 'Especificación del diseño'}
        </h3>
        {frontmatter.description && (
          <p className="text-xs text-gray-500 mt-0.5 truncate">
            {frontmatter.description}
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Paleta de colores */}
        {colorEntries.length > 0 && (
          <section>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Paleta de colores
            </h4>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {colorEntries.map(([name, hex]) => (
                <div key={name} className="flex flex-col gap-1">
                  <div
                    className="h-10 rounded-md shadow-sm border border-black/5 flex items-center justify-center"
                    style={{ backgroundColor: hex }}
                  >
                    <span
                      className="text-xs font-mono font-medium"
                      style={{ color: usesDarkText(hex) ? '#1a1a1a' : '#ffffff' }}
                    >
                      {hex}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 truncate">{name}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Cuerpo Markdown */}
        <section>
          <div className="prose prose-sm max-w-none
            prose-headings:text-gray-900 prose-headings:font-semibold
            prose-p:text-gray-700 prose-p:leading-relaxed
            prose-li:text-gray-700 prose-code:text-blue-700
            prose-code:bg-blue-50 prose-code:px-1 prose-code:rounded">
            <Markdown>{body}</Markdown>
          </div>
        </section>

        {/* Nota informativa */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
          Sistema de diseño generado por el Paso 1 del pipeline. Contiene tokens de
          diseño (colores, tipografía, espaciado) y guías de implementación.
        </div>
      </div>
    </div>
  );
};

export default DesignPreview;
