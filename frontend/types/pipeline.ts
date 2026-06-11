export type PipelineStatus = 'idle' | 'running' | 'completed' | 'error';
export type PipelineStep = 'analyzing' | 'generating' | 'editing' | 'completed' | null;

export interface SavedDesign {
  id: string;
  name: string;
  htmlOutput: string;
  designMarkdown: string;
  savedAt: number;
}

export interface SelectedElement {
  tag: string;
  id: string;
  classes: string;
  text: string;
  outerHTML: string;
}

export interface PipelineState {
  status: PipelineStatus;
  currentStep: PipelineStep;
  designMarkdown: string;
  htmlOutput: string;
  error: string | null;
  elapsedMs: number | null;
  projectId: string | null;
  studioMode: boolean;
  savedDesigns: SavedDesign[];
  selectedElement: SelectedElement | null;
}

export interface PipelineResponse {
  design_markdown: string;
  html_output: string;
}

export interface GenerateRequest {
  design_brief: string;
  project_type?: string;
}

export interface EditRequest {
  html_actual: string;
  instruccion: string;
  elemento_contexto?: string;
  design_markdown?: string;
}

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
