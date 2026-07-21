import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';

const HelpSearch = ({ onSearch = null, placeholder = "Search for articles, guides, and more..." }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  
  const navigate = useNavigate();

  // Debounced search for dropdown
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    const delayDebounceFn = setTimeout(async () => {
      try {
        setIsSearching(true);
        const res = await helpApi.searchArticles({ keyword: query, limit: 5 });
        if (res.data?.success) {
          setResults(res.data.data);
          setShowDropdown(true);
        }
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    if (onSearch) {
      onSearch(query);
    } else {
      // If we are not on a dedicated search page, just show dropdown or navigate to an article if exact match
      // For now, if they press enter, let's navigate to the first result if available
      if (results.length > 0) {
        navigate(`/help/article/${results[0].slug}`);
        setShowDropdown(false);
      }
    }
  };

  const handleResultClick = (slug) => {
    navigate(`/help/article/${slug}`);
    setShowDropdown(false);
    setQuery('');
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto z-40">
      <form onSubmit={handleSubmit} className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-on-surface-variant">
          <span className="material-symbols-outlined">search</span>
        </div>
        <input
          type="text"
          className="w-full pl-12 pr-4 py-4 rounded-full border border-outline-variant bg-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent shadow-sm text-on-surface transition-all placeholder-on-surface-variant"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => { if (results.length > 0) setShowDropdown(true); }}
          onBlur={() => {
            // Delay hiding to allow clicking a result
            setTimeout(() => setShowDropdown(false), 200);
          }}
        />
        {isSearching && (
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
            <div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full"></div>
          </div>
        )}
      </form>

      {/* Dropdown Results */}
      {showDropdown && (
        <div className="absolute mt-2 w-full bg-surface border border-outline-variant rounded-xl shadow-lg overflow-hidden flex flex-col min-w-0">
          {results.length > 0 ? (
            <ul className="divide-y divide-outline-variant max-h-80 overflow-y-auto">
              {results.map((article) => (
                <li key={article.id}>
                  <button
                    type="button"
                    className="w-full text-left px-4 py-3 hover:bg-surface-container-high transition-colors flex flex-col items-start gap-1"
                    onClick={() => handleResultClick(article.slug)}
                  >
                    <span className="text-on-surface font-medium truncate w-full">{article.title}</span>
                    <span className="text-xs text-on-surface-variant truncate w-full">
                      {article.category?.name || 'General'} • {article.view_count || 0} views
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-center text-on-surface-variant text-sm">
              No articles found matching "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HelpSearch;
