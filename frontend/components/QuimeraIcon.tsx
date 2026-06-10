import type { FC } from 'react';

interface QuimeraIconProps {
  size?: number;
  className?: string;
}

const QuimeraIcon: FC<QuimeraIconProps> = ({ size = 28, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 280 260"
    xmlns="http://www.w3.org/2000/svg"
    aria-label="Quimera AI"
    className={className}
  >
    <defs>
      <radialGradient id="qi-blue" cx="36%" cy="30%" r="70%">
        <stop offset="0%" stopColor="#88C8FA"/>
        <stop offset="100%" stopColor="#1E5EC8"/>
      </radialGradient>
      <radialGradient id="qi-orange" cx="36%" cy="30%" r="70%">
        <stop offset="0%" stopColor="#FCD96A"/>
        <stop offset="100%" stopColor="#D47208"/>
      </radialGradient>
      <radialGradient id="qi-pink" cx="36%" cy="30%" r="70%">
        <stop offset="0%" stopColor="#F888CC"/>
        <stop offset="100%" stopColor="#BC0E7C"/>
      </radialGradient>
    </defs>
    <path d="M 111 88 C 150 50 172 44 170 76"    fill="none" stroke="#7CD8F8" strokeWidth="5" strokeLinecap="round" opacity="0.7"/>
    <path d="M 207 84 C 244 118 244 162 213 162" fill="none" stroke="#7CD8F8" strokeWidth="5" strokeLinecap="round" opacity="0.7"/>
    <path d="M 113 165 C 150 212 177 222 174 202" fill="none" stroke="#7CD8F8" strokeWidth="5" strokeLinecap="round" opacity="0.7"/>
    <circle cx="78"  cy="128" r="52" fill="url(#qi-blue)"/>
    <circle cx="200" cy="46"  r="38" fill="url(#qi-orange)"/>
    <circle cx="208" cy="196" r="42" fill="url(#qi-pink)"/>
  </svg>
);

export default QuimeraIcon;
