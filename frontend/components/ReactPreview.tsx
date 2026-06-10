'use client';

import { useState } from 'react';
import type { FC } from 'react';
import { IconCopy, IconCheck, IconDownload, IconExternalLink } from './Icons';

interface HtmlCodeViewProps {
  htmlOutput: string;
}

const HtmlCodeView: FC<HtmlCodeViewProps> = ({ htmlOutput }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(htmlOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'quimera-diseno.html';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOpenInBrowser = () => {
    const blob = new Blob([htmlOutput], { type: 'text/html' });
    const url  = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  const lineCount = htmlOutput.split('\n').length;
  const sizeKb    = (new Blob([htmlOutput]).size / 1024).toFixed(1);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-white">
      {/* Barra de acciones */}
      <div className="flex items-center justify-between border-b border-gray-100 bg-white px-4 py-3">
        <div className="flex items-center gap-2.5">
          <h3 className="text-sm font-semibold text-gray-800">HTML generado</h3>
          <span className="text-xs text-gray-400 tabular-nums">{lineCount} líneas · {sizeKb} KB</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-md transition-colors"
            title="Copiar código"
          >
            {copied
              ? <><IconCheck size={13} className="text-green-600"/><span className="text-green-700">Copiado</span></>
              : <><IconCopy size={13}/>Copiar</>
            }
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-medium rounded-md transition-colors"
            title="Descargar como archivo .html"
          >
            <IconDownload size={13}/>
            Descargar .html
          </button>
          <button
            onClick={handleOpenInBrowser}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium rounded-md transition-colors"
            title="Abrir en el navegador"
          >
            <IconExternalLink size={13}/>
            Abrir
          </button>
        </div>
      </div>

      {/* Código */}
      <div className="flex-1 overflow-auto bg-gray-950 p-4">
        <pre className="text-gray-200 text-xs font-mono leading-relaxed whitespace-pre-wrap break-words">
          <code>{htmlOutput}</code>
        </pre>
      </div>
    </div>
  );
};

export default HtmlCodeView;
