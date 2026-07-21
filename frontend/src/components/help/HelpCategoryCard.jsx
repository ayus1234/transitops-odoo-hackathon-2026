import React from 'react';
import { Link } from 'react-router-dom';

const HelpCategoryCard = ({ category }) => {
  return (
    <Link 
      to={`/help/category/${category.id}`}
      className="card hover:border-primary/30 hover:shadow-md transition-all group h-full flex flex-col"
    >
      <div className="p-6 flex flex-col items-center text-center space-y-4 h-full">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
          <span className="material-symbols-outlined text-3xl">
            {category.icon || 'folder'}
          </span>
        </div>
        
        <div className="flex-grow">
          <h3 className="text-lg font-semibold text-on-surface mb-2">
            {category.name}
          </h3>
          <p className="text-sm text-on-surface-variant line-clamp-2">
            {category.description}
          </p>
        </div>
        
        <div className="text-xs font-medium text-primary bg-primary/10 px-3 py-1 rounded-full mt-4">
          View Articles
        </div>
      </div>
    </Link>
  );
};

export default HelpCategoryCard;
