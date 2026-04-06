package com.zorva.gigshield.ui.gigscore

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.databinding.ActivityGigscoreBinding

class GigScoreActivity : AppCompatActivity() {

    private lateinit var binding: ActivityGigscoreBinding
    private val viewModel: GigScoreViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityGigscoreBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }

        binding.btnRecalculate.setOnClickListener { viewModel.recalculate() }

        observeViewModel()
        viewModel.loadCurrentScore()
    }

    private fun observeViewModel() {
        viewModel.isLoading.observe(this) { loading ->
            binding.btnRecalculate.isEnabled = !loading
        }

        viewModel.isRecalculating.observe(this) { recalc ->
            binding.btnRecalculate.text = if (recalc) "Calculating…" else "Recalculate Score"
            binding.btnRecalculate.isEnabled = !recalc
        }

        viewModel.gigScore.observe(this) { score ->
            if (score != null) renderScore(score) else showNoScore()
        }

        viewModel.error.observe(this) { err ->
            if (!err.isNullOrBlank()) {
                Toast.makeText(this, err, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showNoScore() {
        binding.tvScore.text = "--"
        binding.tvScoreStatus.text = "No score yet — tap Recalculate"
        binding.tvComputedAt.text = ""
        binding.pbIncomeConsistency.progress = 0
        binding.pbTripCompletion.progress = 0
        binding.pbRatingReliability.progress = 0
        binding.pbWorkPattern.progress = 0
        binding.pbPlatformDiversity.progress = 0
    }

    private fun renderScore(score: GigScore) {
        val s = score.score.toInt()
        binding.tvScore.text = s.toString()
        binding.tvScoreStatus.text = scoreLabel(s)
        binding.tvComputedAt.text = score.computed_at?.take(16)?.replace("T", "  ") ?: ""

        score.breakdown?.let { b ->
            fun pct(v: Double) = (v / 100.0 * 100).toInt().coerceIn(0, 100)
            fun fmt(v: Double) = "${v.toInt()}/100"

            binding.tvIncomeConsistency.text = fmt(b.income_consistency)
            binding.pbIncomeConsistency.progress = pct(b.income_consistency)

            binding.tvTripCompletion.text = fmt(b.trip_completion)
            binding.pbTripCompletion.progress = pct(b.trip_completion)

            binding.tvRatingReliability.text = fmt(b.rating_reliability)
            binding.pbRatingReliability.progress = pct(b.rating_reliability)

            binding.tvWorkPattern.text = fmt(b.work_pattern)
            binding.pbWorkPattern.progress = pct(b.work_pattern)

            binding.tvPlatformDiversity.text = fmt(b.platform_diversity)
            binding.pbPlatformDiversity.progress = pct(b.platform_diversity)
        }
    }

    private fun scoreLabel(score: Int): String = when {
        score >= 750 -> "🟢 Excellent"
        score >= 600 -> "🟡 Good"
        score >= 450 -> "🟠 Fair"
        else         -> "🔴 Needs Improvement"
    }
}
