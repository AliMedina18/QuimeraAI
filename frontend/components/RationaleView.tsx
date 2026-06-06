'use client';

import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

interface Props {
  markdown: string;
}

const components: Components = {
  h1: ({ children }) => (
    <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-lg font-bold text-gray-800 mb-3 mt-5">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-base font-semibold text-gray-700 mb-2 mt-4">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm text-gray-700 leading-relaxed mb-3">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc list-inside text-sm text-gray-700 mb-3 space-y-1 pl-2">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-inside text-sm text-gray-700 mb-3 space-y-1 pl-2">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="leading-relaxed">{children}</li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-gray-900">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic text-gray-600">{children}</em>
  ),
  code: ({ children, className }) => {
    const isBlock = className?.includes('language-');
    if (isBlock) {
      return (
        <pre className="bg-gray-900 text-gray-100 text-xs rounded-lg p-4 overflow-x-auto mb-3 font-mono">
          <code>{children}</code>
        </pre>
      );
    }
    return (
      <code className="bg-gray-100 text-gray-800 text-xs px-1.5 py-0.5 rounded font-mono">
        {children}
      </code>
    );
  },
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-blue-300 pl-4 text-sm text-gray-600 italic my-3">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="border-gray-200 my-5" />,
};

export default function RationaleView({ markdown }: Props) {
  if (!markdown) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        El rationale de diseño aparecerá aquí una vez generado
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <ReactMarkdown components={components}>{markdown}</ReactMarkdown>
    </div>
  );
}
