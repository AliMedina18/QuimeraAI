'use client';
import type { FC } from 'react';

interface QuimeraLoaderProps {
  label?: string;
  size?: number;
}

const QuimeraLoader: FC<QuimeraLoaderProps> = ({ label, size = 128 }) => (
  <div className="flex flex-col items-center gap-5">
    <svg
      width={size}
      height={Math.round(size * 0.93)}
      viewBox="0 0 280 260"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Cargando"
      role="img"
    >
      <defs>
        <radialGradient id="ql-blue" cx="36%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#88C8FA"/>
          <stop offset="100%" stopColor="#1E5EC8"/>
        </radialGradient>
        <radialGradient id="ql-orange" cx="36%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#FCD96A"/>
          <stop offset="100%" stopColor="#D47208"/>
        </radialGradient>
        <radialGradient id="ql-pink" cx="36%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#F888CC"/>
          <stop offset="100%" stopColor="#BC0E7C"/>
        </radialGradient>
      </defs>

      {/* Rutas principales (carril exterior) */}
      <path id="ql-bo"  d="M 111 88 C 150 50 172 44 170 76"    fill="none" stroke="#7CD8F8" strokeWidth="2.8" strokeLinecap="round" opacity="0.75"/>
      <path id="ql-bo2" d="M 115 82 C 155 44 177 38 175 70"    fill="none" stroke="#7CD8F8" strokeWidth="1.8" strokeLinecap="round" opacity="0.38"/>
      <path id="ql-op"  d="M 207 84 C 244 118 244 162 213 162" fill="none" stroke="#7CD8F8" strokeWidth="2.8" strokeLinecap="round" opacity="0.75"/>
      <path id="ql-op2" d="M 213 87 C 250 122 250 167 219 167" fill="none" stroke="#7CD8F8" strokeWidth="1.8" strokeLinecap="round" opacity="0.38"/>
      <path id="ql-bp"  d="M 113 165 C 150 212 177 222 174 202" fill="none" stroke="#7CD8F8" strokeWidth="2.8" strokeLinecap="round" opacity="0.75"/>
      <path id="ql-bp2" d="M 107 162 C 143 208 170 218 168 198" fill="none" stroke="#7CD8F8" strokeWidth="1.8" strokeLinecap="round" opacity="0.38"/>

      {/* Azul → Naranja (adelante) */}
      <circle r="4.8" fill="#4EA8E8"><animateMotion dur="1.6s" repeatCount="indefinite" begin="0s" calcMode="linear"><mpath href="#ql-bo"/></animateMotion></circle>
      <circle r="3.4" fill="#4EA8E8" opacity="0.75"><animateMotion dur="1.6s" repeatCount="indefinite" begin="-0.4s" calcMode="linear"><mpath href="#ql-bo"/></animateMotion></circle>
      <circle r="2.4" fill="#4EA8E8" opacity="0.5"><animateMotion dur="1.6s" repeatCount="indefinite" begin="-0.8s" calcMode="linear"><mpath href="#ql-bo"/></animateMotion></circle>
      <circle r="1.8" fill="#4EA8E8" opacity="0.28"><animateMotion dur="1.6s" repeatCount="indefinite" begin="-1.2s" calcMode="linear"><mpath href="#ql-bo"/></animateMotion></circle>
      {/* Naranja → Azul (reversa) */}
      <circle r="3.2" fill="#F0A820" opacity="0.65"><animateMotion dur="2.1s" repeatCount="indefinite" begin="-0.3s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-bo2"/></animateMotion></circle>
      <circle r="2.0" fill="#F0A820" opacity="0.38"><animateMotion dur="2.1s" repeatCount="indefinite" begin="-1.35s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-bo2"/></animateMotion></circle>

      {/* Naranja → Rosa (adelante) */}
      <circle r="4.8" fill="#F0A820"><animateMotion dur="1.9s" repeatCount="indefinite" begin="0s" calcMode="linear"><mpath href="#ql-op"/></animateMotion></circle>
      <circle r="3.4" fill="#F0A820" opacity="0.75"><animateMotion dur="1.9s" repeatCount="indefinite" begin="-0.475s" calcMode="linear"><mpath href="#ql-op"/></animateMotion></circle>
      <circle r="2.4" fill="#F0A820" opacity="0.5"><animateMotion dur="1.9s" repeatCount="indefinite" begin="-0.95s" calcMode="linear"><mpath href="#ql-op"/></animateMotion></circle>
      <circle r="1.8" fill="#F0A820" opacity="0.28"><animateMotion dur="1.9s" repeatCount="indefinite" begin="-1.425s" calcMode="linear"><mpath href="#ql-op"/></animateMotion></circle>
      {/* Rosa → Naranja (reversa) */}
      <circle r="3.2" fill="#E82898" opacity="0.65"><animateMotion dur="2.4s" repeatCount="indefinite" begin="-0.5s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-op2"/></animateMotion></circle>
      <circle r="2.0" fill="#E82898" opacity="0.38"><animateMotion dur="2.4s" repeatCount="indefinite" begin="-1.7s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-op2"/></animateMotion></circle>

      {/* Azul → Rosa (adelante) */}
      <circle r="4.8" fill="#E82898"><animateMotion dur="2.2s" repeatCount="indefinite" begin="0s" calcMode="linear"><mpath href="#ql-bp"/></animateMotion></circle>
      <circle r="3.4" fill="#E82898" opacity="0.75"><animateMotion dur="2.2s" repeatCount="indefinite" begin="-0.55s" calcMode="linear"><mpath href="#ql-bp"/></animateMotion></circle>
      <circle r="2.4" fill="#E82898" opacity="0.5"><animateMotion dur="2.2s" repeatCount="indefinite" begin="-1.1s" calcMode="linear"><mpath href="#ql-bp"/></animateMotion></circle>
      <circle r="1.8" fill="#E82898" opacity="0.28"><animateMotion dur="2.2s" repeatCount="indefinite" begin="-1.65s" calcMode="linear"><mpath href="#ql-bp"/></animateMotion></circle>
      {/* Rosa → Azul (reversa) */}
      <circle r="3.2" fill="#4EA8E8" opacity="0.65"><animateMotion dur="1.85s" repeatCount="indefinite" begin="-0.7s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-bp2"/></animateMotion></circle>
      <circle r="2.0" fill="#4EA8E8" opacity="0.38"><animateMotion dur="1.85s" repeatCount="indefinite" begin="-1.6s" calcMode="linear" keyPoints="1;0" keyTimes="0;1"><mpath href="#ql-bp2"/></animateMotion></circle>

      {/* Esferas (encima de los puntos) */}
      <circle cx="78" cy="128" r="52" fill="url(#ql-blue)">
        <animate attributeName="r" values="52;56;52;54;52" dur="3.2s" repeatCount="indefinite" begin="0s" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1"/>
        <animate attributeName="opacity" values="1;0.85;1" dur="3.2s" repeatCount="indefinite" begin="0s"/>
      </circle>
      <circle cx="200" cy="46" r="38" fill="url(#ql-orange)">
        <animate attributeName="r" values="38;42;38;40;38" dur="3.2s" repeatCount="indefinite" begin="-1.07s" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1"/>
        <animate attributeName="opacity" values="1;0.85;1" dur="3.2s" repeatCount="indefinite" begin="-1.07s"/>
      </circle>
      <circle cx="208" cy="196" r="42" fill="url(#ql-pink)">
        <animate attributeName="r" values="42;46;42;44;42" dur="3.2s" repeatCount="indefinite" begin="-2.13s" calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1;0.4 0 0.6 1"/>
        <animate attributeName="opacity" values="1;0.85;1" dur="3.2s" repeatCount="indefinite" begin="-2.13s"/>
      </circle>
    </svg>

    {label && (
      <p className="text-[13px] font-medium text-gray-400 tracking-wide animate-pulse">
        {label}
      </p>
    )}
  </div>
);

export default QuimeraLoader;
