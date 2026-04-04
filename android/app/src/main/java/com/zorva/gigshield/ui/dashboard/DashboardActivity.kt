package com.zorva.gigshield.ui.dashboard

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.zorva.gigshield.R
import com.zorva.gigshield.ui.legal.LegalShieldActivity
import com.zorva.gigshield.ui.ocr.OcrScannerActivity
import com.zorva.gigshield.ui.sos.SosActivity
import com.zorva.gigshield.databinding.ActivityDashboardBinding

/**
 * Main dashboard showing GigScore, income summary, and quick actions.
 */
class DashboardActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDashboardBinding
    private val viewModel: DashboardViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        observeData()
        viewModel.loadDashboard()
    }

    private fun setupUI() {
        // Quick action buttons
        binding.btnSos.setOnClickListener {
            startActivity(Intent(this, SosActivity::class.java))
        }

        binding.btnScanEarnings.setOnClickListener {
            startActivity(Intent(this, OcrScannerActivity::class.java))
        }

        binding.btnLegalShield.setOnClickListener {
            startActivity(Intent(this, LegalShieldActivity::class.java))
        }

        binding.btnRefreshScore.setOnClickListener {
            viewModel.refreshGigScore()
        }

        // Swipe to refresh
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadDashboard()
        }
    }

    private fun observeData() {
        viewModel.gigScore.observe(this) { score ->
            binding.tvGigScore.text = score.score.toInt().toString()
            binding.tvScoreLabel.text = getScoreLabel(score.score)
            binding.progressScore.progress = ((score.score / 900.0) * 100).toInt()

            // Sub-scores
            score.breakdown?.let { b ->
                binding.tvIncomeConsistency.text = "Income: ${b.income_consistency.toInt()}%"
                binding.tvTripCompletion.text = "Trips: ${b.trip_completion.toInt()}%"
                binding.tvRating.text = "Rating: ${b.rating_reliability.toInt()}%"
                binding.tvWorkPattern.text = "Pattern: ${b.work_pattern.toInt()}%"
                binding.tvPlatformDiversity.text = "Diversity: ${b.platform_diversity.toInt()}%"
            }
        }

        viewModel.incomeSummary.observe(this) { summary ->
            binding.tvTotalEarnings.text = "₹${String.format("%,.0f", summary["total_earnings"] as? Double ?: 0.0)}"
            binding.tvDailyAvg.text = "₹${String.format("%,.0f", summary["average_daily"] as? Double ?: 0.0)}/day"
        }

        viewModel.isLoading.observe(this) { loading ->
            binding.swipeRefresh.isRefreshing = loading
        }

        viewModel.error.observe(this) { error ->
            error?.let { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() }
        }
    }

    private fun getScoreLabel(score: Double): String = when {
        score >= 750 -> "Excellent"
        score >= 600 -> "Good"
        score >= 450 -> "Fair"
        score >= 300 -> "Building"
        else -> "Getting Started"
    }
}
