'use client';

import { useState } from 'react';

interface Props {
  userName?: string;
  onRate: (stars: number, comment: string) => void;
  onDismiss: () => void;
}

const STAR_LABELS = ['', 'Decepcionante', 'Mejorable', 'Buena', 'Muy buena', '¡Excelente!'];

const STAR_EMOJIS = ['', '😞', '😐', '🙂', '😊', '🤩'];

export default function RatingModal({ userName, onRate, onDismiss }: Props) {
  const [hovered, setHovered] = useState(0);
  const [selected, setSelected] = useState(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const active = hovered || selected;

  async function handleSubmit() {
    if (!selected) return;
    setSubmitted(true);
    await new Promise(r => setTimeout(r, 1400));
    onRate(selected, comment.trim());
  }

  return (
    <>
      <style>{`
        @keyframes backdrop-in {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes card-in {
          from { opacity: 0; transform: scale(0.93) translateY(16px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
        @keyframes star-pop {
          0%   { transform: scale(1); }
          40%  { transform: scale(1.35); }
          100% { transform: scale(1); }
        }
        @keyframes success-bounce {
          0%   { transform: scale(0.5); opacity: 0; }
          60%  { transform: scale(1.15); opacity: 1; }
          100% { transform: scale(1); }
        }
        @keyframes success-text {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .backdrop { animation: backdrop-in 0.25s ease both; }
        .card     { animation: card-in 0.35s cubic-bezier(0.16,1,0.3,1) both; }
        .star-clicked { animation: star-pop 0.2s ease-out; }
        .success-icon { animation: success-bounce 0.5s cubic-bezier(0.16,1,0.3,1) both; }
        .success-text { animation: success-text 0.4s ease 0.15s both; }
        .success-sub  { animation: success-text 0.4s ease 0.3s both; }

        .star-btn {
          padding: 4px;
          transition: transform 0.12s ease;
          cursor: pointer;
          background: none;
          border: none;
          line-height: 0;
        }
        .star-btn:hover { transform: scale(1.15); }
        .star-btn:active { transform: scale(0.9); }

        .rating-input {
          width: 100%;
          border-radius: 12px;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.1);
          padding: 10px 14px;
          font-size: 13px;
          color: rgba(255,255,255,0.75);
          outline: none;
          resize: none;
          transition: border-color 0.15s, box-shadow 0.15s;
          font-family: inherit;
        }
        .rating-input::placeholder { color: rgba(255,255,255,0.2); }
        .rating-input:focus {
          border-color: rgba(99,102,241,0.5);
          box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
        }
      `}</style>

      {/* Backdrop */}
      <div
        className="backdrop fixed inset-0 z-50 flex items-center justify-center p-4"
        style={{ background: 'rgba(0,0,0,0.72)', backdropFilter: 'blur(8px)' }}
      >
        <div
          className="card w-full max-w-sm rounded-2xl overflow-hidden"
          style={{
            background: '#1C1C1F',
            border: '1px solid rgba(255,255,255,0.09)',
            boxShadow: '0 24px 64px rgba(0,0,0,0.6)',
          }}
        >
          {submitted ? (
            /* ── Estado de éxito ─────────────────────────────────── */
            <div className="flex flex-col items-center gap-3 py-12 px-6">
              <span className="success-icon text-6xl select-none">
                {STAR_EMOJIS[selected] || '🎉'}
              </span>
              <div className="text-center">
                <p className="success-text text-[16px] font-bold text-white/90">
                  ¡Gracias{userName && userName !== 'Invitado' ? `, ${userName}` : ''}!
                </p>
                <p className="success-sub text-[12px] text-white/35 mt-1 leading-relaxed">
                  Tu opinión ayuda a mejorar Quimera.<br/>
                  Ya puedes seguir diseñando.
                </p>
              </div>
            </div>
          ) : (
            /* ── Formulario de rating ────────────────────────────── */
            <>
              {/* Header con gradiente sutil */}
              <div
                className="px-6 pt-6 pb-5"
                style={{
                  background: 'linear-gradient(180deg, rgba(99,102,241,0.06) 0%, transparent 100%)',
                  borderBottom: '1px solid rgba(255,255,255,0.06)',
                }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-[15px] font-bold text-white/90 leading-snug">
                      ¿Cómo fue tu experiencia?
                    </p>
                    <p className="text-[12px] text-white/35 mt-0.5 leading-relaxed">
                      Tu primer diseño está listo — dinos qué te pareció
                    </p>
                  </div>
                  <button
                    onClick={onDismiss}
                    className="w-7 h-7 flex items-center justify-center rounded-lg text-white/25 hover:text-white/60 hover:bg-white/7 transition-all shrink-0 ml-3"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>

              <div className="px-6 py-5 flex flex-col gap-5">

                {/* Estrellas */}
                <div className="flex flex-col items-center gap-2.5">
                  <div className="flex items-center gap-0.5">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        type="button"
                        className="star-btn"
                        onMouseEnter={() => setHovered(star)}
                        onMouseLeave={() => setHovered(0)}
                        onClick={() => setSelected(star)}
                        aria-label={`${star} estrella${star > 1 ? 's' : ''}`}
                      >
                        <svg width="38" height="38" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                            fill={active >= star ? '#FBBF24' : 'rgba(255,255,255,0.08)'}
                            stroke={active >= star ? '#F59E0B' : 'rgba(255,255,255,0.12)'}
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            style={{ transition: 'fill 0.1s, stroke 0.1s' }}
                          />
                        </svg>
                      </button>
                    ))}
                  </div>

                  {/* Label de calificación */}
                  <div className="h-5 flex items-center">
                    {active > 0 && (
                      <p className="text-[12px] font-semibold text-amber-400">
                        {STAR_LABELS[active]}
                      </p>
                    )}
                  </div>
                </div>

                {/* Comentario */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-semibold text-white/28 uppercase tracking-[0.08em]">
                    Comentario <span className="text-white/18 font-normal normal-case tracking-normal">(opcional)</span>
                  </label>
                  <textarea
                    value={comment}
                    onChange={e => setComment(e.target.value)}
                    placeholder="¿Qué funcionó bien? ¿Qué mejorarías?"
                    rows={3}
                    className="rating-input"
                  />
                </div>

                {/* Botones */}
                <div className="flex gap-2">
                  <button
                    onClick={handleSubmit}
                    disabled={!selected}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 text-[13px] font-semibold text-white rounded-xl transition-all active:scale-[0.98] disabled:opacity-30 disabled:cursor-not-allowed"
                    style={{
                      background: selected ? 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)' : 'rgba(255,255,255,0.06)',
                      boxShadow: selected ? '0 2px 12px rgba(99,102,241,0.3)' : 'none',
                      transition: 'background 0.2s, box-shadow 0.2s',
                    }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 6L9 17l-5-5"/>
                    </svg>
                    Enviar valoración
                  </button>
                  <button
                    onClick={onDismiss}
                    className="px-3.5 py-2.5 text-[13px] text-white/35 hover:text-white/60 rounded-xl transition-all hover:bg-white/5"
                    style={{ border: '1px solid rgba(255,255,255,0.08)' }}
                  >
                    Ahora no
                  </button>
                </div>

              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
