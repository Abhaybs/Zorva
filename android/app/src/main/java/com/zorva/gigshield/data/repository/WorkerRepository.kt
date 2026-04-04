package com.zorva.gigshield.data.repository

import com.zorva.gigshield.data.api.ZorvaApiService
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.data.model.Worker
import com.zorva.gigshield.util.Constants
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Repository providing access to Zorva backend APIs.
 *
 * Acts as a single source of truth for data access,
 * abstracting Retrofit calls behind clean suspend functions.
 */
class WorkerRepository {

    private val api: ZorvaApiService

    init {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .addInterceptor { chain ->
                // Add auth token to every request
                val request = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer dev-token")
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
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    // ── Income ──────────────────────────────────────────────

    suspend fun addIncome(income: Income): Result<Income> = runCatching {
        val response = api.addIncomeRecord(income)
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    suspend fun getIncomeSummary(days: Int = 30): Result<Map<String, Any>> = runCatching {
        val response = api.getIncomeSummary(days)
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    suspend fun getIncomeHistory(
        limit: Int = 50,
        platform: String? = null
    ): Result<List<Income>> = runCatching {
        val response = api.getIncomeHistory(limit, 0, platform)
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    // ── GigScore ────────────────────────────────────────────

    suspend fun getCurrentGigScore(): Result<GigScore> = runCatching {
        val response = api.getCurrentGigScore()
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    suspend fun calculateGigScore(workerId: String): Result<GigScore> = runCatching {
        val response = api.calculateGigScore(mapOf("worker_id" to workerId))
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    // ── SOS ─────────────────────────────────────────────────

    suspend fun triggerSos(
        workerId: String,
        lat: Double,
        lng: Double,
        message: String? = null
    ): Result<Map<String, Any>> = runCatching {
        val body = mutableMapOf<String, Any>(
            "worker_id" to workerId,
            "latitude" to lat,
            "longitude" to lng
        )
        message?.let { body["message"] = it }
        val response = api.triggerSos(body)
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }

    // ── Schemes ─────────────────────────────────────────────

    suspend fun getEligibleSchemes(): Result<Map<String, Any>> = runCatching {
        val response = api.getEligibleSchemes()
        if (response.isSuccessful) response.body()!!
        else throw Exception("API error: ${response.code()}")
    }
}
