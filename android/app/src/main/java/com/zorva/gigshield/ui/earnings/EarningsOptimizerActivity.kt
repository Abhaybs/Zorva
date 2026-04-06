package com.zorva.gigshield.ui.earnings

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.LocationServices
import com.google.android.material.card.MaterialCardView
import com.zorva.gigshield.R
import com.zorva.gigshield.data.model.BestHour
import com.zorva.gigshield.data.model.ZoneRecommendation
import com.zorva.gigshield.databinding.ActivityEarningsOptimizerBinding

class EarningsOptimizerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityEarningsOptimizerBinding
    private val viewModel: EarningsOptimizerViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityEarningsOptimizerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.apply {
            title = "Earn More"
            setDisplayHomeAsUpEnabled(true)
        }

        observeData()

        binding.swipeRefresh.setOnRefreshListener {
            loadZonesWithLocation()
        }

        loadZonesWithLocation()
    }

    private fun loadZonesWithLocation() {
        val fused = LocationServices.getFusedLocationProviderClient(this)
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {
            fused.lastLocation.addOnSuccessListener { loc ->
                viewModel.loadRecommendedZones(lat = loc?.latitude, lng = loc?.longitude)
            }.addOnFailureListener {
                viewModel.loadRecommendedZones()
            }
        } else {
            viewModel.loadRecommendedZones()
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }

    private fun observeData() {
        viewModel.isLoadingZones.observe(this) { loading ->
            binding.pbZones.visibility = if (loading) View.VISIBLE else View.GONE
            if (!loading) binding.swipeRefresh.isRefreshing = false
        }

        viewModel.isLoadingHours.observe(this) { loading ->
            binding.pbHours.visibility = if (loading) View.VISIBLE else View.GONE
        }

        viewModel.zones.observe(this) { zones ->
            renderZones(zones)
        }

        viewModel.bestHours.observe(this) { hours ->
            val zone = viewModel.selectedZone.value ?: ""
            binding.tvBestHoursTitle.text = "⏰ Best Hours — $zone"
            renderBestHours(hours)
        }

        viewModel.error.observe(this) { error ->
            error?.let { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() }
        }
    }

    private fun renderZones(zones: List<ZoneRecommendation>) {
        // Remove old zone cards (keep ProgressBar as first child)
        val pb = binding.llZones.findViewById<ProgressBar>(R.id.pbZones)
        binding.llZones.removeAllViews()
        binding.llZones.addView(pb)

        val rankEmoji = listOf("🥇", "🥈", "🥉", "4️⃣", "5️⃣")

        zones.forEachIndexed { index, zone ->
            val card = buildZoneCard(zone, rankEmoji.getOrElse(index) { "${index + 1}." })
            binding.llZones.addView(card)
        }
    }

    private fun buildZoneCard(zone: ZoneRecommendation, rank: String): MaterialCardView {
        val card = MaterialCardView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).also { it.bottomMargin = dpToPx(10) }
            setCardBackgroundColor(Color.parseColor("#1E2A2A"))
            radius = dpToPx(12).toFloat()
            cardElevation = dpToPx(3).toFloat()
        }

        val inner = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(dpToPx(16), dpToPx(14), dpToPx(16), dpToPx(14))
            gravity = Gravity.CENTER_VERTICAL
        }

        // Rank + zone name + city
        val leftCol = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        leftCol.addView(TextView(this).apply {
            text = "$rank  ${zone.zone_name}"
            textSize = 16f
            setTextColor(Color.WHITE)
            setTypeface(null, android.graphics.Typeface.BOLD)
        })
        leftCol.addView(TextView(this).apply {
            text = "${zone.city}  •  ${zone.active_workers} workers  •  ${zone.surge_multiplier}x surge"
            textSize = 12f
            setTextColor(Color.parseColor("#9EADA8"))
        })

        // Earnings per hour (right side, tappable → load best hours)
        val earningsText = TextView(this).apply {
            text = "₹${zone.predicted_earnings_per_hour.toInt()}/hr"
            textSize = 18f
            setTextColor(Color.parseColor("#00BCD4"))
            setTypeface(null, android.graphics.Typeface.BOLD)
        }

        inner.addView(leftCol)
        inner.addView(earningsText)
        card.addView(inner)

        card.setOnClickListener { viewModel.loadBestHours(zone.zone_name) }
        return card
    }

    private fun renderBestHours(hours: List<BestHour>) {
        val pb = binding.llBestHours.findViewById<ProgressBar>(R.id.pbHours)
        binding.llBestHours.removeAllViews()
        binding.llBestHours.addView(pb)

        hours.forEach { hour ->
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).also { it.bottomMargin = dpToPx(8) }
                setPadding(dpToPx(12), dpToPx(10), dpToPx(12), dpToPx(10))
                setBackgroundColor(Color.parseColor("#1A2424"))
            }

            val timeLabel = TextView(this).apply {
                text = hour.label
                textSize = 14f
                setTextColor(Color.parseColor("#9EADA8"))
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            val earningsLabel = TextView(this).apply {
                text = "₹${hour.predicted_earnings_per_hour.toInt()}/hr"
                textSize = 14f
                setTextColor(Color.parseColor("#4CAF50"))
                setTypeface(null, android.graphics.Typeface.BOLD)
            }

            row.addView(timeLabel)
            row.addView(earningsLabel)
            binding.llBestHours.addView(row)
        }
    }

    private fun dpToPx(dp: Int): Int =
        (dp * resources.displayMetrics.density).toInt()
}
