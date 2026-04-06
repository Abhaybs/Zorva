package com.zorva.gigshield.ui.earnings

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.model.BestHour
import com.zorva.gigshield.data.model.ZoneRecommendation
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

class EarningsOptimizerViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _zones = MutableLiveData<List<ZoneRecommendation>>()
    val zones: LiveData<List<ZoneRecommendation>> = _zones

    private val _bestHours = MutableLiveData<List<BestHour>>()
    val bestHours: LiveData<List<BestHour>> = _bestHours

    private val _selectedZone = MutableLiveData<String>()
    val selectedZone: LiveData<String> = _selectedZone

    private val _isLoadingZones = MutableLiveData(false)
    val isLoadingZones: LiveData<Boolean> = _isLoadingZones

    private val _isLoadingHours = MutableLiveData(false)
    val isLoadingHours: LiveData<Boolean> = _isLoadingHours

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadRecommendedZones(lat: Double? = null, lng: Double? = null) {
        viewModelScope.launch {
            _isLoadingZones.value = true
            _error.value = null
            repository.getRecommendedZones(lat = lat, lng = lng).fold(
                onSuccess = { response ->
                    _zones.value = response.zones.orEmpty()
                    // Auto-load best hours for the top zone
                    response.zones.orEmpty().firstOrNull()?.let { loadBestHours(it.zone_name) }
                },
                onFailure = { _error.value = "Could not load zones: ${it.message}" }
            )
            _isLoadingZones.value = false
        }
    }

    fun loadBestHours(zoneName: String) {
        _selectedZone.value = zoneName
        viewModelScope.launch {
            _isLoadingHours.value = true
            repository.getBestHours(zoneName).fold(
                onSuccess = { _bestHours.value = it.top_hours },
                onFailure = { _error.value = "Could not load hours: ${it.message}" }
            )
            _isLoadingHours.value = false
        }
    }
}
