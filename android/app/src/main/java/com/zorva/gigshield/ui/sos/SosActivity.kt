package com.zorva.gigshield.ui.sos

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import com.zorva.gigshield.databinding.ActivitySosBinding

/**
 * SOS emergency screen — one-tap emergency trigger with GPS broadcast.
 */
class SosActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySosBinding
    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private val viewModel: SosViewModel by viewModels()

    companion object {
        private const val LOCATION_PERMISSION_REQUEST = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySosBinding.inflate(layoutInflater)
        setContentView(binding.root)

        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

        setupUI()
        observeData()
    }

    private fun setupUI() {
        // Giant SOS button
        binding.btnSosTrigger.setOnClickListener {
            triggerSos()
        }

        binding.btnCancel.setOnClickListener {
            finish()
        }

        binding.btnResolve.setOnClickListener {
            viewModel.resolveSos()
        }
    }

    private fun triggerSos() {
        if (ActivityCompat.checkSelfPermission(
                this, Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
                LOCATION_PERMISSION_REQUEST
            )
            return
        }

        fusedLocationClient.lastLocation.addOnSuccessListener { location ->
            if (location != null) {
                viewModel.triggerSos(
                    latitude = location.latitude,
                    longitude = location.longitude,
                    message = binding.etMessage.text.toString().ifBlank { null }
                )
            } else {
                Toast.makeText(this, "Could not get location", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun observeData() {
        viewModel.sosStatus.observe(this) { status ->
            binding.tvStatus.text = "Status: $status"
        }

        viewModel.isTriggered.observe(this) { triggered ->
            binding.btnSosTrigger.isEnabled = !triggered
            binding.btnResolve.isEnabled = triggered
        }

        viewModel.error.observe(this) { error ->
            error?.let { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() }
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_PERMISSION_REQUEST) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                triggerSos()
            } else {
                Toast.makeText(this, "Location permission required for SOS", Toast.LENGTH_LONG).show()
            }
        }
    }
}
