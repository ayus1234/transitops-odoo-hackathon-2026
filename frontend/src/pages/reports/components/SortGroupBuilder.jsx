import React from 'react';
import { MODULE_FIELDS } from '../constants';

const SortGroupBuilder = ({ module, groupBy, setGroupBy, sortBy, setSortBy, sortOrder, setSortOrder }) => {
  if (!module) return null;

  const fields = MODULE_FIELDS[module] || [];

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col gap-4 h-full">
      <div className="flex-1">
        <h3 className="text-title-sm font-title-sm text-on-surface mb-xs">Group By</h3>
        <select 
          value={groupBy} 
          onChange={(e) => setGroupBy(e.target.value)}
          className="w-full bg-surface-container-lowest border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
        >
          <option value="">-- None --</option>
          {fields.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>
      
      <div className="flex-1">
        <h3 className="text-title-sm font-title-sm text-on-surface mb-xs">Sort By</h3>
        <div className="flex gap-2">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="flex-1 bg-surface-container-lowest border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
          >
            <option value="">-- None --</option>
            {fields.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
          <select 
            value={sortOrder} 
            onChange={(e) => setSortOrder(e.target.value)}
            className="w-[80px] bg-surface-container-lowest border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
          >
            <option value="asc">ASC</option>
            <option value="desc">DESC</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default SortGroupBuilder;
