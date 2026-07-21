import React from 'react';
import { CHART_TYPES } from '../constants';

const ChartSelector = ({ selectedChart, onChange }) => {
  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm h-full flex flex-col">
      <h3 className="text-title-sm font-title-sm text-on-surface mb-sm">Visual Type</h3>
      <div className="flex flex-wrap gap-2">
        {CHART_TYPES.map((chart) => (
          <button
            key={chart.id}
            onClick={() => onChange(chart.id)}
            className={`flex flex-col items-center justify-center p-2 rounded border transition-all flex-1 min-w-[70px] ${
              selectedChart === chart.id
                ? 'bg-primary-container border-primary text-on-primary-container ring-1 ring-primary'
                : 'bg-surface border-outline-variant text-on-surface-variant hover:bg-surface-container hover:border-outline'
            }`}
            title={chart.name}
          >
            <span className={`material-symbols-outlined text-xl mb-1 ${selectedChart === chart.id ? 'text-primary' : ''}`}>
              {chart.icon}
            </span>
            <span className="text-[10px] font-bold text-center leading-tight">{chart.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChartSelector;
