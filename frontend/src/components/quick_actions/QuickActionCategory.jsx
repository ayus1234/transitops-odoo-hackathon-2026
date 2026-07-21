import React from 'react';

const QuickActionCategory = ({ title, icon, children }) => {
  if (!children || (Array.isArray(children) && children.length === 0)) {
    return null;
  }
  
  return (
    <div className="mb-lg">
      <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mb-md px-1">
        {icon && (
          <span className="material-symbols-outlined text-[18px] text-primary">
            {icon}
          </span>
        )}
        <h3 className="font-label-lg text-label-lg font-bold text-on-surface uppercase tracking-wider opacity-80">
          {title}
        </h3>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {children}
      </div>
    </div>
  );
};

export default QuickActionCategory;
