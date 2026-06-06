'use client';

import type { AestheticScores } from '@/types/pipeline';
import { CRITERIA_LABELS, CRITERIA_DESCRIPTIONS } from '@/types/pipeline';

interface Props {
  scores: AestheticScores | null;
  scoresHistory: AestheticScores[];
}

const CRITERIA_KEYS = [
  'color_harmony',
  'wcag_contrast',
  'composition_balance',
  'visual_hierarchy',
  'gestalt_compliance',
  'whitespace_quality',
  'brand_consistency',
  'accessibility',
] as const;

function scoreColor(score: number) {
  if (score >= 85) return 'bg-green-500';
  if (score >= 70) return 'bg-yellow-400';
  return 'bg-red-400';
}

function scoreTextColor(score: number) {
  if (score >= 85) return 'text-green-700';
  if (score >= 70) return 'text-yellow-700';
  return 'text-red-600';
}

export default function Scorecard({ scores, scoresHistory }: Props) {
  if (!scores) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        Aún no hay scores disponibles
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Overall score */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Motor de Evaluación Estética</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Iteración {scores.iteration} ·{' '}
            {scores.passed ? (
              <span className="text-green-600 font-medium">Aprobado ✅</span>
            ) : (
              <span className="text-red-500 font-medium">No aprobado</span>
            )}
          </p>
        </div>
        <div className="text-right">
          <span className={`text-4xl font-black ${scoreTextColor(scores.overall_score)}`}>
            {scores.overall_score.toFixed(1)}
          </span>
          <p className="text-xs text-gray-400">/ 100</p>
        </div>
      </div>

      {/* Barra general */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-8">
        <div
          className={`${scoreColor(scores.overall_score)} h-2 rounded-full transition-all duration-700`}
          style={{ '--progress-width': `${scores.overall_score}%` } as React.CSSProperties}
        />
      </div>

      {/* Criterios individuales */}
      <div className="flex flex-col gap-4">
        {CRITERIA_KEYS.map(key => {
          const value = scores[key];
          return (
            <div key={key}>
              <div className="flex items-center justify-between mb-1">
                <div>
                  <span className="text-sm font-medium text-gray-700">
                    {CRITERIA_LABELS[key]}
                  </span>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {CRITERIA_DESCRIPTIONS[key]}
                  </p>
                </div>
                <span className={`text-sm font-bold ml-4 ${scoreTextColor(value)}`}>
                  {value.toFixed(1)}
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-1.5">
                <div
                  className={`${scoreColor(value)} h-1.5 rounded-full transition-all duration-500`}
                  style={{ '--progress-width': `${value}%` } as React.CSSProperties}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Historial de iteraciones */}
      {scoresHistory.length > 1 && (
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Evolución por iteración
          </h3>
          <div className="flex gap-3">
            {scoresHistory.map((hist, i) => (
              <div
                key={i}
                className={`flex-1 rounded-lg border px-3 py-2 text-center ${
                  i === scoresHistory.length - 1
                    ? 'border-blue-300 bg-blue-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <p className="text-xs text-gray-400">It. {hist.iteration}</p>
                <p className={`text-base font-bold ${scoreTextColor(hist.overall_score)}`}>
                  {hist.overall_score.toFixed(1)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
