'use client';

interface Props {
  reactComponent: string;
  designTokensCss: string;
}

/**
 * Renderiza el componente React generado dentro de un iframe usando:
 * - Babel Standalone para transpilar TSX en el browser
 * - React UMD + ReactDOM UMD desde CDN (sin build step)
 * - Design tokens CSS inyectados directamente
 * - Tailwind CSS CDN (Play CDN)
 */
export default function Preview({ reactComponent, designTokensCss }: Props) {
  if (!reactComponent) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400 text-sm gap-2">
        <span className="text-4xl">🖥</span>
        <p>El preview aparecerá aquí una vez generado el componente</p>
      </div>
    );
  }

  // Transformar imports de React para que no rompan en modo UMD
  // El componente viene con `import React...` que no funciona en browser ESM sin bundler
  const componentCode = reactComponent
    // 1. Eliminar import statements
    .replace(/^import\s+.*?from\s+['"][^'"]+['"]\s*;?\s*$/gm, '')
    // 2. Eliminar 'export default' dejando la declaracion (function/const/class)
    .replace(/^export\s+default\s+/gm, '')
    // 3. Eliminar named exports: export { Foo, Bar }
    .replace(/^export\s+\{[^}]*\}\s*;?\s*$/gm, '')
    // 4. Eliminar 'export' en declaraciones: export function / export const
    .replace(/^export\s+(function|const|class|let|var)\s+/gm, '$1 ')
    .trim();

  // Extraer el nombre real del componente del código generado
  // Busca la primera declaracion con mayuscula: function Foo / const Foo / class Foo
  const extractedName = (() => {
    const m = componentCode.match(/^(?:function|const|class)\s+([A-Z][a-zA-Z0-9]*)/m);
    return m ? m[1] : null;
  })();

  // Lista de nombres candidatos — el extraido va primero
  const candidateNames = [
    ...(extractedName ? [extractedName] : []),
    'QuimeraComponent', 'App', 'Component', 'Dashboard',
    'LandingPage', 'Page', 'Layout', 'Hero', 'Section',
    'RestaurantePage', 'Homepage', 'Main', 'Wrapper',
  ];

  const srcdoc = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Preview</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Design tokens generados por Quimera */
    ${designTokensCss}

    body { margin: 0; padding: 16px; background: #f9fafb; font-family: sans-serif; }
    #root { min-height: 100vh; }

    /* Error overlay */
    #error-overlay {
      display: none;
      position: fixed; inset: 0;
      background: #fef2f2;
      color: #991b1b;
      font-family: monospace; font-size: 12px;
      padding: 24px; overflow: auto;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <div id="error-overlay"></div>
  <script type="text/babel" data-presets="react,typescript">
    const { useState, useEffect, useRef, useCallback, useMemo } = React;

    ${componentCode}

    // Detectar el componente exportado
    // Los candidatos incluyen el nombre extraido del codigo generado
    function findExportedComponent() {
      const names = ${JSON.stringify(candidateNames)};
      for (const name of names) {
        try {
          // eslint-disable-next-line no-eval
          const val = eval(name);
          if (typeof val === 'function') return val;
        } catch (_) {}
      }
      return null;
    }

    try {
      const ExportedComponent = findExportedComponent();
      if (ExportedComponent) {
        ReactDOM.createRoot(document.getElementById('root')).render(
          React.createElement(ExportedComponent)
        );
      } else {
        document.getElementById('root').innerHTML =
          '<p style="color:#6b7280;font-size:14px;padding:24px">⚠️ No se encontró un componente exportado con nombre estándar. Revisa el tab "Código".</p>';
      }
    } catch (err) {
      const overlay = document.getElementById('error-overlay');
      overlay.style.display = 'block';
      overlay.textContent = '❌ Error de renderizado:\\n\\n' + err.stack;
    }
  </script>
</body>
</html>`;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white text-xs text-gray-400">
        <span>Preview — renderizado en navegador con Babel + React UMD</span>
        <span className="text-yellow-500">
          ⚠️ Imports externos no disponibles en preview
        </span>
      </div>
      <iframe
        srcDoc={srcdoc}
        sandbox="allow-scripts"
        className="flex-1 w-full border-0 bg-white"
        title="Component Preview"
      />
    </div>
  );
}
