/**
 * Skin-Wiki Page - Educational Content Hub
 * Requirements: 16.1, 16.2
 */

import React from 'react';
import { SkinWikiArticleList } from '../components/education/SkinWikiArticleList';

export const SkinWikiPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <SkinWikiArticleList />
      </div>
    </div>
  );
};
