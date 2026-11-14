plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.ramsha.secondbrain"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    flavorDimensions += "flavor"
    productFlavors {
        create("dev") {
            dimension = "flavor"
            applicationId = "com.ramsha.secondbrain.dev"
            resValue("string", "app_name", "Second Brain Dev")
            buildConfigField("String", "APP_ID", "\"com.ramsha.secondbrain.dev\"")
            buildConfigField("String", "API_BASE_URL", "\"https://dev.api.secondbrain.dev\"")
            signingConfig = signingConfigs.getByName("debug")
        }
        create("staging") {
            dimension = "flavor"
            applicationId = "com.ramsha.secondbrain.staging"
            resValue("string", "app_name", "Second Brain Staging")
            buildConfigField("String", "APP_ID", "\"com.ramsha.secondbrain.staging\"")
            buildConfigField("String", "API_BASE_URL", "\"https://staging.api.secondbrain.dev\"")
            signingConfig = signingConfigs.getByName("debug")
        }
        create("prod") {
            dimension = "flavor"
            applicationId = "com.ramsha.secondbrain"
            resValue("string", "app_name", "Second Brain")
            buildConfigField("String", "APP_ID", "\"com.ramsha.secondbrain\"")
            buildConfigField("String", "API_BASE_URL", "\"https://api.secondbrain.dev\"")
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.ramsha.secondbrain.dev"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
