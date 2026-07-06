"""
Performance Report Generator
Generates a comprehensive performance report from test results

Usage:
    python performance_report.py
"""

import json
import time
from datetime import datetime
from pathlib import Path
import statistics


class PerformanceReport:
    """Generate performance reports from test results"""
    
    def __init__(self):
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'backend': {},
            'frontend': {},
            'summary': {}
        }
    
    def add_backend_metrics(self, metrics: dict):
        """Add backend performance metrics"""
        self.report_data['backend'] = metrics
    
    def add_frontend_metrics(self, metrics: dict):
        """Add frontend performance metrics"""
        self.report_data['frontend'] = metrics
    
    def calculate_summary(self):
        """Calculate overall performance summary"""
        backend = self.report_data['backend']
        frontend = self.report_data['frontend']
        
        # Check if targets are met
        targets_met = []
        targets_failed = []
        
        # Backend targets
        if backend.get('ai_p95', 0) < 10.0:
            targets_met.append('AI Analysis (95th percentile < 10s)')
        else:
            targets_failed.append(f"AI Analysis (95th percentile: {backend.get('ai_p95', 0):.2f}s > 10s)")
        
        if backend.get('api_avg', 0) < 0.5:
            targets_met.append('API Response (average < 500ms)')
        else:
            targets_failed.append(f"API Response (average: {backend.get('api_avg', 0)*1000:.0f}ms > 500ms)")
        
        # Frontend targets
        if frontend.get('page_load', 0) < 3.0:
            targets_met.append('Page Load (< 3s)')
        else:
            targets_failed.append(f"Page Load ({frontend.get('page_load', 0):.2f}s > 3s)")
        
        if frontend.get('fcp', 0) < 1.5:
            targets_met.append('First Contentful Paint (< 1.5s)')
        else:
            targets_failed.append(f"FCP ({frontend.get('fcp', 0):.2f}s > 1.5s)")
        
        if frontend.get('bundle_size_kb', 0) < 500:
            targets_met.append('Bundle Size (< 500KB gzipped)')
        else:
            targets_failed.append(f"Bundle Size ({frontend.get('bundle_size_kb', 0):.0f}KB > 500KB)")
        
        self.report_data['summary'] = {
            'targets_met': targets_met,
            'targets_failed': targets_failed,
            'overall_status': 'PASS' if len(targets_failed) == 0 else 'FAIL',
            'score': len(targets_met) / (len(targets_met) + len(targets_failed)) * 100
        }
    
    def generate_markdown(self) -> str:
        """Generate markdown report"""
        md = []
        
        md.append("# SkinGuard Performance Report")
        md.append("")
        md.append(f"**Generated:** {self.report_data['timestamp']}")
        md.append("")
        
        # Summary
        summary = self.report_data['summary']
        md.append("## Summary")
        md.append("")
        md.append(f"**Overall Status:** {summary['overall_status']}")
        md.append(f"**Performance Score:** {summary['score']:.1f}%")
        md.append("")
        
        # Targets Met
        if summary['targets_met']:
            md.append("### ✓ Targets Met")
            md.append("")
            for target in summary['targets_met']:
                md.append(f"- ✓ {target}")
            md.append("")
        
        # Targets Failed
        if summary['targets_failed']:
            md.append("### ✗ Targets Failed")
            md.append("")
            for target in summary['targets_failed']:
                md.append(f"- ✗ {target}")
            md.append("")
        
        # Backend Metrics
        backend = self.report_data['backend']
        if backend:
            md.append("## Backend Performance")
            md.append("")
            md.append("| Metric | Value | Target | Status |")
            md.append("|--------|-------|--------|--------|")
            
            ai_p95 = backend.get('ai_p95', 0)
            md.append(f"| AI Analysis (95th percentile) | {ai_p95:.2f}s | < 10s | {'✓' if ai_p95 < 10 else '✗'} |")
            
            ai_avg = backend.get('ai_avg', 0)
            md.append(f"| AI Analysis (average) | {ai_avg:.2f}s | < 8s | {'✓' if ai_avg < 8 else '✗'} |")
            
            gatekeeper_p95 = backend.get('gatekeeper_p95', 0)
            md.append(f"| Gatekeeper (95th percentile) | {gatekeeper_p95:.2f}s | < 2s | {'✓' if gatekeeper_p95 < 2 else '✗'} |")
            
            api_avg = backend.get('api_avg', 0)
            md.append(f"| API Response (average) | {api_avg*1000:.0f}ms | < 500ms | {'✓' if api_avg < 0.5 else '✗'} |")
            
            md.append("")
        
        # Frontend Metrics
        frontend = self.report_data['frontend']
        if frontend:
            md.append("## Frontend Performance")
            md.append("")
            md.append("| Metric | Value | Target | Status |")
            md.append("|--------|-------|--------|--------|")
            
            page_load = frontend.get('page_load', 0)
            md.append(f"| Page Load Time | {page_load:.2f}s | < 3s | {'✓' if page_load < 3 else '✗'} |")
            
            fcp = frontend.get('fcp', 0)
            md.append(f"| First Contentful Paint | {fcp:.2f}s | < 1.5s | {'✓' if fcp < 1.5 else '✗'} |")
            
            bundle_size = frontend.get('bundle_size_kb', 0)
            md.append(f"| Bundle Size (gzipped) | {bundle_size:.0f}KB | < 500KB | {'✓' if bundle_size < 500 else '✗'} |")
            
            mobile_load = frontend.get('mobile_load', 0)
            md.append(f"| Mobile Load Time | {mobile_load:.2f}s | < 4s | {'✓' if mobile_load < 4 else '✗'} |")
            
            g3_load = frontend.get('3g_load', 0)
            md.append(f"| 3G Load Time | {g3_load:.2f}s | < 10s | {'✓' if g3_load < 10 else '✗'} |")
            
            md.append("")
        
        # Recommendations
        md.append("## Recommendations")
        md.append("")
        
        if summary['targets_failed']:
            md.append("### Priority Issues")
            md.append("")
            
            for target in summary['targets_failed']:
                if 'AI Analysis' in target:
                    md.append("**AI Analysis Performance:**")
                    md.append("- Check GPU availability and utilization")
                    md.append("- Verify model caching is working")
                    md.append("- Consider model optimization (quantization)")
                    md.append("- Profile with cProfile to identify bottlenecks")
                    md.append("")
                
                elif 'API Response' in target:
                    md.append("**API Response Time:**")
                    md.append("- Add database indexes for slow queries")
                    md.append("- Enable Redis caching for frequent queries")
                    md.append("- Optimize N+1 queries")
                    md.append("- Use connection pooling")
                    md.append("")
                
                elif 'Page Load' in target or 'FCP' in target:
                    md.append("**Frontend Load Time:**")
                    md.append("- Run bundle analysis: `npm run build:analyze`")
                    md.append("- Optimize images (compress, WebP)")
                    md.append("- Enable code splitting for large components")
                    md.append("- Minimize render-blocking resources")
                    md.append("")
                
                elif 'Bundle Size' in target:
                    md.append("**Bundle Size:**")
                    md.append("- Analyze bundle: `npm run build:analyze`")
                    md.append("- Remove unused dependencies")
                    md.append("- Lazy load heavy components")
                    md.append("- Use dynamic imports")
                    md.append("")
        else:
            md.append("All performance targets are met! 🎉")
            md.append("")
            md.append("Continue monitoring:")
            md.append("- Run performance tests regularly")
            md.append("- Monitor production metrics")
            md.append("- Set up alerts for performance degradation")
            md.append("")
        
        # Next Steps
        md.append("## Next Steps")
        md.append("")
        md.append("1. Review failed targets and implement recommendations")
        md.append("2. Run Lighthouse audit: `cd frontend && npm run lighthouse`")
        md.append("3. Monitor production performance metrics")
        md.append("4. Set up continuous performance monitoring")
        md.append("5. Schedule regular performance testing")
        md.append("")
        
        return "\n".join(md)
    
    def save_report(self, output_path: str = "performance_report.md"):
        """Save report to file"""
        self.calculate_summary()
        markdown = self.generate_markdown()
        
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        print(f"Performance report saved to: {output_path}")
        
        # Also save JSON
        json_path = output_path.replace('.md', '.json')
        with open(json_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        print(f"JSON data saved to: {json_path}")


def main():
    """Generate sample performance report"""
    report = PerformanceReport()
    
    # Sample backend metrics
    report.add_backend_metrics({
        'ai_p95': 4.892,
        'ai_avg': 3.567,
        'ai_min': 2.134,
        'ai_max': 5.678,
        'gatekeeper_p95': 0.845,
        'lesion_detection_p95': 2.341,
        'cancer_classification_p95': 2.156,
        'api_avg': 0.342,
        'api_p95': 0.487
    })
    
    # Sample frontend metrics
    report.add_frontend_metrics({
        'page_load': 2.456,
        'fcp': 1.234,
        'lcp': 2.567,
        'cls': 0.045,
        'tbt': 234,
        'bundle_size_kb': 387,
        'mobile_load': 3.234,
        '3g_load': 8.456
    })
    
    # Generate and save report
    report.save_report('tests/performance/performance_report.md')
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE REPORT SUMMARY")
    print("="*60)
    
    summary = report.report_data['summary']
    print(f"\nOverall Status: {summary['overall_status']}")
    print(f"Performance Score: {summary['score']:.1f}%")
    
    print(f"\nTargets Met: {len(summary['targets_met'])}")
    for target in summary['targets_met']:
        print(f"  ✓ {target}")
    
    if summary['targets_failed']:
        print(f"\nTargets Failed: {len(summary['targets_failed'])}")
        for target in summary['targets_failed']:
            print(f"  ✗ {target}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
