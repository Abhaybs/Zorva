package com.zorva.gigshield.ui.ocr

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch
import java.time.Instant

/**
 * ViewModel for OCR Scanner screen.
 */
class OcrViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _parsedAmount = MutableLiveData<Double>()
    val parsedAmount: LiveData<Double> = _parsedAmount

    private val _parsedPlatform = MutableLiveData<String?>()
    val parsedPlatform: LiveData<String?> = _parsedPlatform

    private val _saveStatus = MutableLiveData<String>()
    val saveStatus: LiveData<String> = _saveStatus

    private val platformKeywords = mapOf(
        "swiggy" to listOf("swiggy"),
        "zomato" to listOf("zomato"),
        "ola" to listOf("ola"),
        "uber" to listOf("uber"),
        "dunzo" to listOf("dunzo"),
        "rapido" to listOf("rapido"),
        "zepto" to listOf("zepto"),
        "blinkit" to listOf("blinkit"),
    )

    fun parseEarningsText(rawText: String) {
        val textLower = rawText.lowercase()

        // Extract amounts (₹X,XXX.XX pattern)
        val amountRegex = Regex("""[₹Rs.INR]\s*([\d,]+\.?\d*)""", RegexOption.IGNORE_CASE)
        val amounts = amountRegex.findAll(rawText)
            .map { it.groupValues[1].replace(",", "").toDoubleOrNull() ?: 0.0 }
            .filter { it > 0 }
            .toList()

        _parsedAmount.value = amounts.maxOrNull() ?: 0.0

        // Detect platform
        var detectedPlatform: String? = null
        for ((platform, keywords) in platformKeywords) {
            if (keywords.any { it in textLower }) {
                detectedPlatform = platform
                break
            }
        }
        _parsedPlatform.value = detectedPlatform

        _saveStatus.value = if (amounts.isNotEmpty()) "Ready to save" else "No amount detected"
    }

    fun saveExtractedIncome() {
        val amount = _parsedAmount.value ?: return
        val platform = _parsedPlatform.value ?: "other"

        if (amount <= 0) {
            _saveStatus.value = "No valid amount to save"
            return
        }

        viewModelScope.launch {
            _saveStatus.value = "Saving..."
            val income = Income(
                amount = amount,
                platform = platform,
                source = "screenshot_ocr",
                description = "Extracted via OCR scanner",
                earned_at = Instant.now().toString()
            )

            repository.addIncome(income).fold(
                onSuccess = { _saveStatus.value = "✓ Saved ₹${String.format("%,.2f", amount)}" },
                onFailure = { _saveStatus.value = "Save failed: ${it.message}" }
            )
        }
    }
}

