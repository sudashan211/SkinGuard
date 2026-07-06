import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Hook to sync language preference with backend
 * Implements Requirements 19.1, 19.2
 */
export const useLanguage = () => {
  const { i18n } = useTranslation();
  const { user, token } = useAuthStore();

  // Sync language preference to backend when it changes
  useEffect(() => {
    const syncLanguagePreference = async () => {
      if (user && token && i18n.language !== user.language_preference) {
        try {
          await axios.put(
            `${API_BASE_URL}/api/auth/profile`,
            { language_preference: i18n.language },
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          );
        } catch (error) {
          console.error('Failed to sync language preference:', error);
        }
      }
    };

    syncLanguagePreference();
  }, [i18n.language, user, token]);

  // Set language from user preference on mount
  useEffect(() => {
    if (user?.language_preference && i18n.language !== user.language_preference) {
      i18n.changeLanguage(user.language_preference);
    }
  }, [user?.language_preference, i18n]);

  return {
    currentLanguage: i18n.language,
    changeLanguage: i18n.changeLanguage
  };
};
