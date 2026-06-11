import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatUI from '@/components/ChatUI';
import type { PipelineState } from '@/types/pipeline';

// Mock de subcomponentes pesados para aislar ChatUI
jest.mock('@/components/BriefSuggestions', () => ({
  __esModule: true,
  default: () => <div data-testid="brief-suggestions" />,
}));
jest.mock('@/components/Icons', () => ({
  IconSend: () => <span>Send</span>,
  IconCheck: () => <span>Check</span>,
  IconAlertCircle: () => <span>Alert</span>,
}));

// Estado base válido — usa strings vacíos donde el tipo no admite null
const idleState: PipelineState = {
  status: 'idle',
  currentStep: null,
  htmlOutput: '',
  designMarkdown: '',
  error: null,
  elapsedMs: null,
  projectId: null,
  studioMode: false,
  selectedElement: null,
  savedDesigns: [],
};

const runningState: PipelineState = {
  ...idleState,
  status: 'running',
  currentStep: 'analyzing',
};

const completedState: PipelineState = {
  ...idleState,
  status: 'completed',
  htmlOutput: '<html><body>Sitio generado</body></html>',
  designMarkdown: '# Diseño',
  elapsedMs: 2345,
};

const errorState: PipelineState = {
  ...idleState,
  status: 'error',
  error: 'Timeout de Gemini',
};

// ─── Render básico ────────────────────────────────────────────────────────────

describe('ChatUI — render básico', () => {
  it('muestra el textarea y el botón en estado idle', () => {
    render(<ChatUI state={idleState} onGenerate={jest.fn()} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /generar interfaz/i })).toBeInTheDocument();
  });

  it('botón deshabilitado con brief vacío', () => {
    render(<ChatUI state={idleState} onGenerate={jest.fn()} />);
    expect(screen.getByRole('button', { name: /generar interfaz/i })).toBeDisabled();
  });

  it('botón habilitado con brief > 10 caracteres', () => {
    render(<ChatUI state={idleState} onGenerate={jest.fn()} />);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'Agencia de diseño premium' },
    });
    expect(screen.getByRole('button', { name: /generar interfaz/i })).not.toBeDisabled();
  });

  it('muestra el contador de caracteres', () => {
    render(<ChatUI state={idleState} onGenerate={jest.fn()} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Hola mundo test' } });
    expect(screen.getByText('15')).toBeInTheDocument();
  });
});

// ─── Envío ────────────────────────────────────────────────────────────────────

describe('ChatUI — envío del formulario', () => {
  it('llama onGenerate con el brief al hacer submit', () => {
    const onGenerate = jest.fn();
    render(<ChatUI state={idleState} onGenerate={onGenerate} />);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'Restaurante de sushi premium con hero animado' },
    });
    fireEvent.submit(screen.getByRole('textbox').closest('form')!);
    expect(onGenerate).toHaveBeenCalledWith('Restaurante de sushi premium con hero animado');
  });

  it('no llama onGenerate con brief corto (≤10 chars)', () => {
    const onGenerate = jest.fn();
    render(<ChatUI state={idleState} onGenerate={onGenerate} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Corto' } });
    fireEvent.submit(screen.getByRole('textbox').closest('form')!);
    expect(onGenerate).not.toHaveBeenCalled();
  });
});

// ─── externalBrief (prompts de ejemplo) ──────────────────────────────────────

describe('ChatUI — externalBrief', () => {
  it('prefill el textarea cuando externalBrief pasa de null a string', () => {
    const { rerender } = render(
      <ChatUI state={idleState} onGenerate={jest.fn()} externalBrief={null} />
    );
    const ta = screen.getByRole('textbox') as HTMLTextAreaElement;
    expect(ta.value).toBe('');

    rerender(
      <ChatUI
        state={idleState}
        onGenerate={jest.fn()}
        externalBrief="Agencia de diseño minimalista con portfolio"
      />
    );
    expect(ta.value).toBe('Agencia de diseño minimalista con portfolio');
  });

  it('textarea vacío cuando externalBrief es null', () => {
    render(<ChatUI state={idleState} onGenerate={jest.fn()} externalBrief={null} />);
    const ta = screen.getByRole('textbox') as HTMLTextAreaElement;
    expect(ta.value).toBe('');
  });

  it('puede enviar un brief prefillado desde ejemplo', () => {
    const onGenerate = jest.fn();
    render(
      <ChatUI
        state={idleState}
        onGenerate={onGenerate}
        externalBrief="Tienda de ropa urbana y streetwear premium"
      />
    );
    fireEvent.submit(screen.getByRole('textbox').closest('form')!);
    expect(onGenerate).toHaveBeenCalledWith('Tienda de ropa urbana y streetwear premium');
  });
});

// ─── Estado running ───────────────────────────────────────────────────────────

describe('ChatUI — estado running', () => {
  it('textarea deshabilitado mientras genera', () => {
    render(<ChatUI state={runningState} onGenerate={jest.fn()} />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('muestra "Generando" en el botón', () => {
    render(<ChatUI state={runningState} onGenerate={jest.fn()} />);
    expect(screen.getByText(/generando/i)).toBeInTheDocument();
  });

  it('muestra el label del paso "Analizando brief"', () => {
    render(<ChatUI state={runningState} onGenerate={jest.fn()} />);
    expect(screen.getByText(/analizando brief/i)).toBeInTheDocument();
  });
});

// ─── Estado error ─────────────────────────────────────────────────────────────

describe('ChatUI — estado error', () => {
  it('muestra el mensaje de error', () => {
    render(<ChatUI state={errorState} onGenerate={jest.fn()} />);
    expect(screen.getByText('Timeout de Gemini')).toBeInTheDocument();
  });
});

// ─── Estado completed ─────────────────────────────────────────────────────────

describe('ChatUI — estado completed', () => {
  it('muestra badge de éxito', () => {
    render(<ChatUI state={completedState} onGenerate={jest.fn()} />);
    expect(screen.getByText(/diseño generado/i)).toBeInTheDocument();
  });

  it('muestra el tiempo transcurrido formateado', () => {
    render(<ChatUI state={completedState} onGenerate={jest.fn()} />);
    expect(screen.getByText(/2\.3s/)).toBeInTheDocument();
  });
});
