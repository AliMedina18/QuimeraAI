/**
 * Tests para useStudio — hook de estado del Studio Mode.
 * No llama a la red; fetch y localStorage estan mockeados.
 */
import { renderHook, act } from '@testing-library/react';
import { useStudio, STUDIO_STORAGE_KEY } from '@/hooks/useStudio';

// ─── Mock de localStorage ─────────────────────────────────────────────────────

const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();

Object.defineProperty(global, 'localStorage', { value: localStorageMock });

// ─── Mock de fetch ────────────────────────────────────────────────────────────

global.fetch = jest.fn();

function mockFetchOk(body: object) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => body,
  });
}

// ─── Setup / teardown ─────────────────────────────────────────────────────────

beforeEach(() => {
  localStorageMock.clear();
  jest.clearAllMocks();
});

// ─── Carga desde localStorage ─────────────────────────────────────────────────

describe('carga desde localStorage', () => {
  it('carga htmlOutput guardado', async () => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
      htmlOutput: '<html><body>Hola</body></html>',
      designMarkdown: '# Diseño',
      name: 'Mi diseno',
    }));
    const { result } = renderHook(() => useStudio());
    // Esperar a que isLoaded sea true
    await act(async () => {});
    expect(result.current.state.htmlOutput).toBe('<html><body>Hola</body></html>');
    expect(result.current.state.name).toBe('Mi diseno');
    expect(result.current.state.isLoaded).toBe(true);
  });

  it('isLoaded=true aunque localStorage este vacio', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    expect(result.current.state.isLoaded).toBe(true);
    expect(result.current.state.htmlOutput).toBe('');
  });

  it('maneja localStorage corrupto sin crash', async () => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, 'NOT_VALID_JSON{{{');
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    expect(result.current.state.isLoaded).toBe(true);
    expect(result.current.state.htmlOutput).toBe('');
  });
});

// ─── setName ──────────────────────────────────────────────────────────────────

describe('setName', () => {
  it('actualiza el nombre del diseño', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.setName('Nuevo nombre'); });
    expect(result.current.state.name).toBe('Nuevo nombre');
  });
});

// ─── updateElementHtml ────────────────────────────────────────────────────────

describe('updateElementHtml', () => {
  beforeEach(() => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
      htmlOutput: '<body><p id="titulo">Hola</p><p>Mundo</p></body>',
      designMarkdown: '',
      name: 'Test',
    }));
  });

  it('reemplaza el outerHTML del elemento en el HTML completo', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    const oldHtml = '<p id="titulo">Hola</p>';
    const newHtml = '<p id="titulo">Adios</p>';
    act(() => { result.current.updateElementHtml(oldHtml, newHtml); });
    expect(result.current.state.htmlOutput).toContain('<p id="titulo">Adios</p>');
    expect(result.current.state.htmlOutput).not.toContain('<p id="titulo">Hola</p>');
  });

  it('limpia selectedElement tras el update', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => {
      result.current.setSelectedElement({ tag: 'p', id: 'titulo', classes: '', text: 'Hola', outerHTML: '<p id="titulo">Hola</p>' });
    });
    expect(result.current.state.selectedElement).not.toBeNull();
    act(() => { result.current.updateElementHtml('<p id="titulo">Hola</p>', '<p id="titulo">Adios</p>'); });
    expect(result.current.state.selectedElement).toBeNull();
  });

  it('agrega el estado previo al undo stack', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    const originalHtml = result.current.state.htmlOutput;
    act(() => { result.current.updateElementHtml('<p id="titulo">Hola</p>', '<p id="titulo">Adios</p>'); });
    expect(result.current.canUndo).toBe(true);
    act(() => { result.current.undo(); });
    expect(result.current.state.htmlOutput).toBe(originalHtml);
  });
});

// ─── Undo / Redo ──────────────────────────────────────────────────────────────

describe('undo y redo', () => {
  beforeEach(() => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
      htmlOutput: '<p>Version 1</p>',
      designMarkdown: '',
      name: 'Test',
    }));
  });

  it('canUndo empieza en false', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    expect(result.current.canUndo).toBe(false);
  });

  it('canRedo empieza en false', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    expect(result.current.canRedo).toBe(false);
  });

  it('undo restaura el HTML previo', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.updateElementHtml('<p>Version 1</p>', '<p>Version 2</p>'); });
    expect(result.current.state.htmlOutput).toBe('<p>Version 2</p>');
    act(() => { result.current.undo(); });
    expect(result.current.state.htmlOutput).toBe('<p>Version 1</p>');
  });

  it('redo recupera el HTML deshecho', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.updateElementHtml('<p>Version 1</p>', '<p>Version 2</p>'); });
    act(() => { result.current.undo(); });
    expect(result.current.canRedo).toBe(true);
    act(() => { result.current.redo(); });
    expect(result.current.state.htmlOutput).toBe('<p>Version 2</p>');
  });

  it('nueva edicion limpia el stack de redo', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.updateElementHtml('<p>Version 1</p>', '<p>Version 2</p>'); });
    act(() => { result.current.undo(); });
    expect(result.current.canRedo).toBe(true);
    act(() => { result.current.updateElementHtml('<p>Version 1</p>', '<p>Version 3</p>'); });
    expect(result.current.canRedo).toBe(false);
  });

  it('undo no hace nada si el stack esta vacio', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    const html = result.current.state.htmlOutput;
    act(() => { result.current.undo(); });
    expect(result.current.state.htmlOutput).toBe(html);
  });
});

// ─── saveVersion / loadVersion ────────────────────────────────────────────────

describe('saveVersion y loadVersion', () => {
  beforeEach(() => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
      htmlOutput: '<p>HTML inicial</p>',
      designMarkdown: '',
      name: 'Test',
    }));
  });

  it('guarda una version con label por defecto', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.saveVersion(); });
    expect(result.current.state.history).toHaveLength(1);
    expect(result.current.state.history[0].html).toBe('<p>HTML inicial</p>');
    expect(result.current.state.history[0].label).toMatch(/Version/);
  });

  it('guarda una version con label personalizado', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.saveVersion('Antes del cambio grande'); });
    expect(result.current.state.history[0].label).toBe('Antes del cambio grande');
  });

  it('las versiones se apilan en orden inverso (mas reciente primero)', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.saveVersion('Primera'); });
    act(() => { result.current.updateElementHtml('<p>HTML inicial</p>', '<p>Modificado</p>'); });
    act(() => { result.current.saveVersion('Segunda'); });
    expect(result.current.state.history[0].label).toBe('Segunda');
    expect(result.current.state.history[1].label).toBe('Primera');
  });

  it('loadVersion restaura el HTML de esa version', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.saveVersion('Snapshot'); });
    act(() => { result.current.updateElementHtml('<p>HTML inicial</p>', '<p>Nuevo HTML</p>'); });
    expect(result.current.state.htmlOutput).toBe('<p>Nuevo HTML</p>');
    act(() => { result.current.loadVersion(result.current.state.history[0]); });
    expect(result.current.state.htmlOutput).toBe('<p>HTML inicial</p>');
  });
});

// ─── setSelectedElement ───────────────────────────────────────────────────────

describe('setSelectedElement', () => {
  it('actualiza el elemento seleccionado', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    const el = { tag: 'h1', id: '', classes: 'titulo', text: 'Bienvenidos', outerHTML: '<h1>Bienvenidos</h1>' };
    act(() => { result.current.setSelectedElement(el); });
    expect(result.current.state.selectedElement).toEqual(el);
  });

  it('acepta null para limpiar la seleccion', async () => {
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => { result.current.setSelectedElement({ tag: 'p', id: '', classes: '', text: '', outerHTML: '<p></p>' }); });
    act(() => { result.current.setSelectedElement(null); });
    expect(result.current.state.selectedElement).toBeNull();
  });
});

// ─── editWithAI ───────────────────────────────────────────────────────────────

describe('editWithAI', () => {
  beforeEach(() => {
    localStorageMock.setItem(STUDIO_STORAGE_KEY, JSON.stringify({
      htmlOutput: '<p>Original</p>',
      designMarkdown: '# Design',
      name: 'Test',
    }));
  });

  it('actualiza htmlOutput con la respuesta del servidor', async () => {
    mockFetchOk({ html_output: '<p>Editado por IA</p>' });
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    await act(async () => {
      await result.current.editWithAI('cambia el color', '<p>Original</p>', '# Design', null);
    });
    expect(result.current.state.htmlOutput).toBe('<p>Editado por IA</p>');
    expect(result.current.state.isEditingAI).toBe(false);
    expect(result.current.state.aiError).toBeNull();
  });

  it('pone isEditingAI en true durante la llamada', async () => {
    let resolve: (v: unknown) => void;
    (global.fetch as jest.Mock).mockReturnValueOnce(new Promise(r => { resolve = r; }));
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    act(() => {
      result.current.editWithAI('instruccion', '<p>Original</p>', '', null);
    });
    expect(result.current.state.isEditingAI).toBe(true);
    // Resolver la promesa para limpiar
    await act(async () => {
      resolve!({ ok: true, json: async () => ({ html_output: '<p>X</p>' }) });
    });
  });

  it('maneja error del servidor', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({ ok: false, status: 503 });
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    await act(async () => {
      await result.current.editWithAI('instruccion', '<p>Original</p>', '', null);
    });
    expect(result.current.state.isEditingAI).toBe(false);
    expect(result.current.state.aiError).toContain('503');
    expect(result.current.state.htmlOutput).toBe('<p>Original</p>'); // sin cambios
  });

  it('agrega htmlOutput al undo stack tras edicion exitosa', async () => {
    mockFetchOk({ html_output: '<p>Editado</p>' });
    const { result } = renderHook(() => useStudio());
    await act(async () => {});
    await act(async () => {
      await result.current.editWithAI('instruccion', '<p>Original</p>', '', null);
    });
    expect(result.current.canUndo).toBe(true);
  });
});
