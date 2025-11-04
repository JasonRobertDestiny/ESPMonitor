/**
 * ESPMonitor Dashboard JavaScript
 * Handles real-time data updates and user interactions
 */

// Configuration
const API_BASE_URL = '';  // Same origin
const UPDATE_INTERVAL = 5000;  // Update every 5 seconds

// Global state
let updateTimer = null;
let thresholds = {
    temperature: 30.0,
    humidity: 70.0,
    water_level: 80.0
};

// ==================== Utility Functions ====================
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    // Simple console notification (can be enhanced with toast notifications)
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==================== API Functions ====================
async function fetchLatestData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/latest-data?limit=1`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        if (data && data.length > 0) {
            updateDisplay(data[0]);
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    } catch (error) {
        console.error('Error fetching latest data:', error);
        updateConnectionStatus(false);
    }
}

async function fetchThresholds() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/thresholds`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        thresholds = data;
        updateThresholdDisplay();
    } catch (error) {
        console.error('Error fetching thresholds:', error);
    }
}

async function updateThresholds() {
    const newThresholds = {
        temperature: parseFloat(document.getElementById('temp-threshold').value),
        humidity: parseFloat(document.getElementById('humidity-threshold').value),
        water_level: parseFloat(document.getElementById('water-threshold').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/thresholds`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newThresholds)
        });

        if (!response.ok) throw new Error('Failed to update thresholds');

        const result = await response.json();
        thresholds = result.thresholds;
        updateThresholdDisplay();
        showNotification('阈值更新成功', 'success');
    } catch (error) {
        console.error('Error updating thresholds:', error);
        showNotification('阈值更新失败', 'error');
    }
}

async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/latest-data?limit=20`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        updateHistoryTable(data);
    } catch (error) {
        console.error('Error fetching history:', error);
    }
}

async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        updateStatsDisplay(data);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// ==================== Display Update Functions ====================
function updateDisplay(data) {
    // Update main values
    document.getElementById('temperature').textContent = data.temperature.toFixed(1);
    document.getElementById('humidity').textContent = data.humidity.toFixed(1);
    document.getElementById('water-level').textContent = data.water_level.toFixed(1);

    // Update last update time
    document.getElementById('last-update').textContent = `最后更新: ${formatDateTime(data.timestamp)}`;

    // Check for alerts
    checkAlerts(data);
}

function checkAlerts(data) {
    const tempCard = document.querySelector('.data-cards .card:nth-child(1)');
    const humidityCard = document.querySelector('.data-cards .card:nth-child(2)');
    const waterCard = document.querySelector('.data-cards .card:nth-child(3)');

    // Temperature alert
    if (data.temperature > thresholds.temperature) {
        tempCard.classList.add('alert');
    } else {
        tempCard.classList.remove('alert');
    }

    // Humidity alert
    if (data.humidity > thresholds.humidity) {
        humidityCard.classList.add('alert');
    } else {
        humidityCard.classList.remove('alert');
    }

    // Water level alert
    if (data.water_level > thresholds.water_level) {
        waterCard.classList.add('alert');
    } else {
        waterCard.classList.remove('alert');
    }
}

function updateConnectionStatus(isConnected) {
    const statusElement = document.getElementById('connection-status');
    if (isConnected) {
        statusElement.textContent = '在线';
        statusElement.className = 'status-indicator online';
    } else {
        statusElement.textContent = '离线';
        statusElement.className = 'status-indicator offline';
    }
}

function updateThresholdDisplay() {
    document.getElementById('temp-threshold').value = thresholds.temperature;
    document.getElementById('humidity-threshold').value = thresholds.humidity;
    document.getElementById('water-threshold').value = thresholds.water_level;

    document.getElementById('current-temp-threshold').textContent = thresholds.temperature;
    document.getElementById('current-humidity-threshold').textContent = thresholds.humidity;
    document.getElementById('current-water-threshold').textContent = thresholds.water_level;
}

function updateHistoryTable(data) {
    const tbody = document.getElementById('history-body');

    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="no-data">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(item => `
        <tr>
            <td>${formatDateTime(item.timestamp)}</td>
            <td>${item.device_id}</td>
            <td>${item.temperature.toFixed(1)}</td>
            <td>${item.humidity.toFixed(1)}</td>
            <td>${item.water_level.toFixed(1)}</td>
        </tr>
    `).join('');
}

function updateStatsDisplay(stats) {
    if (stats.message) {
        // No data available
        return;
    }

    // Temperature stats
    document.getElementById('avg-temp').textContent = stats.temperature.avg;
    document.getElementById('max-temp').textContent = stats.temperature.max;
    document.getElementById('min-temp').textContent = stats.temperature.min;

    // Humidity stats
    document.getElementById('avg-humidity').textContent = stats.humidity.avg;
    document.getElementById('max-humidity').textContent = stats.humidity.max;
    document.getElementById('min-humidity').textContent = stats.humidity.min;

    // Water level stats
    document.getElementById('avg-water').textContent = stats.water_level.avg;
    document.getElementById('max-water').textContent = stats.water_level.max;
    document.getElementById('min-water').textContent = stats.water_level.min;
}

// ==================== Auto Update ====================
function startAutoUpdate() {
    // Initial fetch
    fetchLatestData();
    fetchThresholds();
    fetchHistory();
    fetchStats();

    // Set up periodic updates
    updateTimer = setInterval(() => {
        fetchLatestData();
        fetchHistory();
        fetchStats();
    }, UPDATE_INTERVAL);
}

function stopAutoUpdate() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
}

// ==================== Event Listeners ====================
document.addEventListener('DOMContentLoaded', () => {
    // Start auto-update
    startAutoUpdate();

    // Update thresholds button
    document.getElementById('update-thresholds').addEventListener('click', updateThresholds);

    // Stop updates when page is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopAutoUpdate();
        } else {
            startAutoUpdate();
        }
    });
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopAutoUpdate();
});
