let map = null;
let busMarker = null;
let stopMarkers = [];
let currentBusId = null;

document.addEventListener('DOMContentLoaded', function() {
    map = L.map('busMap').setView([28.6139, 77.2090], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    const busSelect = document.getElementById('bus-select');
    if (busSelect && busSelect.value) {
        loadBusData(busSelect.value);
    }
});

function selectBus() {
    const busId = document.getElementById('bus-select').value;
    if (!busId) {
        alert('Please select a bus');
        return;
    }
    
    fetch('/select-bus', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bus_id: busId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadBusData(busId);
    });
}

function loadBusData(busId) {
    currentBusId = busId;
    
    fetch(`/bus/${busId}/data`)
        .then(response => response.json())
        .then(data => {
            updateMap(data);
            document.getElementById('bus-info').classList.remove('hidden');
            document.getElementById('stops-list').classList.remove('hidden');
        });
    
    setInterval(() => {
        if (currentBusId) {
            fetch(`/bus/${currentBusId}/location`)
                .then(response => response.json())
                .then(data => updateBusLocation(data));
        }
    }, 5000);
}

function updateMap(data) {
    if (data.current_lat && data.current_lng) {
        if (busMarker) {
            busMarker.setLatLng([data.current_lat, data.current_lng]);
        } else {
            busMarker = L.marker([data.current_lat, data.current_lng]).addTo(map);
        }
        map.setView([data.current_lat, data.current_lng], 14);
    }
    
    stopMarkers.forEach(marker => marker.remove());
    stopMarkers = [];
    
    if (data.stops) {
        let stopsHTML = '';
        data.stops.forEach(stop => {
            const color = stop.is_crossed ? '#ef4444' : '#10b981';
            const marker = L.circleMarker([stop.lat, stop.lng], {
                color: color,
                fillColor: color,
                fillOpacity: 0.5,
                radius: 8
            }).addTo(map).bindPopup(stop.stop_name);
            stopMarkers.push(marker);
            
            stopsHTML += `
                <div class="flex items-center justify-between p-2 rounded" style="background-color: ${stop.is_crossed ? '#fee2e2' : '#d1fae5'}">
                    <span class="text-sm">${stop.stop_name}</span>
                    <span class="text-xs ${stop.is_crossed ? 'text-red-600' : 'text-green-600'}">${stop.is_crossed ? 'Crossed' : 'Upcoming'}</span>
                </div>
            `;
        });
        document.getElementById('stops-container').innerHTML = stopsHTML;
    }
}

function updateBusLocation(data) {
    if (data.lat && data.lng && busMarker) {
        busMarker.setLatLng([data.lat, data.lng]);
    }
}
