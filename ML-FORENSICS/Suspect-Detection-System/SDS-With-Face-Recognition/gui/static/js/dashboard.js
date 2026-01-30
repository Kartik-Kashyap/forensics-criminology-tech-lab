/**
 * Forensic Suspect Detection System
 * Dashboard JavaScript
 */

// ==================== STATE ====================
let systemRunning = false;
let updateInterval = null;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('[SDS] Dashboard initialized');
    
    // Start clock
    updateDateTime();
    setInterval(updateDateTime, 1000);
    
    // Load initial data
    loadWatchlist();
    updateSystemStatus();
    
    // Set up periodic updates
    updateInterval = setInterval(() => {
        if (systemRunning) {
            updateSystemStatus();
            updateAlerts();
        }
    }, 2000);  // Update every 2 seconds
});

// ==================== DATETIME ====================
function updateDateTime() {
    const now = new Date();
    const formatted = now.toISOString().replace('T', ' ').substring(0, 19);
    document.getElementById('datetime').textContent = formatted + ' UTC';
}

// ==================== SYSTEM CONTROL ====================
async function startSystem() {
    try {
        const response = await fetch('/api/system/start', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            systemRunning = true;
            updateSystemStatusUI(true);
            
            // Wait a bit then load cameras
            setTimeout(() => {
                loadCameras();
            }, 1000);
            
            console.log('[SDS] System started');
        } else {
            alert('Failed to start system: ' + data.message);
        }
    } catch (error) {
        console.error('[SDS] Error starting system:', error);
        alert('Error starting system');
    }
}

async function stopSystem() {
    try {
        const response = await fetch('/api/system/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            systemRunning = false;
            updateSystemStatusUI(false);
            clearCameras();
            console.log('[SDS] System stopped');
        } else {
            alert('Failed to stop system: ' + data.message);
        }
    } catch (error) {
        console.error('[SDS] Error stopping system:', error);
        alert('Error stopping system');
    }
}

async function generateReport() {
    try {
        const response = await fetch('/api/report/generate', {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert(`Report generated successfully!\n\nSaved to: ${data.path}\n\nCheck the evidence/ directory.`);
            console.log('[SDS] Report generated:', data.filename);
        } else {
            alert('Failed to generate report: ' + data.message);
        }
    } catch (error) {
        console.error('[SDS] Error generating report:', error);
        alert('Error generating report');
    }
}

function updateSystemStatusUI(running) {
    const indicator = document.getElementById('systemStatusIndicator');
    const statusText = document.getElementById('systemStatusText');
    const btnStart = document.getElementById('btnStart');
    const btnStop = document.getElementById('btnStop');
    
    if (running) {
        indicator.classList.add('active');
        statusText.textContent = 'ACTIVE';
        btnStart.disabled = true;
        btnStop.disabled = false;
    } else {
        indicator.classList.remove('active');
        statusText.textContent = 'STANDBY';
        btnStart.disabled = false;
        btnStop.disabled = true;
    }
}

// ==================== SYSTEM STATUS ====================
async function updateSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        const data = await response.json();
        
        systemRunning = data.running;
        updateSystemStatusUI(data.running);
        
        // Update counts
        document.getElementById('watchlistCount').textContent = data.watchlist_count;
        
        if (data.alerts) {
            document.getElementById('alertCount').textContent = data.alerts.total_alerts;
            
            // Count by risk level
            const critical = data.alerts.alerts_by_risk.CRITICAL || 0;
            const high = data.alerts.alerts_by_risk.HIGH || 0;
            
            document.getElementById('criticalCount').textContent = critical;
            document.getElementById('highCount').textContent = high;
        }
        
    } catch (error) {
        console.error('[SDS] Error updating system status:', error);
    }
}

// ==================== CAMERAS ====================
async function loadCameras() {
    try {
        const response = await fetch('/api/camera/list');
        const cameras = await response.json();
        
        const cameraGrid = document.getElementById('cameraGrid');
        cameraGrid.innerHTML = '';
        
        if (cameras.length === 0) {
            cameraGrid.innerHTML = `
                <div class="camera-placeholder">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                        <circle cx="12" cy="13" r="4"/>
                    </svg>
                    <p>NO CAMERAS DETECTED</p>
                    <p class="small">Check camera connections</p>
                </div>
            `;
            return;
        }
        
        cameras.forEach(cameraId => {
            const feedDiv = document.createElement('div');
            feedDiv.className = 'camera-feed';
            feedDiv.innerHTML = `
                <img src="/video_feed/${cameraId}" alt="${cameraId}">
                <div class="camera-label">${cameraId}</div>
            `;
            cameraGrid.appendChild(feedDiv);
        });
        
        document.getElementById('cameraCount').textContent = `${cameras.length} CAMERAS`;
        
    } catch (error) {
        console.error('[SDS] Error loading cameras:', error);
    }
}

function clearCameras() {
    const cameraGrid = document.getElementById('cameraGrid');
    cameraGrid.innerHTML = `
        <div class="camera-placeholder">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
            </svg>
            <p>SYSTEM STOPPED</p>
        </div>
    `;
    document.getElementById('cameraCount').textContent = '0 CAMERAS';
}

// ==================== ALERTS ====================
async function updateAlerts() {
    try {
        const response = await fetch('/api/alerts/recent?hours=24');
        const alerts = await response.json();
        
        const alertList = document.getElementById('alertList');
        
        if (alerts.length === 0) {
            alertList.innerHTML = `
                <div class="no-alerts">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                    <p>NO ACTIVE ALERTS</p>
                </div>
            `;
            return;
        }
        
        alertList.innerHTML = '';
        
        // Show most recent 20 alerts
        const recentAlerts = alerts.slice(0, 20);
        
        recentAlerts.forEach(alert => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert-item ${alert.risk_level.toLowerCase()}`;
            
            const timestamp = new Date(alert.timestamp).toLocaleString();
            const confidence = (alert.confidence * 100).toFixed(1);
            
            alertDiv.innerHTML = `
                <div class="alert-header">
                    <div class="alert-name">${alert.full_name}</div>
                    <div class="alert-risk ${alert.risk_level.toLowerCase()}">${alert.risk_level}</div>
                </div>
                <div class="alert-details">
                    <div>
                        <span>Alert ID:</span>
                        <span>${alert.alert_id}</span>
                    </div>
                    <div>
                        <span>Person ID:</span>
                        <span>${alert.person_id}</span>
                    </div>
                    <div>
                        <span>Case:</span>
                        <span>${alert.case_id}</span>
                    </div>
                    <div>
                        <span>Status:</span>
                        <span>${alert.legal_status}</span>
                    </div>
                    <div>
                        <span>Camera:</span>
                        <span>${alert.camera_id}</span>
                    </div>
                    <div>
                        <span>Confidence:</span>
                        <span>${confidence}%</span>
                    </div>
                    <div>
                        <span>Time:</span>
                        <span>${timestamp}</span>
                    </div>
                    ${alert.mask_detected ? '<div><span>⚠️ Mask Detected</span></div>' : ''}
                </div>
            `;
            
            alertList.appendChild(alertDiv);
        });
        
    } catch (error) {
        console.error('[SDS] Error updating alerts:', error);
    }
}

// ==================== WATCHLIST ====================
async function loadWatchlist() {
    try {
        const response = await fetch('/api/watchlist');
        const watchlist = await response.json();
        
        const watchlistList = document.getElementById('watchlistList');
        
        if (watchlist.length === 0) {
            watchlistList.innerHTML = '<div class="loading">No entries in watchlist</div>';
            return;
        }
        
        watchlistList.innerHTML = '';
        
        watchlist.forEach(person => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'watchlist-item';
            
            const dateAdded = new Date(person.DateAdded).toLocaleDateString();
            const lastDetected = person.LastDetected ? 
                new Date(person.LastDetected).toLocaleDateString() : 
                'Never';
            
            itemDiv.innerHTML = `
                <div class="watchlist-header">
                    <div class="watchlist-name">${person.FullName}</div>
                    <div class="watchlist-status">${person.LegalStatus}</div>
                </div>
                <div class="watchlist-info">
                    <div>
                        <span>ID:</span>
                        <span>${person.PersonID}</span>
                    </div>
                    <div>
                        <span>Case:</span>
                        <span>${person.CaseID}</span>
                    </div>
                    <div>
                        <span>Risk:</span>
                        <span>${person.RiskLevel}</span>
                    </div>
                    <div>
                        <span>Added:</span>
                        <span>${dateAdded}</span>
                    </div>
                    <div>
                        <span>Last Seen:</span>
                        <span>${lastDetected}</span>
                    </div>
                </div>
            `;
            
            watchlistList.appendChild(itemDiv);
        });
        
        document.getElementById('watchlistCount').textContent = watchlist.length;
        
    } catch (error) {
        console.error('[SDS] Error loading watchlist:', error);
        document.getElementById('watchlistList').innerHTML = 
            '<div class="loading">Error loading watchlist</div>';
    }
}

function refreshWatchlist() {
    loadWatchlist();
}

// ==================== SEARCH ====================
document.getElementById('watchlistSearch').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const items = document.querySelectorAll('.watchlist-item');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function(e) {
    // CTRL+SHIFT+S: Start/Stop system
    if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        if (systemRunning) {
            stopSystem();
        } else {
            startSystem();
        }
    }
});

console.log('[SDS] Dashboard script loaded');