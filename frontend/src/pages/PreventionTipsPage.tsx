/**
 * Prevention Tips Page
 * Requirements: 16.4
 */

import React from 'react';
import { PreventionTips } from '../components/education/PreventionTips';

export const PreventionTipsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <PreventionTips />
      </div>
    </div>
  );
};
