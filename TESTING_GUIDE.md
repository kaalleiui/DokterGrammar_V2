# End-to-End Testing Guide
**Task**: Task 2.1 - End-to-End Testing  
**Date**: 2024-11-27

---

## Quick Start

### Pre-Testing Checklist
- [ ] Run `python test_helper.py stats` to verify app setup
- [ ] Run `python validate_questions.py` to verify question bank
- [ ] Ensure Flutter app can build and run
- [ ] Have a test device/emulator ready

### Testing Environment
- **Platform**: Android/iOS/Desktop (specify)
- **Device**: (specify device/emulator)
- **App Version**: (current version)
- **Database**: Fresh install or existing data

---

## Test Execution Steps

### Phase 1: New User Flow (Critical Path)

#### Step 1.1: Fresh Install Test
1. **Uninstall app** (if installed) or use fresh emulator
2. **Install and launch** app
3. **Expected**: Splash screen appears
4. **Wait**: App should initialize database
5. **Expected**: Navigate to Profile Input Screen

**✅ Pass Criteria**:
- Splash screen displays correctly
- No crashes during initialization
- Navigation to profile input works

**❌ Fail If**:
- App crashes on startup
- Stuck on splash screen
- Database initialization fails

---

#### Step 1.2: Profile Creation
1. **Enter nickname**: "TestUser"
2. **Select goal**: Choose any goal (e.g., "Pass Exam")
3. **Select interests**: Select 2-3 interests (e.g., "anime", "film")
4. **Click "Selanjutnya"**

**✅ Pass Criteria**:
- All fields accept input
- Button enables after required fields filled
- Navigation to placement intro works

**❌ Fail If**:
- Cannot enter nickname
- Cannot select goal/interests
- Button doesn't enable
- Navigation fails

---

#### Step 1.3: Placement Test Intro
1. **Verify screen displays**:
   - Explanation of 50 questions
   - Question types info
   - Estimated duration
2. **Click "Mulai 50 Soal"**

**✅ Pass Criteria**:
- All information displays correctly
- Button works
- Navigation to test screen works

---

#### Step 1.4: Placement Test (50 Questions)
1. **Verify first question loads**
2. **Answer all 50 questions**:
   - Select answers for each question
   - Use Next/Previous buttons
   - Verify progress updates
3. **Complete test**

**✅ Pass Criteria**:
- All 50 questions load
- Can select answers
- Progress updates correctly (1/50, 2/50, etc.)
- Can navigate between questions
- No crashes
- Test completes successfully

**❌ Fail If**:
- Questions don't load
- Cannot select answers
- Progress doesn't update
- App crashes
- Test doesn't complete

**⚠️ Known Issues to Watch For**:
- Score showing 0% (should be fixed)
- Wrong options displayed (should be fixed)
- Duplicate choices (should be fixed)

---

#### Step 1.5: Test Results
1. **Verify results screen displays**:
   - Score (should NOT be 0% if answered correctly)
   - Level calculation
   - Topic breakdown
2. **Check score accuracy**: If answered 40/50 correctly, score should be ~80%
3. **Verify level**: Should match score range
4. **Check topic breakdown**: Should show performance per topic

**✅ Pass Criteria**:
- Score displays correctly (not 0%)
- Level is calculated correctly
- Topic breakdown shows
- All data is accurate

**❌ Fail If**:
- Score is 0% when answers were correct
- Level is wrong
- Topic breakdown missing
- Data is incorrect

---

#### Step 1.6: Explanations
1. **Click "See Explanations"**
2. **Verify explanation screen**:
   - Shows question
   - Shows correct answer
   - Shows user answer
   - Shows explanation text
   - Shows example sentence
3. **Navigate between questions**

**✅ Pass Criteria**:
- All explanations display
- Correct/user answers highlighted
- Explanations are clear
- Navigation works

---

#### Step 1.7: Home Screen
1. **Verify home screen displays**:
   - User level badge
   - Category cards (12 topics)
   - Weakest areas section
   - Main action buttons
2. **Check navigation**: Bottom nav bar works

**✅ Pass Criteria**:
- All elements display
- Data is correct
- Navigation works

---

### Phase 2: Returning User Flow

#### Step 2.1: App Restart
1. **Close app completely**
2. **Reopen app**
3. **Expected**: Should go directly to Home Screen (not onboarding)

**✅ Pass Criteria**:
- Skips onboarding
- Goes to home screen
- User data persists

---

#### Step 2.2: Custom Test
1. **Click "Custom Test"**
2. **Configure test**:
   - Select number of questions (e.g., 20)
   - Select/deselect topics
3. **Click "Start"**
4. **Complete test**
5. **Verify results**

**✅ Pass Criteria**:
- Configuration works
- Test uses selected settings
- Questions are adaptive (favor weak topics)
- Results display correctly

---

#### Step 2.3: Daily Test
1. **Click "Daily Test"**
2. **Complete 5-10 quick questions**
3. **Verify results**
4. **Check streak updates** (if applicable)

**✅ Pass Criteria**:
- Daily test starts
- Questions are quick
- Results display
- Streak updates

---

#### Step 2.4: Reassessment
1. **Click "Reassessment"**
2. **Select type** (Full or Targeted)
3. **Complete test**
4. **Verify level up** (if threshold met)

**✅ Pass Criteria**:
- Reassessment starts
- Uses correct question set
- Level up works correctly
- Level updates in profile

---

### Phase 3: Navigation Testing

#### Step 3.1: Bottom Navigation
1. **Test each tab**:
   - Home
   - Progress
   - Review
   - Profile
2. **Verify current tab is highlighted**
3. **Verify smooth transitions**

**✅ Pass Criteria**:
- All tabs work
- Highlighting is correct
- Transitions are smooth

---

#### Step 3.2: Back Button
1. **Navigate to various screens**
2. **Use back button** (AppBar and system back)
3. **Verify navigation stack**

**✅ Pass Criteria**:
- Back button works everywhere
- Navigation stack is correct
- No navigation loops

---

### Phase 4: Error Scenarios

#### Step 4.1: Empty Database
1. **Clear app data** (Settings → Apps → Clear Data)
2. **Launch app**
3. **Expected**: Should initialize database and go to onboarding

**✅ Pass Criteria**:
- Handles empty database gracefully
- Initializes correctly
- No crashes

---

#### Step 4.2: Invalid Input
1. **Try to submit profile with empty nickname**
2. **Expected**: Should show error message

**✅ Pass Criteria**:
- Validation works
- Error messages are clear
- No crashes

---

### Phase 5: Data Persistence

#### Step 5.1: Profile Persistence
1. **Create profile**
2. **Close app**
3. **Reopen app**
4. **Verify profile data persists**

**✅ Pass Criteria**:
- All profile data persists
- Name, goal, interests all saved

---

#### Step 5.2: Test Results Persistence
1. **Complete a test**
2. **Close app**
3. **Reopen app**
4. **Verify test results are still visible**

**✅ Pass Criteria**:
- Test results persist
- Can view past results
- Progress is saved

---

## Test Results Template

### Test Run #___
**Date**: ___________  
**Tester**: ___________  
**Platform**: ___________  
**Device**: ___________  

#### Results Summary
- New User Flow: ✅ PASS / ❌ FAIL
- Returning User Flow: ✅ PASS / ❌ FAIL
- Navigation: ✅ PASS / ❌ FAIL
- Error Scenarios: ✅ PASS / ❌ FAIL
- Data Persistence: ✅ PASS / ❌ FAIL

#### Issues Found
1. **Issue**: ___________  
   **Severity**: 🔴 Critical / 🟡 High / 🟢 Medium  
   **Steps to Reproduce**: ___________  
   **Expected**: ___________  
   **Actual**: ___________  

2. **Issue**: ___________  
   **Severity**: 🔴 Critical / 🟡 High / 🟢 Medium  
   **Steps to Reproduce**: ___________  
   **Expected**: ___________  
   **Actual**: ___________  

#### Notes
___________  
___________  

---

## Automated Checks

Before manual testing, run these automated checks:

```bash
# Verify question bank
python validate_questions.py

# Check app statistics
python test_helper.py stats

# Verify no duplicates
python find_duplicates.py
```

All should pass before starting manual testing.

---

## Critical Issues to Watch For

1. **Score showing 0%** - Should be fixed, but verify
2. **Wrong options displayed** - Should be fixed, but verify
3. **Duplicate choices** - Should be fixed, but verify
4. **Navigation bugs** - Test all navigation paths
5. **Data not persisting** - Test app restart scenarios
6. **Crashes** - Note any crashes with steps to reproduce

---

## Next Steps After Testing

1. **Document all issues** in TESTING_CHECKLIST.md
2. **Prioritize issues** (Critical, High, Medium)
3. **Fix critical issues** before proceeding
4. **Re-test** after fixes
5. **Update status** in NEXT_DEVELOPMENT_PLAN.md

---

**Testing Status**: ⚠️ READY TO START  
**Last Updated**: 2024-11-27

