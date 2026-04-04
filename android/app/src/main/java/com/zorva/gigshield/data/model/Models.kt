package com.zorva.gigshield.data.model

/**
 * Gig worker profile data class.
 */
data class Worker(
    val id: String? = null,
    val firebase_uid: String? = null,
    val name: String,
    val phone: String,
    val email: String? = null,
    val city: String? = null,
    val platforms: String? = null,
    val last_lat: Double? = null,
    val last_lng: Double? = null,
    val is_active: Boolean = true,
    val created_at: String? = null
)

/**
 * Income record data class.
 */
data class Income(
    val id: String? = null,
    val worker_id: String? = null,
    val amount: Double,
    val currency: String = "INR",
    val platform: String,
    val source: String,
    val description: String? = null,
    val transaction_ref: String? = null,
    val earned_at: String,
    val recorded_at: String? = null
)

/**
 * GigScore data class.
 */
data class GigScore(
    val id: String? = null,
    val worker_id: String? = null,
    val score: Double,
    val breakdown: GigScoreBreakdown? = null,
    val model_version: String? = null,
    val feature_importance: Map<String, Double>? = null,
    val computed_at: String? = null
)

data class GigScoreBreakdown(
    val income_consistency: Double,
    val trip_completion: Double,
    val rating_reliability: Double,
    val work_pattern: Double,
    val platform_diversity: Double
)
