import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';
import FeedbackModal from '../../components/help/FeedbackModal';

const HelpArticle = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  
  const [article, setArticle] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    const fetchArticle = async () => {
      setIsLoading(true);
      try {
        const res = await helpApi.getArticleBySlug(slug);
        if (res.data?.success) {
          setArticle(res.data.data);
        } else {
          navigate('/help');
        }
      } catch (err) {
        console.error('Failed to load article:', err);
        navigate('/help');
      } finally {
        setIsLoading(false);
      }
    };

    if (slug) {
      fetchArticle();
    }
  }, [slug, navigate]);

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-8 w-32 bg-surface-container rounded"></div>
        <div className="h-16 w-3/4 bg-surface-container rounded-lg"></div>
        <div className="flex gap-4">
          <div className="h-6 w-24 bg-surface-container rounded-full"></div>
          <div className="h-6 w-24 bg-surface-container rounded-full"></div>
        </div>
        <div className="space-y-4 mt-8">
          <div className="h-4 w-full bg-surface-container rounded"></div>
          <div className="h-4 w-full bg-surface-container rounded"></div>
          <div className="h-4 w-5/6 bg-surface-container rounded"></div>
          <div className="h-4 w-4/6 bg-surface-container rounded"></div>
        </div>
      </div>
    );
  }

  if (!article) return null;

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto space-y-8">
      {/* Breadcrumbs */}
      <nav className="flex flex-wrap items-center text-sm text-on-surface-variant gap-y-2">
        <Link to="/help" className="hover:text-primary transition-colors flex items-center gap-1">
          <span className="material-symbols-outlined text-[18px]">home</span>
          Help Center
        </Link>
        <span className="mx-2 material-symbols-outlined text-[16px]">chevron_right</span>
        <Link to={`/help/category/${article.category?.id}`} className="hover:text-primary transition-colors truncate max-w-[150px] sm:max-w-xs">
          {article.category?.name}
        </Link>
        <span className="mx-2 material-symbols-outlined text-[16px]">chevron_right</span>
        <span className="text-on-surface font-medium truncate max-w-[150px] sm:max-w-xs">{article.title}</span>
      </nav>

      {/* Article Header */}
      <header className="space-y-6 pb-8 border-b border-outline-variant">
        <div className="flex items-center gap-3">
          {article.is_featured && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              <span className="material-symbols-outlined text-[14px]">star</span>
              Featured
            </span>
          )}
          {article.view_count > 100 && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20">
              <span className="material-symbols-outlined text-[14px]">trending_up</span>
              Popular
            </span>
          )}
        </div>
        
        <h1 className="text-3xl md:text-4xl font-bold text-on-surface leading-tight">
          {article.title}
        </h1>
        
        {article.summary && (
          <p className="text-lg text-on-surface-variant leading-relaxed">
            {article.summary}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-on-surface-variant pt-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-surface-container-highest flex items-center justify-center text-on-surface font-bold text-xs uppercase">
              {article.author?.first_name?.[0] || 'A'}
            </div>
            <span>{article.author ? `${article.author.first_name} ${article.author.last_name}` : 'Admin'}</span>
          </div>
          <div className="flex items-center gap-1.5" title="Last updated">
            <span className="material-symbols-outlined text-[16px]">update</span>
            {new Date(article.updated_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
          <div className="flex items-center gap-1.5" title="Views">
            <span className="material-symbols-outlined text-[16px]">visibility</span>
            {article.view_count} views
          </div>
        </div>
      </header>

      {/* Article Content */}
      <article className="prose prose-on-surface max-w-none pb-8 border-b border-outline-variant">
        {/* Render markdown/HTML content safely. For now, assuming text/html. 
            If using Markdown, a library like react-markdown would be needed. 
            Since we don't know if the backend stores HTML or markdown, we'll dangerouslySetInnerHTML 
            but in a real prod env this MUST be sanitized. */}
        <div 
          className="whitespace-pre-wrap text-base leading-relaxed text-on-surface font-sans"
          dangerouslySetInnerHTML={{ __html: article.content }} 
        />
      </article>

      {/* Tags */}
      {article.tags && Object.keys(article.tags).length > 0 && (
        <div className="py-4">
          <h3 className="text-sm font-semibold text-on-surface mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {Object.keys(article.tags).map(tag => (
              <span key={tag} className="px-3 py-1 rounded-full bg-surface-container text-on-surface-variant text-xs font-medium border border-outline-variant">
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Feedback Section */}
      <section className="bg-surface-container-low rounded-2xl p-8 flex flex-col items-center text-center mt-12">
        <h3 className="text-xl font-semibold text-on-surface mb-2">Was this article helpful?</h3>
        <p className="text-on-surface-variant mb-6">Let us know if this resolved your issue or if we can improve it.</p>
        <button 
          onClick={() => setIsFeedbackOpen(true)}
          className="btn btn-primary"
        >
          <span className="material-symbols-outlined text-[18px]">rate_review</span>
          Provide Feedback
        </button>
      </section>

      <FeedbackModal 
        isOpen={isFeedbackOpen} 
        onClose={() => setIsFeedbackOpen(false)} 
        defaultPage={`Article: ${article.slug}`}
      />
    </div>
  );
};

export default HelpArticle;
