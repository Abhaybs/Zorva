package com.zorva.gigshield.ui.gigscore

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.model.GigScore
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

class GigScoreViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _gigScore = MutableLiveData<GigScore?>()
    val gigScore: LiveData<GigScore?> = _gigScore

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _isRecalculating = MutableLiveData(false)
    val isRecalculating: LiveData<Boolean> = _isRecalculating

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadCurrentScore() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            repository.getCurrentGigScore().fold(
                onSuccess = { _gigScore.value = it },
                onFailure = {
                    // No score yet — prompt user to calculate
                    _gigScore.value = null
                    if (it.message?.contains("404") == false) {
                        _error.value = it.message
                    }
                }
            )
            _isLoading.value = false
        }
    }

    fun recalculate() {
        viewModelScope.launch {
            _isRecalculating.value = true
            _error.value = null
            repository.calculateGigScore().fold(
                onSuccess = { _gigScore.value = it },
                onFailure = { _error.value = "Could not calculate: ${it.message}" }
            )
            _isRecalculating.value = false
        }
    }
}
