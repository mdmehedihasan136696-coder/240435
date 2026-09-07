// Interactive Before/After Split Comparison Slider

const ComparisonSlider = {
    init: function() {
        const sliderContainer = document.getElementById('comparison-slider-container');
        const sliderHandle = document.getElementById('slider-handle');
        const overlayImgBox = document.getElementById('slider-overlay-box');

        if (!sliderContainer || !sliderHandle || !overlayImgBox) return;

        let isDragging = false;

        const moveSlider = (clientX) => {
            const rect = sliderContainer.getBoundingClientRect();
            let x = clientX - rect.left;
            
            // Constrain
            if (x < 0) x = 0;
            if (x > rect.width) x = rect.width;

            const percentage = (x / rect.width) * 100;

            sliderHandle.style.left = `${percentage}%`;
            overlayImgBox.style.width = `${percentage}%`;
        };

        sliderHandle.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault();
        });

        window.addEventListener('mouseup', () => {
            isDragging = false;
        });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            moveSlider(e.clientX);
        });

        // Touch event support for smartphones/tablets
        sliderHandle.addEventListener('touchstart', () => { isDragging = true; });
        window.addEventListener('touchend', () => { isDragging = false; });
        window.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            moveSlider(e.touches[0].clientX);
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ComparisonSlider.init();
});