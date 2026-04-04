"""OCR Pipeline — extract earnings data from screenshots using Tesseract."""

import re
from typing import Optional
from datetime import datetime


class OcrPipeline:
    """
    Process screenshots of gig platform earnings dashboards.

    Uses Tesseract OCR for text extraction and regex + NLP for structured parsing.
    Falls back to regex-only parsing if Tesseract/Pillow not available.
    """

    # Regex patterns for common gig platform earnings formats
    AMOUNT_PATTERNS = [
        r"₹\s*([\d,]+\.?\d*)",
        r"Rs\.?\s*([\d,]+\.?\d*)",
        r"INR\s*([\d,]+\.?\d*)",
        r"Total\s*(?:Earnings?|Income)?\s*[:=]?\s*₹?\s*([\d,]+\.?\d*)",
        r"Net\s*(?:Pay|Earnings?)?\s*[:=]?\s*₹?\s*([\d,]+\.?\d*)",
    ]

    TRIP_PATTERNS = [
        r"(\d+)\s*(?:trips?|rides?|orders?|deliveries)",
        r"(?:Completed|Total)\s*[:=]?\s*(\d+)",
    ]

    DATE_PATTERNS = [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}\s+\w+\s+\d{4})",
        r"(Today|Yesterday)",
    ]

    PLATFORM_KEYWORDS = {
        "swiggy": ["swiggy", "swiggy delivery", "swiggy instamart"],
        "zomato": ["zomato", "zomato delivery"],
        "ola": ["ola", "ola driver"],
        "uber": ["uber", "uber eats", "uber driver"],
        "dunzo": ["dunzo"],
        "zepto": ["zepto"],
        "rapido": ["rapido", "rapido captain"],
        "blinkit": ["blinkit"],
    }

    def __init__(self):
        self._tesseract_available = False
        try:
            import pytesseract
            from PIL import Image
            self._tesseract_available = True
        except ImportError:
            pass

    def extract_from_image(self, image_path: str) -> dict:
        """
        Extract earnings data from a screenshot image.

        Returns structured data: amount, platform, date, trips, raw_text.
        """
        raw_text = self._ocr_extract(image_path)
        return self._parse_text(raw_text)

    def extract_from_text(self, text: str) -> dict:
        """Parse pre-extracted text (useful for testing without OCR)."""
        return self._parse_text(text)

    def _ocr_extract(self, image_path: str) -> str:
        """Run Tesseract OCR on the image."""
        if not self._tesseract_available:
            return f"[OCR unavailable — Tesseract not installed. Image: {image_path}]"

        import pytesseract
        from PIL import Image

        try:
            image = Image.open(image_path)
            # Pre-process for better OCR
            image = image.convert("L")  # Grayscale

            text = pytesseract.image_to_string(
                image,
                lang="eng",
                config="--psm 6",  # Assume uniform block of text
            )
            return text
        except Exception as e:
            return f"[OCR Error: {e}]"

    def _parse_text(self, text: str) -> dict:
        """Parse raw OCR text into structured earnings data."""
        result = {
            "amounts": [],
            "total_amount": None,
            "trips": None,
            "platform": None,
            "date": None,
            "raw_text": text,
            "confidence": "low",
        }

        if not text:
            return result

        text_lower = text.lower()

        # Extract amounts
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = float(match.replace(",", ""))
                if amount > 0:
                    result["amounts"].append(amount)

        if result["amounts"]:
            result["total_amount"] = max(result["amounts"])
            result["confidence"] = "medium"

        # Extract trips
        for pattern in self.TRIP_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["trips"] = int(match.group(1))
                break

        # Detect platform
        for platform, keywords in self.PLATFORM_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    result["platform"] = platform
                    result["confidence"] = "high"
                    break
            if result["platform"]:
                break

        # Extract date
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["date"] = match.group(1)
                break

        return result


if __name__ == "__main__":
    pipeline = OcrPipeline()

    # Test with sample text
    sample_text = """
    Swiggy Delivery Partner
    Date: 15/03/2024

    Today's Summary
    Total Earnings: ₹1,245.50
    Completed: 12 orders
    Distance: 45 km
    Online Hours: 8.5 hrs

    Net Pay = ₹1,245.50
    """

    result = pipeline.extract_from_text(sample_text)
    print(f"Platform: {result['platform']}")
    print(f"Total: ₹{result['total_amount']}")
    print(f"Trips: {result['trips']}")
    print(f"Date: {result['date']}")
    print(f"Confidence: {result['confidence']}")
