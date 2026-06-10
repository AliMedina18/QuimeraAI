'use client';

import type { FC } from 'react';
import { IconExpand } from './Icons';

interface PreviewWindowProps {
  htmlOutput: string;
}

const NAV_BLOCK_SCRIPT = `
<script>
(function() {
  function neutralizeLinks() {
    document.querySelectorAll('a[href]').forEach(function(a) {
      var href = (a.getAttribute('href') || '').trim();
      if (!href || href === '#' || href.startsWith('#') || href.startsWith('javascript:')) return;
      var isExternal = href.indexOf('http://') === 0 || href.indexOf('https://') === 0;
      if (isExternal) {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      } else {
        a.setAttribute('data-href', href);
        a.setAttribute('href', '#');
        a.style.cursor = 'pointer';
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', neutralizeLinks);
  } else {
    neutralizeLinks();
  }
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
    if (!href || href === '#' || href.startsWith('#') || href.startsWith('javascript:')) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var isExternal = href.indexOf('http://') === 0 || href.indexOf('https://') === 0;
    if (isExternal) window.open(href, '_blank', 'noopener');
  }, true);
  document.addEventListener('submit', function(e) { e.preventDefault(); }, true);
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
    const url  = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      <div className="flex items-center justify-between border-b border-gray-100 bg-white px-5 py-3.5">
        <div className="flex items-center gap-2.5">
          <h3 className="text-sm font-semibold text-gray-900">Sitio web generado</h3>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full"/>
            <span className="text-xs text-gray-400">En vivo</span>
          </div>
        </div>
        <button
          onClick={handleOpenFullscreen}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-medium rounded-md transition-colors"
          title="Abrir en pantalla completa"
        >
          <IconExpand size={13}/>
          Expandir
        </button>
      </div>

      <div className="flex-1 overflow-hidden bg-gray-50">
        <iframe
          srcDoc={safeHtml}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-popups allow-forms"
          title="Sitio web generado"
        />
      </div>
    </div>
  );
};

export default PreviewWindow;
