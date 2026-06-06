'use client';

import { useState } from 'react';
import { usePipeline } from '@/hooks/usePipeline';
import ChatUI from '@/components/ChatUI';
import Scorecard from '@/components/Scorecard';
import Preview from '@/components/Preview';
import CodeView from '@/components/CodeView';
import RationaleView from '@/components/RationaleView';

type Tab = 'preview' | 'scorecard' | 'codigo' | 'rationale';

export default function Home() {
  const { state, generate, reset } = usePipeline();
  const [activeTab, setActiveTab] = useState<Tab>('preview');

  const tabs: { id: Tab; label: string; disabled: boolean }[] = [
    { id: 'preview',   label: '🖥 Preview',   disabled: !state.reactComponent },
    { id: 'scorecard', label: '📊 Scorecard',  disabled: !state.scores },
    { id: 'codigo',    label: '{ } Código',    disabled: !state.reactComponent },
    { id: 'rationale', label: '📝 Rationale',  disabled: !state.rationaleDocument },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* ── Panel izquierdo 40% ── */}
      <aside className="w-[40%] min-w-[320px] flex flex-col border-r border-gray-200 bg-white shadow-sm">
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
            >
              Nueva solicitud
            </button>
          )}
        </header>

        {/* Chat UI */}
        <div className="flex-1 overflow-y-auto thin-scroll">
          <ChatUI state={state} onGenerate={generate} />
        </div>
      </aside>

      {/* ── Panel derecho 60% ── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Tabs */}
        <nav className="flex border-b border-gray-200 bg-white px-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => !tab.disabled && setActiveTab(tab.id)}
              disabled={tab.disabled}
              className={`
                px-4 py-3 text-sm font-medium border-b-2 transition-colors
                ${activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
                }
                ${tab.disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {tab.label}
            </button>
          ))}

          {/* Score badge visible en todas las tabs */}
          {state.overallScore !== null && (
            <div className="ml-auto flex items-center gap-2 py-3">
              <span className="text-xs text-gray-400">Score global</span>
              <span
                className={`text-sm font-bold px-2 py-0.5 rounded-full ${
                  state.overallScore >= 85
                    ? 'bg-green-100 text-green-700'
                    : state.overallScore >= 70
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {state.overallScore.toFixed(1)}
              </span>
            </div>
          )}
        </nav>

        {/* Contenido del tab activo */}
        <div className="flex-1 overflow-y-auto thin-scroll bg-gray-50">
          {state.status === 'idle' ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-12">
              <div className="text-6xl mb-4">✦</div>
              <p className="text-gray-400 text-lg">
                Escribe tu brief y pulsa{' '}
                <span className="font-semibold text-gray-600">Generar interfaz</span>
              </p>
              <p className="text-gray-300 text-sm mt-2">
                El agente evaluará tu diseño con 8 criterios estéticos antes de generar el código.
              </p>
            </div>
          ) : (
            <>
              {activeTab === 'preview' && (
                <Preview
                  reactComponent={state.reactComponent}
                  designTokensCss={state.designTokensCss}
                />
              )}
              {activeTab === 'scorecard' && (
                <Scorecard
                  scores={state.scores}
                  scoresHistory={state.scoresHistory}
                />
              )}
              {activeTab === 'codigo' && (
                <CodeView
                  reactComponent={state.reactComponent}
                  designTokensCss={state.designTokensCss}
                />
              )}
              {activeTab === 'rationale' && (
                <RationaleView markdown={state.rationaleDocument} />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
