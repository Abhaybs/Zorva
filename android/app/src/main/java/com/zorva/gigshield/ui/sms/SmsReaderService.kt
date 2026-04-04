package com.zorva.gigshield.ui.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log

/**
 * SMS Broadcast Receiver — automatically captures incoming SMS
 * and filters for gig platform payment messages.
 *
 * Permissions required: RECEIVE_SMS, READ_SMS
 */
class SmsReaderService : BroadcastReceiver() {

    companion object {
        private const val TAG = "SmsReaderService"

        // Gig platform sender IDs / keywords
        private val PLATFORM_SENDERS = listOf(
            "SWIGGY", "ZOMATO", "OLA", "UBER", "RAPIDO",
            "DUNZO", "ZEPTO", "BLINKIT", "PAYTM", "PHONEPE",
            "GPAY", "BHARPE"
        )

        // Payment-related keywords
        private val PAYMENT_KEYWORDS = listOf(
            "credited", "received", "paid", "earnings",
            "payment", "settlement", "transferred"
        )
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)

        for (sms in messages) {
            val sender = sms.displayOriginatingAddress ?: ""
            val body = sms.messageBody ?: ""

            Log.d(TAG, "SMS from: $sender")

            // Check if this is from a gig platform
            val isRelevant = PLATFORM_SENDERS.any { sender.contains(it, ignoreCase = true) }
                || PAYMENT_KEYWORDS.any { body.contains(it, ignoreCase = true) }

            if (isRelevant) {
                Log.i(TAG, "Payment SMS detected from $sender")
                processPaymentSms(context, sender, body)
            }
        }
    }

    private fun processPaymentSms(context: Context, sender: String, body: String) {
        // Extract amount using regex
        val amountRegex = Regex("""(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)""", RegexOption.IGNORE_CASE)
        val match = amountRegex.find(body)
        val amount = match?.groupValues?.get(1)?.replace(",", "")?.toDoubleOrNull()

        if (amount != null && amount > 0) {
            Log.i(TAG, "Extracted ₹$amount from $sender")

            // Detect platform
            val platform = detectPlatform(sender, body)

            // TODO: Save to local DB and sync to backend
            // TODO: Show notification with parsed amount

            Log.i(TAG, "Platform: $platform, Amount: ₹$amount")
        }
    }

    private fun detectPlatform(sender: String, body: String): String {
        val combined = "$sender $body".lowercase()
        return when {
            "swiggy" in combined -> "swiggy"
            "zomato" in combined -> "zomato"
            "ola" in combined -> "ola"
            "uber" in combined -> "uber"
            "rapido" in combined -> "rapido"
            "dunzo" in combined -> "dunzo"
            "zepto" in combined -> "zepto"
            "blinkit" in combined -> "blinkit"
            else -> "other"
        }
    }
}
