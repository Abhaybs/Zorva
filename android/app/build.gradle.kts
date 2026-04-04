plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val backendBaseUrl = (project.findProperty("backendBaseUrl") as String?)
    ?: "AUTO"

val deviceBackendBaseUrl = (project.findProperty("deviceBackendBaseUrl") as String?)
    ?: "http://127.0.0.1:8000/api/v1/"

android {
    namespace = "com.zorva.gigshield"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.zorva.gigshield"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // `backendBaseUrl` can be AUTO, emulator URL, or LAN URL.
        buildConfigField("String", "API_BASE_URL", "\"$backendBaseUrl\"")
        // Used for real devices when API_BASE_URL=AUTO.
        // Override with: -PdeviceBackendBaseUrl=http://<your-pc-lan-ip>:8000/api/v1/
        buildConfigField("String", "DEVICE_API_BASE_URL", "\"$deviceBackendBaseUrl\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

dependencies {
    // ── AndroidX Core ────────────────────────────────────────
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.9.0")
    implementation("androidx.fragment:fragment-ktx:1.7.1")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("com.google.android.material:material:1.12.0")

    // ── Lifecycle (ViewModel + LiveData) ─────────────────────
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.8.2")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.8.2")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.2")

    // ── Coroutines ──────────────────────────────────────────
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")

    // ── Retrofit (Networking) ───────────────────────────────
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // ── Firebase ────────────────────────────────────────────
    implementation(platform("com.google.firebase:firebase-bom:33.1.0"))
    implementation("com.google.firebase:firebase-auth-ktx")
    implementation("com.google.firebase:firebase-messaging-ktx")
    implementation("com.google.firebase:firebase-database-ktx")

    // ── Google Play Services (Location) ─────────────────────
    implementation("com.google.android.gms:play-services-location:21.3.0")

    // ── ML Kit (OCR) ────────────────────────────────────────
    implementation("com.google.mlkit:text-recognition:16.0.0")

    // ── Image Loading ───────────────────────────────────────
    implementation("io.coil-kt:coil:2.6.0")

    // ── Testing ─────────────────────────────────────────────
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
}
