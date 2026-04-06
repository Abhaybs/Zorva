package com.zorva.gigshield.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.zorva.gigshield.data.model.Income
import com.zorva.gigshield.data.repository.WorkerRepository
import kotlinx.coroutines.launch

class DashboardViewModel : ViewModel() {

    private val repository = WorkerRepository()

    private val _platformEarnings = MutableLiveData<Map<String, Double>>(emptyMap())
    val platformEarnings: LiveData<Map<String, Double>> = _platformEarnings

    private val _recentIncome = MutableLiveData<List<Income>>(emptyList())
    val recentIncome: LiveData<List<Income>> = _recentIncome

    private val _bestZone = MutableLiveData<String?>(null)
    val bestZone: LiveData<String?> = _bestZone

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    fun loadDashboard(lat: Double? = null, lng: Double? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            // Income history → platform breakdown + recent activity
            repository.getIncomeHistory(100).fold(
                onSuccess = { history ->
                    val grouped = history.groupBy { it.platform.lowercase() }
                    _platformEarnings.value = grouped.mapValues { (_, v) -> v.sumOf { it.amount } }
                    _recentIncome.value = history.take(8)
                },
                onFailure = { /* silent — show placeholders */ }
            )

            // Best zone for tonight's banner
            repository.getRecommendedZones(1, lat = lat, lng = lng).fold(
                onSuccess = { resp ->
                    resp.zones.orEmpty().firstOrNull()?.let { zone ->
                        _bestZone.value =
                            "${zone.zone_name} 7PM-10PM \u2014 Avg \u20b9${zone.predicted_earnings_per_hour.toInt()}/hr"
                    }
                },
                onFailure = { /* silent */ }
            )

            _isLoading.value = false
        }
    }
}
