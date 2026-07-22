import React from 'react';
import { Link } from 'react-router-dom';

const HelpArticleCard = ({ article }) => {
  const isFeatured = article.is_featured;
  const isPopular = article.view_count > 100;
  
  return (
    <Link 
      to={`/help/article/${article.slug}`}
      className="card hover:border-primary/30 transition-all group flex flex-col h-full"
    >
      <div className="p-5 flex flex-col h-full">
        <div className="flex items-start justify-between mb-3">
          <div className="flex gap-2 flex-wrap">
            {isFeatured && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400">
                <span className="material-symbols-outlined text-[14px]">star</span>
                Featured
              </span>
            )}
            {isPopular && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-green-500/10 text-green-600 dark:text-green-400">
                <span className="material-symbols-outlined text-[14px]">trending_up</span>
                Popular
              </span>
            )}
          </div>
          <span className="text-xs text-on-surface-variant flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">visibility</span>
            {article.view_count || 0}
          </span>
        </div>
        
        <h3 className="text-base font-semibold text-on-surface mb-2 group-hover:text-primary transition-colors line-clamp-2">
          {article.title}
        </h3>
        
        <p className="text-sm text-on-surface-variant mb-4 line-clamp-2 flex-grow">
          {article.summary || article.content?.substring(0, 100) + '...'}
        </p>
        
        <div className="mt-auto flex items-center justify-between text-xs text-on-surface-variant border-t border-outline-variant pt-3">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">calendar_today</span>
            {new Date(article.created_at).toLocaleDateString()}
          </span>
          <span className="flex items-center gap-1 text-primary font-medium group-hover:underline">
            Read More
            <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
          </span>
        </div>
      </div>
    </Link>
  );
};

export default HelpArticleCard;
