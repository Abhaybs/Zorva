"""SMS Parser — extract payment data from gig platform SMS messages."""

import re
from typing import Optional
from datetime import datetime


class SmsParser:
    """
    Parse payment SMS from Indian gig platforms and UPI apps.

    Extracts: amount, platform/sender, transaction type, reference ID.
    """

    # ── Platform SMS patterns ─────────────────────────────────
    PLATFORM_PATTERNS = {
        "swiggy": [
            r"(?:Swiggy|SWIGGY).*?(?:credited|received|paid).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)",
            r"(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:credited|received).*?(?:Swiggy|SWIGGY)",
        ],
        "zomato": [
            r"(?:Zomato|ZOMATO).*?(?:credited|received|paid).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)",
            r"(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:credited|received).*?(?:Zomato|ZOMATO)",
        ],
        "ola": [
            r"(?:Ola|OLA).*?(?:credited|received|paid).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)",
            r"(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:Ola|OLA)",
        ],
        "uber": [
            r"(?:Uber|UBER).*?(?:credited|received|paid).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)",
        ],
        "rapido": [
            r"(?:Rapido|RAPIDO).*?(?:credited|received|paid).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*)",
        ],
    }

    # ── Generic UPI / bank credit patterns ────────────────────
    UPI_PATTERNS = [
        r"(?:credited|received|Cr).*?(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:UPI|IMPS|NEFT)",
        r"(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:credited|Cr).*?(?:A/c|account)",
        r"(?:Rs\.?|₹|INR)\s*([\d,]+\.?\d*).*?(?:received from|credited by)",
    ]

    # ── Reference ID patterns ─────────────────────────────────
    REF_PATTERNS = [
        r"(?:Ref\.?\s*(?:No\.?|ID)?|UPI\s*Ref|Txn\s*(?:ID|No)?)\s*[:=]?\s*([A-Za-z0-9]+)",
        r"(?:UTR|RRN)\s*[:=]?\s*(\d+)",
    ]

    def parse(self, sms_text: str, sender: str = None) -> dict:
        """
        Parse a single SMS message.

        Args:
            sms_text: The SMS body text
            sender: Optional sender ID (e.g., "SWIGGY", "VM-ZOMATO")

        Returns:
            Structured payment data dict.
        """
        result = {
            "amount": None,
            "platform": None,
            "transaction_type": None,  # credit / debit
            "reference_id": None,
            "raw_text": sms_text,
            "is_payment": False,
            "confidence": "low",
        }

        if not sms_text:
            return result

        # Detect platform from sender ID
        if sender:
            sender_upper = sender.upper()
            for platform in self.PLATFORM_PATTERNS:
                if platform.upper() in sender_upper:
                    result["platform"] = platform
                    break

        # Try platform-specific patterns
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, sms_text, re.IGNORECASE)
                if match:
                    result["amount"] = float(match.group(1).replace(",", ""))
                    result["platform"] = platform
                    result["is_payment"] = True
                    result["confidence"] = "high"
                    break
            if result["is_payment"]:
                break

        # Fallback to generic UPI patterns
        if not result["is_payment"]:
            for pattern in self.UPI_PATTERNS:
                match = re.search(pattern, sms_text, re.IGNORECASE)
                if match:
                    result["amount"] = float(match.group(1).replace(",", ""))
                    result["is_payment"] = True
                    result["confidence"] = "medium"
                    break

        # Detect transaction type
        if result["is_payment"]:
            text_lower = sms_text.lower()
            if any(w in text_lower for w in ["credited", "received", "cr"]):
                result["transaction_type"] = "credit"
            elif any(w in text_lower for w in ["debited", "deducted", "dr", "paid"]):
                result["transaction_type"] = "debit"

        # Extract reference ID
        for pattern in self.REF_PATTERNS:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                result["reference_id"] = match.group(1)
                break

        return result

    def parse_batch(self, messages: list[dict]) -> list[dict]:
        """
        Parse multiple SMS messages.

        Each message dict should have 'text' and optionally 'sender' keys.
        Returns only payment-related messages.
        """
        results = []
        for msg in messages:
            parsed = self.parse(msg.get("text", ""), msg.get("sender"))
            if parsed["is_payment"]:
                results.append(parsed)
        return results


if __name__ == "__main__":
    parser = SmsParser()

    # Test messages
    test_messages = [
        {
            "text": "Rs.1,250.00 credited to your A/c XX3456 by Swiggy. UPI Ref: 412345678901. Avl Bal: Rs.15,430.50",
            "sender": "VM-SWIGGY",
        },
        {
            "text": "Zomato: Your earnings of ₹890 for today have been credited. Ref No: ZMT2024031501",
            "sender": "AM-ZOMATO",
        },
        {
            "text": "Dear Customer, Rs.350.00 has been credited to your account via UPI from OLA. UTR: 123456789012",
            "sender": "TM-OLA",
        },
        {
            "text": "Your electricity bill of Rs.1500 is due. Pay now via UPI.",
            "sender": "VM-DISCOM",
        },
    ]

    print("SMS Parsing Results:")
    for msg in test_messages:
        result = parser.parse(msg["text"], msg["sender"])
        if result["is_payment"]:
            print(f"\n  ✓ {result['platform'] or 'Unknown'}: ₹{result['amount']}")
            print(f"    Type: {result['transaction_type']}")
            print(f"    Ref: {result['reference_id']}")
            print(f"    Confidence: {result['confidence']}")
        else:
            print(f"\n  ✗ Not a payment SMS: {msg['text'][:50]}...")
