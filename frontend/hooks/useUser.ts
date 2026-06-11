'use client';

import { useState, useEffect } from 'react';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface QuimeraUser {
  name: string;
  email: string;
  registeredAt: string;
  firstProjectCompleted: boolean;
  firstProjectRated: boolean;
  skippedRegistration?: boolean;
}

export const USER_KEY = 'quimera_user';

export function useUser() {
  const [user, setUser] = useState<QuimeraUser | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      if (raw) setUser(JSON.parse(raw));
    } catch { /* ignore */ }
    setIsLoaded(true);
  }, []);

  function save(u: QuimeraUser) {
    try {
      localStorage.setItem(USER_KEY, JSON.stringify(u));
    } catch { /* ignore */ }
    setUser(u);
  }

  function register(name: string, email: string) {
    save({
      name,
      email,
      registeredAt: new Date().toISOString(),
      firstProjectCompleted: false,
      firstProjectRated: false,
    });

    // Fire-and-forget: enviar email de bienvenida vía backend
    // No bloqueamos el flujo si el backend tarda o falla
    fetch(`${BACKEND_URL}/usuarios/registrar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email }),
    }).catch(err => {
      console.warn('[useUser] Welcome email no enviado:', err);
    });
  }

  function skipRegistration() {
    save({
      name: 'Invitado',
      email: '',
      registeredAt: new Date().toISOString(),
      firstProjectCompleted: false,
      firstProjectRated: false,
      skippedRegistration: true,
    });
  }

  function markFirstProjectCompleted() {
    if (!user || user.firstProjectCompleted) return;
    save({ ...user, firstProjectCompleted: true });
  }

  function markFirstProjectRated() {
    if (!user) return;
    save({ ...user, firstProjectRated: true });
  }

  function logout() {
    try { localStorage.removeItem(USER_KEY); } catch { /* ignore */ }
    setUser(null);
  }

  return {
    user,
    isLoaded,
    register,
    skipRegistration,
    logout,
    markFirstProjectCompleted,
    markFirstProjectRated,
  };
}
