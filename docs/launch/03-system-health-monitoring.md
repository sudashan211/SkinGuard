# SkinGuard System Health Monitoring Dashboard Guide

## Overview

This guide describes the monitoring infrastructure, key metrics, dashboards, and alerting for SkinGuard production environment. Use this guide to understand system health and identify issues quickly.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Sentry     │  │  CloudWatch  │  │   Datadog    │     │
│  │ Error Track  │  │   Metrics    │  │   APM        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Supabase    │  │    Redis     │  │   Custom     │     │
│  │  Dashboard   │  │   Monitor    │  │   Metrics    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Primary Dashboards

### 1. System Overview Dashboard

**URL**: `https://monitoring.skinguard.com/overview`

**Purpose**: High-level system health at a glance

**Key Metrics**:

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Uptime | 99.9% | <99.5% | <99% |
| Error Rate | <0.5% | >1% | >5% |
| API Response Time (p95) | <2s | >3s | >5s |
| AI Inference Time (p95) | <5s | >7s | >10s |
| Active Users (5min) | - | - | 0 (during peak) |
| Database Connections | <80% | >85% | >95% |
| Memory Usage | <70% | >80% | >90% |
| CPU Usage | <60% | >75% | >90% |

**Widgets**:
1. **System Status**: Green/Yellow/Red indicator
2. **Request Rate**: Requests per minute (line chart)
3. **Error Rate**: Percentage over time 