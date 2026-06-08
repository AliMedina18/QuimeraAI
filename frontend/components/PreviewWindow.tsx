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
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-700">🎨 Vista previa en vivo</h3>
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            En vivo
          </div>
        </div>
        <button
          onClick={handleOpenFullscreen}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition flex items-center gap-1.5"
          title="Abrir en pantalla completa"
        >
          🪟 Pantalla completa
        </button>
      </div>

      {/* Iframe — el HTML va directo, sin procesamiento */}
      <div className="flex-1 overflow-hidden bg-gray-100">
        <iframe
          srcDoc={htmlOutput}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          title="Design Preview"
        />
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-gray-50 px-4 py-2 text-xs text-gray-500">
        ✦ Sitio web generado desde tu brief. Redimensiona para ver responsividad.
      </div>
    </div>
  );
};

export default PreviewWindow;
