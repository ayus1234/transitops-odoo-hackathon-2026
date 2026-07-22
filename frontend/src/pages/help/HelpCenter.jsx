import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';
import HelpSearch from '../../components/help/HelpSearch';
import HelpCategoryCard from '../../components/help/HelpCategoryCard';
import HelpArticleCard from '../../components/help/HelpArticleCard';
import FeedbackModal from '../../components/help/FeedbackModal';

const HelpCenter = () => {
  const [categories, setCategories] = useState([]);
  const [featuredArticles, setFeaturedArticles] = useState([]);
  const [popularArticles, setPopularArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    const fetchHelpData = async () => {
      setIsLoading(true);
      try {
        const [catRes, featRes, popRes, statRes] = await Promise.all([
          helpApi.getCategories({ active_only: true, limit: 10 }),
          helpApi.getArticles({ is_featured: true, limit: 3 }),
          helpApi.getPopularArticles({ limit: 3 }),
          helpApi.getStatistics().catch(() => ({ data: { data: null } })) // gracefully handle if user isn't admin
        ]);

        setCategories(catRes.data?.data || []);
        setFeaturedArticles(featRes.data?.data || []);
        setPopularArticles(popRes.data?.data || []);
        setStats(statRes.data?.data);
      } catch (err) {
        console.error('Failed to load help center data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHelpData();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto flex flex-col gap-8 animate-pulse">
        <div className="h-64 bg-surface-container rounded-3xl w-full"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-40 bg-surface-container rounded-2xl"></div>
          <div className="h-40 bg-surface-container rounded-2xl"></div>
          <div className="h-40 bg-surface-container rounded-2xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-12">
      
      {/* Hero Section */}
      <section className="relative rounded-3xl bg-gradient-to-br from-primary/90 to-primary overflow-hidden text-on-primary">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
        <div className="relative z-10 px-6 py-16 md:py-24 flex flex-col items-center text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">How can we help you today?</h1>
          <p className="text-lg md:text-xl text-on-primary/80 mb-10 max-w-2xl">
            Search our knowledge base, browse categories, or reach out to our support team for assistance.
          </p>
          
          <HelpSearch />
          
          <div className="mt-12 flex flex-wrap justify-center gap-4">
            <Link to="/help/tickets" className="bg-surface text-primary px-5 py-2.5 rounded-full font-bold hover:opacity-90 active:scale-95 transition-all flex items-center gap-2 shadow-md">
              <span className="material-symbols-outlined text-[20px]">confirmation_number</span>
              <span>View My Tickets</span>
            </Link>
            <button onClick={() => setIsFeedbackOpen(true)} className="bg-on-primary/10 text-on-primary border border-on-primary/20 px-5 py-2.5 rounded-full font-bold hover:bg-on-primary/20 active:scale-95 transition-all flex items-center gap-2 shadow-sm">
              <span className="material-symbols-outlined text-[20px]">rate_review</span>
              <span>Give Feedback</span>
            </button>
          </div>
        </div>
      </section>

      {/* Admin Statistics (Only shows if backend returns it) */}
      {stats && (
        <section className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-5 gap-4">
          <div className="card p-4 flex flex-col items-center text-center">
            <span className="text-sm text-on-surface-variant font-medium">Total Articles</span>
            <span className="text-2xl font-bold text-primary mt-1">{stats.articles?.total || 0}</span>
          </div>
          <div className="card p-4 flex flex-col items-center text-center">
            <span className="text-sm text-on-surface-variant font-medium">Categories</span>
            <span className="text-2xl font-bold text-primary mt-1">{stats.categories?.total || 0}</span>
          </div>
          <div className="card p-4 flex flex-col items-center text-center">
            <span className="text-sm text-on-surface-variant font-medium">Open Tickets</span>
            <span className="text-2xl font-bold text-amber-500 mt-1">{stats.tickets?.open || 0}</span>
          </div>
          <div className="card p-4 flex flex-col items-center text-center">
            <span className="text-sm text-on-surface-variant font-medium">Resolved Tickets</span>
            <span className="text-2xl font-bold text-green-500 mt-1">{stats.tickets?.resolved || 0}</span>
          </div>
          <div className="card p-4 flex flex-col items-center text-center">
            <span className="text-sm text-on-surface-variant font-medium">Avg Rating</span>
            <span className="text-2xl font-bold text-primary mt-1">{stats.feedback?.average_rating?.toFixed(1) || '0.0'}</span>
          </div>
        </section>
      )}

      {/* Categories Grid */}
      {categories.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-on-surface">Browse by Category</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {categories.map(category => (
              <HelpCategoryCard key={category.id} category={category} />
            ))}
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Featured Articles */}
        {featuredArticles.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-amber-500">star</span>
                Featured Articles
              </h2>
            </div>
            <div className="flex flex-col gap-4">
              {featuredArticles.map(article => (
                <HelpArticleCard key={article.id} article={article} />
              ))}
            </div>
          </section>
        )}

        {/* Popular Articles */}
        {popularArticles.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-green-500">trending_up</span>
                Popular Articles
              </h2>
            </div>
            <div className="flex flex-col gap-4">
              {popularArticles.map(article => (
                <HelpArticleCard key={article.id} article={article} />
              ))}
            </div>
          </section>
        )}
      </div>

      <FeedbackModal 
        isOpen={isFeedbackOpen} 
        onClose={() => setIsFeedbackOpen(false)} 
        defaultPage="Help Center Home"
      />
    </div>
  );
};

export default HelpCenter;
