/**
 * HtmlCodeView.tsx (ReactPreview.tsx) - Muestra el HTML generado con syntax highlighting
 *
 * Características:
 * - Código HTML con highlighting básico
 * - Botón para copiar código
 * - Botón para abrir en nueva ventana (fullscreen)
 */

'use client';

import { useState } from 'react';
import type { FC } from 'react';

interface HtmlCodeViewProps {
  htmlOutput: string;
}

const HtmlCodeView: FC<HtmlCodeViewProps> = ({ htmlOutput }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(htmlOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenFullscreen = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, 'quimera-preview', 'width=1400,height=900');
  };

  const lineCount = htmlOutput.split('\n').length;
  const sizeKb = (new Blob([htmlOutput]).size / 1024).toFixed(1);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Barra de acciones */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50 px-4 py-3">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-gray-700">HTML generado</h3>
          <span className="text-xs text-gray-400">{lineCount} líneas · {sizeKb} KB</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-medium rounded transition"
          >
            {copied ? '✓ Copiado' : '📋 Copiar'}
          </button>
          <button
            onClick={handleOpenFullscreen}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition flex items-center gap-1.5"
          >
            🪟 Abrir en ventana
          </button>
        </div>
      </div>

      {/* Código */}
      <div className="flex-1 overflow-auto p-4 bg-gray-50">
        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed">
          <code>{htmlOutput}</code>
        </pre>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-gray-50 px-4 py-2 text-xs text-gray-500">
        💡 HTML autocontenido — puedes guardarlo como .html y abrirlo directamente en el navegador.
      </div>
    </div>
  );
};

export default HtmlCodeView;
