import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ColorPicker from '@/components/ColorPicker';

describe('ColorPicker', () => {
  it('renderiza sin label', () => {
    const onChange = jest.fn();
    render(<ColorPicker value="#ff0000" onChange={onChange} />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveValue('#ff0000');
  });

  it('renderiza con label', () => {
    render(<ColorPicker value="#ff0000" onChange={jest.fn()} label="Texto" />);
    expect(screen.getByText('Texto')).toBeInTheDocument();
  });

  it('muestra el valor hex actual en el input de texto', () => {
    render(<ColorPicker value="#aabbcc" onChange={jest.fn()} />);
    expect(screen.getByRole('textbox')).toHaveValue('#aabbcc');
  });

  it('llama onChange al escribir un hex valido de 7 caracteres', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<ColorPicker value="#000000" onChange={onChange} />);
    const input = screen.getByRole('textbox');
    await user.clear(input);
    await user.type(input, '#ff5500');
    expect(onChange).toHaveBeenCalledWith('#ff5500');
  });

  it('NO llama onChange si el hex es invalido (menos de 7 chars)', async () => {
    const onChange = jest.fn();
    const user = userEvent.setup();
    render(<ColorPicker value="#000000" onChange={onChange} />);
    const input = screen.getByRole('textbox');
    await user.clear(input);
    await user.type(input, '#abc');
    // #abc tiene 4 chars, no debe llamar onChange
    expect(onChange).not.toHaveBeenCalledWith('#abc');
  });

  it('actualiza el input cuando cambia el prop value', () => {
    const { rerender } = render(<ColorPicker value="#ff0000" onChange={jest.fn()} />);
    expect(screen.getByRole('textbox')).toHaveValue('#ff0000');
    rerender(<ColorPicker value="#00ff00" onChange={jest.fn()} />);
    expect(screen.getByRole('textbox')).toHaveValue('#00ff00');
  });

  it('el native color input tiene el valor correcto', () => {
    render(<ColorPicker value="#123456" onChange={jest.fn()} />);
    // El input type=color es sr-only pero existe en el DOM
    const colorInput = document.querySelector('input[type="color"]') as HTMLInputElement;
    expect(colorInput).toBeTruthy();
    expect(colorInput.value).toBe('#123456');
  });

  it('llama onChange al cambiar el input nativo de color', () => {
    const onChange = jest.fn();
    render(<ColorPicker value="#000000" onChange={onChange} />);
    const colorInput = document.querySelector('input[type="color"]') as HTMLInputElement;
    fireEvent.change(colorInput, { target: { value: '#abcdef' } });
    expect(onChange).toHaveBeenCalledWith('#abcdef');
  });

  it('no crashea con valor vacio', () => {
    expect(() => {
      render(<ColorPicker value="" onChange={jest.fn()} />);
    }).not.toThrow();
  });
});
