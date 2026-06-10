'use client';

import { useState } from 'react';
import { usePipeline } from '@/hooks/usePipeline';
import ChatUI from '@/components/ChatUI';
import DesignPreview from '@/components/DesignPreview';
import HtmlCodeView from '@/components/ReactPreview';
import PreviewWindow from '@/components/PreviewWindow';
import QuimeraLoader from '@/components/QuimeraLoader';
import QuimeraIcon from '@/components/QuimeraIcon';
import { IconGlobe, IconPalette, IconCode, IconX } from '@/components/Icons';

type Tab = 'preview' | 'design' | 'code';

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'preview', label: 'Sitio web', icon: <IconGlobe size={14}/> },
  { id: 'design',  label: 'Diseño',    icon: <IconPalette size={14}/> },
  { id: 'code',    label: 'HTML',      icon: <IconCode size={14}/> },
];

const STEP_LABELS: Record<string, string> = {
  analyzing:  'Analizando brief…',
  generating: 'Generando código…',
};

export default function Home() {
  const { state, generate, reset } = usePipeline();
  const [activeTab, setActiveTab] = useState<Tab>('preview');

  const isRunning   = state.status === 'running';
  const isCompleted = state.status === 'completed' && state.designMarkdown;
  const hasError    = state.status === 'error';

  return (
    <div className="flex flex-col lg:flex-row h-screen overflow-hidden bg-white">
      {/* ── Panel izquierdo ── */}
      <aside className="w-full lg:w-[28%] lg:min-w-[340px] flex flex-col border-r border-gray-100 bg-white order-2 lg:order-1">
        <header className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <QuimeraIcon size={28}/>
            <h1 className="text-base font-bold text-gray-900 tracking-tight">
              Quimera <span className="text-indigo-600">AI</span>
            </h1>
          </div>
          {state.status !== 'idle' && (
            <button
              onClick={reset}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Nueva solicitud"
            >
              <IconX size={14}/>
            </button>
          )}
        </header>

        <div className="flex-1 overflow-y-auto">
          <ChatUI state={state} onGenerate={generate}/>
        </div>
      </aside>

      {/* ── Panel derecho ── */}
      <main className="flex-1 flex flex-col overflow-hidden order-1 lg:order-2">
        {/* Tabs */}
        <nav className="flex border-b border-gray-100 bg-white px-5">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={!isCompleted}
              className={`
                flex items-center gap-1.5 px-4 py-3.5 text-[13px] font-medium border-b-2 transition-all
                ${activeTab === tab.id
                  ? 'border-indigo-600 text-gray-900'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }
                ${!isCompleted ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}

          {isRunning && (
            <div className="ml-auto flex items-center gap-2 py-3 pr-1">
              <span className="text-xs text-gray-400">
                {state.currentStep ? STEP_LABELS[state.currentStep] : 'Procesando…'}
              </span>
            </div>
          )}
        </nav>

        {/* Contenido */}
        <div className="flex-1 overflow-hidden bg-gray-50">
          {state.status === 'idle' ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6 lg:p-12 gap-6">
              <QuimeraLoader size={100}/>
              <p className="text-gray-400 text-sm max-w-xs leading-relaxed">
                Escribe tu brief en el panel izquierdo y haz clic en{' '}
                <span className="font-semibold text-gray-600">Generar interfaz</span>
              </p>
            </div>
          ) : isRunning ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-6">
              <QuimeraLoader
                size={110}
                label={state.currentStep ? STEP_LABELS[state.currentStep] : 'Procesando…'}
              />
            </div>
          ) : hasError ? (
            <div className="flex items-center justify-center h-full p-6">
              <div className="bg-red-50 border border-red-100 rounded-xl p-5 max-w-sm">
                <p className="text-red-700 font-semibold mb-1.5 text-sm">Error al generar</p>
                <p className="text-red-600 text-xs leading-relaxed">{state.error}</p>
                <button
                  onClick={reset}
                  className="mt-4 px-4 py-1.5 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  Intentar nuevamente
                </button>
              </div>
            </div>
          ) : activeTab === 'preview' ? (
            <PreviewWindow htmlOutput={state.htmlOutput}/>
          ) : activeTab === 'design' ? (
            <DesignPreview designMarkdown={state.designMarkdown}/>
          ) : (
            <HtmlCodeView htmlOutput={state.htmlOutput}/>
          )}
        </div>
      </main>
    </div>
  );
}
