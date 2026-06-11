'use client';

import { useState, useEffect } from 'react';

interface ColorPickerProps {
  value: string;
  onChange: (hex: string) => void;
  label?: string;
}

export default function ColorPicker({ value, onChange, label }: ColorPickerProps) {
  const [hexInput, setHexInput] = useState(value);

  useEffect(() => {
    setHexInput(value);
  }, [value]);

  function handleNativeChange(e: React.ChangeEvent<HTMLInputElement>) {
    const hex = e.target.value;
    setHexInput(hex);
    onChange(hex);
  }

  function handleHexInput(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setHexInput(val);
    if (/^#[0-9a-fA-F]{6}$/.test(val)) {
      onChange(val);
    }
  }

  return (
    <div className="flex items-center gap-2">
      {label && (
        <span className="text-xs text-gray-500 w-10 shrink-0">{label}</span>
      )}
      <label className="relative cursor-pointer shrink-0">
        <input
          type="color"
          value={value.length === 7 ? value : '#000000'}
          onChange={handleNativeChange}
          className="sr-only"
        />
        <div
          className="w-8 h-8 rounded-lg border-2 border-white shadow shadow-gray-200 cursor-pointer hover:scale-110 transition-transform"
          style={{ backgroundColor: value }}
        />
      </label>
      <input
        type="text"
        value={hexInput}
        onChange={handleHexInput}
        maxLength={7}
        placeholder="#000000"
        className="flex-1 min-w-0 text-xs font-mono border border-gray-200 rounded-lg px-2 py-1.5 text-gray-700 focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400"
      />
    </div>
  );
}
