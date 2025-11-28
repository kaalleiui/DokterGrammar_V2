import 'package:flutter/material.dart';

class AppColors {
  // Primary - Orange (Matching HTML design)
  static const Color primary = Color(0xFFFF9D3B);         // #FF9D3B - Main orange
  static const Color primaryLight = Color(0xFFFFCF5B);    // #FFCF5B - Light orange
  static const Color primaryDark = Color(0xFFE07C2E);     // #E07C2E - Dark orange
  
  // Secondary
  static const Color secondary = Color(0xFF4A90E2);      // #4A90E2 - Blue
  static const Color accent = Color(0xFFFF6B6B);          // #FF6B6B - Red accent
  
  // Text Colors
  static const Color textPrimary = Color(0xFF333333);     // #333333 - Dark gray
  static const Color textSecondary = Color(0xFF666666);  // #666666 - Medium gray
  static const Color textTertiary = Color(0xFF999999);   // #999999 - Light gray
  
  // Background
  static const Color background = Color(0xFFFFF7E0);     // #FFF7E0 - Warm cream
  static const Color backgroundWhite = Color(0xFFFFFFFF); // #FFFFFF - Pure white
  static const Color cardBackground = Color(0xFFFFFFFF); // #FFFFFF - White cards
  
  // Status Colors
  static const Color success = Color(0xFF4CAF50);         // #4CAF50 - Green
  static const Color error = Color(0xFFE53935);           // #E53935 - Red
  static const Color warning = Color(0xFFFFC107);       // #FFC107 - Yellow/Orange
  
  // Shadows
  static List<BoxShadow> cardShadow = [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 30,
      offset: const Offset(0, 10),
    ),
  ];
  
  static List<BoxShadow> cardShadowHover = [
    BoxShadow(
      color: Colors.black.withOpacity(0.12),
      blurRadius: 40,
      offset: const Offset(0, 15),
    ),
  ];
  
  static List<BoxShadow> buttonShadow = [
    BoxShadow(
      color: primary.withOpacity(0.3), //ni orens jelek bgt
      blurRadius: 15,
      offset: const Offset(0, 4),
    ),
  ];
  
  // Border Radius
  static const double radius = 20.0;      // Card radius
  static const double radiusSmall = 12.0;  // Button/small element radius
  
  // Gradient Definitions
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryLight, primary],
  );
  
  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryLight, primary],
  );
  
  // Legacy support (for backward compatibility)
  static const Color lemonLight = background;
  static const Color lemonSoft = background;
  static const Color lemonMedium = primaryLight;
  static const Color lemonPastel = primaryLight;
  static const Color orangeLight = primaryLight;
  static const Color orangePrimary = primary;
  static const Color orangeDark = primaryDark;
  static const Color backgroundLight = background;
  static const Color textHint = textTertiary;
  
  static const LinearGradient lemonGradient = primaryGradient;
  static const LinearGradient lemonCardGradient = LinearGradient(
    colors: [cardBackground, cardBackground],
  );
  static const LinearGradient lemonHeaderGradient = primaryGradient;
  static const LinearGradient orangeGradient = primaryGradient;
  
  // Level Badge Colors
  static const Color beginner = Color(0xFF81C784);        // Light green
  static const Color elementary = Color(0xFF64B5F6);      // Light blue
  static const Color intermediate = Color(0xFFFFB74D);    // Orange
  static const Color upperIntermediate = Color(0xFFFF8A65); // Deep orange
  static const Color advanced = Color(0xFFBA68C8);        // Purple
  
  // Helper method to get level color
  static Color getLevelColor(String level) {
    switch (level.toLowerCase()) {
      case 'beginner':
        return beginner;
      case 'elementary':
        return elementary;
      case 'intermediate':
        return intermediate;
      case 'upper_intermediate':
        return upperIntermediate;
      case 'advanced':
        return advanced;
      default:
        return textSecondary;
    }
  }
}

