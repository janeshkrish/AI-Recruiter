import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface AutocompleteInputProps {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  suggestions: string[];
}

export default function AutocompleteInput({
  label,
  placeholder,
  value,
  onChange,
  suggestions,
}: AutocompleteInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Filter suggestions based on current input
  const filtered = value.trim()
    ? suggestions.filter((s) =>
        s.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8)
    : [];

  const showDropdown = isOpen && filtered.length > 0;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset highlighted index when filtered results change
  useEffect(() => {
    setHighlightedIndex(-1);
  }, [value]);

  const selectItem = useCallback(
    (item: string) => {
      onChange(item);
      setIsOpen(false);
      setHighlightedIndex(-1);
      inputRef.current?.blur();
    },
    [onChange]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev < filtered.length - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : filtered.length - 1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < filtered.length) {
          selectItem(filtered[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && dropdownRef.current) {
      const items = dropdownRef.current.querySelectorAll('[data-autocomplete-item]');
      items[highlightedIndex]?.scrollIntoView({ block: 'nearest' });
    }
  }, [highlightedIndex]);

  // Highlight matched text within suggestion
  const renderHighlightedText = (text: string) => {
    if (!value.trim()) return text;
    const idx = text.toLowerCase().indexOf(value.toLowerCase());
    if (idx === -1) return text;
    const before = text.slice(0, idx);
    const match = text.slice(idx, idx + value.length);
    const after = text.slice(idx + value.length);
    return (
      <>
        {before}
        <span className="text-violet-400 font-bold">{match}</span>
        {after}
      </>
    );
  };

  return (
    <div ref={containerRef} className="relative">
      <label className="block text-xs font-medium text-slate-500 mb-1.5">{label}</label>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          className="w-full glass-input rounded-lg p-2.5 pr-8 text-sm"
          placeholder={placeholder}
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />
        <ChevronDown
          size={14}
          className={`absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-600 transition-transform duration-200 ${
            showDropdown ? 'rotate-180' : ''
          }`}
        />
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.div
            ref={dropdownRef}
            className="absolute z-50 w-full mt-1 max-h-52 overflow-y-auto rounded-xl border border-white/[0.08] bg-[#0F1117]/95 backdrop-blur-xl shadow-2xl shadow-black/40"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
          >
            {filtered.map((item, i) => (
              <button
                key={item}
                data-autocomplete-item
                className={`w-full text-left px-3 py-2.5 text-sm transition-colors ${
                  i === highlightedIndex
                    ? 'bg-violet-500/15 text-white'
                    : 'text-slate-400 hover:bg-white/[0.04] hover:text-white'
                }`}
                onClick={() => selectItem(item)}
                onMouseEnter={() => setHighlightedIndex(i)}
              >
                {renderHighlightedText(item)}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
