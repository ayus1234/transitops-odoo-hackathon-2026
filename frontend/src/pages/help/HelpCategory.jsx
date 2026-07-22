import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';
import HelpArticleCard from '../../components/help/HelpArticleCard';
import HelpSearch from '../../components/help/HelpSearch';

const HelpCategory = () => {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  
  const [category, setCategory] = useState(null);
  const [articles, setArticles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCategoryData = async () => {
      setIsLoading(true);
      try {
        // Fetch categories to find the current one
        const catRes = await helpApi.getCategories();
        const currentCat = catRes.data?.data?.find(c => c.id === categoryId);
        
        if (!currentCat) {
          navigate('/help');
          return;
        }
        
        setCategory(currentCat);

        // Fetch articles for this category
        const artRes = await helpApi.getArticles({ category_id: categoryId, is_published: true, limit: 100 });
        setArticles(artRes.data?.data || []);
      } catch (err) {
        console.error('Failed to load category data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (categoryId) {
      fetchCategoryData();
    }
  }, [categoryId, navigate]);

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-pulse">
        <div className="h-8 w-24 bg-surface-container rounded"></div>
        <div className="h-32 bg-surface-container rounded-2xl w-full"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="h-48 bg-surface-container rounded-2xl"></div>
          <div className="h-48 bg-surface-container rounded-2xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8">
      {/* Breadcrumb & Navigation */}
      <nav className="flex items-center text-sm text-on-surface-variant">
        <Link to="/help" className="hover:text-primary transition-colors flex items-center gap-1">
          <span className="material-symbols-outlined text-[18px]">home</span>
          Help Center
        </Link>
        <span className="mx-2 material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface font-medium">{category?.name}</span>
      </nav>

      {/* Category Header */}
      <div className="card p-8 border-l-4 border-l-primary bg-surface flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
            <span className="material-symbols-outlined text-3xl">
              {category?.icon || 'folder'}
            </span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-on-surface mb-2">{category?.name}</h1>
            <p className="text-on-surface-variant max-w-2xl">
              {category?.description || `Browse all articles related to ${category?.name}.`}
            </p>
          </div>
        </div>
        
        <div className="w-full md:w-auto md:min-w-[300px]">
          <HelpSearch placeholder={`Search in ${category?.name}...`} />
        </div>
      </div>

      {/* Articles Grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-on-surface">Articles ({articles.length})</h2>
        </div>
        
        {articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map(article => (
              <HelpArticleCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <div className="card p-12 flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant mb-4">
              <span className="material-symbols-outlined text-3xl">article</span>
            </div>
            <h3 className="text-lg font-medium text-on-surface mb-2">No Articles Found</h3>
            <p className="text-on-surface-variant">There are currently no published articles in this category.</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default HelpCategory;
