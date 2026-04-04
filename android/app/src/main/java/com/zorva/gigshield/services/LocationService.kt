package com.zorva.gigshield.services

import android.app.*
import android.content.Intent
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import com.google.android.gms.location.*
import com.zorva.gigshield.ZorvaApp
import com.zorva.gigshield.ui.dashboard.DashboardActivity
import com.zorva.gigshield.util.Constants

/**
 * Foreground service for continuous GPS tracking during active work sessions.
 *
 * Tracks worker location at regular intervals and:
 * - Sends coordinates to backend for SOS system
 * - Logs work patterns for GigScore computation
 * - Powers the real-time tracking during SOS events
 */
class LocationService : Service() {

    companion object {
        private const val TAG = "LocationService"
        private const val NOTIFICATION_ID = 1001
    }

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback

    override fun onCreate() {
        super.onCreate()
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                for (location in result.locations) {
                    Log.d(TAG, "Location update: ${location.latitude}, ${location.longitude}")
                    // TODO: Send to backend / Firebase RTDB for live tracking
                    // TODO: Log for work pattern analysis
                }
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification())
        startLocationUpdates()
        return START_STICKY
    }

    private fun startLocationUpdates() {
        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            Constants.LOCATION_UPDATE_INTERVAL_MS
        )
            .setMinUpdateIntervalMillis(Constants.LOCATION_FASTEST_INTERVAL_MS)
            .build()

        try {
            fusedLocationClient.requestLocationUpdates(
                locationRequest, locationCallback, Looper.getMainLooper()
            )
            Log.i(TAG, "Location updates started")
        } catch (e: SecurityException) {
            Log.e(TAG, "Missing location permission", e)
        }
    }

    private fun createNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, DashboardActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, ZorvaApp.CHANNEL_LOCATION)
            .setContentTitle("Zorva — Active Session")
            .setContentText("Tracking your work session for GigScore")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }

    override fun onDestroy() {
        super.onDestroy()
        fusedLocationClient.removeLocationUpdates(locationCallback)
        Log.i(TAG, "Location updates stopped")
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
