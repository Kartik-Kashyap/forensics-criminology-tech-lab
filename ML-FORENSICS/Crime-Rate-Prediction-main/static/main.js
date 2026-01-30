/**
 * Crime Analysis Unit - Dashboard Intelligence
 * Developed by Kartik Kashyap
 */

document.addEventListener('DOMContentLoaded', () => {
    // Reference the Temporal Horizon Dropdown
    const yearDropdown = document.getElementById("year-dropdown");

    if (yearDropdown) {
        // Current year for reference
        const currentYear = new Date().getFullYear();
        const startYear = 2014; // Dataset baseline
        const endYear = 2035; // Proportional projection

        // Loop and add the Year values to DropDownList
        for (let i = startYear; i <= endYear; i++) {
            const option = document.createElement("option");
            option.innerHTML = i;
            option.value = i;

            // Default to matching current year if in range
            if (i === currentYear) {
                option.selected = true;
            }

            yearDropdown.appendChild(option);
        }
    }

    // Add subtle interactivity to form fields
    const inputs = document.querySelectorAll('select');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
        });
    });

    // Handle Form Submission with Loading Overlay
    const form = document.querySelector('.analysis-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    if (form && loadingOverlay) {
        form.addEventListener('submit', (e) => {
            loadingOverlay.classList.remove('hidden');
        });
    }

    // Console aesthetic initialization
    console.log("%c CRIMEVIEW FORSENSIC SYSTEM v2.0 ", "background: #00d4ff; color: #000; font-weight: bold; padding: 2px 5px;");
    console.log("%c [SYSTEM]: Initializing Analysis Engine...", "color: #00d4ff;");
    console.log("%c [SUCCESS]: Neural Weights Loaded. Ready for Query.", "color: #00ff88;");
});