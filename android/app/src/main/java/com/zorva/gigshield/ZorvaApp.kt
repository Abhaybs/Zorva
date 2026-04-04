package com.zorva.gigshield

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

/**
 * Zorva / GigShield Application class.
 *
 * Initialises Firebase, notification channels, and global singletons.
 */
class ZorvaApp : Application() {

    companion object {
        const val CHANNEL_SOS = "sos_channel"
        const val CHANNEL_LOCATION = "location_channel"
        const val CHANNEL_INCOME = "income_channel"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
        // Firebase is auto-initialised via google-services.json
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)

            // SOS Channel — high priority
            val sosChannel = NotificationChannel(
                CHANNEL_SOS,
                "SOS Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Emergency SOS alerts and peer notifications"
                enableVibration(true)
            }
            manager.createNotificationChannel(sosChannel)

            // Location Tracking Channel
            val locationChannel = NotificationChannel(
                CHANNEL_LOCATION,
                "Location Tracking",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "GPS tracking during active work sessions"
            }
            manager.createNotificationChannel(locationChannel)

            // Income Notifications Channel
            val incomeChannel = NotificationChannel(
                CHANNEL_INCOME,
                "Income Updates",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Payment received and income summary notifications"
            }
            manager.createNotificationChannel(incomeChannel)
        }
    }
}
