// This script handles the dynamic threshold slider on the result page.
document.addEventListener('DOMContentLoaded', () => {
    const thresholdSlider = document.getElementById('threshold-slider');
    const thresholdValueSpan = document.getElementById('threshold-value');
    const riskCategorySpan = document.getElementById('risk-category');
    const hiddenProbInput = document.getElementById('probability-hidden');

    if (thresholdSlider && thresholdValueSpan && riskCategorySpan && hiddenProbInput) {
        const probability = parseFloat(hiddenProbInput.value);
        const updateClassification = () => {
            const threshold = parseInt(thresholdSlider.value, 10) / 100.0;
            thresholdValueSpan.textContent = `${thresholdSlider.value}%`;
            if (probability >= threshold) {
                riskCategorySpan.textContent = 'High Risk';
                riskCategorySpan.classList.remove('low');
                riskCategorySpan.classList.add('high');
            } else {
                riskCategorySpan.textContent = 'Low Risk';
                riskCategorySpan.classList.remove('high');
                riskCategorySpan.classList.add('low');
            }
        };
        // Initialize display
        updateClassification();
        // Update on slider change
        thresholdSlider.addEventListener('input', updateClassification);
    }
});