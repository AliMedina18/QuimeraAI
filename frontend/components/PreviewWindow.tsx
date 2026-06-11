'use client';

import { useEffect, useCallback, useState, type FC } from 'react';
import { IconExpand } from './Icons';
import type { SelectedElement } from '@/types/pipeline';

interface PreviewWindowProps {
  htmlOutput: string;
  studioMode?: boolean;
  selectedElement?: SelectedElement | null;
  onElementSelected?: (element: SelectedElement | null) => void;
  onElementEdited?: (oldOuterHtml: string, newOuterHtml: string) => void;
}

const NAV_BLOCK_SCRIPT = `<script>
(function() {
  function neutralizeLinks() {
    document.querySelectorAll('a[href]').forEach(function(a) {
      var href = (a.getAttribute('href') || '').trim();
      if (!href || href === '#' || href.startsWith('#') || href.startsWith('javascript:')) return;
      var isExternal = href.indexOf('http://') === 0 || href.indexOf('https://') === 0;
      if (isExternal) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
      else { a.setAttribute('data-href', href); a.setAttribute('href', '#'); a.style.cursor = 'pointer'; }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', neutralizeLinks);
  else neutralizeLinks();
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
    e.preventDefault(); e.stopImmediatePropagation();
    if (href.indexOf('http://') === 0 || href.indexOf('https://') === 0) window.open(href, '_blank', 'noopener');
  }, true);
  document.addEventListener('submit', function(e) { e.preventDefault(); }, true);
})();
<\/script>`;

const STUDIO_SELECT_SCRIPT = `<script>
(function() {
  // ---- Estado ----
  var selectedEl = null;
  var hoveredEl = null;
  var editingEl = null;
  var editingOldHtml = null;
  var editingCancelled = false;
  var overlayEl = null;
  var resizeEl = null;
  var resizeCursor = null;
  var resizeStartX = 0, resizeStartY = 0;
  var resizeStartW = 0, resizeStartH = 0;
  var resizeOldHtml = null;

  var RESIZE_FLAGS = {
    'nw-resize': {n:1,w:1,e:0,s:0},
    'n-resize':  {n:1,w:0,e:0,s:0},
    'ne-resize': {n:1,w:0,e:1,s:0},
    'w-resize':  {n:0,w:1,e:0,s:0},
    'e-resize':  {n:0,w:0,e:1,s:0},
    'sw-resize': {n:0,w:1,e:0,s:1},
    's-resize':  {n:0,w:0,e:0,s:1},
    'se-resize': {n:0,w:0,e:1,s:1},
  };

  // ---- Helpers ----
  function isIgnorable(el) {
    if (!el || el === document.body || el === document.documentElement) return true;
    var tag = el.tagName && el.tagName.toLowerCase();
    return tag === 'html' || tag === 'body' || tag === 'head' || tag === 'script' || tag === 'style';
  }

  /**
   * Devuelve el outerHTML del elemento SIN los estilos de highlight que
   * inyectamos (outline, outlineOffset, boxShadow). Así el string coincide
   * exactamente con lo que está en el HTML fuente de React y los reemplazos
   * de color/resize/IA funcionan correctamente.
   */
  function getCleanOuterHtml(el) {
    var savedOutline       = el.style.outline;
    var savedOffset        = el.style.outlineOffset;
    var savedShadow        = el.style.boxShadow;
    el.style.outline       = '';
    el.style.outlineOffset = '';
    el.style.boxShadow     = '';
    var html = el.outerHTML;
    el.style.outline       = savedOutline;
    el.style.outlineOffset = savedOffset;
    el.style.boxShadow     = savedShadow;
    return html;
  }

  // Highlight visible en cualquier fondo: halo blanco + borde indigo
  function applyHoverHighlight(el) {
    el.style.outline = '2px solid rgba(99,102,241,0.7)';
    el.style.outlineOffset = '3px';
    el.style.boxShadow = '0 0 0 2px rgba(255,255,255,0.7)';
  }

  function applySelectHighlight(el) {
    el.style.outline = '2px solid #6366f1';
    el.style.outlineOffset = '3px';
    el.style.boxShadow = '0 0 0 2px rgba(255,255,255,0.9), 0 0 0 6px rgba(99,102,241,0.35)';
  }

  function clearHighlight(el) {
    el.style.outline = '';
    el.style.outlineOffset = '';
    el.style.boxShadow = '';
  }

  function clearHover() {
    if (hoveredEl && hoveredEl !== selectedEl) clearHighlight(hoveredEl);
    hoveredEl = null;
  }

  function clearSelected() {
    removeOverlay();
    if (selectedEl) clearHighlight(selectedEl);
    selectedEl = null;
  }

  // ---- Edicion de texto ----
  function finishEditing(save) {
    if (!editingEl) return;
    var el = editingEl;
    var oldHtml = editingOldHtml;
    var wasCancelled = editingCancelled;
    editingEl = null; editingOldHtml = null; editingCancelled = false;
    el.contentEditable = 'false';
    clearHighlight(el);
    if (save && !wasCancelled) {
      // Limpiar contenteditable Y los estilos de highlight antes de comparar
      var newHtml = getCleanOuterHtml(el).replace(/\s+contenteditable\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]*)/gi, '');
      if (newHtml !== oldHtml) {
        window.parent.postMessage({ type: 'QUIMERA_TEXT_EDITED', oldOuterHtml: oldHtml, newOuterHtml: newHtml }, '*');
      }
    }
    window.parent.postMessage({ type: 'QUIMERA_TEXT_EDIT_END' }, '*');
  }

  // ---- Overlay de resize ----
  function updateOverlayPosition() {
    if (!overlayEl || !selectedEl) return;
    var rect = selectedEl.getBoundingClientRect();
    overlayEl.style.left = rect.left + 'px';
    overlayEl.style.top = rect.top + 'px';
    overlayEl.style.width = rect.width + 'px';
    overlayEl.style.height = rect.height + 'px';
  }

  function removeOverlay() {
    if (overlayEl) { try { overlayEl.parentNode.removeChild(overlayEl); } catch(ex){} overlayEl = null; }
  }

  function createOverlay(el) {
    removeOverlay();
    var rect = el.getBoundingClientRect();
    var ov = document.createElement('div');
    ov.style.cssText = 'position:fixed;pointer-events:none;z-index:2147483647;border:2px dashed rgba(99,102,241,0.8);box-sizing:border-box;'
      + 'left:' + rect.left + 'px;top:' + rect.top + 'px;width:' + rect.width + 'px;height:' + rect.height + 'px;';

    var handles = [
      ['nw-resize', 0,   0],
      ['n-resize',  50,  0],
      ['ne-resize', 100, 0],
      ['w-resize',  0,   50],
      ['e-resize',  100, 50],
      ['sw-resize', 0,   100],
      ['s-resize',  50,  100],
      ['se-resize', 100, 100],
    ];

    handles.forEach(function(d) {
      var h = document.createElement('div');
      h.style.cssText = 'position:absolute;width:10px;height:10px;background:white;border:2px solid rgba(99,102,241,1);'
        + 'border-radius:2px;pointer-events:all;box-sizing:border-box;cursor:' + d[0] + ';'
        + 'transform:translate(-50%,-50%);left:' + d[1] + '%;top:' + d[2] + '%;'
        + 'box-shadow:0 1px 4px rgba(0,0,0,0.3);';
      h.addEventListener('mousedown', function(e) {
        e.preventDefault(); e.stopPropagation();
        startResize(el, d[0], e.clientX, e.clientY);
      });
      ov.appendChild(h);
    });

    document.documentElement.appendChild(ov);
    overlayEl = ov;
  }

  // ---- Logica de resize ----
  function startResize(el, cursor, sx, sy) {
    resizeEl = el;
    resizeCursor = cursor;
    resizeStartX = sx; resizeStartY = sy;
    var rect = el.getBoundingClientRect();
    resizeStartW = rect.width; resizeStartH = rect.height;
    resizeOldHtml = getCleanOuterHtml(el); // sin estilos de highlight
    document.addEventListener('mousemove', onResizeMove, true);
    document.addEventListener('mouseup', onResizeEnd, true);
  }

  function onResizeMove(e) {
    if (!resizeEl) return;
    var f = RESIZE_FLAGS[resizeCursor];
    if (!f) return;
    var dx = e.clientX - resizeStartX;
    var dy = e.clientY - resizeStartY;
    if (f.e) resizeEl.style.width = Math.max(20, resizeStartW + dx) + 'px';
    if (f.w) resizeEl.style.width = Math.max(20, resizeStartW - dx) + 'px';
    if (f.s) resizeEl.style.minHeight = Math.max(20, resizeStartH + dy) + 'px';
    if (f.n) resizeEl.style.minHeight = Math.max(20, resizeStartH - dy) + 'px';
    updateOverlayPosition();
  }

  function onResizeEnd() {
    document.removeEventListener('mousemove', onResizeMove, true);
    document.removeEventListener('mouseup', onResizeEnd, true);
    if (!resizeEl) return;
    var f = RESIZE_FLAGS[resizeCursor] || {n:0,w:0,e:0,s:0};
    if (f.e || f.w) {
      var parentW = resizeEl.parentElement ? resizeEl.parentElement.offsetWidth : window.innerWidth;
      if (parentW > 0) {
        var pct = Math.round(resizeEl.offsetWidth / parentW * 1000) / 10;
        resizeEl.style.width = pct + '%';
      }
    }
    var newHtml = getCleanOuterHtml(resizeEl); // sin estilos de highlight
    if (newHtml !== resizeOldHtml) {
      window.parent.postMessage({ type: 'QUIMERA_ELEMENT_RESIZED', oldOuterHtml: resizeOldHtml, newOuterHtml: newHtml }, '*');
    }
    resizeEl = null; resizeCursor = null; resizeOldHtml = null;
    updateOverlayPosition();
  }

  // ---- Listeners de mouse ----
  document.addEventListener('mouseover', function(e) {
    if (editingEl || resizeEl) return;
    var el = e.target;
    if (isIgnorable(el) || el === selectedEl) return;
    clearHover(); hoveredEl = el;
    applyHoverHighlight(el);
  }, true);

  document.addEventListener('mouseout', function(e) {
    if (editingEl || resizeEl) return;
    var el = e.target;
    if (el === hoveredEl && el !== selectedEl) { clearHighlight(el); hoveredEl = null; }
  }, true);

  document.addEventListener('click', function(e) {
    if (editingEl || resizeEl) return;
    if (overlayEl && overlayEl.contains(e.target)) return;
    var el = e.target;
    if (isIgnorable(el)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (el === selectedEl) {
      clearSelected();
      window.parent.postMessage({ type: 'QUIMERA_ELEMENT_DESELECTED' }, '*');
      return;
    }
    clearSelected();
    selectedEl = el;
    applySelectHighlight(el);
    createOverlay(el);
    window.parent.postMessage({
      type: 'QUIMERA_ELEMENT_SELECTED',
      tag: (el.tagName || 'div').toLowerCase(),
      id: el.id || '',
      classes: (typeof el.className === 'string' ? el.className : '') || '',
      text: (el.innerText || '').slice(0, 120),
      outerHTML: getCleanOuterHtml(el),
    }, '*');
  }, true);

  // ---- Doble clic: edicion de texto ----
  document.addEventListener('dblclick', function(e) {
    if (resizeEl) return;
    var el = e.target;
    if (isIgnorable(el)) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (editingEl && editingEl !== el) finishEditing(true);
    clearSelected(); removeOverlay();
    editingOldHtml = el.outerHTML;
    editingEl = el;
    el.contentEditable = 'true';
    el.style.outline = '2px solid rgba(16,185,129,1)';
    el.style.outlineOffset = '3px';
    el.style.boxShadow = '0 0 0 2px rgba(255,255,255,0.9), 0 0 0 6px rgba(16,185,129,0.25)';
    el.focus();
    window.parent.postMessage({ type: 'QUIMERA_TEXT_EDIT_START', tag: el.tagName.toLowerCase() }, '*');
  }, true);

  document.addEventListener('keydown', function(e) {
    if (!editingEl) return;
    if (e.key === 'Escape') { e.preventDefault(); editingCancelled = true; editingEl.blur(); }
    if (e.key === 'Enter' && !e.shiftKey) {
      var tag = editingEl.tagName.toLowerCase();
      var blockTags = ['div','p','section','article','header','footer','main','aside','li','ul','ol','nav','form'];
      if (!blockTags.includes(tag)) { e.preventDefault(); editingEl.blur(); }
    }
  }, true);

  document.addEventListener('focusout', function(e) {
    if (e.target === editingEl) finishEditing(true);
  }, true);

  window.addEventListener('scroll', function() { updateOverlayPosition(); }, true);

  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'QUIMERA_CLEAR_SELECTION') clearSelected();
  });
})();
<\/script>`;

const PERMISSIVE_CSP = '<meta http-equiv="Content-Security-Policy" content="default-src * \'unsafe-inline\' \'unsafe-eval\' data: blob:;">';

function sanitizeForIframe(html: string): string {
  let out = html.replace(/<meta\s[^>]*http-equiv\s*=\s*["']?Content-Security-Policy["']?[^>]*\/?>/gi, '');
  out = out.replace(/<meta\s[^>]*name\s*=\s*["']?referrer["']?[^>]*no-referrer[^>]*\/?>/gi, '');
  const headMatch = out.match(/<head[^>]*>/i);
  if (headMatch && headMatch.index !== undefined) {
    const insertAt = headMatch.index + headMatch[0].length;
    out = out.slice(0, insertAt) + '\n' + PERMISSIVE_CSP + out.slice(insertAt);
  }
  return out;
}

function injectAfterBody(html: string, script: string): string {
  const bodyMatch = html.match(/<body[^>]*>/i);
  if (bodyMatch && bodyMatch.index !== undefined) {
    const insertAt = bodyMatch.index + bodyMatch[0].length;
    return html.slice(0, insertAt) + script + html.slice(insertAt);
  }
  return script + html;
}

const PreviewWindow: FC<PreviewWindowProps> = ({
  htmlOutput,
  studioMode = false,
  selectedElement,
  onElementSelected,
  onElementEdited,
}) => {
  const [isTextEditing, setIsTextEditing] = useState(false);

  const base = sanitizeForIframe(htmlOutput);
  const withNav = injectAfterBody(base, NAV_BLOCK_SCRIPT);
  const safeHtml = studioMode ? injectAfterBody(withNav, STUDIO_SELECT_SCRIPT) : withNav;

  const handleMessage = useCallback((event: MessageEvent) => {
    const { data } = event;
    if (!data) return;

    if (data.type === 'QUIMERA_TEXT_EDIT_START') { setIsTextEditing(true); return; }
    if (data.type === 'QUIMERA_TEXT_EDIT_END')   { setIsTextEditing(false); return; }

    if (data.type === 'QUIMERA_TEXT_EDITED') {
      onElementEdited?.(data.oldOuterHtml, data.newOuterHtml);
      setIsTextEditing(false);
      return;
    }

    if (data.type === 'QUIMERA_ELEMENT_RESIZED') {
      onElementEdited?.(data.oldOuterHtml, data.newOuterHtml);
      return;
    }

    if (!onElementSelected) return;
    if (data.type === 'QUIMERA_ELEMENT_SELECTED') {
      onElementSelected({
        tag: data.tag,
        id: data.id,
        classes: data.classes,
        text: data.text,
        outerHTML: data.outerHTML,
      });
    } else if (data.type === 'QUIMERA_ELEMENT_DESELECTED') {
      onElementSelected(null);
    }
  }, [onElementSelected, onElementEdited]);

  useEffect(() => {
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [handleMessage]);

  const handleOpenFullscreen = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    window.open(URL.createObjectURL(blob), '_blank');
  };

  const statusDot = isTextEditing
    ? 'bg-emerald-500 animate-pulse'
    : studioMode ? 'bg-indigo-500' : 'bg-green-500';

  const statusLabel = isTextEditing
    ? 'Editando - Enter para guardar, Esc para cancelar'
    : studioMode
      ? (selectedElement
          ? 'Arrastra handles para redimensionar, doble clic para editar texto'
          : 'Clic para seleccionar')
      : 'En vivo';

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      <div className="flex items-center justify-between border-b border-gray-100 bg-white px-5 py-3.5 shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 shrink-0">Sitio web generado</h3>
          <div className="flex items-center gap-1.5 min-w-0">
            <div className={['w-1.5 h-1.5 rounded-full shrink-0', statusDot].join(' ')}/>
            <span className="text-xs text-gray-400 truncate">{statusLabel}</span>
          </div>
        </div>
        <button
          onClick={handleOpenFullscreen}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-medium rounded-md transition-colors shrink-0 ml-2"
        >
          <IconExpand size={12}/>
          Pantalla completa
        </button>
      </div>
      <div className="relative flex-1 overflow-hidden">
        <iframe
          srcDoc={safeHtml}
          className="w-full h-full border-0"
          title="Vista previa"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  );
};

export default PreviewWindow;
