'use client';

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface Props {
  reactComponent: string;
  designTokensCss: string;
}

type CodeTab = 'tsx' | 'css';

export default function CodeView({ reactComponent, designTokensCss }: Props) {
  const [tab, setTab] = useState<CodeTab>('tsx');
  const [copied, setCopied] = useState(false);

  if (!reactComponent) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        El código aparecerá aquí una vez generado
      </div>
    );
  }

  const currentCode = tab === 'tsx' ? reactComponent : designTokensCss;
  const language    = tab === 'tsx' ? 'tsx' : 'css';

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(currentCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_) {
      // clipboard no disponible en iframe sandbox
    }
  }

  const lines = currentCode.split('\n').length;
  const bytes = new TextEncoder().encode(currentCode).length;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-200 bg-gray-800 text-xs">
        {/* Sub-tabs */}
        <div className="flex gap-1">
          <button
            onClick={() => setTab('tsx')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition-colors ${
              tab === 'tsx'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            component.tsx
          </button>
          <button
            onClick={() => setTab('css')}
            className={`px-3 py-1 rounded text-xs font-mono font-medium transition-colors ${
              tab === 'css'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            design-tokens.css
          </button>
        </div>

        <span className="ml-auto text-gray-500">
          {lines} líneas · {(bytes / 1024).toFixed(1)} KB
        </span>

        <button
          onClick={copyToClipboard}
          className="px-2 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600 transition-colors"
        >
          {copied ? '✅ Copiado' : '📋 Copiar'}
        </button>
      </div>

      {/* Código */}
      <div className="flex-1 overflow-auto thin-scroll">
        <SyntaxHighlighter
          language={language}
          style={oneDark}
          showLineNumbers
          wrapLongLines={false}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            minHeight: '100%',
            fontSize: '12px',
            lineHeight: '1.6',
          }}
        >
          {currentCode}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
