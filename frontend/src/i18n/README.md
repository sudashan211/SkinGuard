# Internationalization (i18n) Implementation Guide

## Overview

SkinGuard supports 5 languages as per Requirements 19.1-19.6:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Mandarin Chinese (zh)

## Setup Complete

✅ i18next and react-i18next installed
✅ Language detection from browser configured
✅ Translation files created for all 5 languages
✅ Language switcher component created
✅ Backend language_preference support added
✅ Property tests implemented and passing

## Translation Files

All translation files are located in `frontend/src/i18n/locales/`:
- `en.json` - English
- `es.json` - Spanish
- `fr.json` - French
- `de.json` - German
- `zh.json` - Chinese

## Usage in Components

### Basic Usage

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.appName')}</h1>
      <button>{t('common.submit')}</button>
    </div>
  );
}
```

### With Variables

```typescript
const { t } = useTranslation();

// Translation: "Welcome, {{name}}!"
<p>{t('welcome', { name: user.name })}</p>
```

### Language Switcher

Add the LanguageSwitcher component to your layout:

```typescript
import { LanguageSwitcher } from '@/components/common/LanguageSwitcher';

function Header() {
  return (
    <header>
      <LanguageSwitcher />
    </header>
  );
}
```

### Sync with Backend

Use the `useLanguage` hook to automatically sync language preference with the backend:

```typescript
import { useLanguage } from '@/hooks/useLanguage';

function App() {
  useLanguage(); // Automatically syncs language preference
  
  return <YourApp />;
}
```

## Translation Keys Structure

### Common
- `common.appName` - Application name
- `common.loading` - Loading text
- `common.error` - Error text
- `common.success` - Success text
- `common.cancel` - Cancel button
- `common.save` - Save button
- etc.

### Authentication
- `auth.login` - Login text
- `auth.signup` - Signup text
- `auth.email` - Email label
- `auth.password` - Password label
- etc.

### Patient Dashboard
- `patient.dashboard` - Dashboard title
- `patient.uploadImage` - Upload image button
- `patient.results` - Results text
- etc.

### Medical Disclaimers
- `results.disclaimer` - Main AI disclaimer (Requirement 19.3)
- `results.urgentWarning` - Urgent case warning
- `education.checkRegularly` - Self-examination reminder

### Cancer Types (Requirement 19.4)
- `cancerTypes.melanoma` - Melanoma
- `cancerTypes.basalCellCarcinoma` - Basal Cell Carcinoma
- `cancerTypes.squamousCellCarcinoma` - Squamous Cell Carcinoma
- `cancerTypes.actinticKeratosis` - Actinic Keratosis
- `cancerTypes.benignKeratosis` - Benign Keratosis
- `cancerTypes.dermatofibroma` - Dermatofibroma
- `cancerTypes.vascularLesion` - Vascular Lesion

## Component Integration Examples

### Results Display with Disclaimer

```typescript
import { useTranslation } from 'react-i18next';

function ResultsDisplay({ result }) {
  const { t } = useTranslation();
  
  return (
    <div>
      <h2>{t('results.title')}</h2>
      
      {/* AI Predictions */}
      <div>
        <h3>{t('results.predictions')}</h3>
        {result.predictions.map(pred => (
          <div key={pred.type}>
            <span>{t(`cancerTypes.${pred.type}`)}</span>
            <span>{pred.probability}%</span>
          </div>
        ))}
      </div>
      
      {/* Medical Disclaimer (Requirement 19.3) */}
      <div className="disclaimer">
        <p>{t('results.disclaimer')}</p>
      </div>
      
      {/* Urgent Warning */}
      {result.risk_level === 'urgent' && (
        <div className="alert">
          <p>{t('results.urgentWarning')}</p>
          <button>{t('results.emergencyConsultation')}</button>
        </div>
      )}
    </div>
  );
}
```

### Doctor Locator

```typescript
import { useTranslation } from 'react-i18next';

function DoctorLocator() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('doctorLocator.title')}</h1>
      <input placeholder={t('doctorLocator.searchPlaceholder')} />
      
      {doctors.map(doctor => (
        <div key={doctor.id}>
          <h3>{doctor.name}</h3>
          <p>{t('doctorLocator.distance')}: {doctor.distance}km</p>
          <button>{t('doctorLocator.bookAppointment')}</button>
          <a href={doctor.whatsappUrl}>
            {t('doctorLocator.contactViaWhatsApp')}
          </a>
        </div>
      ))}
    </div>
  );
}
```

### Symptom Wizard

```typescript
import { useTranslation } from 'react-i18next';

function SymptomWizard({ step }) {
  const { t } = useTranslation();
  
  return (
    <div>
      <h2>{t('symptomWizard.title')}</h2>
      
      {step === 1 && (
        <div>
          <h3>{t('symptomWizard.step1.title')}</h3>
          <p>{t('symptomWizard.step1.description')}</p>
          <input placeholder={t('symptomWizard.step1.bodyLocation')} />
        </div>
      )}
      
      {step === 2 && (
        <div>
          <h3>{t('symptomWizard.step2.title')}</h3>
          <p>{t('symptomWizard.step2.description')}</p>
          <label>
            <input type="checkbox" />
            {t('symptomWizard.step2.itching')}
          </label>
          <label>
            <input type="checkbox" />
            {t('symptomWizard.step2.pain')}
          </label>
        </div>
      )}
      
      <button>{t('common.next')}</button>
    </div>
  );
}
```

## Browser Language Detection (Requirement 19.1)

The i18n configuration automatically detects the browser's Accept-Language header and sets the interface language accordingly. The detection order is:

1. localStorage (user's saved preference)
2. Browser navigator language
3. HTML tag language
4. Fallback to English

## Language Preference Persistence (Requirement 19.2)

When a user changes their language preference:

1. The selection is saved to localStorage
2. The selection is synced to the backend via PUT /api/auth/profile
3. On page reload, the language is restored from localStorage
4. When the user logs in, their saved preference is loaded from the backend

## Content Translation Enforcement (Requirement 19.6)

For Skin-Wiki content and educational articles, the system should enforce that all translations exist before publication. This is implemented in the admin panel:

```typescript
function SkinWikiEditor() {
  const { t } = useTranslation();
  const [translations, setTranslations] = useState({});
  
  const canPublish = () => {
    const requiredLanguages = ['en', 'es', 'fr', 'de', 'zh'];
    return requiredLanguages.every(lang => 
      translations[lang]?.title && translations[lang]?.body
    );
  };
  
  return (
    <div>
      {/* Translation inputs for each language */}
      <button disabled={!canPublish()}>
        {t('admin.publishArticle')}
      </button>
    </div>
  );
}
```

## Testing

Property-based tests are implemented in `tests/property/test_i18n_properties.py`:

- ✅ Property 57: Browser Language Detection
- ✅ Property 58: Language Preference Persistence
- ✅ Property 59: Disclaimer Translation
- ✅ Property 60: AI Result Translation
- ✅ Property 61: Minimum Language Support
- ✅ Property 62: Content Translation Completeness

## Next Steps for Full Integration

To complete the translation integration across all components:

1. Import `useTranslation` in each component
2. Replace hardcoded strings with `t('key')` calls
3. Test each component in all 5 languages
4. Add LanguageSwitcher to main navigation
5. Implement content translation enforcement in admin panel
6. Add language preference to user settings page

## Maintenance

When adding new UI text:

1. Add the key to `en.json` first
2. Add translations to all other language files (es, fr, de, zh)
3. Use the key in your component with `t('your.key')`
4. Test in all languages

## Resources

- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Documentation](https://www.i18next.com/)
- ISO 639-1 Language Codes
