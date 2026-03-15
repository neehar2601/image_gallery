# Complete S3 Public → Private Migration Guide with CloudFront

**Project**: Felicity Image Gallery  
**Date**: March 15, 2026  
**CloudFront**: `dqp3gxaurv69w.cloudfront.net`  
**S3 Bucket**: `felicity2025`  
**API Gateway**: `e87ewu7ddb.execute-api.ap-south-1.amazonaws.com/images`  
**Status**: ✅ LIVE & WORKING

---

## Executive Summary

**Migrated public S3 bucket to private using CloudFront OAC + API Gateway behaviors while keeping 100% same URLs and functionality.**

**Key Results**:
- S3 bucket **private** (Block Public Access = ALL ON)
- Same URLs work (`dqp3gxaurv69w.cloudfront.net`)
- Zero frontend changes required after Lambda/HTML updates
- CDN caching + global edge delivery

## Before (Public S3 - ❌ BROKEN)

```
Browser
  ↓
Public S3: felicity2025.s3.amazonaws.com/index.html
  ↓ Lambda returns S3 URLs
["https://felicity2025.s3.ap-south-1.amazonaws.com/photo.jpg"] ❌ AccessDenied
```

**Problems**:
- Public bucket (security risk)
- Direct S3 URLs fail after blocking public access
- No CDN caching
- Regional latency

## After (Private S3 + CloudFront - ✅ WORKING)

```
Browser
  ↓ CDN Edge
CloudFront dqp3gxaurv69w.cloudfront.net
  ├─ /* → S3 OAC → felicity2025 (private)
  │     ↓
  │  index.html + photo.jpg
  └─ /images → API Gateway → Lambda → ["photo.jpg"]
```

---

## Complete Migration Steps

### Phase 1: S3 Hardening

#### 1.1 Bucket Policy (OAC)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowCloudFrontServicePrincipal",
    "Effect": "Allow",
    "Principal": {"Service": "cloudfront.amazonaws.com"},
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": ["arn:aws:s3:::felicity2025", "arn:aws:s3:::felicity2025/*"],
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::826021122371:distribution/E2QYSGNDZCKAXG"
      }
    }
  }]
}
```

#### 1.2 S3 Settings
```
✅ Block ALL public access
✅ Object Ownership = Bucket owner enforced
❌ Disable Static Website Hosting
```

### Phase 2: CloudFront Configuration

#### 2.1 Origins
| Name | Domain | Origin Path | Type |
|------|--------|-------------|------|
| S3 | `felicity2025.s3.amazonaws.com` | BLANK | S3 OAC |
| API | `e87ewu7ddb.execute-api.ap-south-1.amazonaws.com` | BLANK | Custom |

#### 2.2 Behaviors (Order Critical!)
| Priority | Path Pattern | Origin | Cache Policy | Notes |
|----------|--------------|--------|--------------|-------|
| **1** | `/images` | API Gateway | **CachingDisabled** | API calls |
| **2** | `/*` (Default) | S3 OAC | Managed-CachingOptimized | Static files |

### Phase 3: Lambda Rewrite

**Before** (❌ Direct S3 URLs):
```python
images = [f"https://felicity2025.s3.ap-south-1.amazonaws.com/{obj['Key']}"...]
```

**After** (✅ S3 Keys):
```python
images = [obj['Key'] for obj in response["Contents"] 
          if obj['Key'].lower().endswith(('.jpg','.jpeg','.png','.gif','.webp'))]
```

### Phase 4: HTML Frontend

**Before** (❌):
```javascript
const apiUrl = "https://e87ewu7ddb.../images";
img.src = url; // Direct S3
```

**After** (✅):
```javascript
const apiUrl = '/images';
img.src = window.location.origin + '/' + key; // CloudFront URLs
```

---

## Debug Journey & Issues Solved

### Issue 1: S3 AccessDenied (Initial)
```
Error: <Code>AccessDenied</Code>
```
**Root Cause**: Missing `s3:ListBucket` in OAC policy  
**Fix**: Added both `s3:GetObject` + `s3:ListBucket`

### Issue 2: Images Not Loading After Public Block
```
<img src="https://felicity2025.s3..."> → 403
```
**Root Cause**: Direct S3 URLs in Lambda response  
**Fix**: Lambda returns keys → Frontend prepends CloudFront domain

### Issue 3: CloudFront `/images` 404
```
https://cloudfront.net/images → 404 (S3 "NoSuchKey")
```
**Root Cause**: No `/images` behavior → Default S3 origin  
**Fix**: Created `/images` behavior → API Gateway origin

### Issue 4: API Gateway "Not Found" (Double Path)
```
CloudFront /images → API-GW /images/images → 404
```
**Root Cause**: Origin path `/images` + behavior `/images`  
**Fix**: Origin path = **BLANK**

### Issue 5: `/api/*` Behavior 404
```
CloudFront /api/images → API-GW /api/images → 404
```
**Root Cause**: Behavior strips `/api/*` → `images`, API expects `/images`  
**Fix**: Origin path = `/images` (rewrites `images` → `/images`)

### Issue 6: Cache Stale Content
```
Images show old broken versions
```
**Fix**: Invalidation `/*`

---

## Path Pattern + Origin Path Formula

```
Origin receives = (Viewer URL - Behavior Pattern) + Origin Path
```

**Examples**:
```
Viewer: /api/images, Behavior: /api/*, Origin path: /images
→ Strip /api → images + /images → /images ✅

Viewer: /photo.jpg, Behavior: /*, Origin path: BLANK  
→ photo.jpg + BLANK → photo.jpg ✅

Viewer: /v1/images, Behavior: /v1/*, Origin path: /images
→ Strip /v1 → images + /images → /images ✅
```

## Final Working URLs

```
✅ https://dqp3gxaurv69w.cloudfront.net/ → index.html (S3)
✅ https://dqp3gxaurv69w.cloudfront.net/images → ["photo.jpg"] (Lambda)
✅ https://dqp3gxaurv69w.cloudfront.net/photo.jpg → Image (S3 OAC)
❌ https://felicity2025.s3.amazonaws.com/photo.jpg → AccessDenied ✅
```

## Architecture Diagram

```
┌─ Browser ──────────────────────┐
│ https://dqp3gxaurv69w.cf.net/  │
└──────────┬─────────────────────┘
           │
    ┌──────▼──────┐
    │ CloudFront  │
    │ Behaviors:  │
    │ /images     │─── API GW ── Lambda ── ["photo.jpg"]
    │ /* (S3 OAC) │
    │              │
    └───▲──────────┘
        │ OAC
        ▼
  Private S3
felicity2025
├── index.html
└── photo.jpg
```

## Pro Tips & Gotchas

```
1. **Behavior Order = Priority**: /api/* MUST be above /*
2. **Origin Path NEVER regex**: Only literal prefixes
3. **S3 OAC requires ListBucket**: For directory listings
4. **API Gateway stage prefix**: /PROD/images vs /images
5. **Cache per behavior**: /api/* cache ≠ /* cache
6. **Invalidate /* after changes**: Always
```

## Monitoring & Costs

```
✅ CloudWatch: CloudFront + API Gateway + Lambda logs
✅ Cost: ~$0.085/GB + $0.01/10k requests (Free Tier eligible)
✅ S3: $0.023/GB storage + OAC = FREE
```

**Migration SUCCESS!** Private S3 + CDN + Zero-downtime.[web:1][web:28][web:36]
