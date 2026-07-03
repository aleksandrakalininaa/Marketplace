import { useState, useEffect, useRef } from 'react';

interface SearchBarProps {
  initialValue?: string;
  placeholder?: string;
  onSearch: (value: string) => void;
}

/** Строка поиска с debounce 300ms */
export function SearchBar({ initialValue = '', placeholder = 'Поиск товаров...', onSearch }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  const emitChange = (newValue: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onSearch(newValue.trim());
    }, 300);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    setValue(v);
    emitChange(v);
  };

  const handleClear = () => {
    setValue('');
    if (debounceRef.current) clearTimeout(debounceRef.current);
    onSearch('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      onSearch(value.trim());
    }
  };

  return (
    <div className="search-bar">
      <span className="search-icon">🔍</span>
      <input
        type="text"
        className="search-input"
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
      />
      {value && (
        <button className="search-clear" onClick={handleClear}>
          ✕
        </button>
      )}
    </div>
  );
}