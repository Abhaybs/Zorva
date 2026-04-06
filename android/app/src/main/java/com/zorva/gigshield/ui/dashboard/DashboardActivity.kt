package com.zorva.gigshield.ui.dashboard

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.LocationServices
import com.zorva.gigshield.R
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.databinding.ActivityDashboardBinding
import com.zorva.gigshield.ui.earnings.EarningsOptimizerActivity
import com.zorva.gigshield.ui.gigscore.GigScoreActivity
import com.zorva.gigshield.ui.legal.LegalShieldActivity
import com.zorva.gigshield.ui.ocr.OcrScannerActivity
import com.zorva.gigshield.ui.sos.SosActivity

class DashboardActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDashboardBinding
    private val viewModel: DashboardViewModel by viewModels()

    private val platformColors = mapOf(
        "swiggy"  to Color.parseColor("#FF6B00"),
        "ola"     to Color.parseColor("#00C853"),
        "zomato"  to Color.parseColor("#E23744"),
        "rapido"  to Color.parseColor("#FFD600"),
        "zepto"   to Color.parseColor("#9B59B6"),
        "blinkit" to Color.parseColor("#F1C40F"),
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)
        supportActionBar?.hide()

        setupTiles()
        setupBestZone()
        setupBottomNav()
        observeData()
        loadDashboardWithLocation()
    }

    private fun loadDashboardWithLocation() {
        val fused = LocationServices.getFusedLocationProviderClient(this)
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {
            fused.lastLocation.addOnSuccessListener { loc ->
                viewModel.loadDashboard(lat = loc?.latitude, lng = loc?.longitude)
            }.addOnFailureListener {
                viewModel.loadDashboard()
            }
        } else {
            viewModel.loadDashboard()
        }
    }

    private fun setupTiles() {
        binding.tileIncome.setOnClickListener {
            startActivity(Intent(this, OcrScannerActivity::class.java))
        }
        binding.tileGigScore.setOnClickListener {
            startActivity(Intent(this, GigScoreActivity::class.java))
        }
        binding.tileInsurance.setOnClickListener {
            Toast.makeText(this, "Insurance plans coming soon", Toast.LENGTH_SHORT).show()
        }
        binding.tileSos.setOnClickListener {
            startActivity(Intent(this, SosActivity::class.java))
        }
    }

    private fun setupBestZone() {
        binding.btnDismissZone.setOnClickListener {
            binding.cardBestZone.visibility = View.GONE
        }
        binding.cardBestZone.setOnClickListener {
            startActivity(Intent(this, EarningsOptimizerActivity::class.java))
        }
    }

    private fun setupBottomNav() {
        binding.bottomNav.selectedItemId = R.id.nav_home
        binding.bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> true
                R.id.nav_income -> {
                    startActivity(Intent(this, OcrScannerActivity::class.java))
                    true
                }
                R.id.nav_score -> {
                    startActivity(Intent(this, GigScoreActivity::class.java))
                    true
                }
                R.id.nav_shield -> {
                    startActivity(Intent(this, LegalShieldActivity::class.java))
                    true
                }
                R.id.nav_more -> {
                    startActivity(Intent(this, SosActivity::class.java))
                    true
                }
                else -> false
            }
        }
    }

    private fun observeData() {
        viewModel.isLoading.observe(this) { loading ->
            binding.swipeRefresh.isRefreshing = loading
        }

        viewModel.platformEarnings.observe(this) { earnings ->
            binding.tvSwiggyAmount.text = "₹${earnings["swiggy"]?.toInt() ?: "--"}"
            binding.tvOlaAmount.text    = "₹${earnings["ola"]?.toInt()    ?: "--"}"
            binding.tvZomatoAmount.text = "₹${earnings["zomato"]?.toInt() ?: "--"}"
        }

        viewModel.bestZone.observe(this) { zone ->
            if (!zone.isNullOrBlank()) {
                binding.tvBestZone.text = zone
                binding.cardBestZone.visibility = View.VISIBLE
            }
        }

        viewModel.recentIncome.observe(this) { history ->
            renderRecentActivity(history)
        }

        viewModel.error.observe(this) { error ->
            error?.let { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() }
        }

        binding.swipeRefresh.setOnRefreshListener {
            loadDashboardWithLocation()
        }
    }

    private fun renderRecentActivity(history: List<Income>) {
        binding.llRecentActivity.removeAllViews()
        if (history.isEmpty()) {
            val empty = TextView(this).apply {
                text = "No recent income. Tap Scan to add your first entry."
                textSize = 13f
                setTextColor(Color.parseColor("#707070"))
            }
            binding.llRecentActivity.addView(empty)
            return
        }

        history.forEach { income ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).also { it.bottomMargin = dpToPx(12) }
                gravity = android.view.Gravity.CENTER_VERTICAL
            }

            // Left: platform + date
            val leftCol = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            val platformColor = platformColors[income.platform.lowercase()] ?: Color.GRAY
            leftCol.addView(TextView(this).apply {
                text = income.platform.replaceFirstChar { it.uppercase() }
                textSize = 14f
                setTextColor(platformColor)
                setTypeface(null, Typeface.BOLD)
            })
            leftCol.addView(TextView(this).apply {
                text = income.earned_at.take(10)
                textSize = 12f
                setTextColor(Color.parseColor("#707070"))
            })

            // Right: amount
            val amountTv = TextView(this).apply {
                text = "₹${income.amount.toInt()}"
                textSize = 15f
                setTextColor(Color.parseColor("#4CAF50"))
                setTypeface(null, Typeface.BOLD)
            }

            row.addView(leftCol)
            row.addView(amountTv)
            binding.llRecentActivity.addView(row)
        }
    }

    private fun dpToPx(dp: Int): Int =
        (dp * resources.displayMetrics.density).toInt()
}
