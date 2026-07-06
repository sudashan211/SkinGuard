# SkinGuard - Doctor/Dermatologist Stakeholder Questionnaire

## Introduction

Thank you for taking the time to evaluate SkinGuard, an AI-powered skin cancer screening application. Your feedback as a medical professional is invaluable in ensuring this tool meets clinical needs and provides real value to both healthcare providers and patients.

**Estimated Time:** 15-20 minutes

---

## Section 1: Background Information

### 1.1 Professional Background
- **Name:** ___________________________
- **Specialization:** ___________________________
- **Years of Experience:** ___________________________
- **Current Practice:** 
  - [ ] Private Clinic
  - [ ] Hospital
  - [ ] Academic Medical Center
  - [ ] Other: ___________________________

### 1.2 Current Practice
- **Average number of skin cancer screenings per week:** ___________________________
- **Do you currently use any digital tools for skin cancer screening?**
  - [ ] Yes (Please specify: ___________________________)
  - [ ] No

---

## Section 2: AI Model & Diagnostic Accuracy

### 2.1 AI Model Performance
The SkinGuard app uses a Vision Transformer (ViT) model with **84% accuracy** on the HAM10000 dataset for classifying 7 types of skin lesions:
- Melanoma
- Basal Cell Carcinoma
- Actinic Keratoses
- Melanocytic Nevi (moles)
- Benign Keratosis
- Vascular Lesions
- Dermatofibroma

**Questions:**

1. **Is 84% accuracy acceptable for a screening tool (not diagnostic)?**
   - [ ] Yes, acceptable for screening
   - [ ] No, needs to be higher
   - [ ] Unsure
   - **Comments:** ___________________________

2. **What minimum accuracy would you consider acceptable for a screening tool?**
   - [ ] 70-75%
   - [ ] 75-80%
   - [ ] 80-85%
   - [ ] 85-90%
   - [ ] 90%+
   - **Reasoning:** ___________________________

3. **The model has high confidence (95.29% average). Is this important to you?**
   - [ ] Very important
   - [ ] Somewhat important
   - [ ] Not important
   - **Why:** ___________________________

4. **The model tends to over-predict melanoma (false positives). Is this acceptable?**
   - [ ] Yes, better safe than sorry
   - [ ] No, too many false alarms
   - [ ] Depends on the rate
   - **Comments:** ___________________________

5. **Would you trust AI predictions to help prioritize which patients to see first?**
   - [ ] Yes, definitely
   - [ ] Yes, with caution
   - [ ] No, I prefer my own judgment
   - **Explain:** ___________________________

---

## Section 3: Hospital/Clinic Dashboard

### 3.1 Pending Reports View
The app shows pending patient reports grouped by patient, with collapsible sections.

**Questions:**

6. **Is the collapsible patient grouping helpful for organizing reports?**
   - [ ] Very helpful
   - [ ] Somewhat helpful
   - [ ] Not helpful
   - [ ] Prefer a different layout
   - **Suggestions:** ___________________________

7. **What information is most important to see at a glance for each patient?**
   - [ ] Patient name
   - [ ] Age and skin type
   - [ ] Number of reports
   - [ ] Urgent case indicator
   - [ ] Date of report
   - [ ] Other: ___________________________

8. **How would you prefer reports to be sorted?**
   - [ ] By urgency (urgent first)
   - [ ] By date (newest first)
   - [ ] By patient name (alphabetical)
   - [ ] By number of reports
   - [ ] Other: ___________________________

9. **Is the risk level categorization (Urgent, High, Medium, Low) clear and useful?**
   - [ ] Yes, very clear
   - [ ] Somewhat clear
   - [ ] Confusing
   - [ ] Would prefer different categories
   - **Suggestions:** ___________________________

---

## Section 4: Patient Privacy & Appointments

### 4.1 Privacy Protection
Patient details (name, email, medical reports) are hidden until the hospital confirms the appointment.

**Questions:**

10. **Is this privacy approach appropriate?**
    - [ ] Yes, good for patient privacy
    - [ ] No, I need to see details before confirming
    - [ ] Depends on the situation
    - **Reasoning:** ___________________________

11. **What information would you need to see BEFORE confirming an appointment?**
    - [ ] Patient name
    - [ ] Age and skin type
    - [ ] Brief symptom description
    - [ ] AI risk level
    - [ ] Image preview (blurred)
    - [ ] Nothing, current approach is fine
    - [ ] Other: ___________________________

12. **After confirming an appointment, is the revealed information sufficient?**
    - [ ] Yes, all necessary information is shown
    - [ ] No, missing: ___________________________
    - [ ] Too much information
    - **Comments:** ___________________________

---

## Section 5: Patient Health Profiles

### 5.1 Profile Information
Clicking a patient's name shows their health profile with:
- Basic info (name, email, age, skin type)
- Family history
- Recent skin analysis reports (last 10)

**Questions:**

13. **Is the patient health profile information adequate for clinical decision-making?**
    - [ ] Yes, sufficient
    - [ ] No, needs more information
    - [ ] Too much information
    - **What's missing:** ___________________________

14. **What additional patient information would be helpful?**
    - [ ] Medical history (other conditions)
    - [ ] Current medications
    - [ ] Previous treatments
    - [ ] Allergies
    - [ ] Sun exposure history
    - [ ] Previous biopsies/diagnoses
    - [ ] Other: ___________________________

15. **Is showing the last 10 reports sufficient, or would you prefer more/less?**
    - [ ] 10 is perfect
    - [ ] Show more: _____ reports
    - [ ] Show less: _____ reports
    - [ ] Show all reports
    - **Reasoning:** ___________________________

---

## Section 6: Workflow & Usability

### 6.1 Clinical Workflow

16. **How well does the app fit into your current workflow?**
    - [ ] Fits perfectly
    - [ ] Fits with minor adjustments
    - [ ] Requires significant workflow changes
    - [ ] Doesn't fit at all
    - **Explain:** ___________________________

17. **What is the most time-consuming part of reviewing patient reports?**
    - [ ] Finding the right patient
    - [ ] Reviewing AI predictions
    - [ ] Checking patient history
    - [ ] Making clinical decisions
    - [ ] Documenting findings
    - [ ] Other: ___________________________

18. **Would you use this app to:**
    - [ ] Screen all patients
    - [ ] Only high-risk patients
    - [ ] Only patients who request it
    - [ ] As a second opinion
    - [ ] Not sure yet
    - **Explain:** ___________________________

19. **How important is it to see the AI's confidence level for each prediction?**
    - [ ] Very important
    - [ ] Somewhat important
    - [ ] Not important
    - **Why:** ___________________________

20. **Would you like to see the AI's reasoning (e.g., which features it detected)?**
    - [ ] Yes, very helpful
    - [ ] Maybe, if it's simple
    - [ ] No, just the result is fine
    - **Comments:** ___________________________

---

## Section 7: Hospital Finder Feature

### 7.1 Google Maps Integration
Patients can find nearby hospitals/clinics using Google Maps, sorted by rating and distance.

**Questions:**

21. **Is it appropriate for patients to book appointments directly through the app?**
    - [ ] Yes, very convenient
    - [ ] Yes, but with some concerns
    - [ ] No, prefer traditional booking
    - **Concerns/Comments:** ___________________________

22. **Should the app show:**
    - [ ] Only dermatology specialists
    - [ ] Both specialists and general hospitals
    - [ ] All hospitals (current approach)
    - [ ] Other: ___________________________

23. **What information about your hospital/clinic should be displayed to patients?**
    - [ ] Name and location
    - [ ] Ratings and reviews
    - [ ] Operating hours
    - [ ] Specializations
    - [ ] Wait times
    - [ ] Insurance accepted
    - [ ] Other: ___________________________

---

## Section 8: Clinical Decision Support

### 8.1 AI Recommendations

24. **Would you like the app to provide treatment recommendations?**
    - [ ] Yes, evidence-based suggestions
    - [ ] Yes, but only general guidance
    - [ ] No, I make my own decisions
    - [ ] Unsure
    - **Comments:** ___________________________

25. **Should the app suggest follow-up intervals based on risk level?**
    - [ ] Yes, very helpful
    - [ ] Yes, but as suggestions only
    - [ ] No, I determine follow-ups
    - **Reasoning:** ___________________________

26. **Would you like the app to flag cases that need urgent attention?**
    - [ ] Yes, with notifications
    - [ ] Yes, but only visual indicators
    - [ ] No, I review all cases
    - **Preferences:** ___________________________

27. **Should the app compare current images with previous reports automatically?**
    - [ ] Yes, very useful for tracking changes
    - [ ] Maybe, if accurate
    - [ ] No, I do this manually
    - **Comments:** ___________________________

---

## Section 9: Trust & Reliability

### 9.1 Clinical Trust

28. **How much do you trust AI for skin cancer screening?**
    - [ ] Completely trust
    - [ ] Trust with verification
    - [ ] Somewhat skeptical
    - [ ] Don't trust at all
    - **Explain:** ___________________________

29. **What would increase your trust in the AI model?**
    - [ ] Higher accuracy
    - [ ] Clinical validation studies
    - [ ] Transparency in how it works
    - [ ] Peer-reviewed publications
    - [ ] Real-world performance data
    - [ ] Other: ___________________________

30. **Would you recommend this app to your patients?**
    - [ ] Yes, definitely
    - [ ] Yes, with reservations
    - [ ] No, not yet
    - [ ] Never
    - **Why/Why not:** ___________________________

31. **What are your main concerns about using AI in dermatology?**
    - [ ] Accuracy/reliability
    - [ ] Legal liability
    - [ ] Patient safety
    - [ ] Over-reliance on technology
    - [ ] Data privacy
    - [ ] Cost
    - [ ] Other: ___________________________

---

## Section 10: Features & Improvements

### 10.1 Missing Features

32. **What features are missing that would make this app more useful?**
    - [ ] Teledermatology/video consultations
    - [ ] Integration with EHR systems
    - [ ] Prescription management
    - [ ] Patient education materials
    - [ ] Billing/insurance integration
    - [ ] Multi-language support
    - [ ] Other: ___________________________

33. **Would you like to add notes or annotations to patient reports?**
    - [ ] Yes, essential
    - [ ] Yes, would be helpful
    - [ ] Not necessary
    - **What kind of notes:** ___________________________

34. **Should patients be able to message you through the app?**
    - [ ] Yes, for follow-up questions
    - [ ] Yes, but with limitations
    - [ ] No, prefer other channels
    - **Concerns:** ___________________________

35. **Would you like analytics/reports on your practice (e.g., case volume, outcomes)?**
    - [ ] Yes, very useful
    - [ ] Maybe, depends on what's shown
    - [ ] No, not interested
    - **What metrics:** ___________________________

---

## Section 11: User Experience

### 11.1 Interface & Design

36. **How would you rate the overall user interface?**
    - [ ] Excellent
    - [ ] Good
    - [ ] Average
    - [ ] Poor
    - **Suggestions:** ___________________________

37. **Is the dashboard easy to navigate?**
    - [ ] Very easy
    - [ ] Somewhat easy
    - [ ] Confusing
    - [ ] Very confusing
    - **What's confusing:** ___________________________

38. **Are the colors and visual indicators (red for urgent, etc.) appropriate?**
    - [ ] Yes, very clear
    - [ ] Mostly clear
    - [ ] Could be improved
    - **Suggestions:** ___________________________

39. **Is the text size and readability adequate?**
    - [ ] Perfect
    - [ ] Too small
    - [ ] Too large
    - [ ] Inconsistent
    - **Comments:** ___________________________

---

## Section 12: Implementation & Adoption

### 12.1 Practical Considerations

40. **How likely are you to use this app in your practice?**
    - [ ] Very likely
    - [ ] Somewhat likely
    - [ ] Unlikely
    - [ ] Very unlikely
    - **Why:** ___________________________

41. **What would be the biggest barrier to adopting this app?**
    - [ ] Cost
    - [ ] Training staff
    - [ ] Integration with existing systems
    - [ ] Regulatory/legal concerns
    - [ ] Patient acceptance
    - [ ] Time constraints
    - [ ] Other: ___________________________

42. **How much training would you need to use this app effectively?**
    - [ ] None, it's intuitive
    - [ ] 15-30 minutes
    - [ ] 1-2 hours
    - [ ] Half day
    - [ ] Full day
    - **Comments:** ___________________________

43. **Would you want your staff (nurses, assistants) to use this app?**
    - [ ] Yes, for initial screening
    - [ ] Yes, for data entry
    - [ ] No, doctors only
    - [ ] Unsure
    - **Reasoning:** ___________________________

---

## Section 13: Pricing & Value

### 13.1 Business Model

44. **What pricing model would be most acceptable?**
    - [ ] Free (ad-supported)
    - [ ] Monthly subscription per doctor
    - [ ] Per-patient fee
    - [ ] One-time license fee
    - [ ] Institutional license
    - [ ] Other: ___________________________

45. **What would you consider a fair price for this app?**
    - [ ] Free
    - [ ] $10-50/month
    - [ ] $50-100/month
    - [ ] $100-200/month
    - [ ] $200+/month
    - [ ] Depends on features
    - **Comments:** ___________________________

46. **Would this app save you time in your practice?**
    - [ ] Yes, significant time savings
    - [ ] Yes, some time savings
    - [ ] No time savings
    - [ ] Might increase time
    - **Estimate:** _____ minutes/hours per week

47. **Would this app improve patient outcomes?**
    - [ ] Yes, definitely
    - [ ] Possibly
    - [ ] Unlikely
    - [ ] Too early to tell
    - **How:** ___________________________

---

## Section 14: Regulatory & Legal

### 14.1 Compliance

48. **Are you concerned about liability when using AI-assisted diagnosis?**
    - [ ] Very concerned
    - [ ] Somewhat concerned
    - [ ] Not concerned
    - **Explain:** ___________________________

49. **Should the app have a disclaimer that it's a screening tool, not diagnostic?**
    - [ ] Yes, absolutely necessary
    - [ ] Yes, but make it subtle
    - [ ] Not necessary
    - **Wording suggestions:** ___________________________

50. **What regulatory approvals would you want to see before using this app?**
    - [ ] FDA clearance
    - [ ] CE marking (Europe)
    - [ ] Clinical validation studies
    - [ ] Peer-reviewed publications
    - [ ] Professional society endorsement
    - [ ] Other: ___________________________

---

## Section 15: Open Feedback

### 15.1 General Comments

51. **What do you like most about SkinGuard?**

    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________

52. **What do you like least about SkinGuard?**

    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________

53. **What is the ONE thing that would make you definitely use this app?**

    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________

54. **What is the ONE thing that would prevent you from using this app?**

    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________

55. **Any other comments, suggestions, or concerns?**

    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________
    ___________________________________________________________________________

---

## Section 16: Follow-Up

### 16.1 Future Engagement

56. **Would you be interested in participating in a pilot study?**
    - [ ] Yes
    - [ ] Maybe
    - [ ] No

57. **Can we contact you for follow-up questions?**
    - [ ] Yes
    - [ ] No
    
    **Email:** ___________________________
    **Phone:** ___________________________

58. **Would you like to receive updates about SkinGuard development?**
    - [ ] Yes
    - [ ] No

---

## Thank You!

Thank you for taking the time to complete this questionnaire. Your feedback is invaluable in making SkinGuard a useful tool for dermatologists and improving patient care.

**Date Completed:** ___________________________

**Signature:** ___________________________

---

## For Internal Use Only

**Interviewer:** ___________________________
**Date:** ___________________________
**Notes:** ___________________________

