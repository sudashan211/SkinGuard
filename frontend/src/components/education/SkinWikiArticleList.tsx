/**
 * Skin-Wiki Article List Component
 * Requirements: 16.1, 16.2
 * 
 * Displays all 7 cancer types with images and descriptions
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { educationService } from '../../services/education';
import { SkinWikiArticle, CANCER_TYPE_LABELS, CANCER_TYPE_COLORS } from '../../types/education';

export const SkinWikiArticleList: React.FC = () => {
  const [articles, setArticles] = useState<SkinWikiArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const data = await educationService.getAllArticles();
      setArticles(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800">{error}</p>
        <button
          onClick={loadArticles}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Skin Cancer Encyclopedia</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Learn about different types of skin lesions, their risk factors, symptoms, and treatment options.
          This information is for educational purposes only and should not replace professional medical advice.
        </p>
      </div>

      {/* Educational Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg
            className="w-6 h-6 text-amber-600 mt-0.5 mr-3 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h3 className="font-semibold text-amber-900 mb-1">Educational Content Disclaimer</h3>
            <p className="text-sm text-amber-800">
              This content is for educational purposes only and does not constitute medical advice.
              Always consult with qualified healthcare professionals for diagnosis and treatment.
            </p>
          </div>
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <Link
            key={article.id}
            to={`/skin-wiki/${article.slug}`}
            className="group bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
          >
            {/* Article Image */}
            {article.image_url && (
              <div className="aspect-video w-full overflow-hidden bg-gray-100">
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
            )}

            {/* Article Content */}
            <div className="p-6">
              {/* Cancer Type Badge */}
              <div className="mb-3">
                <span
                  className={`inline-block px-3 py-1 text-xs font-semibold rounded-full border ${
                    CANCER_TYPE_COLORS[article.cancer_type]
                  }`}
                >
                  {CANCER_TYPE_LABELS[article.cancer_type]}
                </span>
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                {article.title}
              </h3>

              {/* Summary */}
              <p className="text-gray-600 text-sm line-clamp-3 mb-4">{article.summary}</p>

              {/* Read More Link */}
              <div className="flex items-center text-blue-600 font-medium text-sm">
                <span>Learn More</span>
                <svg
                  className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Empty State */}
      {articles.length === 0 && (
        <div className="text-center py-12">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
          <p className="text-gray-600">No articles available yet.</p>
        </div>
      )}
    </div>
  );
};
