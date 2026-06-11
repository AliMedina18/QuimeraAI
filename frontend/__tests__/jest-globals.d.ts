/**
 * Declaraciones globales de Jest + @testing-library para VS Code.
 * Cubre: describe/it/expect, jest.Mock, toBeInTheDocument y módulos de testing.
 * Archivo solo para __tests__/ — no afecta el build de producción.
 */

// ─── Tipos base de jest-dom (toBeInTheDocument, toBeDisabled, etc.) ───────────
import '@testing-library/jest-dom/jest-globals';

import type {
  describe as _describe,
  it as _it,
  test as _test,
  expect as _expect,
  beforeAll as _beforeAll,
  beforeEach as _beforeEach,
  afterAll as _afterAll,
  afterEach as _afterEach,
  jest as _jest,
} from '@jest/globals';

// ─── Globales de Jest ─────────────────────────────────────────────────────────

declare global {
  const describe: typeof _describe;
  const fdescribe: typeof _describe;
  const xdescribe: typeof _describe;
  const it: typeof _it;
  const fit: typeof _it;
  const xit: typeof _it;
  const test: typeof _test;
  const xtest: typeof _test;
  const expect: typeof _expect;
  const beforeAll: typeof _beforeAll;
  const beforeEach: typeof _beforeEach;
  const afterAll: typeof _afterAll;
  const afterEach: typeof _afterEach;
  const jest: typeof _jest;
}

// ─── Namespace jest (jest.Mock<T>, jest.Mocked<T>, etc.) ─────────────────────

/* eslint-disable @typescript-eslint/no-explicit-any */
declare namespace jest {
  type Mock<T extends (...args: any[]) => any = (...args: any[]) => any> = {
    (...args: Parameters<T>): ReturnType<T>;
    mockReturnValue(val: ReturnType<T>): jest.Mock<T>;
    mockReturnValueOnce(val: ReturnType<T>): jest.Mock<T>;
    mockResolvedValue(val: Awaited<ReturnType<T>>): jest.Mock<T>;
    mockResolvedValueOnce(val: Awaited<ReturnType<T>>): jest.Mock<T>;
    mockRejectedValueOnce(val: unknown): jest.Mock<T>;
    mockImplementation(fn: T): jest.Mock<T>;
    mockImplementationOnce(fn: T): jest.Mock<T>;
    mockReturnThis(): jest.Mock<T>;
    mockClear(): jest.Mock<T>;
    mockReset(): jest.Mock<T>;
    mockRestore(): void;
    mock: {
      calls: Array<Parameters<T>>;
      results: Array<{ type: 'return' | 'throw'; value: ReturnType<T> }>;
      instances: any[];
    };
  };
  type MockedFunction<T extends (...args: any[]) => any> = Mock<T>;
  type Mocked<T> = {
    [K in keyof T]: T[K] extends (...args: any[]) => any ? Mock<T[K]> : T[K];
  };
  type SpyInstance<T extends (...args: any[]) => any = (...args: any[]) => any> = Mock<T>;
}
/* eslint-enable @typescript-eslint/no-explicit-any */

// ─── Módulos de @testing-library ─────────────────────────────────────────────
// Declaraciones mínimas para que VS Code no marque "module not found"
// cuando los tipos reales vienen del paquete instalado en node_modules.

declare module '@testing-library/react' {
  import type React from 'react';
  export interface RenderResult {
    container: HTMLElement;
    baseElement: HTMLElement;
    rerender: (ui: React.ReactElement) => void;
    unmount: () => void;
  }
  export function render(ui: React.ReactElement, options?: object): RenderResult;
  export const screen: {
    getByRole: (role: string, options?: object) => HTMLElement;
    queryByRole: (role: string, options?: object) => HTMLElement | null;
    getAllByRole: (role: string, options?: object) => HTMLElement[];
    getByText: (text: string | RegExp, options?: object) => HTMLElement;
    queryByText: (text: string | RegExp, options?: object) => HTMLElement | null;
    getAllByText: (text: string | RegExp, options?: object) => HTMLElement[];
    getByTestId: (id: string) => HTMLElement;
    queryByTestId: (id: string) => HTMLElement | null;
    getByPlaceholderText: (text: string | RegExp) => HTMLElement;
    getByLabelText: (text: string | RegExp) => HTMLElement;
    getByDisplayValue: (value: string | RegExp) => HTMLElement;
    [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  export const fireEvent: {
    (element: HTMLElement | Document, event: Event): boolean;
    change: (el: Element, init?: object) => boolean;
    click: (el: Element, init?: object) => boolean;
    submit: (el: Element, init?: object) => boolean;
    keyDown: (el: Element, init?: object) => boolean;
    keyUp: (el: Element, init?: object) => boolean;
    focus: (el: Element) => boolean;
    blur: (el: Element) => boolean;
    [key: string]: any; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  export function act(fn: () => void | Promise<void>): Promise<void>;
  export function waitFor<T>(fn: () => T | Promise<T>, options?: object): Promise<T>;
  export function within(element: HTMLElement): typeof screen;
  export interface RenderHookResult<Result, Props> {
    result: { current: Result };
    rerender: (props?: Props) => void;
    unmount: () => void;
  }
  export function renderHook<Result, Props>(
    fn: (props: Props) => Result,
    options?: { initialProps?: Props }
  ): RenderHookResult<Result, Props>;
}

declare module '@testing-library/user-event' {
  const userEvent: {
    setup: (options?: object) => {
      click: (element: Element) => Promise<void>;
      type: (element: Element, text: string, options?: object) => Promise<void>;
      clear: (element: Element) => Promise<void>;
      keyboard: (text: string) => Promise<void>;
      tab: (options?: object) => Promise<void>;
      hover: (element: Element) => Promise<void>;
      unhover: (element: Element) => Promise<void>;
      selectOptions: (element: Element, values: string | string[]) => Promise<void>;
    };
    click: (element: Element) => Promise<void>;
    type: (element: Element, text: string) => Promise<void>;
  };
  export default userEvent;
}

export {};
