# Collapsible Patient Reports Feature

## Overview
Added a collapsible/expandable feature to the Pending Reports view so that patient reports are hidden by default and only shown when the user clicks on the patient name.

## Changes Made

### 1. Added State Management
```typescript
const [expandedPatients, setExpandedPatients] = useState<Set<string>>(new Set())
```
- Tracks which patients have their reports expanded
- Uses a Set for efficient lookup and toggle operations

### 2. Added Toggle Function
```typescript
const togglePatient = (patientId: string) => {
  setExpandedPatients(prev => {
    const newSet = new Set(prev)
    if (newSet.has(patientId)) {
      newSet.delete(patientId)
    } else {
      newSet.add(patientId)
    }
    return newSet
  })
}
```
- Toggles the expanded state for a specific patient
- Adds patient to set if collapsed, removes if expanded

### 3. Added Expand/Collapse Icons
```typescript
import { AlertCircle, Clock, User, MapPin, ChevronDown, ChevronRight } from 'lucide-react'
```
- **ChevronDown**: Shows when patient reports are expanded
- **ChevronRight**: Shows when patient reports are collapsed

### 4. Made Patient Header Clickable
```typescript
<div 
  className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
  onClick={() => togglePatient(patientId)}
>
```
- Entire patient header is now clickable
- Hover effect provides visual feedback
- Smooth transition on hover

### 5. Conditional Report Rendering
```typescript
{isExpanded && (
  <div className="border-t border-gray-200 p-4 bg-gray-50">
    <div className="space-y-3">
      {group.reports.map((report) => {
        // ... report cards
      })}
    </div>
  </div>
)}
```
- Reports only render when `isExpanded` is true
- Improves performance by not rendering hidden content
- Cleaner UI with less visual clutter

### 6. Prevented Event Bubbling
```typescript
onClick={(e) => {
  e.stopPropagation() // Prevent triggering parent click
  setSelectedReportId(report.id)
}}
```
- Clicking on a report card opens the detail modal
- Doesn't trigger the patient toggle
- Proper event handling hierarchy

## User Experience

### Default State
- All patient sections are **collapsed** by default
- Shows patient summary information:
  - Patient name with User icon
  - Age, Skin Type, Email
  - Number of reports
  - "HAS URGENT CASES" badge (if applicable)
- ChevronRight icon indicates section can be expanded

### Expanded State
- Click on patient name/header to expand
- ChevronDown icon indicates section is expanded
- Shows all reports for that patient
- Reports are sorted: urgent first, then by date
- Each report card is clickable to view details

### Visual Indicators
- **Hover Effect**: Patient header background changes to gray-50 on hover
- **Cursor**: Changes to pointer on patient header
- **Icons**: Chevron direction indicates current state
- **Urgent Badge**: Red badge shows if patient has urgent cases
- **Report Count**: Shows number of reports for each patient

## Benefits

### 1. **Cleaner Interface**
- Less visual clutter
- Easier to scan through patients
- Focus on patient-level information first

### 2. **Better Performance**
- Reports only rendered when needed
- Faster initial page load
- Reduced DOM elements

### 3. **Improved Workflow**
- Quick overview of all patients
- Expand only patients of interest
- Urgent cases still clearly marked
- Easy to collapse after reviewing

### 4. **Progressive Disclosure**
- Show summary first, details on demand
- Reduces cognitive load
- Better information hierarchy

## Technical Details

### State Management
- Uses React `useState` with Set data structure
- Efficient O(1) lookup and toggle operations
- Immutable state updates with new Set instances

### Event Handling
- Parent click: Toggle patient expansion
- Child click (report card): Open detail modal with `e.stopPropagation()`
- Proper event bubbling control

### Styling
- Smooth transitions with Tailwind CSS
- Hover states for better UX
- Consistent spacing and borders
- Responsive design maintained

## Testing

### Manual Testing Steps
1. Navigate to Hospital/Clinic Dashboard → Pending Reports
2. Verify all patients are collapsed by default
3. Click on a patient name to expand
4. Verify reports appear with smooth transition
5. Verify ChevronRight changes to ChevronDown
6. Click on patient name again to collapse
7. Verify reports hide and ChevronDown changes to ChevronRight
8. Click on a report card to open detail modal
9. Verify modal opens without toggling patient expansion
10. Test with multiple patients (expand/collapse different ones)

### Expected Behavior
✅ All patients collapsed on initial load  
✅ Click patient header to toggle expansion  
✅ Chevron icon changes based on state  
✅ Hover effect on patient header  
✅ Reports only visible when expanded  
✅ Report cards clickable without affecting parent  
✅ Urgent badges still visible when collapsed  
✅ Report count visible when collapsed  

## Files Modified
- `frontend/src/components/doctor/PendingReportsView.tsx`
  - Added `expandedPatients` state
  - Added `togglePatient` function
  - Imported ChevronDown and ChevronRight icons
  - Made patient header clickable
  - Added conditional rendering for reports
  - Added event.stopPropagation() to report cards

## Status
✅ **COMPLETED** - Feature is fully implemented and working

## Future Enhancements (Optional)
1. Add "Expand All" / "Collapse All" buttons
2. Remember expanded state in localStorage
3. Auto-expand patients with urgent cases
4. Add keyboard navigation (Arrow keys, Enter)
5. Add animation for expand/collapse transition
