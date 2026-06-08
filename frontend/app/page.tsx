'use client';

import { useState } from 'react';
import { usePipeline } from '@/hooks/usePipeline';
import ChatUI from '@/components/ChatUI';
import DesignPreview from '@/components/DesignPreview';
import HtmlCodeView from '@/components/ReactPreview';
import PreviewWindow from '@/components/PreviewWindow';

type Tab = 'preview' | 'design' | 'code';

/**
 * Home - Página principal Quimera AI
 *
 * Layout:
 * - Lado izquierdo (40%): ChatUI (input del brief)
 * - Lado derecho (60%): Tabs con DESIGN.md y preview del sitio
 * - Responsive: en móvil se apilan verticalmente
 */
export default function Home() {
  const { state, generate, reset } = usePipeline();
  const [activeTab, setActiveTab] = useState<Tab>('preview');

  const isRunning = state.status === 'running';
  const isCompleted = state.status === 'completed' && state.designMarkdown;
  const hasError = state.status === 'error';

  return (
    <div className="flex flex-col lg:flex-row h-screen overflow-hidden bg-gray-50">
      {/* ── Panel izquierdo (Chat) 40% en desktop, 100% en móvil ── */}
      <aside className="w-full lg:w-[40%] lg:min-w-[320px] flex flex-col border-r border-gray-200 bg-white shadow-sm lg:shadow-none order-2 lg:order-1">
        {/* Header */}
        <header className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <span className="text-2xl">✦</span>
            <h1 className="text-lg font-bold text-gray-900 tracking-tight">
              Quimera <span className="text-blue-600">AI</span>
            </h1>
          </div>
          {state.status !== 'idle' && (
            <button
              onClick={reset}
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
              title="Nueva solicitud"
            >
              ✕
            </button>
          )}
        </header>

        {/* Chat UI */}
        <div className="flex-1 overflow-y-auto thin-scroll">
          <ChatUI state={state} onGenerate={generate} />
        </div>
      </aside>

      {/* ── Panel derecho (Preview) 60% en desktop, 100% en móvil ── */}
      <main className="flex-1 flex flex-col overflow-hidden order-1 lg:order-2">
        {/* Tabs */}
        <nav className="flex border-b border-gray-200 bg-white px-4">
          <button
            onClick={() => setActiveTab('preview')}
            disabled={!isCompleted}
            className={`
              px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${activeTab === 'preview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
              }
              ${!isCompleted ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            🎨 Vista previa
          </button>

          <button
            onClick={() => setActiveTab('design')}
            disabled={!isCompleted}
            className={`
              px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${activeTab === 'design'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
              }
              ${!isCompleted ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            📐 Diseño
          </button>

          <button
            onClick={() => setActiveTab('code')}
            disabled={!isCompleted}
            className={`
              px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${activeTab === 'code'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
              }
              ${!isCompleted ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            &lt;/&gt; HTML
          </button>

          {/* Loading indicator */}
          {isRunning && (
            <div className="ml-auto flex items-center gap-2 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
              <span className="text-xs text-gray-400">Generando...</span>
            </div>
          )}
        </nav>

        {/* Contenido */}
        <div className="flex-1 overflow-hidden bg-gray-50">
          {state.status === 'idle' ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6 lg:p-12">
              <div className="text-5xl lg:text-6xl mb-4">✦</div>
              <p className="text-gray-400 text-base lg:text-lg max-w-sm">
                Escribe tu brief en el panel izquierdo y haz clic en{' '}
                <span className="font-semibold text-gray-600">Generar</span>
              </p>
            </div>
          ) : isRunning ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6">
              <div className="flex gap-2 mb-4">
                <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" />
                <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
              <p className="text-gray-600">Generando diseño y HTML...</p>
            </div>
          ) : hasError ? (
            <div className="flex items-center justify-center h-full p-6">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-sm">
                <p className="text-red-700 font-semibold mb-2">Error</p>
                <p className="text-red-600 text-sm">{state.error}</p>
                <button
                  onClick={reset}
                  className="mt-3 px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition"
                >
                  Intentar nuevamente
                </button>
              </div>
            </div>
          ) : activeTab === 'preview' ? (
            <PreviewWindow htmlOutput={state.htmlOutput} />
          ) : activeTab === 'design' ? (
            <DesignPreview designMarkdown={state.designMarkdown} />
          ) : (
            <HtmlCodeView htmlOutput={state.htmlOutput} />
          )}
        </div>
      </main>
    </div>
  );
}
