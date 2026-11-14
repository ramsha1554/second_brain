import 'dart:convert';
import 'dart:io';

/// Environment configuration reader for Flutter flavors.
class Environment {
  static String? _appId;
  static String? _appName;
  static String? _apiBaseUrl;

  /// Load environment configuration based on APP_FLAVOR.
  static Future<void> load() async {
    final envFile = _getEnvFile();
    if (envFile == null) return;

    final jsonString = await File(envFile).readAsString();
    final envData = jsonDecode(jsonString) as Map<String, dynamic>;

    _appId = envData['appId'] as String?;
    _appName = envData['appName'] as String?;
    _apiBaseUrl = envData['apiBaseUrl'] as String?;
  }

  /// Get environment file path based on APP_FLAVOR dart-define.
  static String? _getEnvFile() {
    const flavor = String.fromEnvironment('APP_FLAVOR', defaultValue: 'dev');
    switch (flavor) {
      case 'dev':
        return 'lib/core/environment/env/dev.json';
      case 'staging':
        return 'lib/core/environment/env/staging.json';
      case 'prod':
        return 'lib/core/environment/env/prod.json';
      default:
        return 'lib/core/environment/env/dev.json';
    }
  }

  /// Application ID for current flavor.
  static String get appId => _appId ?? 'com.ramsha.secondbrain.dev';

  /// Application name for current flavor.
  static String get appName => _appName ?? 'Second Brain Dev';

  /// API base URL for current flavor.
  static String get apiBaseUrl => _apiBaseUrl ?? 'https://dev.api.secondbrain.dev';
}
