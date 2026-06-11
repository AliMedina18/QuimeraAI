'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import type { SelectedElement } from '@/types/pipeline';
import { replaceColorInHtml, applyColorToElement } from '@/utils/colorUtils';

export const STUDIO_STORAGE_KEY = 'quimera_studio_design';

export interface StoredDesign {
  htmlOutput: string;
  designMarkdown: string;
  name: string;
  history?: HistoryEntry[];
}

export interface HistoryEntry {
  html: string;
  label: string;
  savedAt: number;
}

export interface StudioState {
  htmlOutput: string;
  designMarkdown: string;
  name: string;
  selectedElement: SelectedElement | null;
  history: HistoryEntry[];
  isLoaded: boolean;
  isEditingAI: boolean;
  aiError: string | null;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const MAX_UNDO = 50;

export function useStudio() {
  const [state, setState] = useState<StudioState>({
    htmlOutput: '',
    designMarkdown: '',
    name: 'Diseno sin titulo',
    selectedElement: null,
    history: [],
    isLoaded: false,
    isEditingAI: false,
    aiError: null,
  });

  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const undoStack = useRef<string[]>([]);
  const redoStack = useRef<string[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  // Cargar desde localStorage al montar
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STUDIO_STORAGE_KEY);
      if (raw) {
        const data: StoredDesign = JSON.parse(raw);
        setState(s => ({
          ...s,
          htmlOutput: data.htmlOutput || '',
          designMarkdown: data.designMarkdown || '',
          name: data.name || 'Diseno sin titulo',
          history: data.history || [],
          isLoaded: true,
        }));
      } else {
        setState(s => ({ ...s, isLoaded: true }));
      }
    } catch {
      setState(s => ({ ...s, isLoaded: true }));
    }
  }, []);

  // Persistir en localStorage cuando cambia el HTML
  useEffect(() => {
    if (!state.isLoaded || !state.htmlOutput) return;
    try {
      localStorage.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
        htmlOutput: state.htmlOutput,
        designMarkdown: state.designMarkdown,
        name: state.name,
        history: state.history,
      } as StoredDesign));
    } catch { /* ignore quota errors */ }
  }, [state.htmlOutput, state.designMarkdown, state.name, state.isLoaded, state.history]);

  // Agregar al stack de undo y actualizar flags
  const pushUndo = useCallback((html: string) => {
    undoStack.current.push(html);
    if (undoStack.current.length > MAX_UNDO) undoStack.current.shift();
    redoStack.current = [];
    setCanUndo(true);
    setCanRedo(false);
  }, []);

  const undo = useCallback(() => {
    const prev = undoStack.current.pop();
    if (!prev) return;
    setState(s => {
      redoStack.current.push(s.htmlOutput);
      return { ...s, htmlOutput: prev, selectedElement: null };
    });
    setCanUndo(undoStack.current.length > 0);
    setCanRedo(true);
  }, []);

  const redo = useCallback(() => {
    const next = redoStack.current.pop();
    if (!next) return;
    setState(s => {
      undoStack.current.push(s.htmlOutput);
      return { ...s, htmlOutput: next, selectedElement: null };
    });
    setCanUndo(true);
    setCanRedo(redoStack.current.length > 0);
  }, []);

  const setSelectedElement = useCallback((el: SelectedElement | null) => {
    setState(s => ({ ...s, selectedElement: el }));
  }, []);

  // Reemplaza el outerHTML de un elemento en el HTML completo (texto editado o resize)
  const updateElementHtml = useCallback((oldHtml: string, newHtml: string) => {
    setState(s => {
      pushUndo(s.htmlOutput);
      return {
        ...s,
        htmlOutput: s.htmlOutput.split(oldHtml).join(newHtml),
        selectedElement: null,
      };
    });
  }, [pushUndo]);

  // Aplica color de texto o fondo al elemento seleccionado
  const applyElementColor = useCallback((property: 'color' | 'background-color', newColor: string) => {
    setState(s => {
      if (!s.selectedElement || !s.htmlOutput) return s;
      pushUndo(s.htmlOutput);
      const { html, newOuterHtml } = applyColorToElement(
        s.htmlOutput, s.selectedElement.outerHTML, property, newColor
      );
      return { ...s, htmlOutput: html, selectedElement: { ...s.selectedElement, outerHTML: newOuterHtml } };
    });
  }, [pushUndo]);

  // Reemplaza un color globalmente en todo el HTML
  const replaceGlobalColor = useCallback((oldColor: string, newColor: string) => {
    setState(s => {
      pushUndo(s.htmlOutput);
      return { ...s, htmlOutput: replaceColorInHtml(s.htmlOutput, oldColor, newColor) };
    });
  }, [pushUndo]);

  // Guarda una version con nombre
  const saveVersion = useCallback((label?: string) => {
    setState(s => {
      const ts = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
      const entry: HistoryEntry = {
        html: s.htmlOutput,
        label: label ?? ('Version ' + ts),
        savedAt: Date.now(),
      };
      return { ...s, history: [entry, ...s.history] };
    });
  }, []);

  // Restaura una version guardada
  const loadVersion = useCallback((entry: HistoryEntry) => {
    setState(s => {
      pushUndo(s.htmlOutput);
      return { ...s, htmlOutput: entry.html, selectedElement: null };
    });
  }, [pushUndo]);

  // Edicion por IA — params explícitos para evitar closures obsoletas
  const editWithAI = useCallback(async (
    instruccion: string,
    htmlOutput: string,
    designMarkdown: string,
    selectedElement: SelectedElement | null,
  ) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState(s => ({ ...s, isEditingAI: true, aiError: null }));

    try {
      const response = await fetch(BACKEND_URL + '/editar-diseno', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          html_actual: htmlOutput,
          instruccion,
          elemento_contexto: selectedElement?.outerHTML ?? undefined,
          design_markdown: designMarkdown || undefined,
        }),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error('Error del servidor: ' + response.status);
      const data = await response.json();
      setState(s => {
        pushUndo(s.htmlOutput);
        return {
          ...s,
          htmlOutput: data.html_output || s.htmlOutput,
          selectedElement: null,
          isEditingAI: false,
          aiError: null,
        };
      });
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      setState(s => ({ ...s, isEditingAI: false, aiError: (err as Error).message }));
    }
  }, [pushUndo]);

  const setName = useCallback((name: string) => {
    setState(s => ({ ...s, name }));
  }, []);

  return {
    state,
    canUndo,
    canRedo,
    undo,
    redo,
    setSelectedElement,
    updateElementHtml,
    applyElementColor,
    replaceGlobalColor,
    saveVersion,
    loadVersion,
    editWithAI,
    setName,
  };
}
