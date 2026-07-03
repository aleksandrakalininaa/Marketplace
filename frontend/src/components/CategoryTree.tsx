import { useState } from 'react';
import type { CategoryNode } from '../api/catalog';

interface CategoryTreeProps {
  categories: CategoryNode[];
  activeId: string | null;
  onSelect: (id: string) => void;
}

/** Рекурсивный компонент дерева категорий */
export function CategoryTree({ categories, activeId, onSelect }: CategoryTreeProps) {
  return (
    <ul className="category-tree">
      {categories.map((cat) => (
        <CategoryNodeItem key={cat.id} category={cat} activeId={activeId} onSelect={onSelect} />
      ))}
    </ul>
  );
}

function CategoryNodeItem({
  category,
  activeId,
  onSelect,
  depth = 0,
}: {
  category: CategoryNode;
  activeId: string | null;
  onSelect: (id: string) => void;
  depth?: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = category.children && category.children.length > 0;
  const isActive = activeId === category.id;

  return (
    <li>
      <button
        className={`category-tree-item ${isActive ? 'active' : ''}`}
        style={{ paddingLeft: `${12 + depth * 20}px` }}
        onClick={() => onSelect(category.id)}
      >
        {hasChildren && (
          <span
            className="tree-toggle"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
          >
            {expanded ? '▾' : '▸'}
          </span>
        )}
        <span className="category-name">{category.name}</span>
      </button>
      {hasChildren && expanded && (
        <ul>
          {category.children!.map((child) => (
            <CategoryNodeItem
              key={child.id}
              category={child}
              activeId={activeId}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}