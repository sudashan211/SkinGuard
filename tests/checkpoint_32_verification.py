"""
Checkpoint 32: Advanced Features Verification
Requirements: 21.1, 21.3, 21.4, 19.1-19.6

This script verifies:
1. PWA offline functionality
2. Multi-language switching
3. Mobile responsiveness
"""

import os
import json
from pathlib import Path

class CheckpointVerifier:
    def __init__(self):
        self.frontend_path = Path(__file__).parent.parent / "frontend"
        self.results = {
            "pwa": {"passed": [], "failed": []},
            "i18n": {"passed": [], "failed": []},
            "mobile": {"passed": [], "failed": []}
        }
    
    def verify_pwa_configuration(self):
        """Verify PWA is properly configured"""
        print("\n=== Verifying PWA Configuration ===")
        
        # Check vite.config.ts has PWA plugin
        vite_config = self.frontend_path / "vite.config.ts"
        if vite_config.exists():
            content = vite_config.read_text()
            if "VitePWA" in content and "workbox" in content:
                self.results["pwa"]["passed"].append("✓ Vite PWA plugin configured")
            else:
                self.results["pwa"]["failed"].append("✗ Vite PWA plugin not found")
        else:
            self.results["pwa"]["failed"].append("✗ vite.config.ts not found")
        
        # Check manifest.json exists
        manifest = self.frontend_path / "public" / "manifest.json"
        if manifest.exists():
            try:
                manifest_data = json.loads(manifest.read_text())
                required_fields = ["name", "short_name", "display", "icons"]
                if all(field in manifest_data for field in required_fields):
                    self.results["pwa"]["passed"].append("✓ manifest.json properly configured")
                    
                    # Check icons
                    if len(manifest_data.get("icons", [])) >= 2:
                        self.results["pwa"]["passed"].append("✓ PWA icons configured")
                    else:
                        self.results["pwa"]["failed"].append("✗ Insufficient PWA icons")
                else:
                    self.results["pwa"]["failed"].append("✗ manifest.json missing required fields")
            except json.JSONDecodeError:
                self.results["pwa"]["failed"].append("✗ manifest.json is invalid JSON")
        else:
            self.results["pwa"]["failed"].append("✗ manifest.json not found")
        
        # Check PWAHandler component exists
        pwa_handler = self.frontend_path / "src" / "components" / "common" / "PWAHandler.tsx"
        if pwa_handler.exists():
            content = pwa_handler.read_text()
            if "beforeinstallprompt" in content.lower():
                self.results["pwa"]["passed"].append("✓ PWA install prompt handler implemented")
            else:
                self.results["pwa"]["failed"].append("✗ PWA install prompt not implemented")
            
            if "useNetworkStatus" in content:
                self.results["pwa"]["passed"].append("✓ Network status monitoring implemented")
            else:
                self.results["pwa"]["failed"].append("✗ Network status monitoring missing")
        else:
            self.results["pwa"]["failed"].append("✗ PWAHandler component not found")
        
        # Check sync service exists
        sync_service = self.frontend_path / "src" / "services" / "syncService.ts"
        if sync_service.exists():
            content = sync_service.read_text()
            if "PendingUpload" in content and "syncPendingUploads" in content:
                self.results["pwa"]["passed"].append("✓ Offline sync service implemented")
            else:
                self.results["pwa"]["failed"].append("✗ Sync service incomplete")
        else:
            self.results["pwa"]["failed"].append("✗ Sync service not found")
    
    def verify_i18n_configuration(self):
        """Verify multi-language support"""
        print("\n=== Verifying Multi-Language Support ===")
        
        # Check i18n config
        i18n_config = self.frontend_path / "src" / "i18n" / "config.ts"
        if i18n_config.exists():
            content = i18n_config.read_text()
            if "i18next" in content and "LanguageDetector" in content:
                self.results["i18n"]["passed"].append("✓ i18next configured with language detection")
            else:
                self.results["i18n"]["failed"].append("✗ i18next not properly configured")
        else:
            self.results["i18n"]["failed"].append("✗ i18n config not found")
        
        # Check translation files
        locales_path = self.frontend_path / "src" / "i18n" / "locales"
        required_languages = ["en", "es", "fr", "de", "zh"]
        
        if locales_path.exists():
            found_languages = []
            for lang in required_languages:
                lang_file = locales_path / f"{lang}.json"
                if lang_file.exists():
                    try:
                        translations = json.loads(lang_file.read_text(encoding='utf-8'))
                        if translations:  # Has content
                            found_languages.append(lang)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        self.results["i18n"]["failed"].append(f"✗ {lang}.json error: {str(e)}")
            
            if len(found_languages) >= 5:
                self.results["i18n"]["passed"].append(f"✓ All 5 required languages present: {', '.join(found_languages)}")
            else:
                self.results["i18n"]["failed"].append(f"✗ Missing languages. Found: {', '.join(found_languages)}")
        else:
            self.results["i18n"]["failed"].append("✗ Locales directory not found")
        
        # Check LanguageSwitcher component
        lang_switcher = self.frontend_path / "src" / "components" / "common" / "LanguageSwitcher.tsx"
        if lang_switcher.exists():
            content = lang_switcher.read_text()
            if "useTranslation" in content and "changeLanguage" in content:
                self.results["i18n"]["passed"].append("✓ Language switcher component implemented")
            else:
                self.results["i18n"]["failed"].append("✗ Language switcher incomplete")
        else:
            self.results["i18n"]["failed"].append("✗ Language switcher not found")
        
        # Check useLanguage hook
        use_language = self.frontend_path / "src" / "hooks" / "useLanguage.ts"
        if use_language.exists():
            content = use_language.read_text()
            if "language_preference" in content:
                self.results["i18n"]["passed"].append("✓ Language preference persistence implemented")
            else:
                self.results["i18n"]["failed"].append("✗ Language persistence missing")
        else:
            self.results["i18n"]["failed"].append("✗ useLanguage hook not found")
    
    def verify_mobile_responsiveness(self):
        """Verify mobile-specific features"""
        print("\n=== Verifying Mobile Responsiveness ===")
        
        # Check touch gestures hook
        touch_gestures = self.frontend_path / "src" / "hooks" / "useTouchGestures.ts"
        if touch_gestures.exists():
            content = touch_gestures.read_text()
            if "getTouchDistance" in content and "handleTouchMove" in content:
                self.results["mobile"]["passed"].append("✓ Touch gestures (pinch/zoom) implemented")
            else:
                self.results["mobile"]["failed"].append("✗ Touch gestures incomplete")
        else:
            self.results["mobile"]["failed"].append("✗ Touch gestures hook not found")
        
        # Check TouchImageViewer component
        touch_viewer = self.frontend_path / "src" / "components" / "common" / "TouchImageViewer.tsx"
        if touch_viewer.exists():
            content = touch_viewer.read_text()
            if "useTouchGestures" in content and "getTransformStyle" in content:
                self.results["mobile"]["passed"].append("✓ Touch image viewer implemented")
            else:
                self.results["mobile"]["failed"].append("✗ Touch image viewer incomplete")
        else:
            self.results["mobile"]["failed"].append("✗ Touch image viewer not found")
        
        # Check Tailwind CSS responsive classes usage
        sample_components = [
            self.frontend_path / "src" / "components" / "patient" / "DiagnosticUploader.tsx",
            self.frontend_path / "src" / "components" / "patient" / "DoctorMap.tsx",
            self.frontend_path / "src" / "pages" / "LandingPage.tsx"
        ]
        
        responsive_found = False
        for component in sample_components:
            if component.exists():
                content = component.read_text()
                # Check for responsive classes (md:, lg:, sm:)
                if any(prefix in content for prefix in ["md:", "lg:", "sm:", "xl:"]):
                    responsive_found = True
                    break
        
        if responsive_found:
            self.results["mobile"]["passed"].append("✓ Responsive CSS classes used")
        else:
            self.results["mobile"]["failed"].append("✗ No responsive CSS classes found")
        
        # Check camera integration in DiagnosticUploader
        uploader = self.frontend_path / "src" / "components" / "patient" / "DiagnosticUploader.tsx"
        if uploader.exists():
            content = uploader.read_text()
            if "capture" in content.lower() or "camera" in content.lower():
                self.results["mobile"]["passed"].append("✓ Mobile camera capture supported")
            else:
                self.results["mobile"]["failed"].append("✗ Camera capture not implemented")
        else:
            self.results["mobile"]["failed"].append("✗ DiagnosticUploader not found")
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "="*60)
        print("CHECKPOINT 32 VERIFICATION RESULTS")
        print("="*60)
        
        categories = [
            ("PWA Offline Functionality", "pwa"),
            ("Multi-Language Support", "i18n"),
            ("Mobile Responsiveness", "mobile")
        ]
        
        total_passed = 0
        total_failed = 0
        
        for title, key in categories:
            print(f"\n{title}:")
            print("-" * 60)
            
            for item in self.results[key]["passed"]:
                print(f"  {item}")
                total_passed += 1
            
            for item in self.results[key]["failed"]:
                print(f"  {item}")
                total_failed += 1
        
        print("\n" + "="*60)
        print(f"SUMMARY: {total_passed} passed, {total_failed} failed")
        print("="*60)
        
        if total_failed == 0:
            print("\n✅ All checkpoint requirements verified successfully!")
            return True
        else:
            print(f"\n⚠️  {total_failed} issue(s) found. Please review.")
            return False
    
    def run(self):
        """Run all verifications"""
        print("Starting Checkpoint 32 Verification...")
        
        self.verify_pwa_configuration()
        self.verify_i18n_configuration()
        self.verify_mobile_responsiveness()
        
        return self.print_results()


if __name__ == "__main__":
    verifier = CheckpointVerifier()
    success = verifier.run()
    exit(0 if success else 1)
