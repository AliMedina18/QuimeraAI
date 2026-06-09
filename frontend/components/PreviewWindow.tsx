/**
 * PreviewWindow.tsx - Renderiza el HTML generado en un iframe
 */
'use client';

import type { FC } from 'react';

interface PreviewWindowProps {
  htmlOutput: string;
}

/**
 * Script inyectado en el HTML generado para bloquear toda navegacion no deseada.
 * Tres capas de proteccion:
 *   1. Walk-up manual del DOM (captura clicks en SVG/iconos/elementos anidados)
 *   2. Bloqueo de form submit
 *   3. Navigation API (captura onclick con window.location = '...')
 */
const NAV_BLOCK_SCRIPT = `
<script>
(function() {
  function findAnchor(el) {
    while (el && el !== document.body) {
      if (el.tagName && el.tagName.toUpperCase() === 'A') return el;
      el = el.parentNode;
    }
    return null;
  }

  document.addEventListener('click', function(e) {
    var a = findAnchor(e.target);
    if (!a) return;
    var href = (a.getAttribute('href') || '').trim();
    if (!href || href.startsWith('javascript:') || href.startsWith('#')) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var isHttp = href.indexOf('http://') === 0 || href.indexOf('https://') === 0;
    if (isHttp) window.open(href, '_blank', 'noopener');
  }, true);

  document.addEventListener('submit', function(e) {
    e.preventDefault();
  }, true);

  if (window.navigation) {
    window.navigation.addEventListener('navigate', function(e) {
      var url = (e.destination && e.destination.url) || '';
      var currentBase = location.href.split('#')[0];
      var destBase = url.split('#')[0];
      if (destBase !== currentBase && e.canIntercept) {
        e.intercept({ handler: function() {} });
      }
    });
  }
})();
<\/script>`;

const injectNavBlock = (html: string): string => {
  const bodyMatch = html.match(/<body[^>]*>/i);
  if (bodyMatch && bodyMatch.index !== undefined) {
    const insertAt = bodyMatch.index + bodyMatch[0].length;
    return html.slice(0, insertAt) + NAV_BLOCK_SCRIPT + html.slice(insertAt);
  }
  return NAV_BLOCK_SCRIPT + html;
};

const PreviewWindow: FC<PreviewWindowProps> = ({ htmlOutput }) => {
  const safeHtml = injectNavBlock(htmlOutput);

  const handleOpenFullscreen = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, 'quimera-preview', 'width=1400,height=900');
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
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
          className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-md transition-all duration-150"
          title="Abrir en pantalla completa"
        >
          Expandir
        </button>
      </div>

      <div className="flex-1 overflow-hidden bg-gray-50">
        <iframe
          srcDoc={safeHtml}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          title="Design Preview"
        />
      </div>
    </div>
  );
};

export default PreviewWindow;
