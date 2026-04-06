package com.zorva.gigshield.data.api

import com.zorva.gigshield.data.model.BestHoursResponse
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.data.model.SosRequest
import com.zorva.gigshield.data.model.SosResponse
import com.zorva.gigshield.data.model.Worker
import com.zorva.gigshield.data.model.ZoneRecommendationsResponse
import retrofit2.Response
import retrofit2.http.*

/**
 * Retrofit interface defining all Zorva backend API endpoints.
 */
interface ZorvaApiService {

    // ── Worker / Auth ───────────────────────────────────────
    @POST("workers/register")
    suspend fun registerWorker(@Body worker: Worker): Response<Worker>

    @GET("workers/me")
    suspend fun getProfile(): Response<Worker>

    @PUT("workers/me")
    suspend fun updateProfile(@Body worker: Worker): Response<Worker>

    // ── Income ──────────────────────────────────────────────
    @POST("income/record")
    suspend fun addIncomeRecord(@Body income: Income): Response<Income>

    @GET("income/summary")
    suspend fun getIncomeSummary(
        @Query("days") days: Int = 30
    ): Response<Map<String, Any>>

    @GET("income/history")
    suspend fun getIncomeHistory(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
        @Query("platform") platform: String? = null
    ): Response<List<Income>>

    // ── GigScore ────────────────────────────────────────────
    @POST("gigscore/calculate")
    suspend fun calculateGigScore(): Response<GigScore>

    @GET("gigscore/current")
    suspend fun getCurrentGigScore(): Response<GigScore>

    @GET("gigscore/history")
    suspend fun getGigScoreHistory(
        @Query("limit") limit: Int = 10
    ): Response<Map<String, Any>>

    // ── Insurance ───────────────────────────────────────────
    @GET("insurance/plans")
    suspend fun getInsurancePlans(): Response<List<Map<String, Any>>>

    @POST("insurance/subscribe")
    suspend fun subscribeInsurance(@Body body: Map<String, Any>): Response<Map<String, Any>>

    @POST("insurance/claim")
    suspend fun fileClaim(@Body body: Map<String, Any>): Response<Map<String, Any>>

    @GET("insurance/my-policies")
    suspend fun getMyPolicies(): Response<List<Map<String, Any>>>

    // ── SOS ─────────────────────────────────────────────────
    @POST("sos/trigger")
    suspend fun triggerSos(@Body body: SosRequest): Response<SosResponse>

    @GET("sos/status/{eventId}")
    suspend fun getSosStatus(
        @Path("eventId") eventId: String
    ): Response<SosResponse>

    @PUT("sos/resolve/{eventId}")
    suspend fun resolveSos(
        @Path("eventId") eventId: String,
        @Body body: @JvmSuppressWildcards Map<String, Any>
    ): Response<SosResponse>

    @GET("sos/active")
    suspend fun getActiveSos(): Response<List<Map<String, Any>>>

    // ── Schemes ─────────────────────────────────────────────
    @GET("schemes/eligible")
    suspend fun getEligibleSchemes(): Response<Map<String, Any>>

    @GET("schemes/all")
    suspend fun getAllSchemes(): Response<Map<String, Any>>

    // ── Earnings Optimizer ──────────────────────────────────
    @GET("earnings/zones")
    suspend fun getRecommendedZones(
        @Query("top_n") topN: Int = 5,
        @Query("lat") lat: Double? = null,
        @Query("lng") lng: Double? = null
    ): Response<ZoneRecommendationsResponse>

    @GET("earnings/best-hours")
    suspend fun getBestHours(
        @Query("zone") zone: String
    ): Response<BestHoursResponse>
}
