import React from 'react';
import { MODULE_FIELDS, OPERATORS } from '../constants';

const FilterBuilder = ({ module, filters, onChange }) => {
  if (!module) {
    return (
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm opacity-50 pointer-events-none">
        <h3 className="text-title-sm font-title-sm text-on-surface mb-sm">3. Filters</h3>
        <p className="text-body-sm text-on-surface-variant">Please select a module first.</p>
      </div>
    );
  }

  const fields = MODULE_FIELDS[module] || [];

  const addFilter = () => {
    onChange([...filters, { field: fields[0] || '', operator: 'Equals', value: '' }]);
  };

  const updateFilter = (index, key, value) => {
    const newFilters = [...filters];
    newFilters[index][key] = value;
    onChange(newFilters);
  };

  const removeFilter = (index) => {
    const newFilters = [...filters];
    newFilters.splice(index, 1);
    onChange(newFilters);
  };

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-sm">
        <h3 className="text-title-sm font-title-sm text-on-surface">3. Filters</h3>
        <button onClick={addFilter} className="text-[11px] font-bold text-primary flex items-center gap-1 hover:underline">
          <span className="material-symbols-outlined text-[14px]">add</span> Add Filter
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {filters.length === 0 && (
          <p className="text-body-sm text-on-surface-variant text-center py-4">No filters applied. All records will be returned.</p>
        )}
        {filters.map((filter, index) => (
          <div key={index} className="flex flex-wrap items-center gap-2 bg-surface-container-lowest p-2 rounded border border-outline-variant">
            <select 
              value={filter.field} 
              onChange={(e) => updateFilter(index, 'field', e.target.value)}
              className="flex-1 min-w-[100px] bg-surface border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
            >
              {fields.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
            
            <select 
              value={filter.operator} 
              onChange={(e) => updateFilter(index, 'operator', e.target.value)}
              className="flex-1 min-w-[90px] bg-surface border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
            >
              {OPERATORS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
            
            <input 
              type="text" 
              value={filter.value}
              onChange={(e) => updateFilter(index, 'value', e.target.value)}
              placeholder="Value"
              className="flex-1 min-w-[120px] bg-surface border border-outline-variant text-body-sm px-2 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
            />
            
            <button onClick={() => removeFilter(index)} className="text-error hover:bg-error-container p-1 rounded transition-colors">
              <span className="material-symbols-outlined text-sm">close</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FilterBuilder;
