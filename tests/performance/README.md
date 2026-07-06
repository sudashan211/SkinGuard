# Performance Testing for SkinGuard

This directory contains performance tests for the SkinGuard platform, validating Requirements 20.1 (Performance Monitoring and Analytics).

## Overview

Performance testing ensures:
- AI analysis completes within 10 seconds (95th percentile)
- API responses average under 500ms
- Frontend loads within 3 seconds (First Contentful Paint)
- Bundle size stays under 500KB (gzipped)
- Application works on 3G connections

## Test Files

### 1. Backend Performance Tests

**File:** `test_ai_performance.py`

Tests AI processing pipeline performance:
- 95th percentile AI analysis time < 10 seconds
- Average response time < 8 seconds
- Individual component performance (Gatekeeper, Lesion Detection, Classification)

**Run:**
```bash
cd tests
python -m pytest performance/test_ai_performance.py -v -s -m performance
```

**Expected Output:**
```
AI PERFORMANCE TEST - 95th Percentile Analysis
Running 100 AI analyses to measure performance...
Target: 95th percentile < 10 seconds
------------------------------------------------------------
Completed 10/100 analyses... Current avg: 3.45s
Completed 20/100 analyses... Current avg: 3.52s
...
------------------------------------------------------------
PERFORMANCE RESULTS:
  Minimum:        2.134s
  Average:        3.567s
  50th percentile: 3.421s
  95th percentile: 4.892s ✓ PASS
  99th percentile: 5.234s
  Maximum:        5.678s
```

### 2. Load Testing

**File:** `locustfile.py`

Simulates multiple users accessing the platform simultaneously.

**Install Locust:**
```bash
pip install locust
```

**Run Load Test (Web UI):**
```bash
cd tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser.

**Run Load Test (Headless):**
```bash
# 50 users, spawn 5 per second, run for 5 minutes
locust -f locustfile.py --host=http://localhost:8000 \
       --users 50 --spawn-rate 5 --run-time 5m --headless
```

**Load Test Scenarios:**
- `SkinGuardUser`: Simulates patient users (view reports, upload images, find doctors)
- `DoctorUser`: Simulates doctor users (view pending reports, manage appointments)

**Task Weights:**
- View reports: 3x (most common)
- Find nearby doctors: 2x
- Upload image: 1x (resource intensive)
- View appointments: 1x
- Health check: 1x

### 3. Frontend Performance Tests

**File:** `frontend/tests/e2e/performance.spec.ts`

E2E performance tests using Playwright:
- Page load time < 3 seconds
- 3G connection performance
- First Contentful Paint < 1.5 seconds
- Bundle size validation
- API response times
- Mobile performance
- PWA service worker
- Code splitting verification
- Image optimization

**Run:**
```bash
cd frontend
npm run test:performance
```

**Run with specific browser:**
```bash
npx playwright test tests/e2e/performance.spec.ts --project=chromium
```

### 4. Lighthouse CI

**File:** `frontend/lighthouserc.json`

Automated performance monitoring with Lighthouse.

**Run Lighthouse locally:**
```bash
cd frontend
npm run build
npm run preview  # Start preview server

# In another terminal
npm run lighthouse
```

**Lighthouse Metrics:**
- Performance Score: > 80
- Accessibility Score: > 90
- Best Practices Score: > 90
- SEO Score: > 80
- First Contentful Paint: < 2s
- Largest Contentful Paint: < 3s
- Cumulative Layout Shift: < 0.1
- Total Blocking Time: < 300ms
- Speed Index: < 3s

## Performance Targets

### Backend Performance

| Metric | Target | Test |
|--------|--------|------|
| AI Analysis (95th percentile) | < 10s | `test_ai_analysis_95th_percentile_under_10_seconds` |
| AI Analysis (average) | < 8s | `test_ai_analysis_average_response_time` |
| Gatekeeper (95th percentile) | < 2s | `test_gatekeeper_performance` |
| Lesion Detection (95th percentile) | < 5s | `test_lesion_detection_performance` |
| Cancer Classification (95th percentile) | < 5s | `test_cancer_classification_performance` |
| API Response (average) | < 500ms | Load test |

### Frontend Performance

| Metric | Target | Test |
|--------|--------|------|
| Page Load Time | < 3s | `page loads within 3 seconds on fast connection` |
| 3G Load Time | < 10s | `app works on 3G connection` |
| First Contentful Paint | < 1.5s | `First Contentful Paint is under 1.5 seconds` |
| Bundle Size (gzipped) | < 500KB | `bundle size is reasonable` |
| Mobile Load Time | < 4s | `mobile performance is acceptable` |

## Optimization Strategies

### 1. Frontend Optimizations

**Code Splitting:**
- Implemented in `vite.config.ts`
- Separate chunks for React, UI libraries, forms, queries, maps, i18n
- Lazy loading for route components

**Bundle Optimization:**
- Minification with Terser
- Tree shaking enabled
- Console.log removal in production
- Chunk size warnings at 500KB

**Image Optimization:**
- Lazy loading with `loading="lazy"`
- WebP format support
- Responsive images with `srcset`
- Image compression

**Caching:**
- PWA service worker
- API response caching (24 hours)
- Medical images caching (30 days)
- Static assets caching (30 days)
- Font caching (1 year)

### 2. Backend Optimizations

**AI Model Optimization:**
- Model caching in memory
- Batch processing support
- GPU acceleration (if available)
- Model quantization (future)

**Database Optimization:**
- Indexed queries
- Connection pooling
- Query result caching with Redis
- Efficient JSONB queries

**API Optimization:**
- Response compression (gzip)
- Rate limiting
- Request validation
- Async processing

### 3. Network Optimization

**HTTP/2:**
- Multiplexing
- Server push
- Header compression

**CDN:**
- Static asset delivery
- Image optimization
- Geographic distribution

**Compression:**
- Gzip/Brotli compression
- Image compression
- JSON minification

## Continuous Performance Monitoring

### GitHub Actions Integration

Performance tests run automatically on:
- Every push to main/develop
- Every pull request
- Scheduled daily runs

**Workflow:** `.github/workflows/lighthouse.yml`

### Performance Budgets

Set in `lighthouserc.json`:
- Performance score: 80+
- FCP: < 2s
- LCP: < 3s
- CLS: < 0.1
- TBT: < 300ms

### Alerts

Performance degradation alerts:
- Lighthouse score drops below threshold
- API response time exceeds 5 seconds
- Bundle size increases by > 10%

## Troubleshooting

### Slow AI Analysis

**Symptoms:** AI analysis takes > 10 seconds

**Solutions:**
1. Check GPU availability: `nvidia-smi`
2. Verify model caching is working
3. Check system resources (CPU, RAM)
4. Profile with `cProfile`:
   ```python
   python -m cProfile -o profile.stats backend/app/ai_pipeline.py
   ```
5. Consider model optimization (quantization, pruning)

### Large Bundle Size

**Symptoms:** Bundle > 500KB gzipped

**Solutions:**
1. Analyze bundle: `npm run build:analyze`
2. Check for duplicate dependencies
3. Lazy load heavy components
4. Remove unused dependencies
5. Use dynamic imports

### Slow Page Load

**Symptoms:** Page load > 3 seconds

**Solutions:**
1. Run Lighthouse audit: `npm run lighthouse`
2. Check network waterfall in DevTools
3. Optimize images (compress, WebP)
4. Enable caching
5. Minimize render-blocking resources

### High API Latency

**Symptoms:** API responses > 500ms

**Solutions:**
1. Check database query performance
2. Add database indexes
3. Enable Redis caching
4. Optimize N+1 queries
5. Use connection pooling

## Performance Testing Checklist

Before deploying to production:

- [ ] Run all performance tests: `pytest performance/ -v -s -m performance`
- [ ] Run load test: `locust -f locustfile.py --headless --users 100 --run-time 5m`
- [ ] Run E2E performance tests: `npm run test:performance`
- [ ] Run Lighthouse audit: `npm run lighthouse`
- [ ] Verify bundle size: `npm run build:analyze`
- [ ] Test on 3G connection
- [ ] Test on mobile devices
- [ ] Check PWA functionality
- [ ] Verify caching is working
- [ ] Monitor production metrics

## Resources

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [Locust Documentation](https://docs.locust.io/)
- [Playwright Performance Testing](https://playwright.dev/docs/test-performance)
- [Vite Performance](https://vitejs.dev/guide/performance.html)

## Contact

For performance issues or questions:
- Create an issue in the repository
- Contact the performance team
- Review performance monitoring dashboard

---

**Last Updated:** 2024
**Maintained By:** SkinGuard Development Team
