'use client';

import { useState, useCallback, useRef } from 'react';
import type { PipelineState, SSEEvent, AestheticScores } from '@/types/pipeline';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const initialState: PipelineState = {
  status: 'idle',
  currentStep: null,
  currentIteration: 0,
  events: [],
  scores: null,
  scoresHistory: [],
  designProposal: null,
  reactComponent: '',
  designTokensCss: '',
  rationaleDocument: '',
  projectId: null,
  overallScore: null,
  error: null,
  elapsedMs: null,
  critiquePreview: '',
};

export function usePipeline() {
  const [state, setState] = useState<PipelineState>(initialState);
  const abortRef = useRef<AbortController | null>(null);

  const generate = useCallback(async (brief: string, projectType: string) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({ ...initialState, status: 'running' });

    // Aplicar un evento SSE al estado — definida aqui para capturar setState estable
    function applyEvent(event: SSEEvent) {
      setState(s => {
        const next = { ...s, events: [...s.events, event] };

        if (event.error) {
          return { ...next, status: 'error', error: event.error };
        }

        switch (event.paso) {
          case 'inicio':
            next.currentStep = 'inicio';
            if (event.project_id) next.projectId = event.project_id;
            break;

          case 'analisis':
            next.currentStep = 'analisis';
            if (event.iteration) next.currentIteration = event.iteration;
            if (event.status === 'completado' && event.primary_color) {
              next.designProposal = {
                primary_color:      event.primary_color ?? '',
                secondary_color:    event.secondary_color ?? '',
                accent_color:       event.accent_color ?? '',
                heading_font:       event.heading_font ?? '',
                body_font:          '',
                layout_type:        event.layout_type ?? '',
                color_harmony_type: event.color_harmony_type ?? '',
              };
            }
            break;

          case 'evaluacion':
            next.currentStep = 'evaluacion';
            if (event.overall_score !== undefined) {
              next.overallScore = event.overall_score;
            }
            if (event.aesthetic_scores) {
              next.scores = event.aesthetic_scores as AestheticScores;
              next.scoresHistory = [
                ...s.scoresHistory,
                event.aesthetic_scores as AestheticScores,
              ];
            }
            break;

          case 'correccion':
            next.currentStep = 'correccion';
            next.critiquePreview = event.critique_preview ?? '';
            break;

          case 'generacion':
            next.currentStep = 'generacion';
            break;

          case 'guardando':
            next.currentStep = 'guardando';
            break;

          case 'completado':
            next.currentStep = 'completado';
            next.status = 'completed';
            next.projectId         = event.project_id ?? null;
            next.elapsedMs         = event.elapsed_ms ?? null;
            next.overallScore      = event.overall_score ?? null;
            next.reactComponent    = event.react_component ?? '';
            next.designTokensCss   = event.design_tokens_css ?? '';
            next.rationaleDocument = event.rationale_document ?? '';
            if (event.design_proposal) next.designProposal = event.design_proposal;
            break;
        }

        return next;
      });
    }

    try {
      const response = await fetch(`${BACKEND_URL}/generar-diseno`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          design_brief: brief,
          project_type: projectType || undefined,
        }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const event: SSEEvent = JSON.parse(line.slice(6));
            applyEvent(event);
          } catch {
            // linea malformada — ignorar
          }
        }
      }

      // Si el stream cerró sin evento 'completado' (timeout, error no capturado),
      // pasar a 'completed' para que la UI no quede congelada en 'running'
      setState(s =>
        s.status === 'running' ? { ...s, status: 'completed' } : s
      );
    } catch (err: unknown) {
      if ((err as Error).name === 'AbortError') return;
      setState(s => ({
        ...s,
        status: 'error',
        error: (err as Error).message,
      }));
    }
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(initialState);
  }, []);

  return { state, generate, reset };
}
