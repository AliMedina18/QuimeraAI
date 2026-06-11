/**
 * types/pipeline.ts - Tipos para el pipeline (2 pasos)
 *
 * Pipeline: analyze_and_design() → generate_code()
 * Outputs: DESIGN.md + HTML autocontenido
 */

export type PipelineStatus = 'idle' | 'running' | 'completed' | 'error';
export type PipelineStep = 'analyzing' | 'generating' | 'completed' | null;

export interface PipelineState {
  status: PipelineStatus;
  currentStep: PipelineStep;
  designMarkdown: string;   // DESIGN.md output (paso 1)
  htmlOutput: string;        // HTML autocontenido output (paso 2)
  error: string | null;
  elapsedMs: number | null;
  projectId: string | null;
}

export interface PipelineResponse {
  design_markdown: string;
  html_output: string;
}

export interface GenerateRequest {
  design_brief: string;
  project_type?: string;
}

// ── Sugerencias de brief ──────────────────────────────────────────────────

export interface MissingElement {
  key: string;
  label: string;
  hint: string;
  chip_text: string;
}

export interface StyleSuggestion {
  id: string;
  label: string;
  emoji: string;
  description: string;
  chip_text: string;
}

export interface TemplateSuggestion {
  slug: string;
  label: string;
  mood: string;
  chip_text: string;
}

export interface ColorPalette {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  surface: string;
  text: string;
  chip_text: string;
}

export interface SuggestResponse {
  industry: string;
  confidence: number;
  missing: MissingElement[];
  styles: StyleSuggestion[];
  templates: TemplateSuggestion[];
  palettes: ColorPalette[];
}
estion[];
  palettes: ColorPalette[];
}
