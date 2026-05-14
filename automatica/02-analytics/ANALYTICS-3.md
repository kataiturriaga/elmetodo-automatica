# Analytics Tracking System

Complete reference for the El Método analytics implementation. This document covers every event, parameter, user property, and Firebase Audience used for marketing, engagement tracking, and push notification targeting.

**Analytics Provider**: Firebase Analytics (GA4)
**Infrastructure Status**: Built (`lib/core/analytics/`) — event enum, parameter constants, user properties, Riverpod provider, debug/production switching, route observer, helper extensions.
**Last Updated**: 2026-04-14

---

## Executive Summary

### Implementation Status

| Category | Wired | Total | Coverage |
|----------|-------|-------|----------|
| Screen views (route observer) | 50 | 50 | 100% |
| Screen views (navbar tabs) | 4 | 4 | 100% |
| Custom events | 89 | 112 | 79% |
| User properties | 22 | 24 | 92% |
| Firebase Audiences | 0 | 28 | 0% (need Console setup) |

### Known Issues (Boss Feedback — 2026-03-13)

| Issue | Status | Details |
|-------|--------|---------|
| screen_view not showing for ranking, home, explore | **Wired** | Route observer on root navigator + explicit `logScreenView` in `main_scaffold.dart:56`. If not showing in Firebase Console, check: (1) DebugView, (2) events take up to 24h, (3) ensure production build (debug uses NoopAnalyticsService) |
| `ranking_enrolled` from "Ver mi posición" button | **Wired** | Fires in `profile_providers.dart:149` after ranking onboarding completes |
| Backend analytics integration (payments/cancellations) | **Skipped** | Dashboard panel handles this — no Firebase integration needed |
| `program_type` parameter on `program_enroll` | **Fixed** | Now sends `program_type` (`base`/`completo`) derived from program zones in `training_providers.dart` |
| Verify `program_enroll` fires | **Wired** | Fires with: `program_id`, `program_name`, `entry_point`, `location`, `level`, `program_type` |
| `program_enroll` missing from login subscription intent | **Fixed (2026-04-08)** | `login_method_screen.dart` now fires `logProgramEnroll` when subscribing after login with pending intent |
| Paywall restore not tracked | **Fixed (2026-04-08)** | `paywall_screen.dart:_handleRestore()` now fires `logRestoreAttempted/Completed/Failed` |

### Numbers at a Glance

| Metric | Count |
|--------|-------|
| Total custom events defined | 112 |
| Events wired and sending | 89 |
| Events defined but NOT wired | 5 (intentional — see section below) |
| Automatic screen views | 50 screens |
| User properties defined | 24 (of 25 max) |
| User properties wired | 22 |
| Firebase Audiences | 28 (need Console setup) |
| GA4 custom dimensions to register | 58 event-scoped + 12 user-scoped |

---

## All Proposed Events (Master Table)

Every custom event we will track, organized by domain. Status column indicates whether the event already exists in the codebase enum or is new.

### Screen Views (48 — automatic via route observer)

These fire automatically on every navigation. No manual code needed per screen.

| # | Route | `screen_name` | Widget Class |
|---|-------|---------------|--------------|
| 1 | `/` | `home` | `HomeScreen` |
| 2 | `/training` | `training` | `TrainingScreen` |
| 3 | `/ranking` | `ranking` | `CommunityScreen` |
| 4 | `/explore` | `explore` | `ExploreScreen` |
| 5 | `/profile` | `profile` | `ProfileScreen` |
| 6 | `/login` | `login` | `LoginScreen` |
| 7 | `/login/email` | `login_email` | `EmailLoginScreen` |
| 8 | `/onboarding` | `onboarding` | `WelcomeScreen` |
| 9 | `/onboarding/home-preview` | `onboarding_home_preview` | `OnboardingHomePreviewScreen` |
| 10 | `/training/onboarding-tip` | `training_onboarding_tip` | `OnboardingTipScreen` |
| 11 | `/training/choose-program` | `training_choose_program` | `ChooseProgramScreen` |
| 12 | `/training/program-video` | `training_program_video` | `ProgramVideoScreen` |
| 13 | `/training/location` | `training_location` | `LocationSelectionScreen` |
| 14 | `/training/choose-days` | `training_choose_days` | `ChooseDaysScreen` |
| 15 | `/training/choose-location` | `training_choose_location` | `ChooseLocationScreen` |
| 16 | `/training/session` | `training_session` | `TrainingSessionScreen` |
| 17 | `/training/day` | `training_day` | `TrainingDayScreen` |
| 18 | `/training/exercise` | `exercise_detail` | `ExerciseDetailScreen` |
| 19 | `/training/exercise-video` | `exercise_video` | `ExerciseVideoScreen` |
| 20 | `/training/exercise-history` | `exercise_history` | `ExerciseHistoryScreen` |
| 21 | `/training/session-records` | `session_records` | `SessionRecordsScreen` |
| 22 | `/training/catalog` | `programs_catalog` | `ProgramsCatalogScreen` |
| 23 | `/training/program-detail` | `program_detail` | `ProgramDetailScreen` |
| 24 | `/training/complete` | `training_complete` | `TrainingCompleteScreen` |
| 25 | `/training/rate` | `training_rate` | `TrainingRateScreen` |
| 26 | `/training/program-complete` | `program_complete` | `CompletedProgramScreen` |
| 27 | `/training/rounds-session` | `rounds_session` | `RoundsSessionScreen` |
| 28 | `/training/round-log-history` | `round_log_history` | `RoundLogHistoryScreen` |
| 29 | `/explore/recipes` | `recipe_list` | `RecipeListScreen` |
| 30 | `/explore/recipes/detail` | `recipe_detail` | `RecipeDetailScreen` |
| 31 | `/explore/guides` | `guide_list` | `GuideListScreen` |
| 32 | `/explore/guides/category` | `guide_category` | `GuideCategoryScreen` |
| 33 | `/explore/guides/video` | `guide_video` | `GuideVideoScreen` |
| 34 | `/explore/calculator` | `calorie_calculator` | `CalorieCalculatorScreen` |
| 35 | `/explore/calculator/result` | `calorie_calculator_result` | `CalorieCalculatorResultScreen` |
| 36 | `/explore/satiating-foods` | `satiating_foods_list` | `SatiatingFoodListScreen` |
| 37 | `/explore/satiating-foods/detail` | `satiating_food_detail` | `SatiatingFoodDetailScreen` |
| 38 | `/explore/history` | `program_history` | `ProgramHistoryScreen` |
| 39 | `/ranking/tutorial` | `ranking_tutorial` | `RankingTutorialScreen` |
| 40 | `/profile/gender` | `profile_edit_gender` | `GenderEditScreen` |
| 41 | `/profile/age` | `profile_edit_age` | `AgeEditScreen` |
| 42 | `/profile/weight` | `profile_edit_weight` | `WeightEditScreen` |
| 43 | `/profile/height` | `profile_edit_height` | `HeightEditScreen` |
| 44 | `/profile/theme` | `theme_settings` | `ThemeSettingsScreen` |
| 45 | `/delete-account` | `delete_account` | `DeleteAccountScreen` |
| 46 | `/legal` | `legal_info` | `LegalInfoScreen` |
| 47 | `/paywall` | `paywall` | `PaywallScreen` |
| 48 | `/purchase-complete` | `purchase_complete` | `PurchaseCompleteProgramScreen` |
| 49 | `/video-banner` | `video_banner` | `VideoBannerVideoScreen` |
| 50 | `/training-schedule` | `training_schedule` | `TrainingScheduleScreen` |

### Custom Events (93 total)

Status legend:
- **Wired** = Code calls this event, it fires in production builds
- **Partial** = Event fires but missing parameters
- **Not wired** = Defined in enum/helper but no code calls it yet
- **New** = Not yet defined in enum

| # | Event Name | Domain | Status | Parameters Sent | When Fired |
|---|-----------|--------|--------|-----------------|------------|
| | **AUTHENTICATION** | | | | |
| 1 | `login_attempt` | Auth | **Wired** | `method` | `auth_providers.dart` — emailAuth() |
| 2 | `login_success` | Auth | **Wired** | `method`, `is_new_user`, `is_guest` | `auth_providers.dart` — guestLogin(), emailAuth(), social login |
| 3 | `login_failure` | Auth | **Wired** | `method`, `error_code` | `auth_providers.dart` — all auth methods |
| 4 | `sign_up_success` | Auth | **Wired** | `method` | `auth_providers.dart` — emailAuth() (new user) |
| 5 | `sign_up_failure` | Auth | **Wired** | `method`, `error_code` | `auth_providers.dart` — emailAuth() (new user fails) |
| 6 | `guest_login` | Auth | **Wired** | `is_guest` | `auth_providers.dart` — guestLogin() |
| 7 | `guest_upgrade` | Auth | **Wired** | `method` | `auth_providers.dart` — socialLogin/emailAuth when guest upgrades |
| 8 | `logout_success` | Auth | **Wired** | — | `auth_providers.dart` — logout() |
| 9 | `account_deleted` | Auth | **Wired** | — | `auth_providers.dart` — deleteAccount() |
| 10 | `session_expired` | Auth | **Wired** | `method` | `auth_providers.dart:156` — _handleSessionExpired() |
| 11 | `google_sign_in_start` | Auth | **Wired** | `method` | `auth_providers.dart` — googleLogin() |
| 12 | `google_sign_in_success` | Auth | **Wired** | `method`, `is_new_user` | `auth_providers.dart` — googleLogin() success |
| 13 | `google_sign_in_cancel` | Auth | **Wired** | — | `auth_providers.dart` — googleLogin() cancelled |
| 14 | `apple_sign_in_start` | Auth | **Wired** | `method` | `auth_providers.dart` — appleLogin() |
| 15 | `apple_sign_in_success` | Auth | **Wired** | `method`, `is_new_user` | `auth_providers.dart` — appleLogin() success |
| 16 | `apple_sign_in_cancel` | Auth | **Wired** | — | `auth_providers.dart` — appleLogin() cancelled |
| | **ONBOARDING** | | | | |
| 17 | `onboarding_start` | Onboarding | **Wired** | — | WelcomeScreen shown |
| 18 | `onboarding_complete` | Onboarding | **Wired** | — | User finishes onboarding |
| 19 | `onboarding_skip` | Onboarding | Not wired | — | User skips onboarding |
| | **TRAINING ONBOARDING** | | | | |
| 20 | `training_onboarding_continue_clicked` | Training Onboarding | **Wired** | — | User taps "Continuar" on training tip screen |
| 21 | `program_start_intent_clicked` | Training Onboarding | **Wired** | `template_id` | User taps "Empezar programa" on choose program screen |
| 22 | `program_video_viewed` | Training Onboarding | **Wired** | `program_id` | Program video screen is displayed |
| 23 | `program_video_continue_clicked` | Training Onboarding | **Wired** | `program_id` | User taps "Continuar" after watching video |
| 24 | `program_enroll_intent_clicked` | Training Onboarding | **Wired** | `program_id`, `program_name`, `location` | User taps "Suscribirse" on location selection or choose-days screen |
| 25 | `signup_method_selected` | Training Onboarding | **Wired** | `method`, `entry_point`, `program_id` | User selects signup method (google/apple/email) |
| 26 | `signup_completed` | Training Onboarding | **Wired** | `method`, `is_new_user`, `program_id` | System confirms user authenticated after signup |
| | **TRAINING** | | | | |
| 27 | `program_view` | Training | **Wired** | `program_id`, `program_name`, `content_type` | User views program detail |
| 28 | `program_video_play` | Training | Not wired | — | Watches program intro video |
| 29 | `program_enroll` | Training | **Wired** | `program_id`, `program_name`, `entry_point`, `location`, `level`, `program_type` | `training_providers.dart` — subscribeToProgramNotifier |
| 30 | `program_complete` | Training | **Wired** | `program_id`, `program_name`, `total_days` | `training_complete_screen.dart` — _logAnalytics() |
| 31 | `program_unenroll` | Training | **Wired** | `program_id`, `program_name` | `training_providers.dart` — unsubscribeFromProgram |
| 32 | `training_session_start` | Training | **Wired** | `program_id`, `day_name`, `week_number` | Starts a training day |
| 33 | `training_session_complete` | Training | **Wired** | `day_name`, `program_id`, `week_number` | `training_complete_screen.dart` — _logAnalytics() |
| 34 | `training_session_rate` | Training | **Wired** | `program_id`, `rating`, `perceived_effort` | Rates session difficulty |
| 35 | `exercise_start` | Training | **Wired** | `exercise_id`, `exercise_name`, `program_id` | Opens exercise detail |
| 36 | `exercise_set_log` | Training | **Wired** | `exercise_id`, `exercise_name`, `set_number`, `weight`, `reps` | Logs a set |
| 37 | `exercise_video_play` | Training | **Wired** | `exercise_id`, `exercise_name` | Watches exercise demo video |
| 38 | `exercise_history_view` | Training | **Wired** | `exercise_id`, `exercise_name` | Views exercise PR/history |
| 39 | `training_tab_select` | Training | **Wired** | `tab_name` | Switches training tab |
| 40 | `catalog_filter_apply` | Training | **Wired** | `gender`, `location`, `level`, `objective` | Applies catalog filters |
| 41 | `training_location_select` | Training | **Wired** | `location` | Selects training location |
| 42 | `continuation_program_view` | Training | Not wired | — | Views continuation suggestion |
| 43 | `continuation_reminder_set` | Training | Not wired | — | Sets continuation reminder |
| 44 | `program_completion_archive` | Training | **Wired** | `program_id`, `program_name` | Archives completed program from entreno card |
| 45 | `program_completion_restart` | Training | **Wired** | `program_id`, `program_name` | Restarts completed program from entreno card |
| 46 | `program_completion_start_continuation` | Training | **Wired** | `continuation_program_id`, `continuation_program_name` | `completed_program_screen.dart` |
| | **PEDOMETER / STEPS** | | | | |
| 47 | `pedometer_state_change` | Pedometer | **Wired** | `enabled`, `source` | User enables/disables steps |
| 48 | `pedometer_sync_success` | Pedometer | **Wired** | `steps`, `calories`, `source` | Data synced to backend |
| 49 | `pedometer_permission_granted` | Pedometer | **Wired** | — | `home_providers.dart` — enablePedometer() success |
| 50 | `pedometer_permission_denied` | Pedometer | **Wired** | — | `home_providers.dart` — enablePedometer() failure |
| | **EXPLORE / CONTENT** | | | | |
| 51 | `recipe_view` | Explore | **Wired** | `recipe_id`, `recipe_name`, `content_type` | Opens recipe detail |
| 52 | `recipe_favorite` | Explore | **Wired** | `recipe_id`, `recipe_name` | Favorites a recipe |
| 53 | `recipe_unfavorite` | Explore | **Wired** | `recipe_id`, `recipe_name` | Unfavorites a recipe |
| 54 | `recipe_mode_select` | Explore | **Wired** | `mode`, `recipe_id` | `recipe_detail_screen.dart` — onModeSelected |
| 55 | `recipe_filter_apply` | Explore | **Wired** | `meal_types`, `is_spicy`, `favorites_only` | Applies recipe filters |
| 56 | `guide_category_view` | Explore | **Wired** | `category_id`, `category_name`, `content_type` | Opens guide category |
| 57 | `guide_video_play` | Explore | **Wired** | `video_id`, `video_name`, `category_name` | Plays guide video |
| 58 | `calculator_start` | Explore | **Wired** | — | Opens calorie calculator |
| 59 | `calculator_complete` | Explore | **Wired** | `goal`, `gender`, `age`, `activity_level`, `bmr`, `tdee`, `goal_calories` | Sees calculator results |
| 60 | `program_history_view` | Explore | **Wired** | — | Opens training history |
| 61 | `explore_section_tap` | Explore | **Wired** | `section_name` | `explore_screen.dart` — onTap for catalog/history/guides/recipes |
| 62 | `satiating_food_list_view` | Explore | **Wired** | — | `satiating_food_list_screen.dart` — initState |
| 63 | `satiating_food_detail_view` | Explore | **Wired** | `food_id`, `food_name`, `food_category` | `satiating_food_detail_screen.dart` — on data load |
| 64 | `satiating_food_favorite` | Explore | **Wired** | `food_id`, `food_name`, `is_favorite` | `satiating_food_detail_screen.dart` — favorite toggle |
| 65 | `satiating_food_filter_apply` | Explore | **Wired** | `food_category` | `satiating_food_list_screen.dart` — category chip tap |
| | **RANKING / COMMUNITY** | | | | |
| 66 | `ranking_view` | Ranking | Not wired | — | Views ranking screen |
| 67 | `ranking_enrolled` | Ranking | **Wired** | — (no params) | Joins ranking (fires in `profile_providers.dart:149` after ranking onboarding) |
| 68 | `ranking_filter_change` | Ranking | **Wired** | `filter_type` | `community_screen.dart` — _onFilterTap() |
| 69 | `ranking_tutorial_completed` | Ranking | **Wired** | — | `ranking_tutorial_screen.dart` — user views all 5 pages |
| | **PROFILE** | | | | |
| 70 | `profile_view` | Profile | Not wired | — | Opens profile screen |
| 71 | `profile_field_update` | Profile | **Wired** | `field_name` | `profile_providers.dart` — updateProfile() |
| 72 | `profile_photo_change` | Profile | **Wired** | — | `profile_providers.dart` — uploadProfilePicture() |
| | **ACTIVITY LOGGING** | | | | |
| 73 | `activity_create` | Activity | **Wired** | `activity_type`, `duration_minutes` | `activities_providers.dart` — createActivity() |
| 74 | `activity_delete` | Activity | **Wired** | — | `weekly_activity_log_section.dart` |
| | **APP ENGAGEMENT** | | | | |
| 75 | `tab_select` | Engagement | **Wired** | `tab_name` | Bottom nav tap (in `main_scaffold.dart:53`) |
| 76 | `share_content` | Engagement | Not wired | — | Any share action |
| 77 | `notification_received` | Engagement | **Wired** | `notification_type` | `messaging_service.dart` — _handleForegroundMessage() |
| 78 | `notification_tap` | Engagement | **Wired** | `notification_type`, `action` | `messaging_service.dart` — _handleMessageOpenedApp() |
| | **SUBSCRIPTION / IAP** | | | | |
| 79 | `paywall_viewed` | Subscription | **Wired** | `entry_point` | User sees paywall screen |
| 80 | `purchase_started` | Subscription | **Wired** | `subscription_tier`, `product_id` | User initiates purchase |
| 81 | `purchase_completed` | Subscription | **Wired** | `subscription_tier`, `is_trial`, `product_id` | Purchase verified |
| 82 | `purchase_cancelled` | Subscription | **Wired** | `subscription_tier` | User cancels purchase flow |
| 83 | `purchase_failed` | Subscription | **Wired** | `subscription_tier`, `error_message` | Purchase fails |
| 84 | `restore_attempted` | Subscription | **Wired** | — | User taps Restore Purchases |
| 85 | `restore_completed` | Subscription | **Wired** | — | Restore succeeds |
| 86 | `restore_failed` | Subscription | **Wired** | `error_message` | Restore fails |
| 87 | `trial_banner_tapped` | Subscription | **Wired** | `days_remaining`, `variant` | `trial_expiry_banner.dart` |
| | **ROUNDS (RONDAS v2)** | | | | |
| 88 | `rounds_session_started` | Rounds | **Wired** | `round_mode`, `round_count`, `time_limit`, `exercise_count` | `rounds_session_screen.dart` — session begins |
| 89 | `rounds_session_completed` | Rounds | **Wired** | `round_mode`, `rounds_completed`, `total_time_ms` | `rounds_session_screen.dart` — session saved |
| 90 | `rounds_session_abandoned` | Rounds | **Wired** | `round_mode`, `rounds_completed`, `round_count` | `rounds_session_screen.dart` — partial save on back |
| 91 | `round_log_history_view` | Rounds | **Wired** | `round_mode` | `round_log_history_screen.dart` — initState |
| | **ERRORS** | | | | |
| 92 | `error_occurred` | Error | Not wired | — | Generic error |
| 93 | `network_error` | Error | Not wired | — | Network failure |
| 94 | `api_error` | Error | Not wired | — | API error response |
| | **VIDEO BANNER (HOME)** | | | | |
| 95 | `video_banner_shown` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `days_shown` | `video_banner_card.dart` — once per widget instance when banner becomes visible |
| 96 | `video_banner_dismissed` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `days_shown` | `video_banner_card.dart` — when banner expires (API returns `showBanner: false` after previously shown) |
| 97 | `video_opened` | Home | **Wired** | `video_id`, `video_title`, `user_type` | `video_banner_video_screen.dart` — initState (user taps banner, opens video) |
| 98 | `video_completed` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `seconds_watched`, `percent_watched` | `video_banner_video_screen.dart` — video reaches the end |
| 99 | `video_closed_early` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `seconds_watched`, `percent_watched` | `video_banner_video_screen.dart` — user closes video before end (dispose) |
| 100 | `video_cta_shown` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `cta_type` | `video_banner_video_screen.dart` — CTA panel visible on screen open |
| 101 | `video_cta_tapped` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `cta_type` | `video_banner_video_screen.dart` — CTA button pressed (`choose_program` or `motivation`) |
| 102 | `video_cta_dismissed` | Home | **Wired** | `video_id`, `video_title`, `user_type`, `cta_type` | `video_banner_video_screen.dart` — user closes screen without tapping CTA (dispose) |
| | **TRAINING SCHEDULE** | | | | |
| 103 | `training_schedule_viewed` | Training | **Wired** | `is_editing` | `training_schedule_screen.dart` — initState |
| 104 | `training_schedule_saved` | Training | **Wired** | `day_count`, `reminder_minutes`, `is_update` | `training_schedule_screen.dart` — after successful save |
| 105 | `training_schedule_deleted` | Training | **Wired** | — | `training_schedule_provider.dart` — delete() |
| | **APP LIFECYCLE** | | | | |
| 106 | `app_open` | Lifecycle | **Wired** | — | `app_startup_provider.dart` — _initializePostAuth() |

**Summary by status**:
- **Wired** (sending data in production): 89 events
- **Not wired** (defined but no code calls it): 8 events (mostly error tracking, share, continuation views, ranking_view, profile_view)
- Remaining unwired events are low-priority or have no UI trigger (e.g., `onboarding_skip` has no skip button)

### Remaining Gaps

All boss-reported issues are resolved. Remaining unwired events are low-priority:

1. **`continuation_program_view` / `continuation_reminder_set`** — not wired (continuation feature barely used)
2. **`program_video_play`** — not wired (program intro video auto-plays, `program_video_viewed` already tracks the screen)
3. **`ranking_viewed` / `profile_viewed`** — not wired as explicit events (covered by `screen_view` via route observer)
4. **`share_content`** — not wired (no share feature implemented yet)
5. **Error events (`error_occurred`, `network_error`, `api_error`)** — not wired (Crashlytics handles errors)
6. **`onboarding_skip`** — no skip UI exists, event is not applicable
6. **`onboarding_skip`** — no skip UI exists, event is not applicable

---

## All User Properties (22 of 25 max)

| # | Property | Values | Status | Set When | Marketing Use |
|---|----------|--------|--------|----------|---------------|
| 1 | `is_guest` | `true` / `false` | **Wired** | Login | Segment guests vs registered |
| 2 | `auth_method` | `google` / `apple` / `email` / `guest` | **Wired** | Login | Auth method breakdown |
| 3 | `pedometer_enabled` | `true` / `false` | **Wired** | Toggle | Steps feature adoption |
| 4 | `notifications_enabled` | `true` / `false` | **Wired** | App start + sensor permissions | Push notification eligibility |
| 5 | `app_version` | `1.0.0+20` | **Wired** | App start | Version-specific campaigns |
| 6 | `platform` | `iOS` / `Android` | **Wired** | App start | Platform targeting |
| 7 | `language` | `es` | **Wired** | App start | Language targeting |
| 8 | `theme` | `system` / `light` / `dark` | **Wired** | Theme settings | — |
| 9 | `account_created_at` | ISO date | Not wired | Registration | New user campaigns |
| 10 | `last_login_at` | ISO date | **Wired** | App start | Recency targeting |
| 11 | `gender` | `male` / `female` | **Wired** | Profile fetch/update | Gender-targeted campaigns |
| 12 | `age_group` | `18_24` / `25_34` / `35_44` / `45_54` / `55_plus` | **Wired** | Profile fetch/update | Age-targeted content |
| 13 | `fitness_goal` | `lose_weight` / `maintain` / `gain_muscle` | **Wired** | Calculator complete | Goal-specific programs |
| 14 | `training_level` | `beginner` / `intermediate` / `advanced` | **Wired** | Program enrollment | Level-appropriate suggestions |
| 15 | `training_location` | `gym` / `home_bands` / `home_dumbbells` | **Wired** | Program enrollment | Location-specific programs |
| 16 | `has_active_program` | `true` / `false` | **Wired** | Enroll / unenroll / complete | Re-engagement campaigns |
| 17 | `active_program_name` | Program name string | **Wired** | Program enrollment | Program-specific messaging |
| 18 | `completed_programs` | Count as string (`0`, `1`, `2`...) | **Wired** | Program completion | Loyalty / progression campaigns |
| 19 | `days_since_last_training` | `0` / `1_7` / `8_14` / `15_30` / `30_plus` | **Wired** | Session complete / app open | Churn prevention |
| 20 | `total_training_sessions` | Count as string | Not wired | Session completion | Engagement tiers |
| 21 | `subscription_tier` | `monthly` / `quarterly` / `yearly` / `none` | **Wired** | Purchase/restore | Monetization |
| 22 | `subscription_status` | `active` / `trial` / `expired` / `none` | **Wired** | Purchase/restore | Monetization |

**Wired**: 18 of 22 | **Not wired**: 4 of 22 (`account_created_at`, `total_training_sessions`, `favorite_recipes_count`, `has_used_calculator` — these are set by their respective events, but not on app startup) | **Remaining slots**: 3

---

## All Firebase Audiences (22)

These are user segments created in Firebase Console. They auto-populate based on events + user properties and can be used as targets for push notifications via Firebase Cloud Messaging.

### Acquisition & Activation (4)

| # | Audience Name | Condition | Push Notification Campaign |
|---|--------------|-----------|---------------------------|
| 1 | New Users (7d) | `account_created_at` within last 7 days | Welcome series, onboarding tips |
| 2 | Guests Not Registered | `is_guest = true` for 3+ days | "Create an account to save your progress!" |
| 3 | Registered No Program | `is_guest = false` AND `has_active_program = false` | "Start your first program today!" |
| 4 | Onboarding Dropoff | `onboarding_start` fired but NOT `onboarding_complete` | "Complete your setup to get started" |

### Engagement & Retention (7)

| # | Audience Name | Condition | Push Notification Campaign |
|---|--------------|-----------|---------------------------|
| 5 | Active Trainers | `training_session_complete` in last 7 days | Motivational content, new features |
| 6 | Lapsed Trainers (7-14d) | `has_active_program = true` AND `days_since_last_training = 8_14` | "We miss you! Get back on track" |
| 7 | Churning Users (30d+) | `days_since_last_training = 30_plus` | Win-back with special program offer |
| 8 | Completed a Program | `program_complete` event fired | "Ready for your next challenge?" |
| 9 | High Step Counters | `pedometer_enabled = true` AND high step patterns | Community challenges |
| 10 | Recipe Enthusiasts | `favorite_recipes_count >= 3` | "New recipes just added!" |
| 11 | Calculator Users | `has_used_calculator = true` | Nutrition-focused content |

### Segmentation by Profile (8)

| # | Audience Name | Condition | Push Notification Campaign |
|---|--------------|-----------|---------------------------|
| 12 | Gym Users | `training_location = gym` | Gym-specific programs and tips |
| 13 | Home Workout Users | `training_location` starts with `home_` | Home workout content |
| 14 | Weight Loss Goal | `fitness_goal = lose_weight` | Diet tips, cardio programs |
| 15 | Muscle Gain Goal | `fitness_goal = gain_muscle` | Strength programs, protein recipes |
| 16 | Beginners | `training_level = beginner` | Intro content, technique guides |
| 17 | Advanced Athletes | `training_level = advanced` AND `total_training_sessions >= 50` | Advanced programs, PRs |
| 18 | Men 25-34 | `gender = male` AND `age_group = 25_34` | Targeted program ads |
| 19 | Women 25-34 | `gender = female` AND `age_group = 25_34` | Targeted program ads |

### Lifecycle (3)

| # | Audience Name | Condition | Push Notification Campaign |
|---|--------------|-----------|---------------------------|
| 20 | Power Users | 5+ `training_session_complete` in 7 days | Beta features, referral program |
| 21 | Feature Discoverers | Used 3+ features (training + recipes + calculator + ranking) | Cross-feature promotion |
| 22 | Notification Opted-In | `notifications_enabled = true` | All push campaigns (base audience) |

---

## All Event Parameters (48 unique keys)

Every parameter key used across events. Each must be registered as a **custom dimension** in GA4 Console.

| # | Parameter Key | Type | Used By Events | Example Value |
|---|--------------|------|----------------|---------------|
| 1 | `method` | string | Auth events | `google`, `apple`, `email` |
| 2 | `is_new_user` | boolean | `login_success`, social auth | `true` |
| 3 | `is_guest` | boolean | `login_success` | `true` |
| 4 | `error_code` | string | Failure events | `auth/invalid-email` |
| 5 | `error_message` | string | Error events | `Network timeout` |
| 6 | `device_id` | string | `guest_login` | `elmetodo_uuid-v4` |
| 7 | `content_type` | string | View events | `program`, `recipe`, `guide` |
| 8 | `content_id` | string | Share events | `123` |
| 9 | `item_name` | string | Share events | `Programa Fuerza` |
| 10 | `program_id` | int | Training events | `42` |
| 11 | `program_name` | string | Training events | `Fuerza Básica` |
| 12 | `exercise_id` | int | Exercise events | `156` |
| 13 | `exercise_name` | string | Exercise events | `Press banca` |
| 14 | `day_name` | string | Session events | `Día 1 - Pecho` |
| 15 | `week_number` | int | Session events | `3` |
| 16 | `duration_seconds` | int | `training_session_complete` | `2400` |
| 17 | `exercises_completed` | int | `training_session_complete` | `6` |
| 18 | `set_number` | int | `exercise_set_log` | `3` |
| 19 | `weight` | double | `exercise_set_log` | `80.0` |
| 20 | `reps` | int | `exercise_set_log` | `10` |
| 21 | `rating` | int | `training_session_rate` | `4` |
| 22 | `perceived_effort` | int | `training_session_rate` | `7` |
| 23 | `location` | string | Training events | `gym`, `home_bands` |
| 24 | `level` | string | Training events | `beginner` |
| 25 | `total_days` | int | Program events | `24` |
| 26 | `completed_days` | int | `program_unenroll` | `18` |
| 27 | `duration_weeks` | int | `program_complete` | `4` |
| 28 | `tab_name` | string | Tab events | `training`, `catalog` |
| 29 | `objective` | string | `catalog_filter_apply` | `fuerza` |
| 30 | `recipe_id` | int | Recipe events | `89` |
| 31 | `recipe_name` | string | Recipe events | `Pollo con arroz` |
| 32 | `mode` | string | `recipe_mode_select` | `ligero`, `normal`, `bestia` |
| 33 | `meal_types` | string | `recipe_filter_apply` | `desayuno,comida` |
| 34 | `section_name` | string | `explore_section_tap` | `recipes`, `guides` |
| 35 | `category_id` | int | Guide events | `5` |
| 36 | `category_name` | string | Guide events | `Técnica` |
| 37 | `video_id` | int | Video events | `22` |
| 38 | `video_name` | string | Video events | `Sentadilla correcta` |
| 39 | `template_id` | string | Training onboarding events | `Fuerza Básica` |
| 40 | `entry_point` | string | `program_enroll` | `onboarding`, `catalog` |
| 41 | `program_type` | string | `program_enroll` | `Completo`, `Base`, `Subscripcion`, `Gratis` |
| 42 | `program_goal` | string | `program_enroll` | `Fuerza`, `Hipertrofia` |
| 43 | `program_secondary_goal` | string | `program_enroll` | `Ganar masa muscular` |
| 44 | `food_id` | int | Satiating food events | `15` |
| 45 | `food_name` | string | Satiating food events | `Pollo` |
| 46 | `food_category` | string | Satiating food events | `proteins`, `vegetables` |
| 47 | `is_favorite` | boolean | Satiating food events | `true` |
| 48 | `round_mode` | string | Rounds events | `rounds`, `emom`, `amrap`, `for_time` |
| 49 | `video_title` | string | Video banner events | `Entrena fuerza en casa` |
| 50 | `user_type` | string | Video banner events | `guest`, `trial` |
| 51 | `cta_type` | string | Video banner CTA events | `choose_program`, `motivation` |
| 52 | `seconds_watched` | int | `video_completed`, `video_closed_early` | `45` |
| 53 | `percent_watched` | int | `video_completed`, `video_closed_early` | `0`–`100` |
| 54 | `days_shown` | int | `video_banner_shown`, `video_banner_dismissed` | `1`–`3` |
| 55 | `day_count` | int | `training_schedule_saved` | `2` |
| 56 | `reminder_minutes` | int | `training_schedule_saved` | `5`, `15`, `30` |
| 57 | `is_update` | boolean | `training_schedule_saved` | `true` |
| 58 | `is_editing` | boolean | `training_schedule_viewed` | `true` |

> Less frequently used parameters (`goal`, `gender`, `age`, `activity_level`, `bmr`, `tdee`, `goal_calories`, `filter_type`, `field_name`, `value`, `notification_type`, `action`, `activity_type`, `duration_minutes`, `source`, `steps`, `calories`, `endpoint`, `status_code`, `error_type`, `is_spicy`, `favorites_only`, `round_count`, `time_limit`, `exercise_count`, `rounds_completed`, `total_time_ms`) are documented in the detailed event sections below.

---

## Table of Contents

1. [Event Naming Convention](#event-naming-convention)
2. [Existing Infrastructure](#existing-infrastructure)
3. [Screen Views](#1-screen-views)
4. [Authentication Events](#2-authentication-events)
5. [Onboarding Events](#3-onboarding-events)
6. [Training Onboarding Events](#3a-training-onboarding-events)
7. [Training Events](#4-training-events)
8. [Pedometer / Steps Events](#5-pedometer--steps-events)
9. [Explore / Content Events](#6-explore--content-events)
10. [Ranking / Community Events](#7-ranking--community-events)
11. [Profile Events](#8-profile-events)
12. [Activity Logging Events](#9-activity-logging-events)
13. [App Engagement Events](#10-app-engagement-events)
14. [User Properties](#user-properties)
15. [Firebase Audiences](#firebase-audiences)
16. [Implementation Guide](#implementation-guide)
17. [GA4 Custom Dimensions Checklist](#ga4-custom-dimensions-registration-checklist)
18. [Verification](#verification)
19. [Key Files Reference](#key-files-reference)

---

## Event Naming Convention

Following [GA4 best practices](https://support.google.com/analytics/answer/13316687):

| Rule | Detail |
|------|--------|
| **Format** | `snake_case`, all lowercase |
| **Structure** | `{domain}_{action}` or `{action}_{object}` (verb_noun) |
| **Max length** | 40 characters |
| **Reserved prefixes** | Never use `ga_`, `firebase_`, `google_` |
| **Max custom events** | 500 per project |
| **Max parameters per event** | 25 |
| **Max user properties** | 25 |

### Reusable Verbs

Use these verbs consistently across all domains:

| Verb | Meaning | Example |
|------|---------|---------|
| `view` | User sees content | `recipe_view`, `program_view` |
| `select` | User chooses an option | `tab_select`, `recipe_mode_select` |
| `start` | User begins a flow | `training_session_start`, `calculator_start` |
| `complete` | User finishes a flow | `training_session_complete`, `onboarding_complete` |
| `create` | User creates something | `activity_create` |
| `delete` | User removes something | `activity_delete` |
| `tap` | User taps a UI element | `explore_section_tap` |
| `play` | User plays media | `guide_video_play`, `exercise_video_play` |
| `apply` | User applies a filter | `catalog_filter_apply`, `recipe_filter_apply` |
| `enroll` | User joins something | `program_enroll`, `ranking_enrolled` |

### Reusable Parameter Keys

These parameters appear across multiple events for cross-domain correlation:

| Key | Type | Used In |
|-----|------|---------|
| `content_type` | `string` | `program`, `recipe`, `guide`, `exercise` |
| `content_id` | `string` | Any content item's ID |
| `item_name` | `string` | Human-readable name of any item |
| `method` | `string` | Auth method (`google`, `apple`, `email`, `guest`) |
| `error_code` | `string` | Error identifiers |

---

## Infrastructure (Current State)

### Files

| File | Purpose |
|------|---------|
| `lib/core/analytics/analytics_service.dart` | Abstract interface, `AnalyticsEvent` enum, `AnalyticsParams`, `UserProperties` |
| `lib/core/analytics/firebase_analytics_service.dart` | Firebase Analytics implementation |
| `lib/core/analytics/noop_analytics_service.dart` | No-op implementation for debug mode (logs to console) |
| `lib/core/analytics/analytics_providers.dart` | Riverpod provider + helper extensions |
| `lib/core/analytics/analytics_route_observer.dart` | Auto screen view tracking on navigation |

### Helper Extensions

| Extension | Methods | Location |
|-----------|---------|----------|
| `AnalyticsAuthExtension` | `logLogin()`, `logSignUp()`, `logSocialSignInStart()`, `logSocialSignInResult()`, `setAuthUserProperties()`, `clearUserProperties()` | `analytics_providers.dart` |
| `AnalyticsTrainingExtension` | `logProgramEnroll()`, `logProgramEnrollIntent()`, `logProgramView()`, `logTrainingSessionStart()`, `logTrainingSessionRate()`, etc. | `analytics_providers.dart` |
| `AnalyticsExploreExtension` | `logRecipeView()`, `logRecipeFavorite()`, `logGuideVideoPlay()`, `logCalculatorStart()`, etc. | `analytics_providers.dart` |
| `AnalyticsSubscriptionExtension` | `logPaywallViewed()`, `logPurchaseStarted()`, `logPurchaseCompleted()`, `logRestoreAttempted()`, etc. | `analytics_providers.dart` |
| `AnalyticsPedometerExtension` | `logPedometerStateChange()`, `logPedometerSync()` | `analytics_providers.dart` |
| `AnalyticsEngagementExtension` | `logTabSelect()` | `analytics_providers.dart` |
| `AnalyticsErrorExtension` | `logError()`, `logNetworkError()`, `logApiError()` | `analytics_providers.dart` |
| `AnalyticsVideoBannerExtension` | `logVideoBannerShown()`, `logVideoBannerDismissed()`, `logVideoOpened()`, `logVideoCompleted()`, `logVideoClosedEarly()`, `logVideoCtaShown()`, `logVideoCtaTapped()`, `logVideoCtaDismissed()` | `analytics_providers.dart` |
| `AnalyticsTrainingScheduleExtension` | `logTrainingScheduleViewed()`, `logTrainingScheduleSaved()`, `logTrainingScheduleDeleted()` | `analytics_providers.dart` |

### Debug vs Production

```dart
// analytics_providers.dart
if (AppConfig.isDebug) {
  return NoopAnalyticsService();  // Logs to console, no Firebase pollution
}
return FirebaseAnalyticsService();  // Real Firebase Analytics
```

**Important**: `AppConfig.isDebug` uses `kDebugMode` — only `false` in release/profile builds. Development Firebase distribution builds (APP_ENV=development) still use the real FirebaseAnalyticsService because they're release builds.

### Screen View Tracking

Two mechanisms work together:
1. **`AnalyticsRouteObserver`** — registered on GoRouter's root navigator, fires `screen_view` on every `didPush`/`didReplace`. Covers 48 routes.
2. **`MainScaffold._onNavTap()`** — explicitly calls `logScreenView()` + `logTabSelect()` on bottom nav taps (lines 53-58). This compensates for shell route tab switches not triggering the route observer.

### Currently Wired Events (78/93)

| Event | Where Fired | Notes |
|-------|-------------|-------|
| `login_attempt` | Auth providers | emailAuth() |
| `login_success` | Auth providers | All auth methods |
| `login_failure` | Auth providers | All auth methods |
| `sign_up_success` | Auth providers | emailAuth() new user |
| `sign_up_failure` | Auth providers | emailAuth() new user |
| `guest_login` | Auth providers | guestLogin() |
| `guest_upgrade` | Auth providers | Guest → registered |
| `logout_success` | Auth providers | |
| `account_deleted` | Delete account flow | |
| `session_expired` | Auth providers | _handleSessionExpired() |
| `google_sign_in_start` | Auth providers | googleLogin() |
| `google_sign_in_success` | Auth providers | googleLogin() |
| `google_sign_in_cancel` | Auth providers | googleLogin() |
| `apple_sign_in_start` | Auth providers | appleLogin() |
| `apple_sign_in_success` | Auth providers | appleLogin() |
| `apple_sign_in_cancel` | Auth providers | appleLogin() |
| `onboarding_start` | Welcome screen | |
| `onboarding_complete` | Onboarding flow | |
| `training_onboarding_continue_clicked` | Tip screen | |
| `program_start_intent_clicked` | Choose program screen | |
| `program_video_viewed` | Program video screen | |
| `program_video_continue_clicked` | After video | |
| `program_enroll_intent_clicked` | Location/choose-days screen | |
| `signup_method_selected` | Login method screen | |
| `signup_completed` | After auth in onboarding | |
| `program_view` | Program detail screen | |
| `program_enroll` | `training_providers.dart` + `login_method_screen.dart` | Includes `program_type`. Also fires from login subscription intent flow |
| `program_complete` | `training_complete_screen.dart` | |
| `program_unenroll` | `training_providers.dart` | |
| `training_session_complete` | `training_complete_screen.dart` | |
| `program_completion_archive` | Training card | |
| `program_completion_restart` | Training card | |
| `training_session_start` | Training session screen | |
| `training_session_rate` | Rating screen | |
| `exercise_start` | Exercise detail | |
| `exercise_set_log` | Set logging | |
| `exercise_video_play` | Exercise detail (before nav) | |
| `exercise_history_view` | Exercise detail (before nav) | |
| `training_tab_select` | Training screen tabs | |
| `training_location_select` | Location screen | |
| `catalog_filter_apply` | Catalog filters | |
| `pedometer_state_change` | Pedometer toggle | |
| `pedometer_sync_success` | Pedometer sync | |
| `pedometer_permission_granted` | `home_providers.dart` | enablePedometer() success |
| `pedometer_permission_denied` | `home_providers.dart` | enablePedometer() failure |
| `recipe_view` | Recipe detail | |
| `recipe_favorite` | Recipe favorite toggle | |
| `recipe_unfavorite` | Recipe unfavorite toggle | |
| `recipe_mode_select` | Recipe detail screen | Mode: ligero/normal/bestia |
| `recipe_filter_apply` | Recipe filters | |
| `guide_category_view` | Guide category | |
| `guide_video_play` | Guide video | |
| `calculator_start` | Calculator flow | |
| `calculator_complete` | Calculator result | |
| `program_history_view` | History screen | |
| `explore_section_tap` | Explore screen | catalog/history/guides/recipes/satiating-foods |
| `satiating_food_list_view` | Satiating food list screen | initState |
| `satiating_food_detail_view` | Satiating food detail screen | On data load |
| `satiating_food_favorite` | Satiating food detail screen | Favorite toggle |
| `satiating_food_filter_apply` | Satiating food list screen | Category chip tap |
| `ranking_enrolled` | Ranking onboarding complete | |
| `ranking_filter_change` | Community screen | global/by_age/by_group |
| `ranking_tutorial_completed` | Ranking tutorial screen | User views all 5 pages |
| `profile_updated` | Profile providers | field_name param |
| `profile_photo_changed` | Profile providers | |
| `activity_created` | Activities providers | |
| `activity_deleted` | Weekly activity log | |
| `tab_select` | Bottom nav (`main_scaffold.dart`) | |
| `notification_received` | Messaging service | |
| `notification_tap` | Messaging service | |
| `program_completion_start_continuation` | Completed program screen | |
| `trial_banner_tapped` | Trial expiry banner | |
| `app_open` | App startup provider | |
| `paywall_viewed` | Paywall screen | |
| `purchase_started` | Purchase flow | |
| `purchase_completed` | Purchase success | |
| `purchase_cancelled` | Purchase cancelled | |
| `purchase_failed` | Purchase error | |
| `restore_attempted` | Paywall screen + Community screen | Both restore flows tracked |
| `restore_completed` | Paywall screen + Community screen | |
| `restore_failed` | Paywall screen + Community screen | |
| `rounds_session_started` | Rounds session screen | Session begins |
| `rounds_session_completed` | Rounds session screen | Session saved |
| `rounds_session_abandoned` | Rounds session screen | Partial save on back |
| `round_log_history_view` | Round log history screen | initState |
| `video_banner_shown` | `video_banner_card.dart` | Once per widget instance |
| `video_banner_dismissed` | `video_banner_card.dart` | Banner expires |
| `video_opened` | `video_banner_video_screen.dart` | initState |
| `video_completed` | `video_banner_video_screen.dart` | Video reaches end |
| `video_closed_early` | `video_banner_video_screen.dart` | dispose (if not completed) |
| `video_cta_shown` | `video_banner_video_screen.dart` | initState |
| `video_cta_tapped` | `video_banner_video_screen.dart` | CTA button press |
| `video_cta_dismissed` | `video_banner_video_screen.dart` | dispose (if CTA not tapped) |
| `training_schedule_viewed` | `training_schedule_screen.dart` | initState |
| `training_schedule_saved` | `training_schedule_screen.dart` | Save success |
| `training_schedule_deleted` | `training_schedule_provider.dart` | delete() |

---

## Complete Event Catalog

### 1. Screen Views

Screen views are logged automatically via `AnalyticsRouteObserver` (to be created). Every navigation fires `screen_view` with:

| Parameter | Type | Example |
|-----------|------|---------|
| `screen_name` | `string` | `home`, `training`, `recipe_detail` |
| `screen_class` | `string` | `HomeScreen`, `RecipeDetailScreen` |

#### Screen Name Mapping (Route to Analytics Name)

| Route | Screen Name | Widget Class |
|-------|-------------|--------------|
| `/` | `home` | `HomeScreen` |
| `/training` | `training` | `TrainingScreen` |
| `/ranking` | `ranking` | `CommunityScreen` |
| `/explore` | `explore` | `ExploreScreen` |
| `/profile` | `profile` | `ProfileScreen` |
| `/login` | `login` | `LoginScreen` |
| `/login/email` | `login_email` | `EmailLoginScreen` |
| `/onboarding` | `onboarding` | `WelcomeScreen` |
| `/onboarding/home-preview` | `onboarding_home_preview` | `OnboardingHomePreviewScreen` |
| `/training/onboarding-tip` | `training_onboarding_tip` | `OnboardingTipScreen` |
| `/training/choose-program` | `training_choose_program` | `ChooseProgramScreen` |
| `/training/program-video` | `training_program_video` | `ProgramVideoScreen` |
| `/training/location` | `training_location` | `LocationSelectionScreen` |
| `/training/session` | `training_session` | `TrainingSessionScreen` |
| `/training/day` | `training_day` | `TrainingDayScreen` |
| `/training/exercise` | `exercise_detail` | `ExerciseDetailScreen` |
| `/training/exercise-video` | `exercise_video` | `ExerciseVideoScreen` |
| `/training/exercise-history` | `exercise_history` | `ExerciseHistoryScreen` |
| `/training/session-records` | `session_records` | `SessionRecordsScreen` |
| `/training/catalog` | `programs_catalog` | `ProgramsCatalogScreen` |
| `/training/program-detail` | `program_detail` | `ProgramDetailScreen` |
| `/training/complete` | `training_complete` | `TrainingCompleteScreen` |
| `/training/rate` | `training_rate` | `TrainingRateScreen` |
| `/explore/recipes` | `recipe_list` | `RecipeListScreen` |
| `/explore/recipes/detail` | `recipe_detail` | `RecipeDetailScreen` |
| `/explore/guides` | `guide_list` | `GuideListScreen` |
| `/explore/guides/category` | `guide_category` | `GuideCategoryScreen` |
| `/explore/guides/video` | `guide_video` | `GuideVideoScreen` |
| `/explore/calculator` | `calorie_calculator` | `CalorieCalculatorScreen` |
| `/explore/calculator/result` | `calorie_calculator_result` | `CalorieCalculatorResultScreen` |
| `/explore/history` | `program_history` | `ProgramHistoryScreen` |
| `/profile/gender` | `profile_edit_gender` | `GenderEditScreen` |
| `/profile/age` | `profile_edit_age` | `AgeEditScreen` |
| `/profile/weight` | `profile_edit_weight` | `WeightEditScreen` |
| `/profile/height` | `profile_edit_height` | `HeightEditScreen` |
| `/delete-account` | `delete_account` | `DeleteAccountScreen` |
| `/legal` | `legal_info` | `LegalInfoScreen` |
| `/legal/document` | `legal_document` | `LegalDocumentScreen` |

---

### 2. Authentication Events

**Status**: All auth events fully wired in `auth_providers.dart`. Guest login, email auth, Google sign-in, Apple sign-in, logout, and account deletion all fire their respective events with proper parameters.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `login_attempt` | `loginAttempt` | `method` | User taps any login button |
| `login_success` | `loginSuccess` | `method`, `is_new_user`, `is_guest` | Login succeeds |
| `login_failure` | `loginFailure` | `method`, `error_code` | Login fails |
| `sign_up_success` | `signUpSuccess` | `method` | New account created |
| `sign_up_failure` | `signUpFailure` | `method`, `error_code` | Signup fails |
| `guest_login` | `guestLogin` | `device_id` | Guest auth with device ID |
| `guest_upgrade` | `guestUpgrade` | `method` | Guest registers/links account |
| `logout_success` | `logoutSuccess` | — | User logs out |
| `account_deleted` | `accountDeleted` | — | Account deletion completes |
| `session_expired` | `sessionExpired` | — | Token refresh fails |
| `google_sign_in_start` | `googleSignInStart` | — | Taps Google button |
| `google_sign_in_success` | `googleSignInSuccess` | `is_new_user` | Google auth completes |
| `google_sign_in_cancel` | `googleSignInCancel` | — | User cancels Google flow |
| `apple_sign_in_start` | `appleSignInStart` | — | Taps Apple button |
| `apple_sign_in_success` | `appleSignInSuccess` | `is_new_user` | Apple auth completes |
| `apple_sign_in_cancel` | `appleSignInCancel` | — | User cancels Apple flow |

**Implementation file**: `lib/features/auth/presentation/providers/auth_providers.dart`

**Example**:
```dart
// In social auth provider
analytics.logSocialSignInStart('google');
// ... auth flow ...
analytics.logSocialSignInResult(
  provider: 'google',
  success: true,
  isNewUser: response.isNewUser,
);
```

---

### 3. Onboarding Events

**Status**: `onboarding_start` and `onboarding_complete` wired in `welcome_screen.dart`. `onboarding_skip` not applicable (no skip button exists).

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `onboarding_start` | `onboardingStart` | — | WelcomeScreen shown |
| `onboarding_complete` | `onboardingComplete` | — | User finishes onboarding |
| `onboarding_skip` | `onboardingSkip` | — | N/A — no skip UI exists |

**Implementation file**: `lib/features/onboarding/presentation/screens/welcome_screen.dart`

---

### 3a. Training Onboarding Events

**Status**: All 7 training onboarding events are wired and firing.

These events track the **complete conversion funnel** for new training users — from the first onboarding tip through program selection, video preview, location choice, and signup. This funnel is critical for understanding where users drop off before their first program enrollment.

**Funnel Flow:**
```
TrainingOnboardingTipScreen ("Esta es tu pantalla de entreno")
        ↓ training_onboarding_continue_clicked
ProgramFirstChoiceScreen (Gender selector + Program carousel)
        ↓ program_start_intent_clicked
   ┌────┴────┐
   │ Optional │
   ↓         ↓
ProgramVideoScreen ──→ program_video_viewed (on screen load)
        ↓ program_video_continue_clicked
TrainingLocationScreen ("¿Dónde vas a entrenar?")
        ↓ program_enroll_intent_clicked
LoginMethodScreen ("¡Todo listo para empezar!" — guests only)
        ↓ signup_method_selected
Auth Flow (Google / Apple / Email)
        ↓ signup_completed
   ──→ program_enroll (tracked in Training Events)
```

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `training_onboarding_continue_clicked` | `trainingOnboardingContinueClicked` | — | User taps "Continuar" on the training onboarding tip screen |
| `program_start_intent_clicked` | `programStartIntentClicked` | `template_id` | User taps "Empezar programa" on the choose program screen |
| `program_video_viewed` | `programVideoViewed` | `program_id` | Program video screen is displayed (fires on screen load, not on play) |
| `program_video_continue_clicked` | `programVideoContinueClicked` | `program_id` | User taps "Continuar" after the program video |
| `program_enroll_intent_clicked` | `programEnrollIntentClicked` | `program_id` | User taps "Suscribirse" on the location selection screen |
| `signup_method_selected` | `signupMethodSelected` | `method`, `entry_point`, `program_id` | User selects a signup method (google/apple/email) on the ready screen |
| `signup_completed` | `signupCompleted` | `method`, `is_new_user`, `program_id` | System confirms user authenticated (social auth return or email account created) |

**Parameter details:**

| Parameter | Type | Values | Notes |
|-----------|------|--------|-------|
| `template_id` | string | Grouped program name | Used on choose program screen because grouped programs don't have a single `program_id` yet — the real ID is resolved after location selection |
| `entry_point` | string | `first_program_enroll`, `profile` | Distinguishes training onboarding signup from profile-initiated signup |
| `program_id` | int | Program ID | Available after location resolves the grouped program to a specific variant |

**Implementation files**:
- `lib/features/training/presentation/screens/training_onboarding_tip_screen.dart` — `training_onboarding_continue_clicked`
- `lib/features/training/presentation/screens/program_first_choice_screen.dart` — `program_start_intent_clicked`
- `lib/features/training/presentation/screens/program_video_screen.dart` — `program_video_viewed`, `program_video_continue_clicked`
- `lib/features/training/presentation/screens/training_location_screen.dart` — `program_enroll_intent_clicked`
- `lib/features/auth/presentation/screens/login_method_screen.dart` — `signup_method_selected`
- `lib/features/auth/presentation/screens/email_auth_screen.dart` — `signup_completed`

**Notes:**
- The video screen is **optional** — users can tap "Empezar programa" to go directly to location selection, or "Ver como funciona" to watch the video first.
- `signup_method_selected` and `signup_completed` only fire for **guest users** who need to create an account. Already-authenticated users skip the login screen entirely.
- `signup_completed` fires when the system confirms the user is authenticated (return from social auth provider or after creating an email account). This is distinct from `sign_up_success` (Auth #4) which doesn't carry `program_id` context.

---

### 4. Training Events

**Status**: NEW — must add to `AnalyticsEvent` enum and wire.

This is the **most critical domain** for marketing. Training is the core product.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `program_view` | `programView` | `program_id`, `program_name`, `content_type:program` | User views program detail |
| `program_video_play` | `programVideoPlay` | `program_id`, `program_name` | Watches program intro video |
| `program_enroll` | `programEnroll` | `program_id`, `program_name`, `location`, `level`, `entry_point`, `program_type`, `program_goal`, `program_secondary_goal` | User subscribes to a program |
| `program_complete` | `programComplete` | `program_id`, `program_name`, `total_days`, `duration_weeks` | All training days completed |
| `program_unenroll` | `programUnenroll` | `program_id`, `program_name`, `completed_days`, `total_days` | User leaves a program early |
| `training_session_start` | `trainingSessionStart` | `program_id`, `day_name`, `week_number` | Starts a training day |
| `training_session_complete` | `trainingSessionComplete` | `program_id`, `day_name`, `week_number`, `duration_seconds`, `exercises_completed` | Finishes a session |
| `training_session_rate` | `trainingSessionRate` | `program_id`, `rating`, `perceived_effort` | Rates session difficulty |
| `exercise_start` | `exerciseStart` | `exercise_id`, `exercise_name`, `program_id` | Opens exercise detail |
| `exercise_set_log` | `exerciseSetLog` | `exercise_id`, `exercise_name`, `set_number`, `weight`, `reps` | Logs a set |
| `exercise_video_play` | `exerciseVideoPlay` | `exercise_id`, `exercise_name` | Watches exercise demo video |
| `exercise_history_view` | `exerciseHistoryView` | `exercise_id`, `exercise_name` | Views exercise PR/history |
| `training_tab_select` | `trainingTabSelect` | `tab_name` (`your_programs` / `catalog`) | Switches training tab |
| `catalog_filter_apply` | `catalogFilterApply` | `gender`, `location`, `level`, `objective` | Applies catalog filters |
| `training_location_select` | `trainingLocationSelect` | `location` (`gym` / `home_bands` / `home_dumbbells`) | Selects training location |
| `continuation_program_view` | `continuationProgramView` | `program_id`, `program_name` | Views continuation suggestion |
| `continuation_reminder_set` | `continuationReminderSet` | `program_id` | Sets continuation reminder |
| `program_completion_archive` | `programCompletionArchive` | `program_id`, `program_name` | User archives a completed program from the entreno completed card |
| `program_completion_restart` | `programCompletionRestart` | `program_id`, `program_name` | User restarts a completed program (archive + re-enroll) |
| `program_completion_start_continuation` | `programCompletionStartContinuation` | `continuation_program_id`, `continuation_program_name`, `program_id` | User starts a continuation program from the completion celebration screen |

**Implementation files**:
- `lib/features/training/presentation/providers/training_providers.dart` — enrollment, session flow
- `lib/features/training/presentation/screens/training_session_screen.dart` — session start
- `lib/features/training/presentation/screens/training_complete_screen.dart` — session complete
- `lib/features/training/presentation/screens/training_rate_screen.dart` — rate event
- `lib/features/training/presentation/widgets/program_completed_card.dart` — archive, restart events
- `lib/features/training/presentation/screens/completed_program_screen.dart` — start continuation event
- `lib/features/training/presentation/screens/exercise_detail_screen.dart` — exercise/set events
- `lib/features/training/presentation/screens/program_detail_screen.dart` — program view
- `lib/features/training/presentation/widgets/active_programs_section.dart` — tab select

**Helper extension to add** (`AnalyticsTrainingExtension`):
```dart
extension AnalyticsTrainingExtension on AnalyticsService {
  Future<void> logProgramEnroll({
    required int programId,
    required String programName,
    required String location,
    required String entryPoint,
    required String programType,
    String? level,
    String? programGoal,
    String? programSecondaryGoal,
  }) async {
    await logEvent(AnalyticsEvent.programEnroll, {
      AnalyticsParams.programId: programId,
      AnalyticsParams.programName: programName,
      AnalyticsParams.contentType: 'program',
      AnalyticsParams.location: location,
      AnalyticsParams.entryPoint: entryPoint,
      AnalyticsParams.programType: programType,
      if (level != null) AnalyticsParams.level: level,
      if (programGoal != null) AnalyticsParams.programGoal: programGoal,
      if (programSecondaryGoal != null) AnalyticsParams.programSecondaryGoal: programSecondaryGoal,
    });
    await setUserProperty(
      name: UserProperties.hasActiveProgram,
      value: 'true',
    );
    await setUserProperty(
      name: UserProperties.activeProgramName,
      value: programName,
    );
    await setUserProperty(
      name: UserProperties.trainingLocation,
      value: location,
    );
  }

  Future<void> logSessionComplete({
    required int programId,
    required String dayName,
    required int weekNumber,
    required int durationSeconds,
    required int exercisesCompleted,
  }) async {
    await logEvent(AnalyticsEvent.trainingSessionComplete, {
      AnalyticsParams.programId: programId,
      'day_name': dayName,
      'week_number': weekNumber,
      'duration_seconds': durationSeconds,
      'exercises_completed': exercisesCompleted,
    });
  }

  Future<void> logExerciseSetLog({
    required int exerciseId,
    required String exerciseName,
    required int setNumber,
    double? weight,
    int? reps,
  }) async {
    await logEvent(AnalyticsEvent.exerciseSetLog, {
      AnalyticsParams.exerciseId: exerciseId,
      AnalyticsParams.exerciseName: exerciseName,
      'set_number': setNumber,
      if (weight != null) 'weight': weight,
      if (reps != null) 'reps': reps,
    });
  }
}
```

---

### 5. Pedometer / Steps Events

**Status**: Defined in enum, helper extension built. Need wiring.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `pedometer_enabled` | `pedometerEnabled` | `source` (`health_connect` / `sensor`) | User enables steps |
| `pedometer_disabled` | `pedometerDisabled` | — | User disables steps |
| `pedometer_permission_granted` | `pedometerPermissionGranted` | — | Grants health permission |
| `pedometer_permission_denied` | `pedometerPermissionDenied` | — | Denies health permission |
| `pedometer_sync_success` | `pedometerSyncSuccess` | `steps`, `calories`, `source` | Data synced to backend |

**Implementation file**: `lib/features/home/presentation/providers/home_providers.dart`

---

### 6. Explore / Content Events

**Status**: NEW — must add to `AnalyticsEvent` enum and wire.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `recipe_view` | `recipeView` | `recipe_id`, `recipe_name`, `content_type:recipe` | Opens recipe detail |
| `recipe_favorite` | `recipeFavorite` | `recipe_id`, `recipe_name` | Favorites a recipe |
| `recipe_unfavorite` | `recipeUnfavorite` | `recipe_id`, `recipe_name` | Unfavorites a recipe |
| `recipe_mode_select` | `recipeModeSelect` | `recipe_id`, `mode` (`ligero`/`normal`/`bestia`) | Selects recipe mode |
| `recipe_filter_apply` | `recipeFilterApply` | `meal_types`, `is_spicy`, `favorites_only` | Applies recipe filters |
| `guide_category_view` | `guideCategoryView` | `category_id`, `category_name`, `content_type:guide` | Opens guide category |
| `guide_video_play` | `guideVideoPlay` | `video_id`, `video_name`, `category_name` | Plays guide video |
| `calculator_start` | `calculatorStart` | — | Opens calorie calculator |
| `calculator_complete` | `calculatorComplete` | `goal`, `gender`, `age`, `activity_level`, `bmr`, `tdee`, `goal_calories` | Sees calculator results |
| `program_history_view` | `programHistoryView` | — | Opens training history |
| `explore_section_tap` | `exploreSectionTap` | `section_name` | Taps explore card |

**`section_name` values**: `recipes`, `guides`, `calculator`, `history`, `catalog`

**Implementation files**:
- `lib/features/explore/presentation/screens/recipe_detail_screen.dart` — recipe view/mode
- `lib/features/explore/presentation/providers/recipe_providers.dart` — recipe favorite
- `lib/features/explore/presentation/screens/explore_screen.dart` — section taps
- `lib/features/explore/presentation/screens/guide_category_screen.dart` — guide events
- `lib/features/explore/presentation/screens/calorie_calculator_result_screen.dart` — calculator

**Helper extension to add** (`AnalyticsExploreExtension`):
```dart
extension AnalyticsExploreExtension on AnalyticsService {
  Future<void> logRecipeView({
    required int recipeId,
    required String recipeName,
  }) async {
    await logEvent(AnalyticsEvent.recipeView, {
      'recipe_id': recipeId,
      'recipe_name': recipeName,
      AnalyticsParams.contentType: 'recipe',
    });
  }

  Future<void> logRecipeFavorite({
    required int recipeId,
    required String recipeName,
    required bool isFavorite,
  }) async {
    await logEvent(
      isFavorite ? AnalyticsEvent.recipeFavorite : AnalyticsEvent.recipeUnfavorite,
      {
        'recipe_id': recipeId,
        'recipe_name': recipeName,
      },
    );
  }

  Future<void> logCalculatorComplete({
    required String goal,
    required String gender,
    required int age,
    required String activityLevel,
    required int bmr,
    required int tdee,
    required int goalCalories,
  }) async {
    await logEvent(AnalyticsEvent.calculatorComplete, {
      'goal': goal,
      'gender': gender,
      'age': age,
      'activity_level': activityLevel,
      'bmr': bmr,
      'tdee': tdee,
      'goal_calories': goalCalories,
    });
    await setUserProperty(
      name: UserProperties.hasUsedCalculator,
      value: 'true',
    );
    await setUserProperty(
      name: UserProperties.fitnessGoal,
      value: goal,
    );
  }
}
```

---

### 7. Ranking / Community Events

**Status**: Partially defined in enum. Need wiring + expansion.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `ranking_view` | `rankingViewed` | `filter_type` (`global`/`age_group`) | Views ranking screen |
| `ranking_enrolled` | `rankingEnrolled` | — | Joins ranking competition |
| `ranking_filter_change` | `rankingFilterChange` (NEW) | `filter_type` | Switches ranking filter |

**Implementation file**: `lib/features/ranking/presentation/screens/community_screen.dart`

---

### 8. Profile Events

**Status**: Partially defined in enum. Need wiring + expansion.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `profile_view` | `profileViewed` | — | Opens profile screen |
| `profile_field_update` | `profileUpdated` | `field_name`, `value` | Updates any profile field |
| `profile_photo_change` | `profilePhotoChanged` | — | Changes profile picture |

**`field_name` values**: `gender`, `age`, `weight`, `height`, `name`

**Implementation file**: `lib/features/profile/presentation/screens/profile_screen.dart`

**User properties to update on profile change**:
```dart
// When gender changes
analytics.setUserProperty(name: 'gender', value: 'male');

// When age changes
analytics.setUserProperty(name: 'age_group', value: _ageToGroup(28)); // → '25_34'
```

---

### 9. Activity Logging Events

**Status**: Defined in enum. Need wiring.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `activity_create` | `activityCreated` | `activity_type`, `duration_minutes` | Logs manual activity |
| `activity_delete` | `activityDeleted` | `activity_type` | Deletes an activity |

---

### 10. App Engagement Events

**Status**: NEW — must add to `AnalyticsEvent` enum and wire.

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `tab_select` | `tabSelect` (NEW) | `tab_name` | Bottom nav tap |
| `share_content` | `shareContent` | `content_type`, `content_id`, `item_name` | Any share action |
| `notification_received` | `notificationReceived` (NEW) | `notification_type` | Push notification arrives |
| `notification_tap` | `notificationTap` (NEW) | `notification_type`, `action` | User taps notification |

**`tab_name` values**: `home`, `training`, `ranking`, `explore`

**Implementation files**:
- `lib/core/widgets/navigation/main_scaffold.dart` — bottom nav tab_select
- Push notification handler — notification events

---

### 11. Video Banner Events

**Status**: All 8 events wired and firing.

These events track the **video banner conversion funnel** — from banner display on the home screen through video viewing and CTA interaction. Critical for understanding banner engagement and video-to-conversion rates.

**Funnels:**

1. **Apertura** — How many users who see the banner open the video?
   `video_banner_shown` → `video_opened`

2. **Retención** — How many users who open the video watch it completely?
   `video_opened` → `video_completed`

3. **Conversión** — How many users interact with the CTA?
   `video_cta_shown` → `video_cta_tapped`

| Event | Enum Value | Parameters | When Fired |
|-------|-----------|-----------|------------|
| `video_banner_shown` | `videoBannerShown` | `video_id`, `video_title`, `user_type`, `days_shown` | Banner card becomes visible on home screen (once per instance) |
| `video_banner_dismissed` | `videoBannerDismissed` | `video_id`, `video_title`, `user_type`, `days_shown` | Banner expires (API returns `showBanner: false` after previously shown) |
| `video_opened` | `videoOpened` | `video_id`, `video_title`, `user_type` | User taps banner, video screen opens (initState) |
| `video_completed` | `videoCompleted` | `video_id`, `video_title`, `user_type`, `seconds_watched`, `percent_watched` | Video reaches the end |
| `video_closed_early` | `videoClosedEarly` | `video_id`, `video_title`, `user_type`, `seconds_watched`, `percent_watched` | User closes video before it finishes (dispose) |
| `video_cta_shown` | `videoCtaShown` | `video_id`, `video_title`, `user_type`, `cta_type` | CTA panel visible on video screen open (initState) |
| `video_cta_tapped` | `videoCtaTapped` | `video_id`, `video_title`, `user_type`, `cta_type` | User taps CTA button |
| `video_cta_dismissed` | `videoCtaDismissed` | `video_id`, `video_title`, `user_type`, `cta_type` | User closes screen without tapping CTA (dispose) |

**`user_type` values**: `guest`, `trial`
**`cta_type` values**: `choose_program` (guest → program selection), `motivation` (active user → training schedule)
**`days_shown`**: Days since the banner was first seen (1–3), computed locally via SharedPreferences.

**Implementation files**:
- `lib/features/home/presentation/widgets/video_banner_card.dart` — `video_banner_shown`, `video_banner_dismissed`
- `lib/features/home/presentation/screens/video_banner_video_screen.dart` — all video + CTA events
- `lib/core/analytics/analytics_providers.dart` — `AnalyticsVideoBannerExtension`

---

## User Properties

User properties are attributes that describe segments of your user base. They persist across sessions and are used to build Firebase Audiences for targeted campaigns.

**GA4 limit**: 25 user properties max. We use **22** (10 existing + 12 new). Leaves 3 slots for future use.

### Existing User Properties (10)

| Property | Constant | Values | Set When |
|----------|----------|--------|----------|
| `is_guest` | `UserProperties.isGuest` | `true` / `false` | Login |
| `auth_method` | `UserProperties.authMethod` | `google` / `apple` / `email` / `guest` | Login |
| `pedometer_enabled` | `UserProperties.pedometerEnabled` | `true` / `false` | Toggle pedometer |
| `notifications_enabled` | `UserProperties.notificationsEnabled` | `true` / `false` | Permission grant |
| `app_version` | `UserProperties.appVersion` | `1.2.3` | App start |
| `platform` | `UserProperties.platform` | `ios` / `android` | App start |
| `language` | `UserProperties.language` | `es` / `en` | App start |
| `theme` | `UserProperties.theme` | `dark` / `light` | App start |
| `account_created_at` | `UserProperties.accountCreatedAt` | ISO date | Registration |
| `last_login_at` | `UserProperties.lastLoginAt` | ISO date | Login |

### New User Properties to Add (12)

| Property | Values | Set When | Marketing Use |
|----------|--------|----------|---------------|
| `gender` | `male` / `female` | Profile update | Gender-targeted campaigns |
| `age_group` | `18_24` / `25_34` / `35_44` / `45_54` / `55_plus` | Profile update | Age-targeted content |
| `fitness_goal` | `lose_weight` / `maintain` / `gain_muscle` | Calculator / questionnaire | Goal-specific programs |
| `training_level` | `beginner` / `intermediate` / `advanced` | Program enrollment | Level-appropriate suggestions |
| `training_location` | `gym` / `home_bands` / `home_dumbbells` | Location selection | Location-specific programs |
| `has_active_program` | `true` / `false` | Program enroll/unenroll/complete | Re-engagement campaigns |
| `active_program_name` | Program name string | Program enrollment | Program-specific messaging |
| `completed_programs` | Count as string (`0`, `1`, `2`...) | Program completion | Loyalty/progression campaigns |
| `days_since_last_training` | `0` / `1_7` / `8_14` / `15_30` / `30_plus` | Session complete / app open | Churn prevention |
| `total_training_sessions` | Count as string | Session completion | Engagement tiers |
| `favorite_recipes_count` | Count as string | Favorite toggle | Content engagement |
| `has_used_calculator` | `true` / `false` | Calculator completion | Feature adoption |

### When to Update User Properties

| Lifecycle Moment | Properties to Set/Update |
|-----------------|-------------------------|
| **Login/Auth** | `is_guest`, `auth_method`, `account_created_at`, `last_login_at` |
| **Profile update** | `gender`, `age_group` |
| **Calculator completion** | `fitness_goal`, `has_used_calculator` |
| **Program enrollment** | `has_active_program`, `active_program_name`, `training_level`, `training_location` |
| **Session completion** | `total_training_sessions`, `days_since_last_training` (reset to `0`) |
| **Program completion** | `completed_programs` (increment), `has_active_program` (set `false`) |
| **Program unenroll** | `has_active_program` (set `false`), `active_program_name` (clear) |
| **Recipe favorite** | `favorite_recipes_count` (update count) |
| **App open** | `days_since_last_training` (recalculate), `app_version`, `platform` |

### Age Group Mapping

```dart
String ageToGroup(int age) {
  if (age < 18) return 'under_18';
  if (age <= 24) return '18_24';
  if (age <= 34) return '25_34';
  if (age <= 44) return '35_44';
  if (age <= 54) return '45_54';
  return '55_plus';
}
```

---

## Firebase Audiences

Define these in **Firebase Console > Analytics > Audiences**. They auto-populate based on events + user properties and can be used as targets for **Firebase Cloud Messaging** push notifications.

### Acquisition & Activation

| Audience | Definition | Campaign Use |
|----------|-----------|--------------|
| **New Users (7d)** | `account_created_at` within last 7 days | Welcome series, onboarding tips |
| **Guests Not Registered** | `is_guest = true` for 3+ days | Nudge to register |
| **Registered No Program** | `is_guest = false` AND `has_active_program = false` | "Start your first program!" |
| **Onboarding Dropoff** | `onboarding_start` fired but NOT `onboarding_complete` | Re-engage incomplete onboarding |

### Engagement & Retention

| Audience | Definition | Campaign Use |
|----------|-----------|--------------|
| **Active Trainers** | `training_session_complete` in last 7 days | Motivational content, new features |
| **Lapsed Trainers (7-14d)** | `has_active_program = true` AND `days_since_last_training = 8_14` | "We miss you! Get back on track" |
| **Churning Users (30d+)** | `days_since_last_training = 30_plus` | Win-back with special program offer |
| **Completed a Program** | `program_complete` event fired | "Ready for your next challenge?" |
| **High Step Counters** | `pedometer_enabled = true` AND high step patterns | Community challenges, premium features |
| **Recipe Enthusiasts** | `favorite_recipes_count >= 3` | New recipe notifications |
| **Calculator Users** | `has_used_calculator = true` | Nutrition-focused content |

### Segmentation by Profile

| Audience | Definition | Campaign Use |
|----------|-----------|--------------|
| **Gym Users** | `training_location = gym` | Gym-specific programs/tips |
| **Home Workout Users** | `training_location` starts with `home_` | Home workout content |
| **Weight Loss Goal** | `fitness_goal = lose_weight` | Diet tips, cardio programs |
| **Muscle Gain Goal** | `fitness_goal = gain_muscle` | Strength programs, protein recipes |
| **Beginners** | `training_level = beginner` | Intro content, technique guides |
| **Advanced Athletes** | `training_level = advanced` AND `total_training_sessions >= 50` | Advanced programs, PRs |
| **Men 25-34** | `gender = male` AND `age_group = 25_34` | Targeted program ads |
| **Women 25-34** | `gender = female` AND `age_group = 25_34` | Targeted program ads |

### Lifecycle

| Audience | Definition | Campaign Use |
|----------|-----------|--------------|
| **Power Users** | 5+ `training_session_complete` in 7 days | Beta features, referral program |
| **Feature Discoverers** | Used 3+ features (training + recipes + calculator + ranking) | Cross-feature promotion |
| **Notification Opted-In** | `notifications_enabled = true` | All push campaigns |

### Creating Audiences in Firebase Console

1. Go to **Firebase Console > Analytics > Audiences**
2. Click **New audience**
3. Set conditions using the event names and user properties from this document
4. Save the audience
5. Use in **Cloud Messaging > New campaign > Target > User segment**

> Audiences take up to 24-48 hours to populate after first data flows in.

---

## Implementation Guide

### Step 1: Add New Events to `AnalyticsEvent` Enum

**File**: `lib/core/analytics/analytics_service.dart`

Add these new enum values to the existing `AnalyticsEvent` enum:

```dart
enum AnalyticsEvent {
  // ... existing events ...

  // Training Onboarding (NEW)
  trainingOnboardingContinueClicked,
  programStartIntentClicked,
  programVideoViewed,
  programVideoContinueClicked,
  programEnrollIntentClicked,
  signupMethodSelected,
  signupCompleted,

  // Training (NEW)
  programView,
  programVideoPlay,
  programEnroll,
  programComplete,
  programUnenroll,
  trainingSessionStart,
  trainingSessionComplete,
  trainingSessionRate,
  exerciseStart,
  exerciseSetLog,
  exerciseVideoPlay,
  exerciseHistoryView,
  trainingTabSelect,
  catalogFilterApply,
  trainingLocationSelect,
  continuationProgramView,
  continuationReminderSet,

  // Explore (NEW)
  recipeView,
  recipeFavorite,
  recipeUnfavorite,
  recipeModeSelect,
  recipeFilterApply,
  guideCategoryView,
  guideVideoPlay,
  calculatorStart,
  calculatorComplete,
  programHistoryView,
  exploreSectionTap,

  // Ranking (NEW)
  rankingFilterChange,

  // Engagement (NEW)
  tabSelect,
  notificationReceived,
  notificationTap,

  // Video Banner (Home)
  videoBannerShown,
  videoBannerDismissed,
  videoOpened,
  videoCompleted,
  videoClosedEarly,
  videoCtaShown,
  videoCtaTapped,
  videoCtaDismissed,

  // Training Schedule
  trainingScheduleViewed,
  trainingScheduleSaved,
  trainingScheduleDeleted,
}
```

### Step 2: Add New `AnalyticsParams` Constants

**File**: `lib/core/analytics/analytics_service.dart`

```dart
class AnalyticsParams {
  // ... existing constants ...

  // Training Onboarding
  static const String templateId = 'template_id';
  static const String entryPoint = 'entry_point';
  static const String programType = 'program_type';
  static const String programGoal = 'program_goal';
  static const String programSecondaryGoal = 'program_secondary_goal';

  // Training
  static const String programId = 'program_id';
  static const String programName = 'program_name';
  static const String exerciseId = 'exercise_id';
  static const String exerciseName = 'exercise_name';
  static const String dayName = 'day_name';
  static const String weekNumber = 'week_number';
  static const String durationSeconds = 'duration_seconds';
  static const String exercisesCompleted = 'exercises_completed';
  static const String setNumber = 'set_number';
  static const String weight = 'weight';
  static const String reps = 'reps';
  static const String rating = 'rating';
  static const String perceivedEffort = 'perceived_effort';
  static const String location = 'location';
  static const String level = 'level';
  static const String totalDays = 'total_days';
  static const String completedDays = 'completed_days';
  static const String durationWeeks = 'duration_weeks';
  static const String tabName = 'tab_name';
  static const String objective = 'objective';
  static const String gender = 'gender';

  // Explore / Recipes
  static const String recipeId = 'recipe_id';
  static const String recipeName = 'recipe_name';
  static const String mode = 'mode';
  static const String mealTypes = 'meal_types';
  static const String isSpicy = 'is_spicy';
  static const String favoritesOnly = 'favorites_only';
  static const String categoryId = 'category_id';
  static const String categoryName = 'category_name';
  static const String videoId = 'video_id';
  static const String videoName = 'video_name';
  static const String sectionName = 'section_name';

  // Calculator
  static const String goal = 'goal';
  static const String age = 'age';
  static const String activityLevel = 'activity_level';
  static const String bmr = 'bmr';
  static const String tdee = 'tdee';
  static const String goalCalories = 'goal_calories';

  // Ranking
  static const String filterType = 'filter_type';

  // Profile
  static const String fieldName = 'field_name';
  static const String value = 'value';

  // Notifications
  static const String notificationType = 'notification_type';
  static const String action = 'action';

  // Video Banner
  static const String videoTitle = 'video_title';
  static const String userType = 'user_type';
  static const String ctaType = 'cta_type';
  static const String secondsWatched = 'seconds_watched';
  static const String percentWatched = 'percent_watched';
  static const String daysShown = 'days_shown';

  // Training Schedule
  static const String dayCount = 'day_count';
  static const String reminderMinutes = 'reminder_minutes';
  static const String isUpdate = 'is_update';
  static const String isEditing = 'is_editing';
}
```

### Step 3: Add New `UserProperties` Constants

**File**: `lib/core/analytics/analytics_service.dart`

```dart
class UserProperties {
  // ... existing constants ...

  // Fitness profile (NEW)
  static const String gender = 'gender';
  static const String ageGroup = 'age_group';
  static const String fitnessGoal = 'fitness_goal';
  static const String trainingLevel = 'training_level';
  static const String trainingLocation = 'training_location';

  // Training engagement (NEW)
  static const String hasActiveProgram = 'has_active_program';
  static const String activeProgramName = 'active_program_name';
  static const String completedPrograms = 'completed_programs';
  static const String daysSinceLastTraining = 'days_since_last_training';
  static const String totalTrainingSessions = 'total_training_sessions';

  // Content engagement (NEW)
  static const String favoriteRecipesCount = 'favorite_recipes_count';
  static const String hasUsedCalculator = 'has_used_calculator';
}
```

### Step 4: Create `AnalyticsRouteObserver`

**New file**: `lib/core/analytics/analytics_route_observer.dart`

A `NavigatorObserver` that automatically logs `screen_view` for every GoRouter navigation. Register it in `lib/core/router/app_router.dart`.

```dart
class AnalyticsRouteObserver extends NavigatorObserver {
  final AnalyticsService _analytics;

  AnalyticsRouteObserver(this._analytics);

  static const _routeToScreenName = {
    '/': 'home',
    '/training': 'training',
    '/ranking': 'ranking',
    '/explore': 'explore',
    '/profile': 'profile',
    // ... full mapping from Screen Name Mapping table above
  };

  @override
  void didPush(Route route, Route? previousRoute) {
    _logScreenView(route);
  }

  @override
  void didReplace({Route? newRoute, Route? oldRoute}) {
    if (newRoute != null) _logScreenView(newRoute);
  }

  void _logScreenView(Route route) {
    final path = _extractPath(route);
    final screenName = _routeToScreenName[path] ?? path;
    _analytics.logScreenView(
      screenName: screenName,
      screenClass: route.settings.name,
    );
  }
}
```

### Step 5: Add Helper Extensions

**File**: `lib/core/analytics/analytics_providers.dart`

Add `AnalyticsTrainingExtension`, `AnalyticsExploreExtension`, and `AnalyticsEngagementExtension` (see code examples in event sections above).

### Step 6: Wire Events into Feature Code

For each feature, add `logEvent()` calls at the point of user action. Example patterns:

**In a provider (Riverpod)**:
```dart
final analytics = ref.read(analyticsServiceProvider);
analytics.logEvent(AnalyticsEvent.programEnroll, {
  AnalyticsParams.programId: program.id,
  AnalyticsParams.programName: program.name,
});
```

**In a screen (widget)**:
```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  // Log on screen appearance (for non-route-observer cases)
  ref.listen(someProvider, (prev, next) {
    if (next.hasValue) {
      ref.read(analyticsServiceProvider).logEvent(
        AnalyticsEvent.trainingSessionComplete,
        { /* params */ },
      );
    }
  });
}
```

---

## GA4 Custom Dimensions Registration Checklist

Custom event parameters must be registered as **custom dimensions** in GA4 to appear in reports. Go to **GA4 > Admin > Custom definitions > Create custom dimension**.

### Event-Scoped Custom Dimensions

Register each unique parameter key:

| Parameter | Scope | Description |
|-----------|-------|-------------|
| `program_id` | Event | Training program identifier |
| `program_name` | Event | Training program name |
| `exercise_id` | Event | Exercise identifier |
| `exercise_name` | Event | Exercise name |
| `day_name` | Event | Training day name |
| `week_number` | Event | Training week number |
| `duration_seconds` | Event | Session duration in seconds |
| `exercises_completed` | Event | Number of exercises completed |
| `set_number` | Event | Set number within exercise |
| `weight` | Event | Weight lifted (kg) |
| `reps` | Event | Repetitions performed |
| `rating` | Event | Session rating (1-5) |
| `perceived_effort` | Event | RPE rating |
| `location` | Event | Training location |
| `level` | Event | Training level |
| `total_days` | Event | Total program days |
| `completed_days` | Event | Days completed |
| `duration_weeks` | Event | Program duration in weeks |
| `tab_name` | Event | Tab name selected |
| `recipe_id` | Event | Recipe identifier |
| `recipe_name` | Event | Recipe name |
| `mode` | Event | Recipe mode selection |
| `category_id` | Event | Guide category identifier |
| `category_name` | Event | Guide category name |
| `video_id` | Event | Video identifier |
| `video_name` | Event | Video name |
| `section_name` | Event | Explore section name |
| `goal` | Event | Fitness goal |
| `activity_level` | Event | Activity level |
| `bmr` | Event | Basal metabolic rate |
| `tdee` | Event | Total daily energy expenditure |
| `goal_calories` | Event | Target daily calories |
| `filter_type` | Event | Ranking filter type |
| `field_name` | Event | Profile field name |
| `notification_type` | Event | Push notification type |
| `action` | Event | Notification action |
| `meal_types` | Event | Recipe meal type filter |
| `is_spicy` | Event | Spicy filter toggle |
| `favorites_only` | Event | Favorites filter toggle |
| `objective` | Event | Training objective filter |
| `template_id` | Event | Program group/template identifier |
| `entry_point` | Event | Where user started enrollment (onboarding/catalog) |
| `program_type` | Event | Program type (Completo/Base/Subscripcion/Gratis) |
| `program_goal` | Event | Primary program goal |
| `program_secondary_goal` | Event | Secondary program goal |
| `video_title` | Event | Video banner video title |
| `user_type` | Event | User type (guest/trial) |
| `cta_type` | Event | CTA type (choose_program/motivation) |
| `seconds_watched` | Event | Seconds of video watched |
| `percent_watched` | Event | Percentage of video watched |
| `days_shown` | Event | Days banner has been active |
| `day_count` | Event | Training schedule days selected |
| `reminder_minutes` | Event | Training schedule reminder time |
| `is_update` | Event | Whether schedule is being updated |
| `is_editing` | Event | Whether schedule is in edit mode |

### User-Scoped Custom Dimensions

Register each new user property:

| Property | Description |
|----------|-------------|
| `gender` | User gender |
| `age_group` | User age bracket |
| `fitness_goal` | User fitness goal |
| `training_level` | User training experience level |
| `training_location` | User preferred training location |
| `has_active_program` | Whether user has an active program |
| `active_program_name` | Name of active program |
| `completed_programs` | Number of completed programs |
| `days_since_last_training` | Days since last training session |
| `total_training_sessions` | Total sessions completed |
| `favorite_recipes_count` | Number of favorited recipes |
| `has_used_calculator` | Whether user has used calorie calculator |

> **GA4 Limits**: 50 event-scoped custom dimensions, 25 user-scoped custom dimensions per property.

---

## Verification

### 1. Code Verification
```bash
flutter analyze  # No errors after all changes
```

### 2. Debug View Testing

Enable Firebase DebugView on your test device:

**Android**:
```bash
adb shell setprop debug.firebase.analytics.app com.elmetodo.app
```

**iOS**:
Add `-FIRDebugEnabled` to Xcode scheme arguments.

Then open **Firebase Console > Analytics > DebugView** to see events in real-time.

### 3. Verification Checklist

| Check | How to Verify |
|-------|--------------|
| Screen views fire on navigation | Navigate through all tabs; verify `screen_view` with correct `screen_name` in DebugView |
| Auth events fire | Login/logout; verify `login_success`, `logout_success` events |
| Training events fire | Start a session, log sets, complete; verify full event chain |
| Explore events fire | View recipe, favorite, use calculator; verify events + parameters |
| User properties set | Check Firebase Console > Analytics > User Properties |
| Parameters visible | Click event in DebugView; verify all parameters present |
| No duplicate events | Each action fires exactly one event |
| No debug pollution | Confirm `NoopAnalyticsService` in debug, `FirebaseAnalyticsService` in prod |

### 4. Audience Verification

After 24-48 hours of data flowing:
1. Go to **Firebase Console > Analytics > Audiences**
2. Create audiences from the definitions above
3. Verify user counts match expected values
4. Test push notification targeting with a small audience

---

## Key Files Reference

### Existing Files (to modify)

| File | Changes Needed |
|------|---------------|
| `lib/core/analytics/analytics_service.dart` | Add ~40 events, ~35 params, ~12 user properties |
| `lib/core/analytics/analytics_providers.dart` | Add 3 helper extensions |
| `lib/core/router/app_router.dart` | Register route observer |
| `lib/features/auth/presentation/providers/auth_providers.dart` | Wire auth events + user properties |
| `lib/features/training/presentation/providers/training_providers.dart` | Wire training events |
| `lib/features/training/presentation/screens/training_session_screen.dart` | Session start event |
| `lib/features/training/presentation/screens/training_complete_screen.dart` | Session complete event |
| `lib/features/training/presentation/screens/training_rate_screen.dart` | Rate event |
| `lib/features/training/presentation/screens/exercise_detail_screen.dart` | Exercise/set events |
| `lib/features/training/presentation/screens/program_detail_screen.dart` | Program view event |
| `lib/features/training/presentation/widgets/active_programs_section.dart` | Tab select event |
| `lib/features/explore/presentation/screens/recipe_detail_screen.dart` | Recipe view/mode events |
| `lib/features/explore/presentation/providers/recipe_providers.dart` | Recipe favorite events |
| `lib/features/explore/presentation/screens/explore_screen.dart` | Section tap events |
| `lib/features/explore/presentation/screens/guide_category_screen.dart` | Guide events |
| `lib/features/explore/presentation/screens/calorie_calculator_result_screen.dart` | Calculator events |
| `lib/features/home/presentation/providers/home_providers.dart` | Pedometer events |
| `lib/features/profile/presentation/screens/profile_screen.dart` | Profile events |
| `lib/features/ranking/presentation/screens/community_screen.dart` | Ranking events |
| `lib/features/onboarding/presentation/screens/welcome_screen.dart` | Onboarding events |
| `lib/core/widgets/navigation/main_scaffold.dart` | Bottom nav tab_select event |
| `lib/features/training/presentation/screens/training_onboarding_tip_screen.dart` | Training onboarding continue event |
| `lib/features/training/presentation/screens/program_first_choice_screen.dart` | Program start intent event |
| `lib/features/training/presentation/screens/program_video_screen.dart` | Video viewed/continue events |
| `lib/features/training/presentation/screens/training_location_screen.dart` | Enroll intent event |
| `lib/features/auth/presentation/screens/login_method_screen.dart` | Signup method selected event |
| `lib/features/auth/presentation/screens/email_auth_screen.dart` | Email signup completed event |
| `lib/features/home/presentation/widgets/video_banner_card.dart` | Banner shown/dismissed events |
| `lib/features/home/presentation/screens/video_banner_video_screen.dart` | Video opened/completed/closed + CTA events |
| `lib/features/profile/presentation/screens/training_schedule_screen.dart` | Training schedule viewed/saved events |
| `lib/features/profile/presentation/providers/training_schedule_provider.dart` | Training schedule deleted event |

### New Files (to create)

| File | Purpose |
|------|---------|
| `lib/core/analytics/analytics_route_observer.dart` | Auto screen tracking via GoRouter observer |

---

## Events Defined But Not Wired

These events exist in the enum but have no UI trigger. They are intentionally not wired.

| Event | Reason |
|-------|--------|
| `onboardingSkip` | No skip button exists in the onboarding flow |
| `rankingViewed` / `profileViewed` | Redundant with auto `screen_view` from route observer |
| `shareContent` | No share functionality exists in the app yet |
| `roundsSessionAbandoned` | Users save partial progress instead of abandoning |
| `premiumDropAnnouncementView` / `premiumDropClick` | Drop campaign UI not yet built |

---

## Monetization Funnel Events (Added 2026-03-21)

Events for tracking the trial/subscription conversion funnel. See `monetization-analytics.md` for the full spec.

### Events

| # | Event | Status | Parameters | Where Wired |
|---|-------|--------|------------|-------------|
| 1 | `trial_started` | **Wired** | `program_id`, `program_name` | `paywall_screen.dart` — after purchase completion |
| 2 | `trial_ended` | **Defined** | `converted` (bool) | Needs detection of trial→expired transition |
| 3 | `premium_teaser_view` | **Defined** | `program_id`, `state` | Wire in catalog when premium programs shown |
| 4 | `base_expiry_warning_shown` | **Wired** | `days_remaining`, `channel` | `trial_expiry_banner.dart` — one-time on display |
| 5 | `base_expiry_locked_view` | **Wired** | — | `training_locked_screen.dart` — initState |
| 6 | `base_graduation_view` | **Wired** | `program_id` | `completed_program_screen.dart` — initState |
| 7 | `premium_drop_announcement_view` | **Not wired** | — | Drop campaign feature not yet built |
| 8 | `premium_drop_click` | **Not wired** | `source` | Drop campaign feature not yet built |

Note: `premium_remind_me_tap` maps to the existing `trial_banner_tapped` event (same user action).

### User Properties

| Property | Status | Set When |
|----------|--------|----------|
| `trial_start_date` | **Wired** | `trial_started` event (set in `AnalyticsMonetizationExtension`) |
| `base_program_end_date` | **Defined** | Wire when program enrollment provides end date |

### Helper Extension

`AnalyticsMonetizationExtension` in `analytics_providers.dart` provides:
- `logTrialStarted()` — also sets `subscription_status=trial` + `trial_start_date`
- `logTrialEnded()` — also sets `subscription_status=expired` if not converted
- `logPremiumTeaserView()`
- `logBaseExpiryWarningShown()`
- `logBaseExpiryLockedView()`
- `logBaseGraduationView()`

---

## Sources

- [GA4 Event Naming Rules](https://support.google.com/analytics/answer/13316687)
- [GA4 Recommended Events](https://support.google.com/firebase/answer/9267735)
- [Firebase Audiences](https://support.google.com/firebase/answer/6317509)
- [Custom Dimensions in GA4](https://support.google.com/analytics/answer/14240153)
- [Firebase Push with Audiences](https://onde.app/blog/firebase-how-to-create-custom-audiences-for-push-notifications)
- [GA4 Naming Conventions Best Practices](https://analytify.io/ga4-and-google-tag-manager-naming-conventions/)
