package com.zorva.gigshield.ui.sos

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

/**
 * ViewModel for SOS screen.
 */
class SosViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _sosStatus = MutableLiveData("Ready")
    val sosStatus: LiveData<String> = _sosStatus

    private val _isTriggered = MutableLiveData(false)
    val isTriggered: LiveData<Boolean> = _isTriggered

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    private var currentEventId: String? = null

    fun triggerSos(latitude: Double, longitude: Double, message: String?) {
        viewModelScope.launch {
            _sosStatus.value = "Sending SOS..."

            repository.triggerSos(
                workerId = "dev-worker-001",
                lat = latitude,
                lng = longitude,
                message = message
            ).fold(
                onSuccess = { response ->
                    currentEventId = response["id"] as? String
                    _sosStatus.value = "SOS ACTIVE — Help is on the way"
                    _isTriggered.value = true
                },
                onFailure = {
                    _sosStatus.value = "Failed to send SOS"
                    _error.value = it.message
                }
            )
        }
    }

    fun resolveSos() {
        val eventId = currentEventId ?: return
        viewModelScope.launch {
            _sosStatus.value = "Resolving..."
            // Simplified — real app would call resolve API
            _sosStatus.value = "Resolved"
            _isTriggered.value = false
            currentEventId = null
        }
    }
}
