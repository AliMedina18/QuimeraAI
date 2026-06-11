'use client';

import { useState, useCallback, useEffect } from 'react';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';
export const SESSION_ID_KEY = 'quimera_session_id';

/** Genera o recupera el session_id del navegador */
export function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return '';
  let sid = localStorage.getItem(SESSION_ID_KEY);
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, sid);
  }
  return sid;
}

export interface LibraryDesign {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  has_markdown: boolean;
}

export interface FullDesign extends LibraryDesign {
  html_output: string;
  design_markdown: string;
  session_id: string;
}

export interface LibraryState {
  designs: LibraryDesign[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

export function useLibrary() {
  const [state, setState] = useState<LibraryState>({
    designs: [],
    isLoading: false,
    isSaving: false,
    error: null,
  });

  const sessionId = typeof window !== 'undefined' ? getOrCreateSessionId() : '';

  const fetchDesigns = useCallback(async () => {
    if (!sessionId) return;
    setState(s => ({ ...s, isLoading: true, error: null }));
    try {
      const res = await fetch(`${BACKEND_URL}/biblioteca?session_id=${encodeURIComponent(sessionId)}`);
      if (!res.ok) throw new Error('Error cargando biblioteca');
      const data = await res.json();
      setState(s => ({ ...s, designs: data.designs ?? [], isLoading: false }));
    } catch (e) {
      setState(s => ({ ...s, isLoading: false, error: (e as Error).message }));
    }
  }, [sessionId]);

  // Carga la lista al montar
  useEffect(() => {
    fetchDesigns();
  }, [fetchDesigns]);

  const saveDesign = useCallback(async (
    name: string,
    htmlOutput: string,
    designMarkdown: string,
    designId?: string,
  ): Promise<string | null> => {
    if (!sessionId) return null;
    setState(s => ({ ...s, isSaving: true, error: null }));
    try {
      const res = await fetch(`${BACKEND_URL}/biblioteca/guardar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          name,
          html_output: htmlOutput,
          design_markdown: designMarkdown,
          design_id: designId ?? null,
        }),
      });
      if (!res.ok) throw new Error('Error guardando diseño');
      const data = await res.json();
      await fetchDesigns();                   // refrescar lista
      setState(s => ({ ...s, isSaving: false }));
      return data.design_id as string;
    } catch (e) {
      setState(s => ({ ...s, isSaving: false, error: (e as Error).message }));
      return null;
    }
  }, [sessionId, fetchDesigns]);

  const deleteDesign = useCallback(async (designId: string): Promise<boolean> => {
    try {
      const res = await fetch(`${BACKEND_URL}/biblioteca/${encodeURIComponent(designId)}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Error eliminando diseño');
      setState(s => ({ ...s, designs: s.designs.filter(d => d.id !== designId) }));
      return true;
    } catch (e) {
      setState(s => ({ ...s, error: (e as Error).message }));
      return false;
    }
  }, []);

  const getDesign = useCallback(async (designId: string): Promise<FullDesign | null> => {
    try {
      const res = await fetch(`${BACKEND_URL}/biblioteca/${encodeURIComponent(designId)}`);
      if (!res.ok) return null;
      const data = await res.json();
      return data.design as FullDesign;
    } catch {
      return null;
    }
  }, []);

  return { state, sessionId, fetchDesigns, saveDesign, deleteDesign, getDesign };
}
