package com.zorva.gigshield.data.repository

import com.zorva.gigshield.data.api.ZorvaApiService
import com.zorva.gigshield.data.auth.SupabaseAuthTokenProvider
import com.zorva.gigshield.data.model.BestHoursResponse
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.data.model.SosRequest
import com.zorva.gigshield.data.model.Worker
import com.zorva.gigshield.data.model.ZoneRecommendationsResponse
import com.zorva.gigshield.util.Constants
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.Response
import retrofit2.converter.gson.GsonConverterFactory
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Repository providing access to Zorva backend APIs.
 *
 * Acts as a single source of truth for data access,
 * abstracting Retrofit calls behind clean suspend functions.
 */
class WorkerRepository {

    private val api: ZorvaApiService

    private fun <T> unwrap(response: Response<T>): T {
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("API returned empty body")
        }
        val errorBody = response.errorBody()?.string()?.takeIf { it.isNotBlank() }
        val detail = errorBody ?: "No error body"
        throw Exception("API error: ${response.code()} - $detail")
    }

    init {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor { chain ->
                val token = SupabaseAuthTokenProvider.getAccessToken()
                    ?: throw IOException(
                        SupabaseAuthTokenProvider.getLastError()
                            ?: "Supabase auth token unavailable"
                    )

                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                chain.proceed(request)
            }
            .connectTimeout(Constants.API_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(Constants.API_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(Constants.API_BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        api = retrofit.create(ZorvaApiService::class.java)
    }

    // ── Worker ──────────────────────────────────────────────

    suspend fun getProfile(): Result<Worker> = runCatching {
        val response = api.getProfile()
        unwrap(response)
    }

    // ── Income ──────────────────────────────────────────────

    suspend fun addIncome(income: Income): Result<Income> = runCatching {
        val response = api.addIncomeRecord(income)
        unwrap(response)
    }

    suspend fun getIncomeSummary(days: Int = 30): Result<Map<String, Any>> = runCatching {
        val response = api.getIncomeSummary(days)
        unwrap(response)
    }

    suspend fun getIncomeHistory(
        limit: Int = 50,
        platform: String? = null
    ): Result<List<Income>> = runCatching {
        val response = api.getIncomeHistory(limit, 0, platform)
        unwrap(response)
    }

    // ── GigScore ────────────────────────────────────────────

    suspend fun getCurrentGigScore(): Result<GigScore> = runCatching {
        val response = api.getCurrentGigScore()
        unwrap(response)
    }

    suspend fun calculateGigScore(): Result<GigScore> = runCatching {
        val response = api.calculateGigScore()
        unwrap(response)
    }

    // ── SOS ─────────────────────────────────────────────────

    suspend fun triggerSos(
        workerId: String,
        lat: Double,
        lng: Double,
        message: String? = null
    ): Result<Map<String, Any>> = runCatching {
        val body = SosRequest(
            latitude = lat,
            longitude = lng,
            message = message
        )
        val response = api.triggerSos(body)
        val sos = unwrap(response)
        mapOf(
            "id"     to (sos.id ?: "") as Any,
            "status" to (sos.status ?: "") as Any
        )
    }

    // ── Schemes ─────────────────────────────────────────────

    suspend fun getEligibleSchemes(): Result<Map<String, Any>> = runCatching {
        val response = api.getEligibleSchemes()
        unwrap(response)
    }

    // ── Earnings Optimizer ───────────────────────────────────

    suspend fun getRecommendedZones(topN: Int = 5, lat: Double? = null, lng: Double? = null): Result<ZoneRecommendationsResponse> = runCatching {
        val response = api.getRecommendedZones(topN, lat, lng)
        unwrap(response)
    }

    suspend fun getBestHours(zone: String): Result<BestHoursResponse> = runCatching {
        val response = api.getBestHours(zone)
        unwrap(response)
    }
}
