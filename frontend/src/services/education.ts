/**
 * Education Service - Skin-Wiki API
 * Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
 */

import { api } from './api';
import { SkinWikiArticle, CancerType } from '../types/education';

export const educationService = {
  /**
   * Get all published Skin-Wiki articles
   * Requirement 16.1
   */
  async getAllArticles(): Promise<SkinWikiArticle[]> {
    const response = await api.get('/skin-wiki/articles');
    return response.data;
  },

  /**
   * Get article by cancer type
   * Requirement 16.1, 16.2
   */
  async getArticleByCancerType(cancerType: CancerType): Promise<SkinWikiArticle> {
    const response = await api.get(`/skin-wiki/articles/type/${cancerType}`);
    return response.data;
  },

  /**
   * Get article by slug
   * Requirement 16.1, 16.2
   */
  async getArticleBySlug(slug: string): Promise<SkinWikiArticle> {
    const response = await api.get(`/skin-wiki/articles/${slug}`);
    return response.data;
  },

  /**
   * Get self-examination guide
   * Requirement 16.3
   */
  async getSelfExaminationGuide(): Promise<any> {
    const response = await api.get('/skin-wiki/self-examination-guide');
    return response.data;
  },

  /**
   * Get prevention tips
   * Requirement 16.4
   */
  async getPreventionTips(): Promise<any> {
    const response = await api.get('/skin-wiki/prevention-tips');
    return response.data;
  },
};
