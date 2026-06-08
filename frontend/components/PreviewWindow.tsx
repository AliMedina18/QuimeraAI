/**
 * PreviewWindow.tsx - Renderiza el HTML generado en un iframe
 *
 * Enfoque simple (como Google Stitch):
 * El backend genera HTML autocontenido → se pasa directamente a srcDoc.
 * Sin transpilación, sin Babel, sin CDN de React. Funciona instantáneo.
 */

'use client';

import type { FC } from 'react';

interface PreviewWindowProps {
  htmlOutput: string;
}

const PreviewWindow: FC<PreviewWindowProps> = ({ htmlOutput }) => {
  const handleOpenFullscreen = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, 'quimera-preview', 'width=1400,height=900');
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Header — Apple style: minimal */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-white px-5 py-3.5">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-900">Sitio web generado</h3>
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            En vivo
          </div>
        </div>
        <button
          onClick={handleOpenFullscreen}
          className="
            px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 
            text-xs font-medium rounded-md transition-all duration-150
            flex items-center gap-1.5
          "
          title="Abrir en pantalla completa"
        >
          ↗ Expandir
        </button>
      </div>

      {/* Iframe — full responsive preview */}
      <div className="flex-1 overflow-hidden bg-gray-50">
        <iframe
          srcDoc={htmlOutput}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          title="Design Preview"
        />
      </div>
    </div>
  );
};

export default PreviewWindow;
