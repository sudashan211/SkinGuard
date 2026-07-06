# Image Display Fix

## Issue
Images were not displaying in the frontend application (patient reports, doctor dashboard, comparison view).

## Root Cause
The frontend components were using `image_url` directly from the API response without prepending the backend API URL.

### Example:
- Database stores: `/uploads/user-id/image.jpg`
- Frontend was requesting: `/uploads/user-id/image.jpg` (relative to frontend URL)
- Should request: `http://localhost:8001/uploads/user-id/image.jpg` (backend URL)

## Solution
Updated all frontend components to prepend `import.meta.env.VITE_API_URL` to image URLs.

### Files Fixed:
1. `frontend/src/components/patient/ComparisonView.tsx`
   - Fixed both report1 and report2 image URLs
   
2. `frontend/src/components/patient/ReportHistory.tsx`
   - Fixed thumbnail/image URL in report list
   
3. `frontend/src/components/doctor/PendingReportsView.tsx`
   - Fixed thumbnail/image URL in pending reports
   
4. `frontend/src/components/doctor/ReportDetailView.tsx`
   - Fixed image URL in TouchImageViewer
   
5. `frontend/src/pages/ReportDetailPage.tsx`
   - Already fixed (was done earlier)

### Code Pattern:
```typescript
// Before (WRONG)
<img src={report.image_url} alt="..." />

// After (CORRECT)
<img src={`${import.meta.env.VITE_API_URL}${report.image_url}`} alt="..." />
```

## Backend Configuration
The backend serves images from the `uploads/` directory:
- Location: `backend/uploads/`
- Mounted at: `/uploads` endpoint
- Configuration: `backend/app/main.py` (lines 86-94)

```python
if use_local_storage:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

## Image URL Structure
- Database: `/uploads/{user_id}/{image_filename}.jpg`
- Frontend constructs: `http://localhost:8001/uploads/{user_id}/{image_filename}.jpg`
- Backend serves from: `backend/uploads/{user_id}/{image_filename}.jpg`

## Testing
After fix, images should display in:
1. Patient dashboard - report history
2. Patient report detail page
3. Patient comparison view
4. Doctor pending reports
5. Doctor report detail view

## Environment Variable
Ensure `frontend/.env` has:
```env
VITE_API_URL=http://localhost:8001
```

## Troubleshooting
If images still don't display:
1. Check browser console (F12) for 404 errors
2. Verify backend is running on port 8001
3. Check `backend/uploads/` directory has image files
4. Hard refresh browser (Ctrl+Shift+R)
5. Verify VITE_API_URL is set correctly

---

**Fixed**: April 3, 2026  
**Status**: ✅ Resolved
