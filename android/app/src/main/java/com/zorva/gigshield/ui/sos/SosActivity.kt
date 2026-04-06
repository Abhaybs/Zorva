package com.zorva.gigshield.ui.sos

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.os.CountDownTimer
import android.view.Gravity
import android.view.MotionEvent
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.LocationServices
import com.zorva.gigshield.R
import com.zorva.gigshield.databinding.ActivitySosBinding
import com.zorva.gigshield.ui.dashboard.DashboardActivity
import com.zorva.gigshield.ui.earnings.EarningsOptimizerActivity
import com.zorva.gigshield.ui.gigscore.GigScoreActivity
import com.zorva.gigshield.ui.legal.LegalShieldActivity
import com.zorva.gigshield.ui.ocr.OcrScannerActivity

class SosActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySosBinding
    private val viewModel: SosViewModel by viewModels()
    private var holdTimer: CountDownTimer? = null
    private var sosTriggered = false

    private val nearbyWorkers = listOf(
        Triple("Mohan",  0.3f, "#4CAF50"),
        Triple("Priya",  0.8f, "#FFC107"),
        Triple("Ravi",   1.2f, "#FFC107")
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySosBinding.inflate(layoutInflater)
        setContentView(binding.root)
        supportActionBar?.hide()

        setupHoldButton()
        setupBottomNav()
        renderNearbyWorkers()
        observeData()
    }

    @Suppress("ClickableViewAccessibility")
    private fun setupHoldButton() {
        binding.btnSosHold.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> { startHoldTimer(); true }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> { cancelHoldTimer(); true }
                else -> false
            }
        }
    }

    private fun startHoldTimer() {
        if (sosTriggered) return
        binding.tvSosInstruction.setTextColor(Color.WHITE)
        holdTimer = object : CountDownTimer(2000L, 250L) {
            override fun onTick(remaining: Long) {
                val secs = Math.ceil(remaining / 1000.0).toInt()
                binding.tvSosInstruction.text = "Hold... ${secs}s"
            }
            override fun onFinish() {
                binding.tvSosInstruction.text = "Sending SOS\u2026"
                triggerSos()
            }
        }.start()
    }

    private fun cancelHoldTimer() {
        holdTimer?.cancel()
        holdTimer = null
        if (!sosTriggered) {
            binding.tvSosInstruction.text = "Hold for 2 seconds to trigger\nemergency alert"
            binding.tvSosInstruction.setTextColor(Color.parseColor("#A0B4B0"))
        }
    }

    private fun triggerSos() {
        sosTriggered = true
        val fused = LocationServices.getFusedLocationProviderClient(this)
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {
            viewModel.triggerSos(0.0, 0.0, null)
            return
        }
        fused.lastLocation.addOnSuccessListener { loc ->
            viewModel.triggerSos(loc?.latitude ?: 0.0, loc?.longitude ?: 0.0, null)
        }.addOnFailureListener {
            viewModel.triggerSos(0.0, 0.0, null)
        }
    }

    private fun setupBottomNav() {
        binding.bottomNav.selectedItemId = R.id.nav_more
        binding.bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    val i = Intent(this, DashboardActivity::class.java)
                    i.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                    startActivity(i); true
                }
                R.id.nav_income  -> { startActivity(Intent(this, OcrScannerActivity::class.java)); true }
                R.id.nav_score   -> { startActivity(Intent(this, GigScoreActivity::class.java)); true }
                R.id.nav_shield  -> { startActivity(Intent(this, LegalShieldActivity::class.java)); true }
                R.id.nav_more    -> true
                else             -> false
            }
        }
    }

    private fun renderNearbyWorkers() {
        binding.tvWorkerCount.text = "Nearby Zorva Workers: ${nearbyWorkers.size}"
        nearbyWorkers.forEach { (name, dist, colorHex) ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).also { it.bottomMargin = dpToPx(12) }
            }

            val dot = View(this).apply {
                layoutParams = LinearLayout.LayoutParams(dpToPx(10), dpToPx(10))
                    .also { it.marginEnd = dpToPx(12) }
                background = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL
                    setColor(Color.parseColor(colorHex))
                }
            }

            val label = TextView(this).apply {
                text = "$name  \u2022  ${dist}km away"
                textSize = 14f
                setTextColor(Color.parseColor("#D0E8E4"))
                setTypeface(null, Typeface.NORMAL)
            }

            row.addView(dot)
            row.addView(label)
            binding.llWorkers.addView(row)
        }
    }

    private fun observeData() {
        viewModel.sosStatus.observe(this) { status ->
            if (sosTriggered) {
                binding.tvSosInstruction.text = status ?: "SOS sent"
                binding.tvSosInstruction.setTextColor(Color.parseColor("#4CAF50"))
            }
        }
        viewModel.error.observe(this) { err ->
            err?.let { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        holdTimer?.cancel()
    }

    private fun dpToPx(dp: Int): Int =
        (dp * resources.displayMetrics.density).toInt()
}
