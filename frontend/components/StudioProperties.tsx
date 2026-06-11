'use client';

import { useState, useMemo } from 'react';
import type { PipelineState } from '@/types/pipeline';
import ColorPicker from './ColorPicker';
import { IconCheck } from './Icons';
import { extractColorsFromHtml, getContrastColor } from '@/utils/colorUtils';

interface Props {
  state: PipelineState;
  onApplyElementColor: (property: 'color' | 'background-color', newColor: string) => void;
  onReplaceGlobalColor: (oldColor: string, newColor: string) => void;
  onSaveVersion: () => void;
}

export default function StudioProperties({
  state,
  onApplyElementColor,
  onReplaceGlobalColor,
  onSaveVersion,
}: Props) {
  const [textColor, setTextColor] = useState('#000000');
  const [bgColor, setBgColor] = useState('#ffffff');
  const [replacingColor, setReplacingColor] = useState<string | null>(null);
  const [replacementColor, setReplacementColor] = useState('#000000');
  const [savedFlash, setSavedFlash] = useState(false);

  const siteColors = useMemo(() => {
    if (!state.htmlOutput) return [];
    return extractColorsFromHtml(state.htmlOutput).slice(0, 16);
  }, [state.htmlOutput]);

  const { selectedElement } = state;

  function handleSaveVersion() {
    onSaveVersion();
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 2000);
  }

  function handleReplaceGlobal() {
    if (!replacingColor) return;
    onReplaceGlobalColor(replacingColor, replacementColor);
    setReplacingColor(null);
  }

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-100 overflow-y-auto text-sm">

      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 shrink-0">
        <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">
          Propiedades
        </p>
      </div>

      {/* Guardar version */}
      <div className="px-4 py-3 border-b border-gray-100 shrink-0">
        <button
          onClick={handleSaveVersion}
          className={`
            w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg transition-all
            ${savedFlash
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            }
          `}
        >
          {savedFlash ? (
            <><IconCheck size={12}/> Version guardada</>
          ) : (
            'Guardar version'
          )}
        </button>
        <p className="text-[11px] text-gray-400 text-center mt-1.5">
          Guarda un punto de restauracion
        </p>
      </div>

      {/* Colores del elemento seleccionado */}
      <div className="px-4 py-3 border-b border-gray-100 shrink-0">
        <p className="text-xs font-semibold text-gray-700 mb-3">
          {selectedElement
            ? <>Elemento: <code className="font-mono text-indigo-600 text-[11px]">&lt;{selectedElement.tag}&gt;</code></>
            : 'Colores del elemento'
          }
        </p>
        {selectedElement ? (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <ColorPicker label="Texto" value={textColor} onChange={setTextColor} />
              <button
                onClick={() => onApplyElementColor('color', textColor)}
                className="w-full text-[11px] py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md font-medium transition-colors"
              >
                Aplicar color de texto
              </button>
            </div>
            <div className="space-y-1.5">
              <ColorPicker label="Fondo" value={bgColor} onChange={setBgColor} />
              <button
                onClick={() => onApplyElementColor('background-color', bgColor)}
                className="w-full text-[11px] py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md font-medium transition-colors"
              >
                Aplicar color de fondo
              </button>
            </div>
          </div>
        ) : (
          <p className="text-[12px] text-gray-400 text-center py-2 leading-relaxed">
            Selecciona un elemento en el preview para editar sus colores
          </p>
        )}
      </div>

      {/* Paleta global del sitio */}
      <div className="px-4 py-3 shrink-0">
        <p className="text-xs font-semibold text-gray-700 mb-2.5">Paleta del sitio</p>
        {siteColors.length > 0 ? (
          <>
            <div className="grid grid-cols-4 gap-1.5 mb-3">
              {siteColors.map(color => (
                <button
                  key={color}
                  title={color}
                  onClick={() => {
                    setReplacingColor(prev => prev === color ? null : color);
                    setReplacementColor(color);
                  }}
                  className={`
                    h-9 rounded-lg border-2 transition-all text-[9px] font-mono flex items-end justify-center pb-0.5
                    ${replacingColor === color
                      ? 'border-indigo-500 scale-110 shadow-md'
                      : 'border-transparent hover:border-gray-300 hover:scale-105'
                    }
                  `}
                  style={{ backgroundColor: color, color: getContrastColor(color) }}
                >
                  {replacingColor === color ? '' : ''}
                </button>
              ))}
            </div>

            {/* Panel de reemplazo */}
            {replacingColor && (
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-3 space-y-2.5">
                <p className="text-[11px] text-gray-500">
                  Reemplazar{' '}
                  <span
                    className="inline-block w-3 h-3 rounded-sm align-middle mx-0.5 border border-gray-300"
                    style={{ backgroundColor: replacingColor }}
                  />{' '}
                  <code className="font-mono font-semibold text-gray-700">{replacingColor}</code>
                  {' '}en todo el sitio:
                </p>
                <ColorPicker value={replacementColor} onChange={setReplacementColor} />
                <div className="flex gap-2">
                  <button
                    onClick={handleReplaceGlobal}
                    className="flex-1 text-[11px] py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-semibold transition-colors"
                  >
                    Reemplazar global
                  </button>
                  <button
                    onClick={() => setReplacingColor(null)}
                    className="text-[11px] py-1.5 px-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md font-medium transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            )}

            <p className="text-[11px] text-gray-400 mt-2 text-center">
              Clic en un color para reemplazarlo globalmente
            </p>
          </>
        ) : (
          <p className="text-[12px] text-gray-400 text-center py-2">
            No se detectaron colores hex en el HTML
          </p>
        )}
      </div>
    </div>
  );
}
