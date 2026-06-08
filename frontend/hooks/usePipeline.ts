'use client';

import { useState, useCallback, useRef } from 'react';
import type { PipelineState } from '@/types/pipeline';

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
};

/**
 * usePipeline - Hook para el pipeline (2 pasos)
 * Pipeline: analyze_and_design() → generate_code()
 * Retorna: DESIGN.md + HTML autocontenido
 */
export function usePipeline() {
  const [state, setState] = useState<PipelineState>(initialState);
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(async (brief: string, projectType?: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ ...initialState, status: 'running', currentStep: 'analyzing' });

    try {
      const startTime = Date.now();

      const response = await fetch(`${BACKEND_URL}/generar-diseno`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_brief: brief,
          project_type: projectType || undefined,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = await response.json();

      const elapsedMs = Date.now() - startTime;

      setState({
        status: 'completed',
        currentStep: 'completed',
        designMarkdown: data.design_markdown || '',
        htmlOutput: data.html_output || '',
        error: null,
        elapsedMs,
        projectId: data.project_id || null,
      });
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      
      setState(s => ({
        ...s,
        status: 'error',
        error: (err as Error).message,
        currentStep: null,
      }));
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(initialState);
  }, []);

  return { state, generate, reset };
}
