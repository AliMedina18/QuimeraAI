// Tipos para los eventos SSE del backend Quimera

export type PipelineStatus = 'idle' | 'running' | 'completed' | 'error';

export type PipelineStep =
  | 'inicio'
  | 'analisis'
  | 'evaluacion'
  | 'correccion'
  | 'generacion'
  | 'guardando'
  | 'completado';

export interface AestheticScores {
  color_harmony: number;
  wcag_contrast: number;
  composition_balance: number;
  visual_hierarchy: number;
  gestalt_compliance: number;
  whitespace_quality: number;
  brand_consistency: number;
  accessibility: number;
  overall_score: number;
  passed: boolean;
  iteration: number;
}

export interface DesignProposal {
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  heading_font: string;
  body_font: string;
  layout_type: string;
  color_harmony_type: string;
}

export interface SSEEvent {
  paso: string;
  status?: string;
  project_id?: string;
  iteration?: number;
  // analisis completado
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  heading_font?: string;
  layout_type?: string;
  color_harmony_type?: string;
  // evaluacion
  overall_score?: number;
  approved?: boolean;
  aesthetic_scores?: AestheticScores;
  // correccion
  critique_preview?: string;
  // generacion
  component_size?: number;
  tokens_size?: number;
  // completado
  elapsed_ms?: number;
  iterations?: number;
  design_proposal?: DesignProposal;
  react_component?: string;
  design_tokens_css?: string;
  rationale_document?: string;
  component_url?: string;
  tokens_url?: string;
  rationale_url?: string;
  // error
  error?: string;
}

export interface PipelineState {
  status: PipelineStatus;
  currentStep: PipelineStep | null;
  currentIteration: number;
  events: SSEEvent[];
  scores: AestheticScores | null;
  scoresHistory: AestheticScores[];
  designProposal: DesignProposal | null;
  reactComponent: string;
  designTokensCss: string;
  rationaleDocument: string;
  projectId: string | null;
  overallScore: number | null;
  error: string | null;
  elapsedMs: number | null;
  critiquePreview: string;
}

// Nombres amigables de los criterios en español
export const CRITERIA_LABELS: Record<string, string> = {
  color_harmony:       'Armonía de Color',
  wcag_contrast:       'Contraste WCAG',
  composition_balance: 'Balance Compositivo',
  visual_hierarchy:    'Jerarquía Visual',
  gestalt_compliance:  'Principios Gestalt',
  whitespace_quality:  'Uso del Espacio',
  brand_consistency:   'Consistencia de Marca',
  accessibility:       'Accesibilidad',
};

export const CRITERIA_DESCRIPTIONS: Record<string, string> = {
  color_harmony:       'Los colores forman una armonía visual reconocible: complementaria, análoga o triádica.',
  wcag_contrast:       'El contraste entre texto y fondo cumple el estándar de accesibilidad WCAG 2.1 (4.5:1).',
  composition_balance: 'Los elementos visuales están distribuidos de forma equilibrada en la pantalla.',
  visual_hierarchy:    'Existe una jerarquía clara que guía la mirada del usuario de lo más a lo menos importante.',
  gestalt_compliance:  'El diseño aplica principios Gestalt: proximidad, similitud y continuidad perceptual.',
  whitespace_quality:  'El espacio en blanco está bien utilizado para dar respiro y claridad al contenido.',
  brand_consistency:   'Colores, tipografía y tono son coherentes con la identidad de marca declarada.',
  accessibility:       'El diseño es accesible: tamaños, contraste y estructura apropiados para todos los usuarios.',
};
