package com.zorva.gigshield.ui.ocr

import android.app.Activity
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.zorva.gigshield.databinding.ActivityOcrBinding

/**
 * OCR Scanner — captures/selects earnings screenshots and extracts data.
 */
class OcrScannerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityOcrBinding
    private val viewModel: OcrViewModel by viewModels()
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    private val pickImage = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.data?.let { uri -> processImage(uri) }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOcrBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        observeData()
    }

    private fun setupUI() {
        binding.btnSelectImage.setOnClickListener {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            pickImage.launch(intent)
        }

        binding.btnSaveIncome.setOnClickListener {
            viewModel.saveExtractedIncome()
        }
    }

    private fun processImage(uri: Uri) {
        try {
            val image = InputImage.fromFilePath(this, uri)

            // Show preview
            val bitmap = BitmapFactory.decodeStream(contentResolver.openInputStream(uri))
            binding.ivPreview.setImageBitmap(bitmap)

            // Run ML Kit OCR
            binding.tvStatus.text = "Processing..."
            recognizer.process(image)
                .addOnSuccessListener { visionText ->
                    val rawText = visionText.text
                    binding.tvRawText.text = rawText
                    viewModel.parseEarningsText(rawText)
                    binding.tvStatus.text = "Text extracted — parsing..."
                }
                .addOnFailureListener { e ->
                    binding.tvStatus.text = "OCR failed: ${e.message}"
                    Toast.makeText(this, "OCR failed", Toast.LENGTH_SHORT).show()
                }
        } catch (e: Exception) {
            binding.tvStatus.text = "Error: ${e.message}"
        }
    }

    private fun observeData() {
        viewModel.parsedAmount.observe(this) { amount ->
            binding.tvParsedAmount.text = "Amount: ₹${String.format("%,.2f", amount)}"
        }

        viewModel.parsedPlatform.observe(this) { platform ->
            binding.tvParsedPlatform.text = "Platform: ${platform ?: "Unknown"}"
        }

        viewModel.saveStatus.observe(this) { status ->
            binding.tvStatus.text = status
        }
    }
}
