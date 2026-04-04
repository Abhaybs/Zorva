package com.zorva.gigshield.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

/**
 * ViewModel for the main Dashboard screen.
 */
class DashboardViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _gigScore = MutableLiveData<GigScore>()
    val gigScore: LiveData<GigScore> = _gigScore

    private val _incomeSummary = MutableLiveData<Map<String, Any>>()
    val incomeSummary: LiveData<Map<String, Any>> = _incomeSummary

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadDashboard() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            // Load GigScore
            repository.getCurrentGigScore().fold(
                onSuccess = { _gigScore.value = it },
                onFailure = { _error.value = "Could not load GigScore" }
            )

            // Load income summary
            repository.getIncomeSummary(30).fold(
                onSuccess = { _incomeSummary.value = it },
                onFailure = { _error.value = "Could not load income summary" }
            )

            _isLoading.value = false
        }
    }

    fun refreshGigScore() {
        viewModelScope.launch {
            _isLoading.value = true
            // In real app, get worker ID from shared prefs
            repository.calculateGigScore("dev-worker-001").fold(
                onSuccess = { _gigScore.value = it },
                onFailure = { _error.value = "Score refresh failed: ${it.message}" }
            )
            _isLoading.value = false
        }
    }
}
