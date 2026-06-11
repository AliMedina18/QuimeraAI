/**
 * Utilidades para extraccion y manipulacion de colores en HTML.
 */

/** Normaliza un hex a 6 caracteres minusculas, ej: #abc -> #aabbcc */
function normalizeHex(color: string): string {
  color = color.toLowerCase().trim();
  if (color.length === 4) {
    color = '#' + color[1]+color[1] + color[2]+color[2] + color[3]+color[3];
  }
  return color;
}

/** Extrae todos los colores hex unicos de un string HTML, en orden de aparicion. */
export function extractColorsFromHtml(html: string): string[] {
  const pattern = /#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b/g;
  const seen = new Set<string>();
  const result: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = pattern.exec(html)) !== null) {
    const c = normalizeHex(m[0]);
    if (!seen.has(c)) {
      seen.add(c);
      result.push(c);
    }
  }
  return result;
}

/**
 * Reemplaza todas las ocurrencias de oldColor por newColor en el HTML.
 * Maneja ambas formas: #rrggbb y #rgb. Case-insensitive.
 */
export function replaceColorInHtml(html: string, oldColor: string, newColor: string): string {
  const old6 = normalizeHex(oldColor);
  const new6 = normalizeHex(newColor);

  // Forma abreviada de oldColor (si aplica: #aabbcc -> #abc)
  let short3: string | null = null;
  if (old6[1]===old6[2] && old6[3]===old6[4] && old6[5]===old6[6]) {
    short3 = '#' + old6[1] + old6[3] + old6[5];
  }

  const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  let result = html.replace(new RegExp(escape(old6), 'gi'), new6);
  if (short3) result = result.replace(new RegExp(escape(short3), 'gi'), new6);
  return result;
}

/**
 * Aplica una propiedad CSS (color o background-color) al outerHTML de un elemento,
 * y sustituye esa ocurrencia en el HTML completo.
 */
export function applyColorToElement(
  htmlOutput: string,
  outerHTML: string,
  property: string,
  newColor: string
): { html: string; newOuterHtml: string } {
  const styleRegex = new RegExp(
    `(${property}\\s*:\\s*)(#[0-9a-fA-F]{3,6}|rgba?\\([^)]+\\)|[a-zA-Z]+)`,
    'i'
  );

  let newOuterHtml: string;
  if (styleRegex.test(outerHTML)) {
    // Ya tiene la propiedad: reemplaza el valor
    newOuterHtml = outerHTML.replace(styleRegex, `$1${newColor}`);
  } else {
    // Inyecta o extiende el atributo style
    const hasStyle = /style\s*=\s*["'][^"']*["']/i.test(outerHTML);
    if (hasStyle) {
      newOuterHtml = outerHTML.replace(
        /(style\s*=\s*["'])([^"']*)(["'])/i,
        `$1$2; ${property}: ${newColor}$3`
      );
    } else {
      newOuterHtml = outerHTML.replace(/^<(\w+)/, `<$1 style="${property}: ${newColor}"`);
    }
  }

  const html = htmlOutput.split(outerHTML).join(newOuterHtml);
  return { html, newOuterHtml };
}

/**
 * Devuelve '#000000' o '#ffffff' segun cual da mejor contraste con el color dado.
 */
export function getContrastColor(hex: string): string {
  const h = normalizeHex(hex);
  const r = parseInt(h.slice(1, 3), 16);
  const g = parseInt(h.slice(3, 5), 16);
  const b = parseInt(h.slice(5, 7), 16);
  const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return lum > 0.5 ? '#000000' : '#ffffff';
}
