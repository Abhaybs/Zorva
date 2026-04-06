package com.zorva.gigshield.data.auth

import com.zorva.gigshield.BuildConfig
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Fetches and caches Supabase access tokens using email/password auth.
 *
 * This keeps auth logic centralized for API interceptors.
 */
object SupabaseAuthTokenProvider {

    @Volatile
    private var accessToken: String? = null

    @Volatile
    private var accessTokenExpiryEpochSeconds: Long = 0

    @Volatile
    private var lastErrorMessage: String? = null

    private val authClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build()
    }

    fun getLastError(): String? = lastErrorMessage

    fun getAccessToken(): String? = synchronized(this) {
        val now = System.currentTimeMillis() / 1000
        if (!accessToken.isNullOrBlank() && now < accessTokenExpiryEpochSeconds - 60) {
            return accessToken
        }
        fetchNewToken(now)
    }

    private fun fetchNewToken(nowEpochSeconds: Long): String? {
        if (BuildConfig.SUPABASE_URL.isBlank() || BuildConfig.SUPABASE_ANON_KEY.isBlank()) {
            lastErrorMessage = "Supabase auth is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."
            return null
        }
        if (BuildConfig.SUPABASE_EMAIL.isBlank() || BuildConfig.SUPABASE_PASSWORD.isBlank()) {
            lastErrorMessage = "Supabase credentials missing. Set SUPABASE_EMAIL and SUPABASE_PASSWORD."
            return null
        }

        val authUrl = BuildConfig.SUPABASE_URL.trimEnd('/') + "/auth/v1/token?grant_type=password"
        val payload = JSONObject()
            .put("email", BuildConfig.SUPABASE_EMAIL)
            .put("password", BuildConfig.SUPABASE_PASSWORD)
            .toString()

        val request = Request.Builder()
            .url(authUrl)
            .addHeader("apikey", BuildConfig.SUPABASE_ANON_KEY)
            .addHeader("Content-Type", "application/json")
            .post(payload.toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()

        return try {
            authClient.newCall(request).execute().use { response ->
                val body = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    lastErrorMessage = "Supabase auth failed (${response.code}): $body"
                    return null
                }

                val json = JSONObject(body)
                val token = json.optString("access_token")
                if (token.isNullOrBlank()) {
                    lastErrorMessage = "Supabase auth response missing access_token"
                    return null
                }

                val expiresIn = json.optLong("expires_in", 3600)
                accessToken = token
                accessTokenExpiryEpochSeconds = nowEpochSeconds + maxOf(60, expiresIn)
                lastErrorMessage = null
                token
            }
        } catch (exc: Exception) {
            lastErrorMessage = "Supabase auth request failed: ${exc.message}"
            null
        }
    }
}
