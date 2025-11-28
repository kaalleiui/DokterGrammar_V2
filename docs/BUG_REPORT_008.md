# Bug Report #008 - Multiple Critical Issues

**Status**: 🔴 CRITICAL  
**Reported**: 2024-11-27  
**Platform**: All Platforms

## Description

User reported multiple critical issues affecting test functionality and UI:

### Bug #008.1 - Different Options in Test Questions
**Severity**: 🔴 HIGH  
**Description**: Some questions in the initial test have different options displayed. This suggests the duplicate choice filtering or choice display logic is not working correctly.

**Expected Behavior**: All questions should display their correct, unique options.

**Actual Behavior**: Some questions show different or incorrect options.

---

### Bug #008.2 - 0% Score After Completing 50 Questions
**Severity**: 🔴 CRITICAL  
**Description**: After completing all 50 questions in the placement test, the result screen shows 0% score even though the user answered questions.

**Expected Behavior**: Score should reflect the percentage of correct answers (e.g., if 30/50 correct, show 60%).

**Actual Behavior**: Score always shows 0% regardless of answers.

**Root Cause Analysis**:
- Need to verify if attempts are being saved correctly
- Check if `_testSession!.attempts` is populated when calculating score
- Verify if `ScoringService.calculateScore()` is receiving the attempts correctly
- Check if attempts are persisted to database before score calculation

---

### Bug #008.3 - AppBar Text Alignment Left Instead of Center
**Severity**: 🟡 MEDIUM  
**Description**: Text in the AppBar (test screen) is aligned to the left instead of being centered.

**Expected Behavior**: AppBar title should be centered.

**Actual Behavior**: AppBar title is left-aligned.

**Location**: `lib/presentation/screens/test/test_screen.dart` - AppBar title

---

### Bug #008.4 - Menu Not Scrollable on Main Page
**Severity**: 🟡 MEDIUM  
**Description**: After finishing test and returning to main page, the menu (white red) cannot be scrolled. User wants it changed to yellow-white lemon style and made scrollable.

**Expected Behavior**: 
- Menu should be scrollable
- Menu should use lemon/yellow-white color scheme matching the app design

**Actual Behavior**: 
- Menu is not scrollable
- Menu uses white-red colors instead of lemon style

**Location**: `lib/presentation/screens/home/home_screen.dart` - Bottom navigation or menu section

---

### Bug #008.5 - No Exit/Back Button in Test Screens
**Severity**: 🔴 HIGH  
**Description**: When user clicks "Reassessment Test" or other menu items on main page, there's no exit/back button. If user accidentally selects wrong option, they cannot go back.

**Expected Behavior**: 
- All screens should have a back button or exit option
- User should be able to cancel/exit from test configuration screens
- User should be able to go back from placement intro screen

**Actual Behavior**: 
- No back button in placement intro screen
- No cancel/exit option in custom test config screen
- User is stuck if they select wrong option

**Affected Screens**:
- `lib/presentation/screens/placement/placement_intro_screen.dart`
- `lib/presentation/screens/custom_test/custom_test_config_screen.dart`
- Other test configuration screens

---

## Impact

- **CRITICAL**: Users cannot see their actual test scores (always 0%)
- **HIGH**: Users cannot navigate back from test screens
- **HIGH**: Some questions show incorrect options
- **MEDIUM**: Poor UI/UX with misaligned text and non-scrollable menu

---

## Fix Plan

### Fix #008.1 - Different Options
1. Review choice filtering logic in test screen
2. Ensure unique choices are displayed correctly
3. Verify choice display matches question data

### Fix #008.2 - 0% Score
1. Verify attempts are saved before score calculation
2. Check if `_testSession.attempts` is populated correctly
3. Ensure `ScoringService.calculateScore()` receives attempts
4. Add debug logging to track score calculation
5. Verify attempts are persisted to database

### Fix #008.3 - AppBar Text Alignment
1. Add `centerTitle: true` to AppBar
2. Ensure text is centered

### Fix #008.4 - Scrollable Menu
1. Identify the menu component (likely bottom nav or category list)
2. Wrap in `SingleChildScrollView` or make it scrollable
3. Change colors to lemon/yellow-white scheme
4. Update styling to match app design

### Fix #008.5 - Exit/Back Buttons
1. Add back button to placement intro screen
2. Add cancel/exit button to custom test config screen
3. Add back navigation to all test configuration screens
4. Ensure users can always go back

---

## Files to Change

- `lib/presentation/screens/test/test_screen.dart` - Fix AppBar alignment, verify attempts saving
- `lib/presentation/screens/test_results/test_results_screen.dart` - Verify score display
- `lib/core/services/scoring_service.dart` - Verify score calculation
- `lib/presentation/screens/home/home_screen.dart` - Fix menu scrollability and colors
- `lib/presentation/screens/placement/placement_intro_screen.dart` - Add back button
- `lib/presentation/screens/custom_test/custom_test_config_screen.dart` - Add cancel/exit button
- `lib/presentation/widgets/common/bottom_nav_bar.dart` - Update colors and scrollability

---

## Testing Checklist

- [ ] Verify all questions show correct, unique options
- [ ] Complete 50-question test and verify score is calculated correctly
- [ ] Verify AppBar text is centered
- [ ] Verify menu is scrollable on main page
- [ ] Verify menu uses lemon/yellow-white colors
- [ ] Verify back button works in placement intro screen
- [ ] Verify cancel/exit button works in custom test config
- [ ] Verify all test screens have navigation back option

---

## Priority

🔴 **CRITICAL** - Fix immediately, especially the 0% score bug which makes the app unusable for its primary purpose.

