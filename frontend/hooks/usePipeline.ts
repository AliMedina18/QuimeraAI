'use client';

import { useState, useCallback, useRef } from 'react';
import type { PipelineState, SavedDesign, SelectedElement } from '@/types/pipeline';
import { replaceColorInHtml, applyColorToElement } from '@/utils/colorUtils';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const initialState: PipelineState = {
  status: 'idle',
  currentStep: null,
  designMarkdown: '',
  htmlOutput: '',
  error: null,
  elapsedMs: null,
  projectId: null,
  studioMode: false,
  savedDesigns: [],
  selectedElement: null,
};

export function usePipeline() {
  const [state, setState] = useState<PipelineState>(initialState);
  const abortRef = useRef<AbortController | null>(null);

  // -- Generacion desde cero --------------------------------------------------

  const generate = useCallback(async (brief: string, projectType?: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState(s => ({
      ...s,
      status: 'running',
      currentStep: 'analyzing',
      designMarkdown: '',
      htmlOutput: '',
      error: null,
      elapsedMs: null,
      projectId: null,
      studioMode: false,
      selectedElement: null,
    }));

    try {
      const startTime = Date.now();
      const response = await fetch(`${BACKEND_URL}/generar-diseno`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_brief: brief, project_type: projectType || undefined }),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
      const data = await response.json();
      setState(s => ({
        ...s,
        status: 'completed',
        currentStep: 'completed',
        designMarkdown: data.design_markdown || '',
        htmlOutput: data.html_output || '',
        error: null,
        elapsedMs: Date.now() - startTime,
        projectId: data.project_id || null,
      }));
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      setState(s => ({ ...s, status: 'error', error: (err as Error).message, currentStep: null }));
    }
  }, []);

  // -- Studio Mode: edicion por IA --------------------------------------------

  const editDesign = useCallback(async (instruccion: string) => {
    if (!state.htmlOutput) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const currentHtml = state.htmlOutput;
    const currentMarkdown = state.designMarkdown;
    const currentElement = state.selectedElement;

    setState(s => ({ ...s, status: 'running', currentStep: 'editing', error: null }));

    try {
      const startTime = Date.now();
      const response = await fetch(`${BACKEND_URL}/editar-diseno`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          html_actual: currentHtml,
          instruccion,
          elemento_contexto: currentElement?.outerHTML ?? undefined,
          design_markdown: currentMarkdown || undefined,
        }),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
      const data = await response.json();
      setState(s => ({
        ...s,
        status: 'completed',
        currentStep: 'completed',
        htmlOutput: data.html_output || currentHtml,
        elapsedMs: Date.now() - startTime,
        error: null,
        selectedElement: null,
      }));
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      setState(s => ({ ...s, status: 'error', error: (err as Error).message, currentStep: null }));
    }
  }, [state.htmlOutput, state.designMarkdown, state.selectedElement]);

  // -- Studio Mode: edicion manual de colores ---------------------------------

  const applyElementColor = useCallback((property: 'color' | 'background-color', newColor: string) => {
    setState(s => {
      if (!s.selectedElement || !s.htmlOutput) return s;
      const { html, newOuterHtml } = applyColorToElement(
        s.htmlOutput,
        s.selectedElement.outerHTML,
        property,
        newColor
      );
      return {
        ...s,
        htmlOutput: html,
        selectedElement: { ...s.selectedElement, outerHTML: newOuterHtml },
      };
    });
  }, []);

  const replaceGlobalColor = useCallback((oldColor: string, newColor: string) => {
    setState(s => ({
      ...s,
      htmlOutput: replaceColorInHtml(s.htmlOutput, oldColor, newColor),
    }));
  }, []);

  // -- Studio Mode: edicion de texto inline -----------------------------------

  const updateElementHtml = useCallback((oldOuterHtml: string, newOuterHtml: string) => {
    setState(s => ({
      ...s,
      htmlOutput: s.htmlOutput.split(oldOuterHtml).join(newOuterHtml),
      selectedElement: null,
    }));
  }, []);

  // -- Guardar / Restaurar versiones -----------------------------------------

  const saveDesign = useCallback((briefHint?: string) => {
    setState(s => {
      if (!s.htmlOutput) return s;
      const ts = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
      const name = briefHint ? briefHint.slice(0, 40).trim() : ('Diseno ' + ts);
      const saved: SavedDesign = {
        id: Date.now().toString(),
        name,
        htmlOutput: s.htmlOutput,
        designMarkdown: s.designMarkdown,
        savedAt: Date.now(),
      };
      return { ...s, savedDesigns: [saved, ...s.savedDesigns], studioMode: true };
    });
  }, []);

  const saveVersion = useCallback((name?: string) => {
    setState(s => {
      if (!s.htmlOutput) return s;
      const ts = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
      const saved: SavedDesign = {
        id: Date.now().toString(),
        name: name ?? ('Version ' + ts),
        htmlOutput: s.htmlOutput,
        designMarkdown: s.designMarkdown,
        savedAt: Date.now(),
      };
      return { ...s, savedDesigns: [saved, ...s.savedDesigns] };
    });
  }, []);

  const loadSavedDesign = useCallback((id: string) => {
    setState(s => {
      const design = s.savedDesigns.find(d => d.id === id);
      if (!design) return s;
      return {
        ...s,
        status: 'completed',
        currentStep: 'completed',
        htmlOutput: design.htmlOutput,
        designMarkdown: design.designMarkdown,
        error: null,
        selectedElement: null,
      };
    });
  }, []);

  // -- Seleccion de elemento --------------------------------------------------

  const setSelectedElement = useCallback((element: SelectedElement | null) => {
    setState(s => ({ ...s, selectedElement: element }));
  }, []);

  // -- Modo estudio -----------------------------------------------------------

  const enterStudioMode = useCallback(() => {
    setState(s => ({ ...s, studioMode: true }));
  }, []);

  const exitStudioMode = useCallback(() => {
    setState(s => ({ ...s, studioMode: false, selectedElement: null }));
  }, []);

  // -- Reset -----------------------------------------------------------------

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(s => ({ ...initialState, savedDesigns: s.savedDesigns }));
  }, []);

  return {
    state,
    generate,
    editDesign,
    applyElementColor,
    replaceGlobalColor,
    updateElementHtml,
    saveDesign,
    saveVersion,
    loadSavedDesign,
    setSelectedElement,
    enterStudioMode,
    exitStudioMode,
    reset,
  };
}
