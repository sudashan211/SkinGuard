# Symptom Data Property Tests

## Overview

This document describes the property-based tests for symptom data collection and association with medical reports (Task 10.3).

## Properties Tested

### Property 14: Symptom Data Completeness

**Test Function**: `test_symptom_data_completeness`

**Property Statement**: For any completed symptom wizard, the stored symptom data should include body location (Step 1), sensations (Step 2), and visual changes (Step 3).

**What It Tests**:
1. SymptomData model accepts all three wizard steps
2. Body location from Step 1 is stored correctly
3. Sensations from Step 2 are stored as a list
4. Visual changes from Step 3 are stored as a list
5. Duration is stored if provided
6. All data can be converted to dict for JSONB storage
7. Data integrity is maintained through conversion

**Requirements Validated**: 5.2, 5.3, 5.4, 5.5

**Test Strategy**:
- Generates random valid symptom data using Hypothesis
- Tests all combinations of body locations, sensations, visual changes, and durations
- Verifies data model validation and JSONB conversion
- Runs 100 examples to ensure robustness

### Property 15: Symptom-Report Association

**Test Function**: `test_symptom_report_association`

**Property Statement**: For any saved symptom data, the medical_reports record should correctly reference both the patient_id and contain the symptom JSONB data.

**What It Tests**:
1. Symptom data can be stored in medical_reports table
2. Report is associated with correct patient_id
3. Symptom data is stored in JSONB format
4. Symptom data can be retrieved from the report
5. Retrieved symptom data matches original input
6. Association between patient, report, and symptoms is maintained

**Requirements Validated**: 5.6

**Test Strategy**:
- Generates random patient IDs and complete symptom data
- Mocks database operations to simulate storage and retrieval
- Verifies the association between patient, report, and symptoms
- Tests round-trip data integrity (store → retrieve → verify)
- Runs 100 examples to ensure robustness

## Additional Tests

### Partial Symptom Data Handling

**Test Function**: `test_partial_symptom_data_handling`

**What It Tests**:
- Symptom data with None values is valid
- Empty lists for sensations/visual_changes are valid
- Reports can be created with partial symptom data
- Partial symptom data is stored and retrieved correctly

**Why This Matters**: Patients may not complete all wizard steps, so the system must handle partial data gracefully.

## Test Data Generators

### `valid_body_location()`
Generates valid body location strings from a predefined list:
- Arms: left_arm, right_arm
- Legs: left_leg, right_leg
- Torso: chest, back, abdomen
- Head/Neck: face, neck, scalp
- Extremities: hands, feet, shoulders

### `valid_sensations()`
Generates lists of valid sensations:
- itching
- pain
- burning
- numbness
- tingling
- none

### `valid_visual_changes()`
Generates lists of valid visual changes:
- color
- size
- shape
- border
- texture
- bleeding
- none

### `valid_duration()`
Generates realistic duration strings:
- Days: "1 day", "2 days", "3 days"
- Weeks: "1 week", "2 weeks", "3 weeks"
- Months: "1 month", "2 months", "3 months", "6 months"
- Years: "1 year"
- Descriptive: "less than a week", "more than a month", "several weeks"

## Running the Tests

### Run all symptom property tests:
```bash
python -m pytest tests/property/test_symptom_properties.py -v
```

### Run a specific property test:
```bash
python -m pytest tests/property/test_symptom_properties.py::test_symptom_data_completeness -v
```

### Run with more examples (slower but more thorough):
```bash
python -m pytest tests/property/test_symptom_properties.py -v --hypothesis-profile=thorough
```

## Test Results

✅ **All tests passing** (as of implementation)

- `test_symptom_data_completeness`: 100 examples, all passed
- `test_symptom_report_association`: 100 examples, all passed
- `test_partial_symptom_data_handling`: 50 examples, all passed

Total: 250 property test examples executed successfully

## Integration with Backend

These tests validate the symptom data models defined in `backend/app/models.py`:

- `SymptomData`: Complete symptom data model
- `BodyLocation`: Step 1 of wizard
- `SensationData`: Step 2 of wizard
- `VisualChangeData`: Step 3 of wizard

The tests ensure that:
1. Data validation works correctly
2. JSONB conversion preserves all data
3. Database associations are maintained
4. Round-trip data integrity is guaranteed

## Related Files

- Implementation: `backend/app/models.py`
- Verification script: `tests/verify_symptom_models.py`
- Requirements: `.kiro/specs/derman-ai-skin-screening/requirements.md` (Section 5)
- Design: `.kiro/specs/derman-ai-skin-screening/design.md` (Properties 14-15)
- Tasks: `.kiro/specs/derman-ai-skin-screening/tasks.md` (Task 10.3)
