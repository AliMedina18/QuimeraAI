'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { usePipeline } from '@/hooks/usePipeline';
import { STUDIO_STORAGE_KEY } from '@/hooks/useStudio';
import { useUser } from '@/hooks/useUser';
import ChatUI from '@/components/ChatUI';
import HtmlCodeView from '@/components/ReactPreview';
import PreviewWindow from '@/components/PreviewWindow';
import QuimeraLoader from '@/components/QuimeraLoader';
import QuimeraIcon from '@/components/QuimeraIcon';
import RatingModal from '@/components/RatingModal';
import { IconGlobe, IconCode, IconX } from '@/components/Icons';

type Tab = 'preview' | 'code';

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'preview', label: 'Vista previa', icon: <IconGlobe size={13}/> },
  { id: 'code',    label: 'HTML',         icon: <IconCode  size={13}/> },
];

const STEP_LABELS: Record<string, string> = {
  analyzing:  'Analizando brief...',
  generating: 'Generando código...',
  editing:    'Aplicando cambio...',
};

const EXAMPLE_BRIEFS = [
  {
    label: 'Agencia creativa',
    icon: '✦',
    brief: 'Agencia de diseño y branding. Portfolio de proyectos con grid visual, página de servicios, hero animado, formulario de contacto. Estilo moderno minimalista, blanco y negro con acento naranja.',
  },
  {
    label: 'Restaurante premium',
    icon: '◆',
    brief: 'Restaurante de sushi premium en Ciudad de México. Hero con foto de ambiente, menú con categorías y precios, sección de reservas, testimonios. Colores: negro, rojo, dorado.',
  },
  {
    label: 'SaaS de productividad',
    icon: '▲',
    brief: 'Landing page para app SaaS de gestión de tareas. Hero con demo animado, pricing en 3 planes (Free, Pro, Enterprise), testimonios de clientes, FAQ, CTA final. Azul y violeta.',
  },
  {
    label: 'E-commerce urbano',
    icon: '●',
    brief: 'Tienda online de ropa urbana y streetwear. Hero de temporada, grid de productos con filtros, sección "Más vendidos", newsletter. Estilo bold, tipografía grande, fondo negro.',
  },
];

function IconStudio({ size = 13 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M21 3H15M21 3V9M21 3L12 12"/>
      <path d="M19 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6"/>
    </svg>
  );
}

function IconCheck({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M20 6L9 17l-5-5"/>
    </svg>
  );
}

function StepBadge({ label, active }: { label: string; active: boolean }) {
  return (
    <div className={[
      'flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-medium transition-all',
      active
        ? 'bg-indigo-600 text-white'
        : 'bg-white/8 text-white/25',
    ].join(' ')}>
      {active && <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-pulse"/>}
      {label}
    </div>
  );
}

export default function Home() {
  const { state, generate, reset } = usePipeline();
  const { user, isLoaded: userLoaded, logout, markFirstProjectCompleted, markFirstProjectRated } = useUser();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>('preview');
  const lastBriefRef = useRef('');
  const [externalBrief, setExternalBrief] = useState<string | null>(null);
  const [showRating, setShowRating] = useState(false);

  // Redirigir a /welcome si no hay usuario registrado
  useEffect(() => {
    if (userLoaded && !user) router.replace('/welcome');
  }, [userLoaded, user, router]);

  const isRunning   = state.status === 'running';
  const isCompleted = state.status === 'completed' && !!state.htmlOutput;

  // Marcar + mostrar rating cuando el primer proyecto termina
  useEffect(() => {
    if (!isCompleted || !user || user.firstProjectRated) return;
    if (!user.firstProjectCompleted) {
      markFirstProjectCompleted();
    }
    const t = setTimeout(() => setShowRating(true), 2000);
    return () => clearTimeout(t);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isCompleted]);

  const handleGenerate = useCallback((brief: string) => {
    lastBriefRef.current = brief;
    setExternalBrief(null);
    generate(brief);
  }, [generate]);

  function handleExampleClick(brief: string) {
    setExternalBrief(brief);
  }

  function handleOpenStudio() {
    try {
      localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
        htmlOutput:     state.htmlOutput,
        designMarkdown: state.designMarkdown,
        name:           (lastBriefRef.current.slice(0, 40).trim()) || 'Diseño generado',
      }));
    } catch { /* ignore */ }
    // Marcar primer proyecto completado para trigger del rating
    markFirstProjectCompleted();
    router.push('/studio');
  }

  function handleRatingSubmit(stars: number, comment: string) {
    markFirstProjectRated();
    setShowRating(false);
    // En el futuro: enviar al backend
    console.info('Rating:', stars, comment);
  }

  function handleRatingDismiss() {
    markFirstProjectRated(); // No volver a mostrar
    setShowRating(false);
  }

  // Evitar flash blanco mientras carga el estado de usuario (todos los hooks ya corrieron)
  if (!userLoaded) return null;

  return (
    <div className="flex flex-col lg:flex-row h-screen overflow-hidden bg-[#131315]">

      {/* ── Left sidebar ────────────────────────────────────────────── */}
      <aside className="flex flex-col bg-[#1C1C1F] border-r border-white/[0.06] w-full order-2 lg:order-1 lg:w-[340px] xl:w-[380px] shrink-0">

        {/* Header */}
        <header className="flex items-center justify-between px-5 py-3.5 border-b border-white/[0.06] shrink-0">
          <div className="flex items-center gap-2.5">
            <QuimeraIcon size={24}/>
            <div>
              <h1 className="text-[14px] font-bold text-white/90 leading-none tracking-tight"
                  style={{ letterSpacing: '-0.02em' }}>
                Quimera <span className="text-indigo-400">AI</span>
              </h1>
              {user && !user.skippedRegistration ? (
                <p className="text-[9px] text-white/30 mt-0.5 leading-none">
                  Hola, <span className="text-indigo-400/70">{user.name.split(' ')[0]}</span>
                </p>
              ) : (
                <p className="text-[9px] text-white/25 mt-0.5 leading-none tracking-wide uppercase">
                  Powered by Gemini 2.5
                </p>
              )}

            </div>
          </div>
          <div className="flex items-center gap-1">
            {/* Invitado: botón para registrarse */}
            {user?.skippedRegistration && (
              <a
                href="/welcome"
                className="flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 px-2 py-1.5 rounded-lg transition-all border border-indigo-500/20"
              >
                Crear cuenta
              </a>
            )}
            <a
              href="/biblioteca"
              title="Mis diseños"
              className="flex items-center gap-1 text-[11px] text-white/25 hover:text-indigo-400 hover:bg-white/5 px-2 py-1.5 rounded-lg transition-all"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
              <span className="hidden sm:inline">Biblioteca</span>
            </a>
            {state.status !== 'idle' && (
              <button
                onClick={reset}
                title="Nueva solicitud"
                className="flex items-center gap-1.5 text-[11px] text-white/30 hover:text-white/70 hover:bg-white/7 px-2 py-1.5 rounded-lg transition-all"
              >
                <IconX size={12}/> Nuevo
              </button>
            )}
            {/* Cerrar sesión — solo usuarios registrados */}
            {user && !user.skippedRegistration && (
              <button
                onClick={() => { logout(); router.replace('/welcome'); }}
                title="Cerrar sesión"
                className="flex items-center justify-center w-7 h-7 text-white/20 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </button>
            )}
          </div>
        </header>

        {/* Chat form */}
        <div className="flex-1 overflow-y-auto thin-scroll">
          <ChatUI
            state={state}
            onGenerate={handleGenerate}
            externalBrief={externalBrief}
          />
        </div>

        {/* Studio CTA */}
        {isCompleted && !isRunning && (
          <div className="px-4 py-3 border-t border-white/[0.06] shrink-0">
            <button
              onClick={handleOpenStudio}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-[13px] font-semibold text-white transition-all duration-150 active:scale-[0.98] hover:brightness-110"
              style={{ background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)', boxShadow: '0 2px 12px rgba(99,102,241,0.3)' }}
            >
              <IconStudio size={13}/>
              Abrir en Studio
            </button>
            <p className="text-[10px] text-white/25 text-center mt-1.5">
              Editor visual · IA · Colores · Redimensionado
            </p>
          </div>
        )}
      </aside>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden order-1 lg:order-2 min-w-0">

        {/* Tab bar */}
        <nav className="flex items-center bg-[#1C1C1F] border-b border-white/[0.06] px-4 shrink-0 h-11 gap-1">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={!isCompleted}
              className={[
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all duration-150',
                activeTab === tab.id && isCompleted
                  ? 'bg-white/10 text-white/90'
                  : 'text-white/30 hover:text-white/60 hover:bg-white/5',
                !isCompleted ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer',
              ].join(' ')}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}

          {isRunning && (
            <div className="ml-auto flex items-center gap-1.5">
              {(['analyzing', 'generating'] as const).map(step => (
                <StepBadge
                  key={step}
                  label={step === 'analyzing' ? 'Analizando' : 'Generando'}
                  active={state.currentStep === step}
                />
              ))}
            </div>
          )}

          {isCompleted && !isRunning && (
            <div className="ml-auto flex items-center gap-1.5 text-emerald-400">
              <IconCheck size={13}/>
              <span className="text-[11px] font-medium">
                {state.elapsedMs ? (state.elapsedMs / 1000).toFixed(1) + 's' : 'Listo'}
              </span>
            </div>
          )}
        </nav>

        {/* Content area */}
        <div className="flex-1 overflow-hidden bg-[#131315]">

          {/* Idle: empty state */}
          {state.status === 'idle' && (
            <div
              className="flex flex-col items-center justify-center h-full gap-8 p-8"
              style={{
                backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)',
                backgroundSize: '20px 20px',
              }}
            >
              <div className="flex flex-col items-center gap-4">
                <QuimeraLoader size={80}/>
                <div className="text-center">
                  <p className="text-[17px] font-bold text-white/90 tracking-tight"
                     style={{ letterSpacing: '-0.02em' }}>
                    ¿Qué quieres construir hoy?
                  </p>
                  <p className="text-[13px] text-white/35 mt-1">
                    Describe tu interfaz y Quimera genera el sitio completo
                  </p>
                </div>
              </div>

              {/* Example brief cards */}
              <div className="grid grid-cols-2 gap-2.5 w-full max-w-lg">
                {EXAMPLE_BRIEFS.map(ex => (
                  <button
                    key={ex.label}
                    onClick={() => handleExampleClick(ex.brief)}
                    className="group text-left p-3.5 bg-white/[0.04] rounded-2xl border border-white/10 hover:border-indigo-500/40 hover:bg-white/[0.07] transition-all duration-150 active:scale-[0.98]"
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-[14px] text-indigo-400 font-bold leading-none">{ex.icon}</span>
                      <span className="text-[12px] font-semibold text-white/60 group-hover:text-indigo-300 transition-colors">{ex.label}</span>
                    </div>
                    <p className="text-[10px] text-white/25 leading-relaxed line-clamp-2">
                      {ex.brief.slice(0, 70)}…
                    </p>
                  </button>
                ))}
              </div>

              <div className="flex flex-wrap items-center justify-center gap-2 mt-2">
                {['HTML completo', 'Sistema de diseño', 'WCAG accesible', 'Editable en Studio'].map(f => (
                  <span key={f} className="px-2.5 py-1 bg-white/[0.04] border border-white/10 rounded-full text-[10px] text-white/30 font-medium">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Running: progress */}
          {isRunning && (
            <div
              className="flex flex-col items-center justify-center h-full gap-8"
              style={{
                backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)',
                backgroundSize: '20px 20px',
              }}
            >
              <QuimeraLoader size={100} label={state.currentStep ? STEP_LABELS[state.currentStep] : 'Procesando...'}/>
              <div className="flex items-center gap-3">
                {[
                  { key: 'analyzing', label: 'Analizando' },
                  { key: 'generating', label: 'Generando' },
                ].map((s, i) => {
                  const steps = ['analyzing', 'generating'];
                  const currentIdx = steps.indexOf(state.currentStep ?? '');
                  const stepIdx = i;
                  const isDone   = currentIdx > stepIdx;
                  const isActive = currentIdx === stepIdx;
                  return (
                    <div key={s.key} className="flex items-center gap-3">
                      <div className={[
                        'flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-medium transition-all',
                        isActive ? 'bg-indigo-600 text-white' : isDone ? 'bg-emerald-500/20 text-emerald-400' : 'bg-white/8 text-white/25',
                      ].join(' ')}>
                        {isActive && <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-pulse"/>}
                        {isDone && <IconCheck size={11}/>}
                        {s.label}
                      </div>
                      {i < 1 && <div className="w-6 h-px bg-white/10"/>}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Completed */}
          {isCompleted && !isRunning && (
            <div className="h-full overflow-hidden">
              {activeTab === 'preview'
                ? <PreviewWindow htmlOutput={state.htmlOutput} studioMode={false}/>
                : <HtmlCodeView htmlOutput={state.htmlOutput}/>
              }
            </div>
          )}

          {/* Error */}
          {state.status === 'error' && (
            <div className="flex flex-col items-center justify-center h-full gap-4 p-8">
              <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                <span className="text-red-400 text-xl">!</span>
              </div>
              <div className="text-center">
                <p className="text-[14px] font-semibold text-white/70">Error al generar</p>
                <p className="text-[12px] text-red-400/70 mt-1 max-w-sm leading-relaxed">{state.error}</p>
              </div>
              <button
                onClick={reset}
                className="px-4 py-2 bg-white/8 hover:bg-white/12 text-white/60 text-[12px] font-medium rounded-lg transition-all border border-white/10"
              >
                Intentar de nuevo
              </button>
            </div>
          )}
        </div>
      </main>

      {/* ── Rating modal ───────────────────────────────────────────── */}
      {showRating && (
        <RatingModal
          userName={user?.name}
          onRate={handleRatingSubmit}
          onDismiss={handleRatingDismiss}
        />
      )}
    </div>
  );
}
