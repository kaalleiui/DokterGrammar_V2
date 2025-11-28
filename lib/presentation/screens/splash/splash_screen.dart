import 'package:flutter/material.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/constants/color_scheme.dart';
import '../../../core/database/database_helper.dart';
import '../../../core/services/local_server.dart';
import '../../../core/services/ai_service.dart';
import '../../../data/repositories/user_repository.dart';
import '../../../data/repositories/question_repository.dart';
import '../../../data/repositories/test_repository.dart';
import '../../../data/datasources/assets/question_bank_loader.dart';
import '../onboarding/profile_input_screen.dart';
import '../home/home_screen.dart';
import '../placement/placement_intro_screen.dart';
import '../../theme/page_transitions.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    try {
      // Initialize database
      await DatabaseHelper.instance.database;
      
      // Initialize AI service (load pre-generated explanations)
      await AIService.initialize();
      
      // Initialize local server and rule engine
      await LocalServer.instance.initialize();
      
      // Preload questions from assets if database is empty
      final questionRepo = QuestionRepository();
      final questionCount = await questionRepo.getQuestionCount();
      if (questionCount == 0) {
        final questions = await QuestionBankLoader.loadQuestionsFromAssets();
        if (questions.isNotEmpty) {
          await questionRepo.insertQuestions(questions);
        }
      }
      
      // Check if user profile exists
      final userRepo = UserRepository();
      final user = await userRepo.getCurrentUser();
      
      if (!mounted) return;
      
      // Navigate based on profile existence and placement test completion
      if (user != null) {
        // Validate user ID
        if (user.id == null) {
          if (!mounted) return;
          // User exists but has invalid ID - go to onboarding to recreate profile
          AppNavigator.pushReplacementFadeSlide(
            context,
            const ProfileInputScreen(),
          );
          return;
        }

        // Check if user has completed placement test
        final testRepo = TestRepository();
        final hasCompletedPlacement = await testRepo.hasUserCompletedPlacementTest(user.id!);
        
        if (!mounted) return;
        if (!hasCompletedPlacement) {
          // User exists but hasn't completed placement test - redirect to placement test
          AppNavigator.pushReplacementFadeSlide(
            context,
            const PlacementIntroScreen(),
          );
        } else {
          // User exists and has completed placement test - go to home
          AppNavigator.pushReplacementFadeSlide(
            context,
            const HomeScreen(),
          );
        }
      } else {
        // No user profile - go to onboarding
        if (!mounted) return;
        AppNavigator.pushReplacementFadeSlide(
          context,
          const ProfileInputScreen(),
        );
      }
    } catch (e) {
      // If error, still navigate to onboarding
      if (!mounted) return;
      AppNavigator.pushReplacementFadeSlide(
        context,
        const ProfileInputScreen(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo - matching HTML design
              Container(
                width: 140,
                height: 140,
                decoration: BoxDecoration(
                  gradient: AppColors.primaryGradient,
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withOpacity(0.3),
                      blurRadius: 35,
                      offset: const Offset(0, 15),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.book_outlined,
                  size: 70,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 30),
              Text(
                AppConstants.appName,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Text(
                  AppConstants.appTagline,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 16,
                    color: AppColors.textSecondary,
                  ),
                ),
              ),
              const SizedBox(height: 60),
              const CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
              ),
              const SizedBox(height: 40),
              // Footer - matching HTML design
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Icon(
                    Icons.wifi_off,
                    size: 16,
                    color: AppColors.textTertiary,
                  ),
                  SizedBox(width: 8),
                  Text(
                    '100% Offline • Your Privacy, Our Priority',
                    style: TextStyle(
                      fontSize: 14,
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

