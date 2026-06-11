'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';
import QuimeraLoader from '@/components/QuimeraLoader';
import QuimeraIcon from '@/components/QuimeraIcon';

type Phase = 'intro' | 'moving' | 'settled';

export default function WelcomePage() {
  const { user, isLoaded, register, skipRegistration } = useUser();
  const router = useRouter();
  const [phase, setPhase]           = useState<Phase>('intro');
  const [name, setName]             = useState('');
  const [email, setEmail]           = useState('');
  const [nameErr, setNameErr]       = useState('');
  const [emailErr, setEmailErr]     = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isLoaded && user && !user.skippedRegistration) router.replace('/');
  }, [isLoaded, user, router]);

  // Timers arrancan solo cuando ya sabemos que el usuario debe ver esta página
  useEffect(() => {
    if (!isLoaded) return;
    if (user && !user.skippedRegistration) return;

    const t1 = setTimeout(() => setPhase('moving'),  1300);
    const t2 = setTimeout(() => setPhase('settled'), 2100);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [isLoaded]); // eslint-disable-line react-hooks/exhaustive-deps

  function validate() {
    let ok = true;
    if (!name.trim())                                   { setNameErr('Ingresa tu nombre'); ok = false; }
    else setNameErr('');
    if (!email.trim() || !email.includes('@') || !email.includes('.')) {
      setEmailErr('Ingresa un correo válido'); ok = false;
    } else setEmailErr('');
    return ok;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    await new Promise(r => setTimeout(r, 350));
    register(name.trim(), email.trim().toLowerCase());
    router.replace('/');
  }

  function handleSkip() {
    skipRegistration();
    router.replace('/');
  }

  // Mientras carga localStorage → pantalla en blanco momentánea (normal)
  if (!isLoaded) return null;
  // Si ya está registrado de verdad → redirige (el useEffect lo maneja)
  if (user && !user.skippedRegistration) return null;

  const isMoving  = phase === 'moving';
  const isSettled = phase === 'settled';

  return (
    <>
      <style>{`
        *, *::before, *::after { box-sizing: border-box; }

        .wlc-page {
          min-height: 100dvh;
          background: #0E0E11;
          position: relative;
          overflow: hidden;
        }

        /* ── Dot grid ───────────────────────────────── */
        .wlc-page::before {
          content: '';
          position: absolute;
          inset: 0;
          background-image: radial-gradient(circle, rgba(255,255,255,.03) 1px, transparent 1px);
          background-size: 24px 24px;
          pointer-events: none;
        }

        /* ── Glow ───────────────────────────────────── */
        .wlc-glow {
          position: absolute;
          top: -100px; left: 50%;
          transform: translateX(-50%);
          width: 600px; height: 460px;
          background: radial-gradient(ellipse, rgba(99,102,241,.14) 0%, transparent 65%);
          filter: blur(48px);
          pointer-events: none;
          transition: opacity .8s ease;
        }
        .wlc-glow.dim { opacity: .4; }

        /* ── Logo flotante (solo transform, GPU-acelerado) ── */
        .wlc-floating-logo {
          position: fixed;
          top: 0;
          left: 0;
          z-index: 100;
          transform-origin: top left;
          /* Centrado: logo de 130px → offset = -65px horizontal, -60px vertical */
          transform: translate(calc(50vw - 65px), calc(42vh - 60px)) scale(1);
          transition: transform .8s cubic-bezier(.16,1,.3,1),
                      opacity  .35s ease;
          will-change: transform, opacity;
        }
        .wlc-floating-logo.moving {
          transform: translate(20px, 20px) scale(0.24);
        }
        .wlc-floating-logo.settled {
          transform: translate(20px, 20px) scale(0.24);
          opacity: 0;
          pointer-events: none;
        }

        /* ── Header (aparece cuando el logo llega) ─── */
        .wlc-header {
          position: fixed;
          top: 0; left: 0; right: 0;
          z-index: 40;
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 16px 22px;
          opacity: 0;
          /* Delay: espera a que el logo termine de moverse */
          transition: opacity .5s ease .5s;
        }
        .wlc-header.visible { opacity: 1; }
        .wlc-header-name {
          font-size: 17px;
          font-weight: 800;
          color: #ffffff;
          letter-spacing: -.03em;
        }
        .wlc-header-name span { color: #818cf8; }

        /* ── Contenido principal (form) ─────────────── */
        .wlc-main {
          min-height: 100dvh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 100px 20px 48px;
          opacity: 0;
          transform: translateY(20px);
          transition: opacity .55s cubic-bezier(.16,1,.3,1), transform .55s cubic-bezier(.16,1,.3,1);
        }
        .wlc-main.visible {
          opacity: 1;
          transform: translateY(0);
        }

        /* ── Card con borde gradiente ────────────────── */
        .wlc-card {
          width: 100%;
          max-width: 400px;
          background: linear-gradient(#191920, #191920) padding-box,
                      linear-gradient(145deg, transparent 30%, #e81cff, #40c9ff) border-box;
          border: 2px solid transparent;
          border-radius: 18px;
          padding: 36px 28px;
          display: flex;
          flex-direction: column;
          gap: 0;
        }

        /* Card heading */
        .wlc-card-title {
          font-size: 20px;
          font-weight: 800;
          color: #ffffff;
          letter-spacing: -.03em;
          margin: 0 0 4px;
        }
        .wlc-card-sub {
          font-size: 13px;
          color: rgba(255,255,255,.35);
          margin: 0 0 28px;
          line-height: 1.5;
        }

        /* Grupos de campo */
        .wlc-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 16px;
        }
        .wlc-group label {
          font-size: 11px;
          font-weight: 700;
          color: #717171;
          text-transform: uppercase;
          letter-spacing: .07em;
        }
        .wlc-group input {
          width: 100%;
          padding: 11px 14px;
          border-radius: 9px;
          color: #fff;
          font-family: inherit;
          font-size: 14px;
          background: transparent;
          border: 1px solid #3a3a3a;
          outline: none;
          transition: border-color .15s, box-shadow .15s;
        }
        .wlc-group input::placeholder { color: rgba(255,255,255,.25); }
        .wlc-group input:focus {
          border-color: #e81cff;
          box-shadow: 0 0 0 3px rgba(232,28,255,.12);
        }
        .wlc-group input.err { border-color: rgba(239,68,68,.6); }
        .wlc-err-msg {
          font-size: 11px;
          color: #f87171;
          margin-top: -2px;
        }

        /* Botón principal */
        .wlc-btn {
          width: 100%;
          margin-top: 8px;
          padding: 13px 20px;
          border-radius: 10px;
          border: none;
          cursor: pointer;
          font-family: inherit;
          font-size: 14px;
          font-weight: 700;
          color: #fff;
          letter-spacing: -.01em;
          background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
          box-shadow: 0 4px 20px rgba(99,102,241,.4);
          transition: opacity .15s, transform .1s, box-shadow .15s;
        }
        .wlc-btn:hover:not(:disabled) {
          box-shadow: 0 6px 28px rgba(99,102,241,.55);
        }
        .wlc-btn:active:not(:disabled) { transform: scale(.97); }
        .wlc-btn:disabled { opacity: .4; cursor: not-allowed; }

        /* Skip */
        .wlc-skip-wrap {
          margin-top: 20px;
          text-align: center;
        }
        .wlc-skip {
          font-size: 12px;
          color: rgba(255,255,255,.22);
          background: none;
          border: none;
          cursor: pointer;
          font-family: inherit;
          transition: color .15s;
          padding: 4px 8px;
        }
        .wlc-skip:hover { color: rgba(255,255,255,.5); }

        /* Spinner */
        @keyframes spin { to { transform: rotate(360deg); } }
        .wlc-spin {
          display: inline-block;
          width: 14px; height: 14px;
          border: 2px solid rgba(255,255,255,.25);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin .7s linear infinite;
          vertical-align: middle;
          margin-right: 7px;
        }

        /* ── Responsive ─────────────────────────────── */
        @media (max-width: 480px) {
          .wlc-card { padding: 28px 20px; }
          .wlc-main { padding: 88px 16px 40px; }
          .wlc-header { padding: 14px 18px; }
        }
      `}</style>

      <div className="wlc-page">
        <div className={`wlc-glow${isSettled ? ' dim' : ''}`} />

        {/* ── Logo que se mueve centro → esquina ───── */}
        <div className={`wlc-floating-logo${isMoving ? ' moving' : ''}${isSettled ? ' settled' : ''}`}>
          <QuimeraLoader size={130} />
        </div>

        {/* ── Header fijo (aparece cuando llega el logo) */}
        <header className={`wlc-header${isSettled ? ' visible' : ''}`}>
          <QuimeraIcon size={30} />
          <span className="wlc-header-name">
            Quimera <span>AI</span>
          </span>
        </header>

        {/* ── Formulario ───────────────────────────── */}
        <main className={`wlc-main${isSettled ? ' visible' : ''}`}>
          <div className="wlc-card">

            <p className="wlc-card-title">Crea tu cuenta</p>
            <p className="wlc-card-sub">
              Guarda tus diseños y accede desde cualquier sesión
            </p>

            <form onSubmit={handleSubmit}>
              <div className="wlc-group">
                <label>Tu nombre</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => { setName(e.target.value); setNameErr(''); }}
                  placeholder="Ej: María García"
                  autoFocus
                  autoComplete="name"
                  className={nameErr ? 'err' : ''}
                />
                {nameErr && <span className="wlc-err-msg">{nameErr}</span>}
              </div>

              <div className="wlc-group">
                <label>Correo electrónico</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => { setEmail(e.target.value); setEmailErr(''); }}
                  placeholder="tu@correo.com"
                  autoComplete="email"
                  className={emailErr ? 'err' : ''}
                />
                {emailErr && <span className="wlc-err-msg">{emailErr}</span>}
              </div>

              <button type="submit" disabled={submitting} className="wlc-btn">
                {submitting
                  ? <><span className="wlc-spin" />Entrando…</>
                  : 'Comenzar con Quimera →'}
              </button>
            </form>

            <div className="wlc-skip-wrap">
              <button type="button" onClick={handleSkip} className="wlc-skip">
                Continuar sin registrarme
              </button>
            </div>

          </div>
        </main>
      </div>
    </>
  );
}
