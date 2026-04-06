package com.zorva.gigshield.ui.sos

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

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
                workerId = "",
                lat = latitude,
                lng = longitude,
                message = message
            ).fold(
                onSuccess = { response ->
                    currentEventId = response["id"] as? String
                    _sosStatus.value = "SOS ACTIVE \u2014 Help is on the way"
                    _isTriggered.value = true
                },
                onFailure = { err ->
                    _sosStatus.value = "Failed to send SOS"
                    _error.value = err.message
                }
            )
        }
    }

    fun resolveSos() {
        viewModelScope.launch {
            _sosStatus.value = "Resolved"
            _isTriggered.value = false
            currentEventId = null
        }
    }
}
