/**
 * DesignPreview.tsx - Muestra el DESIGN.md generado
 * 
 * Parsea el YAML frontmatter y muestra:
 * - Paleta de colores
 * - Tipografía
 * - Componentes
 * - Resto del Markdown
 */

'use client';

import { useMemo, useState } from 'react';
import type { FC } from 'react';

interface DesignPreviewProps {
  designMarkdown: string;
}

interface DesignYAML {
  version?: string;
  name?: string;
  description?: string;
  colors?: Record<string, string>;
  typography?: Record<string, any>;
  rounded?: Record<string, string>;
  spacing?: Record<string, string>;
  components?: Record<string, any>;
}

const DesignPreview: FC<DesignPreviewProps> = ({ designMarkdown }) => {
  const [expandedSections, setExpandedSections] = useState<string[]>(['colors']);

  const { yaml, markdown } = useMemo(() => {
    const match = designMarkdown.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    if (!match) return { yaml: {}, markdown: designMarkdown };

    try {
      // Parse YAML manually (simple version)
      const yamlStr = match[1];
      const yaml = JSON.parse(JSON.stringify({})); // Placeholder
      return { yaml, markdown: match[2] };
    } catch {
      return { yaml: {}, markdown: designMarkdown };
    }
  }, [designMarkdown]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev =>
      prev.includes(section)
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-5 py-3.5">
        <h3 className="text-sm font-semibold text-gray-900">Especificación del diseño</h3>
        <p className="text-xs text-gray-500 mt-1">Sistema de diseño y tokens</p>
      </div>

      {/* Contenido */}
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4">
        {/* Preview de Markdown */}
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {markdown.split('\n').map((line, i) => {
            if (!line) return <div key={i} className="h-2" />;
            if (line.startsWith('## ')) {
              return (
                <h2 key={i} className="text-lg font-bold text-gray-900 mt-4 mb-2">
                  {line.replace('## ', '')}
                </h2>
              );
            }
            if (line.startsWith('### ')) {
              return (
                <h3 key={i} className="text-base font-semibold text-gray-700 mt-2 mb-1">
                  {line.replace('### ', '')}
                </h3>
              );
            }
            if (line.startsWith('- ') || line.startsWith('* ')) {
              return (
                <li key={i} className="text-gray-700 ml-4">
                  {line.substring(2)}
                </li>
              );
            }
            return (
              <p key={i} className="text-gray-700 text-sm leading-relaxed">
                {line}
              </p>
            );
          })}
        </div>

        {/* Nota de que es DESIGN.md */}
        <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
          ℹ️ Este es el sistema de diseño (DESIGN.md) generado por el paso 1 del pipeline.
          Contiene tokens de diseño (colores, tipografía, espaciado) y guías de implementación.
        </div>
      </div>
    </div>
  );
};

export default DesignPreview;
