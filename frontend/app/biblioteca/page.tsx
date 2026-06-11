'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useLibrary, getOrCreateSessionId } from '@/hooks/useLibrary';
import { useUser } from '@/hooks/useUser';
import { STUDIO_STORAGE_KEY } from '@/hooks/useStudio';
import type { LibraryDesign } from '@/hooks/useLibrary';

// ─── Icons ────────────────────────────────────────────────────────────────────

const IconArrow = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>
  </svg>
);
const IconStudio = ({ size = 13 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M21 3H15M21 3V9M21 3L12 12"/>
    <path d="M19 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6"/>
  </svg>
);
const IconTrash = ({ size = 13 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M3 6h18M8 6V4h8v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
  </svg>
);
const IconRefresh = ({ size = 13 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/>
  </svg>
);
const IconEmpty = ({ size = 40 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M9 9h6M9 13h4"/>
  </svg>
);

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  if (!iso) return '—';
  try {
    return new Intl.DateTimeFormat('es-MX', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    }).format(new Date(iso));
  } catch {
    return iso.slice(0, 16).replace('T', ' ');
  }
}

// ─── Design card ──────────────────────────────────────────────────────────────

function DesignCard({
  design, onOpen, onDelete,
}: {
  design: LibraryDesign;
  onOpen: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div className="group flex flex-col bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden hover:border-indigo-500/30 hover:bg-white/[0.06] transition-all duration-150">

      {/* Preview area — placeholder */}
      <div
        className="h-32 bg-gradient-to-br from-indigo-500/10 to-violet-500/5 flex items-center justify-center border-b border-white/[0.06] shrink-0 cursor-pointer"
        onClick={() => onOpen(design.id)}
      >
        <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
          <IconStudio size={18}/>
        </div>
      </div>

      {/* Info */}
      <div className="flex flex-col gap-3 p-4 flex-1">
        <div>
          <p className="text-[13px] font-semibold text-white/80 truncate">{design.name}</p>
          <p className="text-[10px] text-white/25 mt-0.5">{formatDate(design.created_at)}</p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 mt-auto">
          <button
            onClick={() => onOpen(design.id)}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 text-[11px] font-semibold text-white rounded-lg transition-all"
            style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 2px 8px rgba(99,102,241,0.25)' }}
          >
            <IconStudio size={11}/>
            Abrir en Studio
          </button>

          {!confirmDelete ? (
            <button
              onClick={() => setConfirmDelete(true)}
              title="Eliminar"
              className="w-8 h-8 flex items-center justify-center text-white/25 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all border border-white/10 hover:border-red-500/20"
            >
              <IconTrash size={13}/>
            </button>
          ) : (
            <div className="flex gap-1">
              <button
                onClick={() => { onDelete(design.id); setConfirmDelete(false); }}
                className="px-2 py-1 text-[10px] font-semibold bg-red-500/20 text-red-400 border border-red-500/30 rounded-md transition-all hover:bg-red-500/30"
              >
                Sí
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                className="px-2 py-1 text-[10px] text-white/40 border border-white/10 rounded-md hover:bg-white/5"
              >
                No
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function BibliotecaPage() {
  const { state, fetchDesigns, deleteDesign, getDesign } = useLibrary();
  const { user } = useUser();
  const router = useRouter();
  const [openingId, setOpeningId] = useState<string | null>(null);
  const isGuest = !user || user.skippedRegistration;

  async function handleOpen(designId: string) {
    setOpeningId(designId);
    try {
      const full = await getDesign(designId);
      if (!full) return;
      localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
        htmlOutput:     full.html_output,
        designMarkdown: full.design_markdown,
        name:           full.name,
      }));
      router.push('/studio');
    } finally {
      setOpeningId(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#131315]"
      style={{
        backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
    >
      {/* Header */}
      <header className="sticky top-0 z-10 bg-[#1C1C1F]/90 backdrop-blur border-b border-white/[0.06]">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-1.5 text-white/35 hover:text-white/70 text-[12px] transition-colors"
            >
              <IconArrow size={12}/>
              Quimera AI
            </Link>
            <div className="h-3.5 w-px bg-white/10"/>
            <h1 className="text-[14px] font-semibold text-white/80">Mis diseños</h1>
            {state.designs.length > 0 && (
              <span className="text-[10px] bg-indigo-600 text-white rounded-full px-2 py-0.5 font-semibold">
                {state.designs.length}
              </span>
            )}
          </div>
          <button
            onClick={fetchDesigns}
            disabled={state.isLoading}
            title="Actualizar"
            className="p-1.5 text-white/30 hover:text-white/70 hover:bg-white/7 rounded-md transition-all disabled:opacity-30"
          >
            <IconRefresh size={14}/>
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-6 py-8">

        {/* Loading */}
        {state.isLoading && (
          <div className="flex items-center justify-center py-20 gap-3 text-white/30">
            <span className="w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full animate-spin"/>
            <span className="text-[13px]">Cargando diseños…</span>
          </div>
        )}

        {/* Invitado sin cuenta — CTA para registrarse */}
        {isGuest && !state.isLoading && (
          <div className="flex flex-col items-center gap-5 py-20 text-center">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div>
              <p className="text-[15px] font-semibold text-white/70">Crea una cuenta para guardar diseños</p>
              <p className="text-[13px] text-white/30 mt-1.5 max-w-xs leading-relaxed">
                Con tu cuenta puedes guardar y acceder a todos tus diseños desde cualquier sesión.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-center gap-2.5">
              <Link
                href="/welcome"
                className="flex items-center gap-2 px-5 py-2.5 text-[13px] font-semibold text-white rounded-xl transition-all"
                style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 2px 10px rgba(99,102,241,0.3)' }}
              >
                Crear cuenta gratis
              </Link>
              <Link
                href="/"
                className="px-5 py-2.5 text-[13px] text-white/40 hover:text-white/70 border border-white/10 hover:bg-white/5 rounded-xl transition-all"
              >
                Ir a generar diseño
              </Link>
            </div>
          </div>
        )}

        {/* Error — solo si está registrado (invitados ven el CTA de arriba) */}
        {!isGuest && state.error && !state.isLoading && (
          <div className="flex flex-col items-center gap-4 py-16 text-center">
            <div className="w-12 h-12 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center justify-center text-white/20">
              <IconEmpty size={24}/>
            </div>
            <div>
              <p className="text-[14px] font-semibold text-white/60">Sin diseños guardados aún</p>
              <p className="text-[12px] text-white/25 mt-1 max-w-xs leading-relaxed">
                Genera un diseño y guárdalo desde el Studio con el botón{' '}
                <span className="text-indigo-400 font-medium">Guardar en biblioteca</span>
              </p>
            </div>
            <Link
              href="/"
              className="flex items-center gap-2 px-5 py-2.5 text-[13px] font-semibold text-white rounded-xl transition-all"
              style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 2px 10px rgba(99,102,241,0.3)' }}
            >
              Generar mi primer diseño
            </Link>
          </div>
        )}

        {/* Empty — registrado sin diseños */}
        {!isGuest && !state.isLoading && !state.error && state.designs.length === 0 && (
          <div className="flex flex-col items-center gap-5 py-20 text-center">
            <div className="w-14 h-14 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center justify-center text-white/20">
              <IconEmpty size={28}/>
            </div>
            <div>
              <p className="text-[15px] font-semibold text-white/60">Sin diseños guardados</p>
              <p className="text-[13px] text-white/25 mt-1 max-w-sm leading-relaxed">
                Genera un diseño y usa el botón <span className="text-indigo-400 font-medium">Guardar en biblioteca</span> en el Studio
              </p>
            </div>
            <Link
              href="/"
              className="flex items-center gap-2 px-5 py-2.5 text-[13px] font-semibold text-white rounded-xl transition-all"
              style={{ background: 'linear-gradient(135deg,#4F46E5,#7C3AED)', boxShadow: '0 2px 10px rgba(99,102,241,0.3)' }}
            >
              Generar mi primer diseño
            </Link>
          </div>
        )}

        {/* Grid */}
        {!state.isLoading && state.designs.length > 0 && (
          <>
            {openingId && (
              <div className="flex items-center gap-2 mb-6 text-[12px] text-indigo-400/70">
                <span className="w-3 h-3 border-2 border-indigo-400/40 border-t-indigo-400 rounded-full animate-spin"/>
                Cargando diseño…
              </div>
            )}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {state.designs.map(design => (
                <DesignCard
                  key={design.id}
                  design={design}
                  onOpen={handleOpen}
                  onDelete={deleteDesign}
                />
              ))}
            </div>
          </>
        )}

      </main>
    </div>
  );
}
