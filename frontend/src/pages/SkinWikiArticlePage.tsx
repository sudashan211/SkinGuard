/**
 * Skin-Wiki Article Detail Page
 * Requirements: 16.1, 16.2
 */

import React from 'react';
import { SkinWikiArticleDetail } from '../components/education/SkinWikiArticleDetail';

export const SkinWikiArticlePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <SkinWikiArticleDetail />
      </div>
    </div>
  );
};
