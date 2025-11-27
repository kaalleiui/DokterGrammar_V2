# End-to-End Testing Checklist
**Task**: Task 2.1 - End-to-End Testing  
**Date**: 2024-11-27  
**Status**: 🔄 IN PROGRESS

---

## Test Scenarios

### 1. New User Flow (First Time User)
**Priority**: 🔴 CRITICAL

#### 1.1 Splash Screen → Onboarding
- [ ] App opens and shows splash screen
- [ ] Splash screen displays logo and tagline
- [ ] Database initializes correctly
- [ ] App detects no user profile exists
- [ ] App navigates to onboarding screen

#### 1.2 Onboarding → Profile Input
- [ ] Onboarding screen displays correctly
- [ ] "Mulai" button works
- [ ] Profile input screen loads
- [ ] All fields are visible:
  - [ ] Nickname input field
  - [ ] Goal dropdown/selection
  - [ ] Interests multi-select chips
- [ ] Can enter nickname
- [ ] Can select goal
- [ ] Can select multiple interests
- [ ] "Selanjutnya" button enables after required fields filled
- [ ] Navigation to placement intro works

#### 1.3 Placement Test Intro
- [ ] Placement intro screen displays
- [ ] Shows explanation of 50 questions
- [ ] Shows estimated duration
- [ ] Shows question types info
- [ ] "Mulai 50 Soal" button works
- [ ] Back button works (if present)

#### 1.4 Placement Test (50 Questions)
- [ ] Test screen loads with first question
- [ ] Progress indicator shows "1 / 50"
- [ ] Question displays correctly
- [ ] Choices display correctly (if multiple choice)
- [ ] Can select an answer
- [ ] "Next" button works
- [ ] Progress updates correctly
- [ ] Can navigate to previous questions
- [ ] All 50 questions load correctly
- [ ] No crashes during test
- [ ] Timer works (if implemented)
- [ ] Can complete all 50 questions

#### 1.5 Test Results Screen
- [ ] Results screen loads after completing test
- [ ] Score displays correctly (not 0%)
- [ ] Level calculation is correct
- [ ] Topic breakdown shows correctly
- [ ] Pie chart or bar chart displays (if implemented)
- [ ] Weakest areas are highlighted
- [ ] "See Explanations" button works
- [ ] "Start Personalized Training" button works

#### 1.6 Explanation Screen
- [ ] Explanation screen loads
- [ ] Shows question, correct answer, user answer
- [ ] Explanation text displays correctly
- [ ] Example sentence shows
- [ ] Can navigate between questions
- [ ] Can go back to results

#### 1.7 Home Screen (After Placement)
- [ ] Home screen loads
- [ ] Shows user level badge
- [ ] Shows streak (if applicable)
- [ ] Shows weakest areas
- [ ] All main action buttons visible:
  - [ ] Custom Test
  - [ ] Daily Test
  - [ ] Reassessment
  - [ ] Review
- [ ] Navigation works

---

### 2. Returning User Flow
**Priority**: 🔴 CRITICAL

#### 2.1 App Startup (Existing User)
- [ ] App opens
- [ ] Splash screen loads
- [ ] Detects existing user profile
- [ ] Navigates directly to Home screen
- [ ] No onboarding shown

#### 2.2 Home Screen Display
- [ ] User name displays correctly
- [ ] Current level shows
- [ ] Streak count shows (if applicable)
- [ ] Category cards display (12 topics)
- [ ] Weakest areas section shows
- [ ] Recent test results show (if any)

#### 2.3 Custom Test Flow
- [ ] Click "Custom Test" button
- [ ] Custom test config screen loads
- [ ] Can select number of questions
- [ ] Can select/deselect topics
- [ ] Topic distribution preview shows
- [ ] "Start" button works
- [ ] Test screen loads with selected questions
- [ ] Questions are adaptive (favor weak topics)
- [ ] Can complete test
- [ ] Results show correctly

#### 2.4 Daily Test Flow
- [ ] Click "Daily Test" button
- [ ] Daily test starts (5-10 questions)
- [ ] Questions are quick and mixed topics
- [ ] Timer works (if implemented)
- [ ] Can complete daily test
- [ ] Results show correctly
- [ ] Streak updates (if applicable)

#### 2.5 Reassessment Flow
- [ ] Click "Reassessment" button
- [ ] Reassessment options show (Full/Targeted)
- [ ] Can select reassessment type
- [ ] Test starts with appropriate questions
- [ ] Can complete reassessment
- [ ] Level up prompt shows (if threshold met)
- [ ] Level updates correctly

---

### 3. Navigation Flow
**Priority**: 🟡 HIGH

#### 3.1 Bottom Navigation Bar
- [ ] All 4 tabs visible:
  - [ ] Home
  - [ ] Progress
  - [ ] Review
  - [ ] Profile
- [ ] Current screen is highlighted
- [ ] Can navigate between all tabs
- [ ] Navigation is smooth (with transitions)

#### 3.2 Back Button Navigation
- [ ] Back button works on all screens
- [ ] Back button in AppBar works
- [ ] Android back button works (if applicable)
- [ ] Navigation stack is correct
- [ ] No navigation loops

#### 3.3 Screen Transitions
- [ ] All transitions are smooth
- [ ] No jarring screen changes
- [ ] Fade/slide animations work
- [ ] No white flashes

---

### 4. Error Scenarios
**Priority**: 🟡 HIGH

#### 4.1 Empty Database
- [ ] App handles empty database gracefully
- [ ] Shows appropriate error message
- [ ] Can recover (reinitialize database)
- [ ] No crashes

#### 4.2 Invalid Question Data
- [ ] App handles invalid questions gracefully
- [ ] Skips invalid questions
- [ ] Shows warning (in debug mode)
- [ ] Test can still complete

#### 4.3 Network Offline (Should Work Offline)
- [ ] App works completely offline
- [ ] No network requests made
- [ ] All features work offline
- [ ] No "network error" messages

#### 4.4 Low Storage Space
- [ ] App handles low storage gracefully
- [ ] Shows appropriate message
- [ ] Can still function with limited storage
- [ ] Backup/restore works

#### 4.5 Invalid User Input
- [ ] Empty nickname shows error
- [ ] Invalid goal selection handled
- [ ] No crashes on invalid input
- [ ] Error messages are clear

---

### 5. Edge Cases
**Priority**: 🟢 MEDIUM

#### 5.1 User with No Test History
- [ ] Home screen shows "Belum melakukan test"
- [ ] No errors in progress screen
- [ ] Can start first test

#### 5.2 User with 100% Score
- [ ] Results show 100% correctly
- [ ] Level calculation is correct
- [ ] No division by zero errors
- [ ] Can still take more tests

#### 5.3 User with 0% Score
- [ ] Results show 0% correctly
- [ ] Level shows as beginner
- [ ] Weakest areas show all topics
- [ ] Can retake test

#### 5.4 Very Long Names/Interests
- [ ] Long nickname displays correctly
- [ ] Long interest names don't overflow
- [ ] UI doesn't break
- [ ] Text truncates properly

#### 5.5 All Topics at 100% Mastery
- [ ] Progress screen shows correctly
- [ ] No errors in calculations
- [ ] Can still take tests
- [ ] Recommendations work

---

### 6. Data Persistence
**Priority**: 🟡 HIGH

#### 6.1 Profile Persistence
- [ ] User profile saves correctly
- [ ] Profile persists after app restart
- [ ] All fields (name, goal, interests) persist

#### 6.2 Test Results Persistence
- [ ] Test results save correctly
- [ ] Results persist after app restart
- [ ] Can view past test results

#### 6.3 Progress Tracking Persistence
- [ ] Topic performance saves
- [ ] Streak saves correctly
- [ ] Level changes persist
- [ ] Badges persist

---

### 7. Performance Testing
**Priority**: 🟡 HIGH

#### 7.1 App Startup
- [ ] App starts in < 3 seconds
- [ ] Splash screen doesn't hang
- [ ] Database loads quickly
- [ ] Question bank loads quickly

#### 7.2 Screen Transitions
- [ ] All transitions are smooth (60fps)
- [ ] No lag when navigating
- [ ] No white flashes

#### 7.3 Test Screen Performance
- [ ] Questions load quickly
- [ ] No lag when selecting answers
- [ ] Smooth scrolling (if needed)
- [ ] No memory leaks

#### 7.4 Database Performance
- [ ] Queries are fast (< 100ms)
- [ ] No lag when saving results
- [ ] Large question bank loads quickly

---

## Test Execution Log

### Test Run #1
**Date**: ___________  
**Tester**: ___________  
**Platform**: ___________  

**Results**:
- [ ] New User Flow: PASS / FAIL
- [ ] Returning User Flow: PASS / FAIL
- [ ] Navigation Flow: PASS / FAIL
- [ ] Error Scenarios: PASS / FAIL
- [ ] Edge Cases: PASS / FAIL
- [ ] Data Persistence: PASS / FAIL
- [ ] Performance: PASS / FAIL

**Issues Found**:
1. 
2. 
3. 

---

## Known Issues

### Critical Issues
- None yet

### High Priority Issues
- None yet

### Medium Priority Issues
- None yet

---

## Test Completion Status

- [ ] New User Flow: ⚠️ NOT TESTED
- [ ] Returning User Flow: ⚠️ NOT TESTED
- [ ] Navigation Flow: ⚠️ NOT TESTED
- [ ] Error Scenarios: ⚠️ NOT TESTED
- [ ] Edge Cases: ⚠️ NOT TESTED
- [ ] Data Persistence: ⚠️ NOT TESTED
- [ ] Performance: ⚠️ NOT TESTED

**Overall Status**: ⚠️ TESTING IN PROGRESS

---

## Notes

- Manual testing required (no automated tests yet)
- Test on actual device for best results
- Test on different screen sizes if possible
- Test with different user profiles

