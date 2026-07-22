import React from 'react';

const QuickActionCard = ({ action, onExecute, onToggleFavorite, isFavorite, isRestricted }) => {
  return (
    <div 
      className={`flex items-start gap-md p-md bg-surface border border-outline-variant rounded-xl transition-all cursor-pointer group ${isRestricted ? 'opacity-70 hover:opacity-100' : 'hover:bg-surface-variant hover:border-primary/30'}`}
      onClick={() => onExecute(action.id, action.route)}
    >
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-transform ${isRestricted ? 'bg-surface-variant text-on-surface-variant' : 'bg-primary-container text-on-primary-container group-hover:scale-105'}`}>
        <span className="material-symbols-outlined">{isRestricted ? 'lock' : action.icon || 'bolt'}</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-1">
          <h4 className="font-title-sm text-title-sm font-bold text-on-surface flex-1 leading-tight pt-1">
            {action.display_name}
          </h4>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite(action.id, !isFavorite);
            }}
            className={`shrink-0 p-1 rounded-full hover:bg-surface-container-high transition-colors ${isFavorite ? 'text-warning' : 'text-outline-variant hover:text-on-surface-variant'}`}
            title={isFavorite ? "Remove from favorites" : "Add to favorites"}
          >
            <span className={`material-symbols-outlined text-[18px] ${isFavorite ? 'material-icon-filled' : ''}`}>
              {isFavorite ? 'star' : 'star'}
            </span>
          </button>
        </div>
        {action.timestamp && (
          <p className="text-[11px] font-bold text-primary mb-1">
            Used {new Date(action.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
          </p>
        )}
        {action.description && (
          <p className="text-body-sm text-on-surface-variant mt-0.5">
            {action.description}
          </p>
        )}
      </div>
    </div>
  );
};

export default QuickActionCard;
