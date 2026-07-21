import React, { useState } from 'react';
import { MODULE_FIELDS } from '../constants';

const FieldSelector = ({ module, selectedFields, onChange }) => {
  const [searchTerm, setSearchTerm] = useState('');

  if (!module) {
    return (
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm opacity-50 pointer-events-none">
        <h3 className="text-title-sm font-title-sm text-on-surface mb-sm">2. Select Fields</h3>
        <p className="text-body-sm text-on-surface-variant">Please select a module first.</p>
      </div>
    );
  }

  const allFields = MODULE_FIELDS[module] || [];
  const filteredFields = allFields.filter(f => f.toLowerCase().includes(searchTerm.toLowerCase()));

  const handleToggle = (field) => {
    if (selectedFields.includes(field)) {
      onChange(selectedFields.filter(f => f !== field));
    } else {
      onChange([...selectedFields, field]);
    }
  };

  const handleSelectAll = () => onChange([...allFields]);
  const handleClearAll = () => onChange([]);

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-sm">
        <h3 className="text-title-sm font-title-sm text-on-surface">2. Select Fields</h3>
        <div className="flex gap-2">
          <button onClick={handleSelectAll} className="text-[11px] font-bold text-primary hover:underline">Select All</button>
          <button onClick={handleClearAll} className="text-[11px] font-bold text-error hover:underline">Clear All</button>
        </div>
      </div>
      
      <div className="relative mb-sm">
        <span className="material-symbols-outlined absolute left-2 top-2 text-on-surface-variant text-sm">search</span>
        <input 
          type="text" 
          placeholder="Search fields..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-surface-container-lowest border border-outline-variant text-body-sm pl-8 pr-3 py-1.5 rounded focus:ring-primary outline-none focus:border-primary"
        />
      </div>

      <div className="flex-1 overflow-y-auto max-h-[250px] space-y-1 custom-scrollbar pr-1">
        {filteredFields.map(field => (
          <label key={field} className="flex items-center gap-2 p-2 hover:bg-surface-container-low rounded cursor-pointer transition-colors">
            <input 
              type="checkbox" 
              checked={selectedFields.includes(field)}
              onChange={() => handleToggle(field)}
              className="rounded text-primary focus:ring-primary border-outline"
            />
            <span className="text-body-sm text-on-surface">{field}</span>
          </label>
        ))}
        {filteredFields.length === 0 && (
          <p className="text-body-sm text-on-surface-variant p-2 text-center">No fields match your search.</p>
        )}
      </div>
    </div>
  );
};

export default FieldSelector;
