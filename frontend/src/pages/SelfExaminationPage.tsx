/**
 * Self-Examination Guide Page
 * Requirements: 16.3
 */

import React from 'react';
import { SelfExaminationGuide } from '../components/education/SelfExaminationGuide';

export const SelfExaminationPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <SelfExaminationGuide />
      </div>
    </div>
  );
};
