/**
 * GeoRaster NormStudio - Visualization & Map Module
 */

let map = null;
let rasterBoundsLayer = null;

// কালার প্যালেট গ্র্যাডিয়েন্ট ম্যাপ
const COLOR_PALETTES = {
    viridis: 'linear-gradient(to right, #440154, #3b528b, #21908d, #5dc963, #fde725)',
    plasma: 'linear-gradient(to right, #0d0887, #6a00a8, #b12a90, #e16462, #fca636, #f0f921)',
    terrain: 'linear-gradient(to right, #333399, #009966, #ffff66, #996633, #ffffff)',
    turbo: 'linear-gradient(to right, #30123b, #4686fb, #1ae4b6, #a2fc3c, #fb8022, #7a0403)',
    grayscale: 'linear-gradient(to right, #000000, #ffffff)',
    RdYlGn: 'linear-gradient(to right, #a50026, #f46d43, #fee08b, #d9ef8b, #66bd63, #006837)'
};

/**
 * ক্যানভাসে ছবি লোড এবং রেন্ডার করার ফাংশন
 */
function renderImageToCanvas(imageUrl, canvasId, placeholderId) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const placeholder = document.getElementById(placeholderId);

    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.onload = function() {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        if (placeholder) {
            placeholder.classList.add('hidden');
        }
        canvas.classList.remove('hidden');
    };
    img.src = imageUrl;
}

/**
 * ডায়নামিক কালার লেজেন্ড বার আপডেট করা
 */
function updateColorLegend(paletteName) {
    const legendBar = document.getElementById('legendBar');
    if (legendBar && COLOR_PALETTES[paletteName]) {
        legendBar.style.background = COLOR_PALETTES[paletteName];
    }
}

/**
 * Leaflet Interactive Map শুরু করা
 */
function initLeafletMap() {
    if (map) return; // ইতিমধ্যে ইনিশিয়ালাইজ হয়ে থাকলে স্কিপ করবে

    // ডিফল্ট ভিউ: Khulna University, Bangladesh
    map = L.map('leafletMap').setView([22.8021, 89.5342], 12);

    // OpenStreetMap Basemap Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

/**
 * জিওগ্রাফিক বন্ডিং বক্স থাকলে ম্যাপে রাস্টার বাউন্ডারি জুম করা
 */
function updateMapExtent(bounds) {
    initLeafletMap();

    if (!bounds || bounds.left === undefined) {
        return;
    }

    const southWest = L.latLng(bounds.bottom, bounds.left);
    const northEast = L.latLng(bounds.top, bounds.right);
    const latLngBounds = L.latLngBounds(southWest, northEast);

    if (rasterBoundsLayer) {
        map.removeLayer(rasterBoundsLayer);
    }

    rasterBoundsLayer = L.rectangle(latLngBounds, {
        color: "#3b82f6",
        weight: 2,
        fillColor: "#06b6d4",
        fillOpacity: 0.2
    }).addTo(map);

    map.fitBounds(latLngBounds);
}