import {
  extractColorsFromHtml,
  replaceColorInHtml,
  applyColorToElement,
  getContrastColor,
} from '@/utils/colorUtils';

// ─── extractColorsFromHtml ────────────────────────────────────────────────────

describe('extractColorsFromHtml', () => {
  it('extrae colores hex de 6 digitos', () => {
    const html = '<div style="color: #ff0000; background: #00ff00;">texto</div>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toContain('#ff0000');
    expect(colors).toContain('#00ff00');
  });

  it('normaliza colores hex de 3 digitos a 6', () => {
    const html = '<div style="color: #f00;">texto</div>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toContain('#ff0000');
  });

  it('elimina duplicados y preserva orden de aparicion', () => {
    const html = '<p style="color:#aabbcc">a</p><p style="color:#aabbcc">b</p><p style="color:#112233">c</p>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toEqual(['#aabbcc', '#112233']);
  });

  it('retorna array vacio si no hay colores hex', () => {
    const html = '<div style="color: red; background: blue;">texto</div>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toHaveLength(0);
  });

  it('maneja HTML vacio', () => {
    expect(extractColorsFromHtml('')).toEqual([]);
  });

  it('no confunde numeros de 6 digitos que no son colores', () => {
    const html = '<p>El id es 123456 y el color es #abcdef</p>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toContain('#abcdef');
    expect(colors).not.toContain('#123456'); // sin # no debe extraerse
  });

  it('normaliza a minusculas', () => {
    const html = '<div style="color: #FFAABB">x</div>';
    const colors = extractColorsFromHtml(html);
    expect(colors).toContain('#ffaabb');
    expect(colors).not.toContain('#FFAABB');
  });
});

// ─── replaceColorInHtml ───────────────────────────────────────────────────────

describe('replaceColorInHtml', () => {
  it('reemplaza un color hex de 6 digitos', () => {
    const html = '<div style="color: #ff0000;">texto</div>';
    const result = replaceColorInHtml(html, '#ff0000', '#0000ff');
    expect(result).toContain('#0000ff');
    expect(result).not.toContain('#ff0000');
  });

  it('reemplaza todas las ocurrencias del mismo color', () => {
    const html = '<p style="color:#aabbcc">a</p><p style="background:#aabbcc">b</p>';
    const result = replaceColorInHtml(html, '#aabbcc', '#ffffff');
    expect(result.split('#ffffff')).toHaveLength(3); // 2 reemplazos -> 3 partes
    expect(result).not.toContain('#aabbcc');
  });

  it('reemplaza color en forma abreviada (#abc)', () => {
    const html = '<div style="color: #abc;">texto</div>';
    const result = replaceColorInHtml(html, '#aabbcc', '#000000');
    expect(result).toContain('#000000');
    expect(result).not.toContain('#abc');
  });

  it('es case-insensitive al comparar colores', () => {
    const html = '<div style="color: #FFAABB;">texto</div>';
    const result = replaceColorInHtml(html, '#ffaabb', '#000000');
    expect(result).toContain('#000000');
    expect(result).not.toContain('#FFAABB');
  });

  it('no modifica el HTML si el color no existe', () => {
    const html = '<div style="color: #ff0000;">texto</div>';
    const result = replaceColorInHtml(html, '#123456', '#000000');
    expect(result).toBe(html);
  });
});

// ─── applyColorToElement ──────────────────────────────────────────────────────

describe('applyColorToElement', () => {
  it('inserta propiedad color en elemento sin style', () => {
    const outerHTML = '<p>Hola mundo</p>';
    const htmlOutput = '<div>' + outerHTML + '</div>';
    const { html, newOuterHtml } = applyColorToElement(htmlOutput, outerHTML, 'color', '#ff0000');
    expect(newOuterHtml).toContain('color: #ff0000');
    expect(newOuterHtml).toContain('style=');
    expect(html).toContain('color: #ff0000');
  });

  it('modifica propiedad existente en style', () => {
    const outerHTML = '<p style="color: #000000; font-size: 16px;">texto</p>';
    const htmlOutput = '<div>' + outerHTML + '</div>';
    const { newOuterHtml } = applyColorToElement(htmlOutput, outerHTML, 'color', '#ff0000');
    expect(newOuterHtml).toContain('color: #ff0000');
    expect(newOuterHtml).not.toContain('color: #000000');
    expect(newOuterHtml).toContain('font-size: 16px');
  });

  it('agrega background-color a elemento con style existente', () => {
    const outerHTML = '<div style="color: red;">contenido</div>';
    const htmlOutput = '<body>' + outerHTML + '</body>';
    const { newOuterHtml } = applyColorToElement(htmlOutput, outerHTML, 'background-color', '#0000ff');
    expect(newOuterHtml).toContain('background-color: #0000ff');
    expect(newOuterHtml).toContain('color: red');
  });

  it('actualiza el htmlOutput completo reemplazando la ocurrencia', () => {
    const outerHTML = '<span>texto</span>';
    const htmlOutput = '<p>antes</p>' + outerHTML + '<p>despues</p>';
    const { html } = applyColorToElement(htmlOutput, outerHTML, 'color', '#123456');
    expect(html).toContain('color: #123456');
    expect(html).toContain('antes');
    expect(html).toContain('despues');
    expect(html).not.toContain('<span>texto</span>'); // reemplazado
  });
});

// ─── getContrastColor ─────────────────────────────────────────────────────────

describe('getContrastColor', () => {
  it('retorna negro para fondos claros', () => {
    expect(getContrastColor('#ffffff')).toBe('#000000');
    expect(getContrastColor('#ffff00')).toBe('#000000');
    expect(getContrastColor('#aaaaaa')).toBe('#000000');
  });

  it('retorna blanco para fondos oscuros', () => {
    expect(getContrastColor('#000000')).toBe('#ffffff');
    expect(getContrastColor('#0000ff')).toBe('#ffffff');
    expect(getContrastColor('#111111')).toBe('#ffffff');
  });

  it('maneja colores con mayusculas', () => {
    expect(getContrastColor('#FFFFFF')).toBe('#000000');
    expect(getContrastColor('#000000')).toBe('#ffffff');
  });

  it('rojo puro da contraste blanco (luminance baja)', () => {
    expect(getContrastColor('#ff0000')).toBe('#ffffff');
  });

  it('verde puro da contraste negro (luminance alta)', () => {
    expect(getContrastColor('#00ff00')).toBe('#000000');
  });
});
