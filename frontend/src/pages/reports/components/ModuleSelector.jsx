import React from 'react';
import { MODULES } from '../constants';

const ModuleSelector = ({ selectedModule, onChange }) => {
  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm">
      <h3 className="text-title-sm font-title-sm text-on-surface mb-sm">1. Select Data Module</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-sm">
        {MODULES.map((mod) => (
          <button
            key={mod.id}
            onClick={() => onChange(mod.id)}
            className={`flex flex-col items-center justify-center p-md rounded-lg border transition-all ${
              selectedModule === mod.id
                ? 'bg-primary-container border-primary text-on-primary-container ring-2 ring-primary ring-opacity-50'
                : 'bg-surface border-outline-variant text-on-surface-variant hover:bg-surface-container hover:border-outline'
            }`}
          >
            <span className={`material-symbols-outlined text-3xl mb-xs ${selectedModule === mod.id ? 'text-primary' : ''}`}>
              {mod.icon}
            </span>
            <span className="text-body-sm font-bold">{mod.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ModuleSelector;
