# UI Pages List - Dokter Grammar App

Complete list of all UI pages/screens in the application.

## 📱 All UI Pages (13 Screens)

### 1. **Splash Screen**
- **Path**: `lib/presentation/screens/splash/splash_screen.dart`
- **Purpose**: Initial app loading screen, checks user profile and placement test status
- **Navigation**: Routes to ProfileInputScreen, PlacementIntroScreen, or HomeScreen

### 2. **Profile Input Screen** (Onboarding)
- **Path**: `lib/presentation/screens/onboarding/profile_input_screen.dart`
- **Purpose**: User profile creation - nickname, goal, interests
- **Navigation**: Routes to PlacementIntroScreen after profile creation

### 3. **Placement Intro Screen**
- **Path**: `lib/presentation/screens/placement/placement_intro_screen.dart`
- **Purpose**: Introduction and information about placement test
- **Navigation**: Routes to TestScreen to start placement test

### 4. **Home Screen**
- **Path**: `lib/presentation/screens/home/home_screen.dart`
- **Purpose**: Main dashboard - shows placement test card (if not completed), grammar categories, test types, recent activities
- **Navigation**: Routes to various test screens, progress, settings, badges

### 5. **Test Screen**
- **Path**: `lib/presentation/screens/test/test_screen.dart`
- **Purpose**: Core test-taking interface - displays questions, choices, progress bar, navigation buttons
- **Navigation**: Routes to TestResultsScreen after completion

### 6. **Test Results Screen**
- **Path**: `lib/presentation/screens/test_results/test_results_screen.dart`
- **Purpose**: Displays test results - score, level, performance breakdown, explanations
- **Navigation**: Routes to ExplanationScreen or back to HomeScreen

### 7. **Explanation Screen**
- **Path**: `lib/presentation/screens/explanation/explanation_screen.dart`
- **Purpose**: Shows detailed explanation for each question in the test
- **Navigation**: Can navigate through questions, returns to TestResultsScreen

### 8. **Custom Test Config Screen**
- **Path**: `lib/presentation/screens/custom_test/custom_test_config_screen.dart`
- **Purpose**: Configuration screen for custom tests - question count, topic selection
- **Navigation**: Routes to TestScreen with custom test configuration

### 9. **Progress Screen**
- **Path**: `lib/presentation/screens/progress/progress_screen.dart`
- **Purpose**: User progress tracking - overall stats, topic performance, recent test sessions
- **Navigation**: Accessible from HomeScreen bottom navigation

### 10. **Badges Screen**
- **Path**: `lib/presentation/screens/badges/badges_screen.dart`
- **Purpose**: Displays earned badges and achievements
- **Navigation**: Accessible from HomeScreen

### 11. **Settings Screen**
- **Path**: `lib/presentation/screens/settings/settings_screen.dart`
- **Purpose**: App settings - profile management, data & backup, developer options, app info
- **Navigation**: Routes to ProfileInputScreen, BackupScreen, DebugScreen

### 12. **Backup Screen**
- **Path**: `lib/presentation/screens/backup/backup_screen.dart`
- **Purpose**: Backup and restore functionality - export/import data
- **Navigation**: Accessible from SettingsScreen

### 13. **Debug Screen**
- **Path**: `lib/presentation/screens/debug/debug_screen.dart`
- **Purpose**: Developer tools - view test execution logs and callbacks
- **Navigation**: Accessible from SettingsScreen (Developer section)

---

## 📊 Screen Categories

### **Onboarding Flow**
1. Splash Screen
2. Profile Input Screen
3. Placement Intro Screen

### **Main App Flow**
4. Home Screen
5. Test Screen
6. Test Results Screen
7. Explanation Screen

### **Configuration & Customization**
8. Custom Test Config Screen

### **Progress & Achievements**
9. Progress Screen
10. Badges Screen

### **Settings & Utilities**
11. Settings Screen
12. Backup Screen
13. Debug Screen

---

## 🎨 UI Design Status

All screens have been updated with:
- ✅ Lemon gradient aesthetic for cards
- ✅ Dark text colors for better contrast
- ✅ Modern header with lemon gradient
- ✅ Consistent design language
- ✅ No overflow issues
- ✅ Smooth animations and transitions

---

## 📝 Notes

- All screens use `ModernHeader` widget for consistent header design
- All screens use lemon gradient cards (`AppColors.lemonCardGradient`)
- All screens use dark text colors (`AppColors.textPrimary`, `AppColors.textSecondary`)
- Bottom navigation bar is present on HomeScreen, ProgressScreen, and SettingsScreen
- All screens are responsive and handle edge cases (empty states, loading states, errors)

---

*Last Updated: 2024-11-27*

