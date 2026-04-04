package com.zorva.gigshield.util

import android.os.Build
import com.zorva.gigshield.BuildConfig

/**
 * App-wide constants.
 */
object Constants {
    private const val AUTO_API_BASE_URL = "AUTO"
    private const val EMULATOR_API_BASE_URL = "http://10.0.2.2:8000/api/v1/"

    private fun normalizeBaseUrl(url: String): String {
        return if (url.endsWith("/")) url else "$url/"
    }

    private fun isRunningOnEmulator(): Boolean {
        return Build.FINGERPRINT.startsWith("generic") ||
            Build.FINGERPRINT.contains("emulator", ignoreCase = true) ||
            Build.MODEL.contains("Emulator", ignoreCase = true) ||
            Build.MODEL.contains("Android SDK built for", ignoreCase = true) ||
            Build.MANUFACTURER.contains("Genymotion", ignoreCase = true) ||
            (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic")) ||
            Build.PRODUCT == "google_sdk"
    }

    // API
    val API_BASE_URL: String = normalizeBaseUrl(
        when {
            !BuildConfig.API_BASE_URL.equals(AUTO_API_BASE_URL, ignoreCase = true) -> BuildConfig.API_BASE_URL
            isRunningOnEmulator() -> EMULATOR_API_BASE_URL
            else -> BuildConfig.DEVICE_API_BASE_URL
        }
    )
    const val API_TIMEOUT_SECONDS = 30L

    // GigScore
    const val GIGSCORE_MAX = 900
    const val GIGSCORE_EXCELLENT = 750
    const val GIGSCORE_GOOD = 600
    const val GIGSCORE_FAIR = 450
    const val GIGSCORE_LOW = 300

    // Location
    const val LOCATION_UPDATE_INTERVAL_MS = 10_000L    // 10 seconds
    const val LOCATION_FASTEST_INTERVAL_MS = 5_000L

    // SOS
    const val SOS_PEER_RADIUS_KM = 5.0

    // Shared Preferences
    const val PREFS_NAME = "zorva_prefs"
    const val PREF_AUTH_TOKEN = "auth_token"
    const val PREF_WORKER_ID = "worker_id"
}
