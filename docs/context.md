# Dokter Grammar — Product Specification & User Flow

> **Purpose**: This document serves as a structured guide for developers to implement an Android application that is **fully offline** (on-device server) to help English literature students **identify grammar weaknesses**, receive **level assessment** (beginner → advanced), and access **adaptive custom practice** tailored to their weaknesses.

---

## Executive Summary (Elevator Pitch)

Users complete a brief registration (name, goal, interests), then take a **50-question placement test** to determine their grammar level and weak areas. The application provides **question explanations + AI feedback** (on-device), practice recommendations, and a UI focused on **Custom Test** (prioritizing weak areas), **Daily Quick Test**, and **Reassessment** for level progression. All features work **offline** with local storage and a small on-device server for routing requests to local AI models.

---

## Table of Contents

1. [High-level User Flows](#1-high-level-user-flows)
2. [Screen-by-Screen (UI/UX)](#2-screen-by-screen-ui--ux)
3. [Data & Model Architecture](#3-data--model-architecture-offline)
4. [Database Schema](#4-database-schema)
5. [AI Model Schema](#5-ai-model-schema)
6. [Core Data Models](#6-core-data-models)
7. [Project Folder Structure](#7-project-folder-structure)
8. [Adaptive Algorithm](#8-adaptive-algorithm)
9. [Content Design](#9-content-design)
10. [Gamification & Engagement](#10-gamification--engagement)
11. [Offline & Storage Considerations](#11-offline--storage-considerations)
12. [Privacy & Security](#12-privacy--security)
13. [Acceptance Criteria](#13-acceptance-criteria--developer-checklist)
14. [Example User Journeys](#14-example-user-journeys)
15. [Developer Notes & Recommendations](#15-developer-notes--recommendations)
16. [Content Taxonomy](#16-content-taxonomy)

---

## UI Color Scheme

### Color Palette

Based on the requirements:
- **Text**: Dark colors for readability
- **Containers**: Lemon gradient (soft and pastel)
- **Background**: White
- **Secondary**: Orange accents

### Detailed Color Scheme

```dart
// colors.dart
class AppColors {
  // Primary - Lemon Gradient (Soft & Pastel)
  static const Color lemonLight = Color(0xFFFFF9E6);      // Very light lemon
  static const Color lemonSoft = Color(0xFFFFF4CC);       // Soft lemon
  static const Color lemonMedium = Color(0xFFFFE699);     // Medium lemon
  static const Color lemonPastel = Color(0xFFFFD966);     // Pastel lemon
  
  // Secondary - Orange
  static const Color orangeLight = Color(0xFFFFE5CC);      // Light orange
  static const Color orangePrimary = Color(0xFFFFB84D);    // Primary orange
  static const Color orangeDark = Color(0xFFFF9900);      // Dark orange
  
  // Text - Dark Colors
  static const Color textPrimary = Color(0xFF1A1A1A);      // Almost black
  static const Color textSecondary = Color(0xFF4A4A4A);    // Dark gray
  static const Color textTertiary = Color(0xFF6B6B6B);     // Medium gray
  static const Color textHint = Color(0xFF9B9B9B);        // Light gray
  
  // Background
  static const Color backgroundWhite = Color(0xFFFFFFFF);  // Pure white
  static const Color backgroundLight = Color(0xFFFAFAFA); // Off-white
  
  // Status Colors
  static const Color success = Color(0xFF4CAF50);          // Green
  static const Color error = Color(0xFFE53935);           // Red
  static const Color warning = Color(0xFFFFB84D);          // Orange
  static const Color info = Color(0xFF2196F3);            // Blue
  
  // Level Badge Colors
  static const Color beginner = Color(0xFF81C784);        // Light green
  static const Color elementary = Color(0xFF64B5F6);      // Light blue
  static const Color intermediate = Color(0xFFFFB74D);   // Orange
  static const Color upperIntermediate = Color(0xFFFF8A65); // Deep orange
  static const Color advanced = Color(0xFFBA68C8);        // Purple
  
  // Gradient Definitions
  static const LinearGradient lemonGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [lemonLight, lemonSoft, lemonMedium],
  );
  
  static const LinearGradient orangeGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [orangeLight, orangePrimary],
  );
}
```

### Usage Guidelines

- **Primary Buttons**: Lemon gradient with dark text
- **Secondary Buttons**: Orange gradient with white text
- **Cards/Containers**: Lemon gradient (soft) with dark text
- **Background**: White for main screens, off-white for secondary
- **Text**: Dark colors (primary for headings, secondary for body)
- **Accents**: Orange for CTAs, highlights, and important elements

---

## 1. High-level User Flows

### 1.1 First-time User (Onboarding → Placement)

1. **Splash Screen** (branded: Dokter Grammar) → loading local DB & model
2. **Onboarding 1**: Brief benefits (1–2 slides). CTA: "Mulai"
3. **Profile Input**:
   - Nickname (required)
   - Goal (choose: pass exam, improve academic writing, speaking & grammar, etc.)
   - Interests (multi-select: anime, k-pop, film, literature, academic English…) — used for *example sentences* & question context
4. **Permission & Local Server**: Brief explanation "Application runs completely offline; data stored on device." (Accept button)
5. **Placement Test Intro**: Explain 50 questions, estimated duration, question types, and that explanations will be available after completion
6. **Start 50 Questions**

### 1.2 Returning User (Home → Daily/Custom/Reassess)

1. Open → **Homepage** (level summary, streak, practice recommendations)
2. Main buttons:
   - Custom Test (adaptive)
   - Daily Test (quick quiz)
   - Reassessment (full or targeted)
   - Review (question explanations & AI feedback)
   - Progress / Analytics
   - Settings / Backup
3. Select test → run → complete → explanation + update level profile

### 1.3 Level Progression

- After sufficient performance from reassessment (or accumulated scores), system offers **Level Up** and updates question distribution (previously weak areas decrease in frequency; new weak areas increase)

---

## 2. Screen-by-Screen (UI / UX)

> Each screen includes purpose, displayed data, main interactions, and example microcopy.

### 2.1 Splash Screen

- **Purpose**: Load local DB, model, and check if profile exists
- **Content**: Logo, tagline "Dokter Grammar — Diagnose. Latih. Sembuh."
- **Decision**:
  - If profile doesn't exist → route to Onboarding
  - If profile exists → route to Homepage

### 2.2 Onboarding: Profile Input

- **Fields**:
  - Nickname (text input)
  - Goal (dropdown / multi-choice)
  - Interests (chips multi-select; affects content)
- **Action**: "Selanjutnya — Placement Test"
- **Microcopy**: "Choose interests so examples feel familiar."

### 2.3 Placement Test Intro

- **Content**: Explanation of 50 questions, question types (multiple choice, gap-fill, sentence combining), countdown or no time limit option
- **Action**: "Mulai 50 Soal"

### 2.4 Test Screen (Generic)

- **Header**: Progress (e.g., 12 / 50), elapsed time
- **Question Area**: Sentence + options
- **Answer Input**: Radio buttons / drag-and-drop for reordering / text input for short answers
- **Bottom**: Next / Previous (optional: allow back navigation or lock after submit?)
- **Hint System**: Optional hint button (consumes micro-currency or limited per day) — for gamification

### 2.5 End of Test → Scoring & Feedback Summary

- **Top**: Score, computed level (e.g., Intermediate), confidence %
- **Middle**: Area breakdown (pie or bars): Tenses, Complex Sentence, Modals, Conditionals, Articles, Punctuation, Relative Clauses, etc. — sorted by weakness (descending)
- **Bottom**: CTA "See Explanations" and "Start Personalized Training"

### 2.6 Explanation Screen (Per Question)

- Show question, correct answer, user answer highlighted, **AI explanation** (concise), and link to related lessons and practice questions
- Allow "mark as unclear" and "ask follow-up" (on-device AI gives clarifying line)

### 2.7 Homepage / Main Dashboard

- **Top Card**: Current level badge, score, streak/day activity
- **Main Actions** (large buttons):
  - Custom Test (primary)
  - Daily Test (secondary)
  - Reassessment
- **Section**: Weakest areas preview (3 cards) with "Practice now" button each
- **Section**: Recent test results and quick link to explanations
- **Footer**: Profile / Settings / Progress

### 2.8 Custom Test Screen

- UI to confirm: number of questions, duration, topics included (preselected weights favor weakest areas)
- Show preview distribution (e.g., Complex Sentences 40%, Conditionals 25%, Articles 10%, Tenses 25%)
- Start

### 2.9 Daily Quick Test

- 5–10 quick questions, time limited per question (e.g., 30s). Focus on mixed topics; good for retention and streaks

### 2.10 Reassessment

- Option: Full reassessment (50 Q) or Targeted (20 Q focusing on weakest areas)
- After completion: if performance crosses threshold → propose level change

### 2.11 Progress & Analytics

- Timeline of tests, level history, accuracy per topic, time per question
- Suggested learning path (e.g., 2 weeks plan: 15 custom tests + daily practice)

### 2.12 Settings & Data

- Language, Interests (edit), Privacy, Export/Import backup (local file), Reset progress, Model settings (if advanced: smaller model vs full model to save space)
- Info: "All data stored locally — no network."

---

## 3. Data & Model Architecture (Offline)

### 3.1 On-device Server Concept (High Level)

A lightweight local server process inside the app (e.g., via `Isolate`/`Foreground service` pattern) to route:

- UI → Question engine
- UI → Local model inference (feedback/explanation generator)
- UI → Local DB

**Function**: Simplify request/response and concurrency patterns (multiple screens accessing model/DB).

### 3.2 Storage

Use local DB (SQLite / Hive) for:

- User profile
- Question bank (indexed by topic, difficulty, examples with interest tags)
- Test results / attempts
- User performance model (per topic stats)
- Settings & backups

**File Sizes**: Tip for developer — allow model & DB install in app bundle OR download-on-first-run into app storage (but user requested fully offline so bundling or sideload recommended).

### 3.3 Model & Feedback Engine

Two-tier approach:

1. **Rule-based scoring engine** (fast): Grammar rules, pattern matching, deterministic feedback for many MCQ & gap-fill
2. **On-device lightweight generative model** (optional): Produce concise explanations in natural language, paraphrase, produce practice variations. If on-device heavy model not feasible, fallback to **templated explanations + combinatorial templates per error type**

Keep explanation length short (1–3 sentences) and include an example correction.

### 3.4 Question Bank Format (Suggested JSON)

```json
{
  "id": "q1234",
  "type": "multiple_choice",
  "difficulty": 3,
  "topic": "complex_sentences",
  "tags": ["interest:anime", "tense:past"],
  "prompt": "Choose the best sentence combination...",
  "choices": [
    {"id": "a", "text": "..."},
    {"id": "b", "text": "..."}
  ],
  "answer": "b",
  "explanation_template": "Correct: {correct}. Rule: {rule_short}. Example: {example}.",
  "example": "..."
}
```

**Question Types**:
- `multiple_choice` — single best answer
- `gap_fill` — choose word/form
- `reorder` — sentence reordering
- `short_answer` — one word/phrase

---

## 4. Database Schema

### 4.1 SQLite Schema (Complete)

```sql
-- ============================================
-- USER PROFILE & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    goal TEXT NOT NULL, -- 'pass_exam', 'academic_writing', 'speaking_grammar', etc.
    current_level TEXT NOT NULL DEFAULT 'beginner', -- 'beginner', 'elementary', 'intermediate', 'upper_intermediate', 'advanced'
    overall_score REAL DEFAULT 0.0, -- 0.0 to 1.0
    streak_days INTEGER DEFAULT 0,
    last_activity_date TEXT, -- ISO 8601 format
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interest TEXT NOT NULL, -- 'anime', 'k-pop', 'film', 'literature', 'academic_english'
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, interest)
);

-- ============================================
-- QUESTION BANK
-- ============================================

CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, -- 'tenses', 'complex_sentences', 'conditionals', etc.
    display_name TEXT NOT NULL,
    difficulty_base INTEGER NOT NULL DEFAULT 3, -- 1-5
    description TEXT
);

CREATE TABLE questions (
    id TEXT PRIMARY KEY, -- e.g., 'q1234'
    type TEXT NOT NULL, -- 'multiple_choice', 'gap_fill', 'reorder', 'short_answer', 'error_identification'
    difficulty INTEGER NOT NULL, -- 1-5
    topic_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    answer TEXT NOT NULL, -- JSON string for complex answers
    explanation_template TEXT,
    example_sentence TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE question_choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    choice_id TEXT NOT NULL, -- 'a', 'b', 'c', 'd'
    text TEXT NOT NULL,
    is_correct INTEGER DEFAULT 0, -- 0 or 1
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE question_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    tag_type TEXT NOT NULL, -- 'interest', 'tense', 'grammar_point', etc.
    tag_value TEXT NOT NULL, -- 'anime', 'past', 'conditional_3', etc.
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE(question_id, tag_type, tag_value)
);

-- ============================================
-- TEST SESSIONS & ATTEMPTS
-- ============================================

CREATE TABLE test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_type TEXT NOT NULL, -- 'placement', 'custom', 'daily', 'reassessment'
    total_questions INTEGER NOT NULL,
    completed_questions INTEGER DEFAULT 0,
    score REAL, -- NULL until completed
    level_before TEXT,
    level_after TEXT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    duration_seconds INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE test_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_id TEXT NOT NULL,
    user_answer TEXT, -- JSON string for complex answers
    is_correct INTEGER, -- 0 or 1, NULL if not yet answered
    time_spent_seconds INTEGER,
    hint_used INTEGER DEFAULT 0, -- 0 or 1
    answered_at TEXT,
    FOREIGN KEY (session_id) REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- ============================================
-- USER PERFORMANCE TRACKING
-- ============================================

CREATE TABLE user_topic_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    attempts INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    last_attempted_at TEXT,
    mastery_percentage REAL DEFAULT 0.0, -- 0.0 to 1.0
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    UNIQUE(user_id, topic_id)
);

CREATE TABLE user_question_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id TEXT NOT NULL,
    times_attempted INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    last_attempted_at TEXT,
    marked_for_review INTEGER DEFAULT 0, -- 0 or 1
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE(user_id, question_id)
);

-- ============================================
-- EXPLANATIONS & FEEDBACK
-- ============================================

CREATE TABLE explanations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    explanation_text TEXT NOT NULL,
    explanation_type TEXT NOT NULL, -- 'template', 'ai_generated', 'rule_based'
    clarity_rating INTEGER, -- 1-5, user feedback
    marked_unclear INTEGER DEFAULT 0, -- 0 or 1
    follow_up_question TEXT,
    follow_up_answer TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (attempt_id) REFERENCES test_attempts(id) ON DELETE CASCADE
);

-- ============================================
-- GAMIFICATION
-- ============================================

CREATE TABLE badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_type TEXT NOT NULL, -- 'topic_master', 'streak_7', 'streak_30', 'level_up', etc.
    badge_name TEXT NOT NULL,
    earned_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, badge_type)
);

CREATE TABLE daily_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_date TEXT NOT NULL, -- YYYY-MM-DD format
    tests_completed INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, activity_date)
);

-- ============================================
-- SETTINGS & CONFIGURATION
-- ============================================

CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    setting_key TEXT NOT NULL,
    setting_value TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, setting_key)
);

CREATE TABLE notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL, -- 'daily_reminder', 'streak_reminder', 'level_up'
    enabled INTEGER DEFAULT 1, -- 0 or 1
    time_hour INTEGER, -- 0-23
    time_minute INTEGER, -- 0-59
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, notification_type)
);

-- ============================================
-- BACKUP & SYNC
-- ============================================

CREATE TABLE backup_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    backup_file_path TEXT NOT NULL,
    backup_size_bytes INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    version TEXT NOT NULL, -- app version when backup was created
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_questions_topic ON questions(topic_id);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_question_tags_question ON question_tags(question_id);
CREATE INDEX idx_question_tags_value ON question_tags(tag_value);
CREATE INDEX idx_test_sessions_user ON test_sessions(user_id);
CREATE INDEX idx_test_sessions_type ON test_sessions(session_type);
CREATE INDEX idx_test_attempts_session ON test_attempts(session_id);
CREATE INDEX idx_test_attempts_question ON test_attempts(question_id);
CREATE INDEX idx_user_topic_performance_user ON user_topic_performance(user_id);
CREATE INDEX idx_user_topic_performance_topic ON user_topic_performance(topic_id);
CREATE INDEX idx_user_question_history_user ON user_question_history(user_id);
CREATE INDEX idx_daily_activities_user_date ON daily_activities(user_id, activity_date);
```

### 4.2 Database Relationships Diagram

```
users
  ├── user_interests (1:N)
  ├── test_sessions (1:N)
  ├── user_topic_performance (1:N)
  ├── user_question_history (1:N)
  ├── badges (1:N)
  ├── daily_activities (1:N)
  ├── app_settings (1:N)
  ├── notification_preferences (1:N)
  └── backup_metadata (1:N)

topics
  ├── questions (1:N)
  └── user_topic_performance (1:N)

questions
  ├── question_choices (1:N)
  ├── question_tags (1:N)
  ├── test_attempts (1:N)
  └── user_question_history (1:N)

test_sessions
  └── test_attempts (1:N)

test_attempts
  └── explanations (1:N)
```

### 4.3 Database Initialization Script

```sql
-- Insert default topics
INSERT INTO topics (name, display_name, difficulty_base, description) VALUES
('tenses', 'Tenses', 2, 'Simple, continuous, perfect, and perfect continuous tenses'),
('modals_auxiliaries', 'Modals & Auxiliaries', 3, 'Modal verbs and auxiliary verbs'),
('conditionals', 'Conditionals', 4, 'Zero, first, second, third, and mixed conditionals'),
('complex_sentences', 'Complex Sentences', 4, 'Subordination, relative clauses, and complex structures'),
('sentence_combining', 'Sentence Combining & Punctuation', 3, 'Combining sentences and punctuation rules'),
('articles_determiners', 'Articles & Determiners', 2, 'A, an, the, and other determiners'),
('subject_verb_agreement', 'Subject-Verb Agreement', 3, 'Agreement between subject and verb'),
('passive_voice', 'Passive Voice', 3, 'Active and passive voice transformations'),
('reported_speech', 'Reported Speech', 4, 'Direct and indirect speech'),
('prepositions', 'Prepositions', 2, 'Prepositions of time, place, and movement'),
('adjective_clauses', 'Adjective Clauses', 4, 'Relative clauses and adjective clauses'),
('pronouns_reference', 'Pronouns & Reference', 2, 'Pronouns and reference clarity');
```

---

## 5. AI Model Schema

### 5.1 On-Device AI Model Configuration

```json
{
  "model_config": {
    "model_name": "grammar_explainer_v1",
    "model_type": "lightweight_generative",
    "model_format": "onnx",
    "model_size_mb": 45,
    "model_path": "assets/models/grammar_explainer.onnx",
    "vocab_path": "assets/models/vocab.json",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 0.9,
    "fallback_to_template": true
  },
  "rule_engine": {
    "enabled": true,
    "rules_path": "assets/rules/grammar_rules.json",
    "template_path": "assets/templates/explanations.json"
  },
  "explanation_prompt_template": "Explain why '{user_answer}' is incorrect. The correct answer is '{correct_answer}'. Grammar rule: {grammar_rule}. Keep explanation under 3 sentences. Use example: {example_context}."
}
```

### 5.2 AI Explanation Request Schema

```json
{
  "request_id": "req_123456",
  "question_id": "q1234",
  "question_type": "multiple_choice",
  "user_answer": "a",
  "correct_answer": "b",
  "question_prompt": "Choose the best sentence combination...",
  "grammar_topic": "complex_sentences",
  "user_interests": ["anime", "k-pop"],
  "difficulty": 3,
  "context": {
    "user_level": "intermediate",
    "previous_errors": ["tenses", "articles"]
  }
}
```

### 5.3 AI Explanation Response Schema

```json
{
  "request_id": "req_123456",
  "explanation": {
    "text": "The correct answer uses a relative clause correctly. 'Which' refers to the entire previous clause, not just 'the movie'.",
    "type": "ai_generated",
    "confidence": 0.85,
    "rule_applied": "relative_clauses_which_vs_that",
    "example": "If you liked the movie, which was released last year, you should watch the sequel."
  },
  "follow_up_available": true,
  "related_topics": ["relative_clauses", "pronouns_reference"],
  "generation_time_ms": 234
}
```

### 5.4 Grammar Rules Schema (Rule Engine)

```json
{
  "rules": [
    {
      "rule_id": "conditional_3_structure",
      "topic": "conditionals",
      "pattern": "if + past_perfect + would_have + past_participle",
      "explanation_template": "This is a third conditional for past hypothetical situations. Structure: if + past perfect, would have + past participle.",
      "example_correct": "If I had known, I would have gone.",
      "common_errors": [
        {
          "error_pattern": "if + past_simple + would_have",
          "explanation": "Use past perfect (had + past participle) in the if-clause, not simple past."
        }
      ]
    },
    {
      "rule_id": "relative_clause_which_vs_that",
      "topic": "complex_sentences",
      "pattern": "relative_clause_pronoun_selection",
      "explanation_template": "Use 'which' for non-restrictive clauses (with comma) and 'that' for restrictive clauses (no comma).",
      "example_correct": "The book, which I read yesterday, was excellent.",
      "common_errors": [
        {
          "error_pattern": "that_with_comma",
          "explanation": "Don't use 'that' with commas. Use 'which' for non-restrictive clauses."
        }
      ]
    }
  ]
}
```

### 5.5 Explanation Template Schema

```json
{
  "templates": [
    {
      "template_id": "multiple_choice_incorrect",
      "question_type": "multiple_choice",
      "template": "The correct answer is {correct_answer}. {rule_explanation} Example: {example_sentence}",
      "variables": ["correct_answer", "rule_explanation", "example_sentence"]
    },
    {
      "template_id": "gap_fill_tense_error",
      "question_type": "gap_fill",
      "topic": "tenses",
      "template": "You used '{user_answer}', but the correct form is '{correct_answer}' because {tense_rule}. Try: {example}",
      "variables": ["user_answer", "correct_answer", "tense_rule", "example"]
    }
  ]
}
```

---

## 6. Core Data Models

### 6.1 User Profile Model (Dart/Flutter)

```dart
class UserProfile {
  final int? id;
  final String nickname;
  final String goal;
  final String currentLevel; // 'beginner', 'elementary', etc.
  final double overallScore; // 0.0 to 1.0
  final int streakDays;
  final DateTime? lastActivityDate;
  final List<String> interests;
  final DateTime createdAt;
  final DateTime updatedAt;

  UserProfile({
    this.id,
    required this.nickname,
    required this.goal,
    this.currentLevel = 'beginner',
    this.overallScore = 0.0,
    this.streakDays = 0,
    this.lastActivityDate,
    required this.interests,
    required this.createdAt,
    required this.updatedAt,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'nickname': nickname,
    'goal': goal,
    'currentLevel': currentLevel,
    'overallScore': overallScore,
    'streakDays': streakDays,
    'lastActivityDate': lastActivityDate?.toIso8601String(),
    'interests': interests,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
    id: json['id'],
    nickname: json['nickname'],
    goal: json['goal'],
    currentLevel: json['currentLevel'] ?? 'beginner',
    overallScore: json['overallScore']?.toDouble() ?? 0.0,
    streakDays: json['streakDays'] ?? 0,
    lastActivityDate: json['lastActivityDate'] != null 
        ? DateTime.parse(json['lastActivityDate']) 
        : null,
    interests: List<String>.from(json['interests'] ?? []),
    createdAt: DateTime.parse(json['createdAt']),
    updatedAt: DateTime.parse(json['updatedAt']),
  );
}
```

### 6.2 Question Model

```dart
class Question {
  final String id;
  final String type; // 'multiple_choice', 'gap_fill', etc.
  final int difficulty; // 1-5
  final String topicId;
  final String prompt;
  final String answer; // JSON string for complex answers
  final String? explanationTemplate;
  final String? exampleSentence;
  final List<QuestionChoice> choices;
  final List<QuestionTag> tags;

  Question({
    required this.id,
    required this.type,
    required this.difficulty,
    required this.topicId,
    required this.prompt,
    required this.answer,
    this.explanationTemplate,
    this.exampleSentence,
    required this.choices,
    required this.tags,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'difficulty': difficulty,
    'topicId': topicId,
    'prompt': prompt,
    'answer': answer,
    'explanationTemplate': explanationTemplate,
    'exampleSentence': exampleSentence,
    'choices': choices.map((c) => c.toJson()).toList(),
    'tags': tags.map((t) => t.toJson()).toList(),
  };

  factory Question.fromJson(Map<String, dynamic> json) => Question(
    id: json['id'],
    type: json['type'],
    difficulty: json['difficulty'],
    topicId: json['topicId'],
    prompt: json['prompt'],
    answer: json['answer'],
    explanationTemplate: json['explanationTemplate'],
    exampleSentence: json['exampleSentence'],
    choices: (json['choices'] as List?)
        ?.map((c) => QuestionChoice.fromJson(c))
        .toList() ?? [],
    tags: (json['tags'] as List?)
        ?.map((t) => QuestionTag.fromJson(t))
        .toList() ?? [],
  );
}

class QuestionChoice {
  final String choiceId; // 'a', 'b', 'c', 'd'
  final String text;
  final bool isCorrect;

  QuestionChoice({
    required this.choiceId,
    required this.text,
    this.isCorrect = false,
  });

  Map<String, dynamic> toJson() => {
    'choiceId': choiceId,
    'text': text,
    'isCorrect': isCorrect,
  };

  factory QuestionChoice.fromJson(Map<String, dynamic> json) => QuestionChoice(
    choiceId: json['choiceId'],
    text: json['text'],
    isCorrect: json['isCorrect'] ?? false,
  );
}

class QuestionTag {
  final String tagType; // 'interest', 'tense', 'grammar_point'
  final String tagValue; // 'anime', 'past', 'conditional_3'

  QuestionTag({
    required this.tagType,
    required this.tagValue,
  });

  Map<String, dynamic> toJson() => {
    'tagType': tagType,
    'tagValue': tagValue,
  };

  factory QuestionTag.fromJson(Map<String, dynamic> json) => QuestionTag(
    tagType: json['tagType'],
    tagValue: json['tagValue'],
  );
}
```

### 6.3 Test Session Model

```dart
class TestSession {
  final int? id;
  final int userId;
  final String sessionType; // 'placement', 'custom', 'daily', 'reassessment'
  final int totalQuestions;
  final int completedQuestions;
  final double? score; // NULL until completed
  final String? levelBefore;
  final String? levelAfter;
  final DateTime startedAt;
  final DateTime? completedAt;
  final int? durationSeconds;
  final List<TestAttempt> attempts;

  TestSession({
    this.id,
    required this.userId,
    required this.sessionType,
    required this.totalQuestions,
    this.completedQuestions = 0,
    this.score,
    this.levelBefore,
    this.levelAfter,
    required this.startedAt,
    this.completedAt,
    this.durationSeconds,
    this.attempts = const [],
  });

  bool get isCompleted => completedAt != null;
  double get progress => totalQuestions > 0 ? completedQuestions / totalQuestions : 0.0;

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'sessionType': sessionType,
    'totalQuestions': totalQuestions,
    'completedQuestions': completedQuestions,
    'score': score,
    'levelBefore': levelBefore,
    'levelAfter': levelAfter,
    'startedAt': startedAt.toIso8601String(),
    'completedAt': completedAt?.toIso8601String(),
    'durationSeconds': durationSeconds,
    'attempts': attempts.map((a) => a.toJson()).toList(),
  };
}

class TestAttempt {
  final int? id;
  final int sessionId;
  final String questionId;
  final String? userAnswer;
  final bool? isCorrect;
  final int? timeSpentSeconds;
  final bool hintUsed;
  final DateTime? answeredAt;

  TestAttempt({
    this.id,
    required this.sessionId,
    required this.questionId,
    this.userAnswer,
    this.isCorrect,
    this.timeSpentSeconds,
    this.hintUsed = false,
    this.answeredAt,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'sessionId': sessionId,
    'questionId': questionId,
    'userAnswer': userAnswer,
    'isCorrect': isCorrect,
    'timeSpentSeconds': timeSpentSeconds,
    'hintUsed': hintUsed ? 1 : 0,
    'answeredAt': answeredAt?.toIso8601String(),
  };
}
```

### 6.4 Topic Performance Model

```dart
class TopicPerformance {
  final int? id;
  final int userId;
  final int topicId;
  final int attempts;
  final int correct;
  final int totalTimeSeconds;
  final DateTime? lastAttemptedAt;
  final double masteryPercentage; // 0.0 to 1.0

  TopicPerformance({
    this.id,
    required this.userId,
    required this.topicId,
    this.attempts = 0,
    this.correct = 0,
    this.totalTimeSeconds = 0,
    this.lastAttemptedAt,
    this.masteryPercentage = 0.0,
  });

  double get accuracy => attempts > 0 ? correct / attempts : 0.0;
  double get averageTimeSeconds => attempts > 0 ? totalTimeSeconds / attempts : 0.0;

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'topicId': topicId,
    'attempts': attempts,
    'correct': correct,
    'totalTimeSeconds': totalTimeSeconds,
    'lastAttemptedAt': lastAttemptedAt?.toIso8601String(),
    'masteryPercentage': masteryPercentage,
  };
}
```

### 6.5 API Request/Response Schemas (On-Device Server)

```dart
// Request to generate explanation
class ExplanationRequest {
  final String questionId;
  final String userAnswer;
  final String correctAnswer;
  final String questionType;
  final String grammarTopic;
  final List<String> userInterests;
  final int difficulty;
  final Map<String, dynamic>? context;

  ExplanationRequest({
    required this.questionId,
    required this.userAnswer,
    required this.correctAnswer,
    required this.questionType,
    required this.grammarTopic,
    required this.userInterests,
    required this.difficulty,
    this.context,
  });

  Map<String, dynamic> toJson() => {
    'questionId': questionId,
    'userAnswer': userAnswer,
    'correctAnswer': correctAnswer,
    'questionType': questionType,
    'grammarTopic': grammarTopic,
    'userInterests': userInterests,
    'difficulty': difficulty,
    'context': context,
  };
}

// Response from explanation generator
class ExplanationResponse {
  final String explanationText;
  final String explanationType; // 'template', 'ai_generated', 'rule_based'
  final double? confidence;
  final String? ruleApplied;
  final String? example;
  final bool followUpAvailable;
  final List<String>? relatedTopics;
  final int generationTimeMs;

  ExplanationResponse({
    required this.explanationText,
    required this.explanationType,
    this.confidence,
    this.ruleApplied,
    this.example,
    this.followUpAvailable = false,
    this.relatedTopics,
    this.generationTimeMs = 0,
  });

  factory ExplanationResponse.fromJson(Map<String, dynamic> json) => ExplanationResponse(
    explanationText: json['explanationText'],
    explanationType: json['explanationType'],
    confidence: json['confidence']?.toDouble(),
    ruleApplied: json['ruleApplied'],
    example: json['example'],
    followUpAvailable: json['followUpAvailable'] ?? false,
    relatedTopics: json['relatedTopics'] != null 
        ? List<String>.from(json['relatedTopics']) 
        : null,
    generationTimeMs: json['generationTimeMs'] ?? 0,
  );
}
```

---

## 7. Project Folder Structure

### 7.1 Optimal Flutter/Dart Folder Structure

```
dokter_grammar2/
├── android/                          # Android platform files
├── ios/                              # iOS platform files
├── lib/
│   ├── main.dart                     # App entry point
│   │
│   ├── core/                         # Core functionality
│   │   ├── constants/
│   │   │   ├── app_constants.dart    # App-wide constants
│   │   │   ├── color_scheme.dart     # Color definitions
│   │   │   └── strings.dart          # String constants
│   │   ├── database/
│   │   │   ├── database_helper.dart  # SQLite helper
│   │   │   ├── migrations/          # DB migration scripts
│   │   │   └── schema.sql            # Database schema
│   │   ├── models/                   # Data models (see section 6)
│   │   │   ├── user_profile.dart
│   │   │   ├── question.dart
│   │   │   ├── test_session.dart
│   │   │   ├── topic_performance.dart
│   │   │   └── explanation.dart
│   │   ├── services/
│   │   │   ├── local_server.dart     # On-device server
│   │   │   ├── ai_service.dart       # AI model service
│   │   │   ├── rule_engine.dart     # Rule-based explanations
│   │   │   ├── scoring_service.dart  # Level calculation
│   │   │   ├── notification_service.dart
│   │   │   └── backup_service.dart
│   │   ├── utils/
│   │   │   ├── date_utils.dart
│   │   │   ├── json_utils.dart
│   │   │   └── validation_utils.dart
│   │   └── errors/
│   │       ├── app_exception.dart
│   │       └── error_handler.dart
│   │
│   ├── data/                         # Data layer
│   │   ├── repositories/
│   │   │   ├── user_repository.dart
│   │   │   ├── question_repository.dart
│   │   │   ├── test_repository.dart
│   │   │   └── performance_repository.dart
│   │   ├── datasources/
│   │   │   ├── local/
│   │   │   │   ├── user_local_datasource.dart
│   │   │   │   ├── question_local_datasource.dart
│   │   │   │   └── test_local_datasource.dart
│   │   │   └── assets/
│   │   │       └── question_bank_loader.dart
│   │   └── providers/
│   │       └── question_bank_provider.dart
│   │
│   ├── domain/                       # Business logic
│   │   ├── entities/                 # Domain entities
│   │   ├── usecases/
│   │   │   ├── user/
│   │   │   │   ├── create_user_profile.dart
│   │   │   │   ├── update_user_level.dart
│   │   │   │   └── update_streak.dart
│   │   │   ├── test/
│   │   │   │   ├── start_test_session.dart
│   │   │   │   ├── submit_answer.dart
│   │   │   │   ├── complete_test.dart
│   │   │   │   └── calculate_score.dart
│   │   │   ├── question/
│   │   │   │   ├── get_adaptive_questions.dart
│   │   │   │   ├── get_daily_questions.dart
│   │   │   │   └── filter_by_interests.dart
│   │   │   └── explanation/
│   │   │       ├── generate_explanation.dart
│   │   │       └── get_follow_up.dart
│   │   └── algorithms/
│   │       ├── adaptive_algorithm.dart
│   │       ├── level_calculator.dart
│   │       └── topic_selector.dart
│   │
│   ├── presentation/                 # UI layer
│   │   ├── screens/
│   │   │   ├── splash/
│   │   │   │   └── splash_screen.dart
│   │   │   ├── onboarding/
│   │   │   │   ├── onboarding_screen.dart
│   │   │   │   └── profile_input_screen.dart
│   │   │   ├── test/
│   │   │   │   ├── placement_intro_screen.dart
│   │   │   │   ├── test_screen.dart
│   │   │   │   ├── test_results_screen.dart
│   │   │   │   └── explanation_screen.dart
│   │   │   ├── home/
│   │   │   │   └── home_screen.dart
│   │   │   ├── custom_test/
│   │   │   │   ├── custom_test_config_screen.dart
│   │   │   │   └── custom_test_screen.dart
│   │   │   ├── daily_test/
│   │   │   │   └── daily_test_screen.dart
│   │   │   ├── reassessment/
│   │   │   │   └── reassessment_screen.dart
│   │   │   ├── progress/
│   │   │   │   └── progress_screen.dart
│   │   │   └── settings/
│   │   │       └── settings_screen.dart
│   │   ├── widgets/
│   │   │   ├── common/
│   │   │   │   ├── custom_button.dart
│   │   │   │   ├── level_badge.dart
│   │   │   │   ├── progress_bar.dart
│   │   │   │   └── topic_card.dart
│   │   │   ├── test/
│   │   │   │   ├── question_card.dart
│   │   │   │   ├── choice_button.dart
│   │   │   │   ├── timer_widget.dart
│   │   │   │   └── hint_button.dart
│   │   │   └── charts/
│   │   │       ├── topic_breakdown_chart.dart
│   │   │       └── progress_timeline.dart
│   │   ├── providers/                # State management (Provider/Riverpod)
│   │   │   ├── user_provider.dart
│   │   │   ├── test_provider.dart
│   │   │   ├── question_provider.dart
│   │   │   └── performance_provider.dart
│   │   └── theme/
│   │       ├── app_theme.dart
│   │       ├── colors.dart
│   │       └── text_styles.dart
│   │
│   └── assets/                       # Static assets
│       ├── images/
│       │   ├── logo.png
│       │   └── icons/
│       ├── models/                   # AI models
│       │   ├── grammar_explainer.onnx
│       │   └── vocab.json
│       ├── data/
│       │   ├── question_bank.json
│       │   ├── grammar_rules.json
│       │   └── explanation_templates.json
│       └── fonts/
│
├── test/                             # Unit & widget tests
│   ├── unit/
│   │   ├── domain/
│   │   ├── data/
│   │   └── core/
│   └── widget/
│
├── pubspec.yaml                      # Dependencies
├── analysis_options.yaml
└── README.md
```

### 7.2 Key Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  provider: ^6.1.1
  # OR riverpod: ^2.4.9
  
  # Database
  sqflite: ^2.3.0
  path: ^1.8.3
  
  # Local Storage
  shared_preferences: ^2.2.2
  path_provider: ^2.1.1
  
  # JSON
  json_annotation: ^4.8.1
  
  # AI/ML (if using on-device models)
  # tflite_flutter: ^0.10.4
  # OR onnxruntime: ^1.15.0
  
  # UI
  flutter_svg: ^2.0.9
  fl_chart: ^0.65.0
  
  # Utils
  intl: ^0.18.1
  uuid: ^4.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
```

### 7.3 Asset Organization

```
assets/
├── images/
│   ├── logo/
│   │   ├── logo.png
│   │   └── logo_icon.png
│   └── illustrations/
│       ├── onboarding_1.png
│       └── onboarding_2.png
│
├── models/                           # AI models (large files)
│   ├── grammar_explainer.onnx       # ~45 MB
│   ├── vocab.json
│   └── config.json
│
├── data/                             # Initial data
│   ├── question_bank.json           # Question database
│   ├── grammar_rules.json           # Rule engine rules
│   ├── explanation_templates.json   # Template explanations
│   └── topics.json                  # Topic definitions
│
└── fonts/
    └── custom_font.ttf
```

### 7.4 Configuration Files

```
config/
├── app_config.dart                   # App configuration
├── database_config.dart              # DB settings
├── ai_config.dart                    # AI model settings
└── feature_flags.dart                # Feature toggles
```

---

## 8. Adaptive Algorithm

### 4.1 Placement Scoring

For each topic keep counters:

- `attempts`, `correct`, `avg_time`

Convert to **topic_score = correct/attempts**.

Overall level computed by weighted average across topics (weights by difficulty).

Map numeric score to levels (example thresholds):

| Level | Score Range |
|-------|-------------|
| Beginner | 0–39% |
| Elementary | 40–54% |
| Intermediate | 55–69% |
| Upper-Intermediate | 70–84% |
| Advanced | 85–100% |

*(Developer can tune thresholds during testing.)*

### 4.2 Personalization Logic for Custom Test

For a 20-question custom test:

- Allocate **50%** questions from top 3 weakest topics (by `topic_score` ascending)
- **30%** from medium topics
- **20%** random from strengths to keep variety

For Daily Test: sample uniformly, but bias slightly to weak topics.

### 4.3 Reassessment Logic (Level Up)

Reassessment passes if:

- Weighted accuracy in reassessment ≥ level threshold (e.g., ≥ level boundary + margin)
- OR improvement across weakest topics ≥ 15% over last X attempts

If pass → level up + new recommendation set.

---

## 9. Content Design

### 5.1 Question Types

- **Multiple choice (single best)** — good for grammar recognition
- **Gap fill** — choose word/form
- **Sentence combining / rewriting** — test complex sentence formation
- **Error identification** — find the incorrect part
- **Short answer (one word/phrase)** — limited use; needs auto scoring heuristics

### 5.2 Explanations / Feedback

Keep explanations:

- Short, precise, rule-based
- Always include: which part is wrong → why → correct sentence/example
- Use user interests in examples (e.g., anime-themed sentences if selected)

**Example**:

> **Correct:** "If I had known, I would have gone."
>
> **Why:** This is a third conditional for past hypothetical; structure = *if + past perfect, would have + past participle.*
>
> **Try:** "If she had studied, she would have passed the exam."

### 5.3 Microcopy Rules (UX Writing)

Use active, encouraging tone. Example CTAs:

- "Latihan Sekarang"
- "Lihat Pembahasan"
- "Reassess untuk naik level"

Notifications:

- "Daily Test tersedia — 5 pertanyaan cepat"

---

## 10. Gamification & Engagement

- **Streaks**: Reward daily practice
- **Badges**: For mastering a topic (e.g., "Tenses Doctor")
- **Progress Bar**: Per topic mastery (0–100%)
- **Reminders (Local Notifications)**: Configurable, offline
- **Limited Hints**: Preserve challenge

---

## 11. Offline & Storage Considerations

### 7.1 App Bundle Size vs Local Model Tradeoff

- If including large on-device models → warn user on install size
- Option: Ship compact rule-engine by default and provide an optional (local) model package during initial setup that user can accept to download (but user requested fully offline — so prefer bundling or allow sideload)

### 7.2 Backups

- Implement export/import of DB (file encryption optional) so user can move device
- **Permissions**: Minimal (storage for backups). No network required

---

## 12. Privacy & Security

- All data local
- No analytics collection by default
- If offering cloud backup later, require explicit opt-in and encryption
- Provide "Delete my data" button

---

## 13. Acceptance Criteria / Developer Checklist

### Core (MVP)

- [ ] App runs fully offline; local DB initialized on first run
- [ ] Onboarding with profile and interests
- [ ] Placement test: 50 questions, progress tracking, saved responses
- [ ] Scoring engine returns level and topic breakdown at end of test
- [ ] Explanation screen per question with templated explanations
- [ ] Homepage with Custom Test, Daily Test, Reassessment, Progress
- [ ] Custom Test selection respects topic weighting by weakness
- [ ] Reassessment logic updates level when thresholds met
- [ ] Local export/import backup
- [ ] Settings for interests & model preference

### Nice-to-have (Post-MVP)

- [ ] On-device generative explanation model fallback
- [ ] Speech-to-text for short answer input (offline)
- [ ] Spaced repetition scheduling for practice items
- [ ] Lightweight animations/microinteractions

---

## 14. Example User Journeys

### A. New User — "Fitri"

1. Fitri installs Dokter Grammar → splash loads → onboarding
2. Fills name "Fitri", goal "passing literature exam", interests "film, k-pop"
3. Takes placement test 50 questions → completes → score 58% → level: Intermediate
4. Topic breakdown shows "Complex Sentence" 32%, "Relative Clauses" 40%
5. Fitri presses "Start Personalized Training" → Custom Test (20 questions) with 50% from Complex Sentence
6. After 2 weeks, Fitri takes Reassessment → score increases → level up → practice recommendations change

### B. Returning User — "Andi" (Daily Habit)

1. Opens app → Homepage shows streak 5 days
2. Selects Daily Test (5 questions) → completes → instant feedback → one weak topic flagged → "Practice 3 questions lagi" → Andi starts short practice

### C. Power User — "Lina"

1. Completes placement → reviews explanations, marks unclear items
2. Requests targeted practice for conditionals → uses Custom Test → tracks progress in analytics
3. Exports backup to local file before factory reset

---

## 15. Developer Notes & Recommendations

### 11.1 Content Management

- **Question bank authoring tool**: Create editor (desktop/web) to input questions with interest tags so content team can easily add questions without rebuilding app

### 11.2 Testing & Optimization

- **Testing**: Run A/B on thresholds with sample students; adjust mapping score→level
- **Performance**: Preload next questions; lazy load explanations to avoid UI jank

### 11.3 Localization

- Default UI: Bahasa Indonesia; allow English later

### 11.4 Design Guidelines

- Prioritize clear hierarchy
- Large actionable buttons for test start
- Keep sentences in explanations short and natural

### 11.5 Minimal Wireframe (Textual)

```
Splash → Onboarding/Profile → Placement Test (50) → Results (Level + Breakdown) → Explanation (per Q) → Homepage

Homepage quick actions: [Custom Test] [Daily Test] [Reassessment] [Review]

Persistent navbar: Home | Progress | Review | Settings
```

---

## 16. Content Taxonomy

Suggested grammar topics with difficulty levels (1–5) and baseline 100–200 questions per topic for robust adaptive sampling:

1. **Tenses** (simple → perfect continuous)
2. **Modals & Auxiliaries**
3. **Conditionals** (zero → mixed)
4. **Complex Sentences** (subordination, relative clauses)
5. **Sentence Combining & Punctuation**
6. **Articles & Determiners**
7. **Subject-Verb Agreement**
8. **Passive Voice**
9. **Reported Speech**
10. **Prepositions**
11. **Adjective Clauses**
12. **Pronouns & Reference**

---

## Next Steps (Practical)

1. Create **MVP scope** based on Acceptance Criteria
2. Prepare sample **question set** (min 300 Q) and topic tag mapping
3. Design **DB schema** and small on-device server skeleton
4. Decide on explanation engine: rule-templated first; optional on-device AI later
5. UI: Create low-fi clickable prototype (Figma) based on screen descriptions above

---

## Document Version

- **Version**: 1.0
- **Last Updated**: 2024
- **Status**: Draft for Development

---

*This document is a living specification and should be updated as the product evolves.*

