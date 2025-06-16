// TravelAI JavaScript Application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
    
    // Form enhancements
    enhanceForms();
    
    // Progress animations
    animateProgress();
    
    // Auto-save form data
    enableFormAutoSave();
    
    // Initialize date validation
    initializeDateValidation();
    
    // Initialize weather notifications
    const notificationBtn = document.getElementById('enableNotifications');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            window.TravelAI.requestNotificationPermission();
        });
    }
});

function initializeApp() {
    console.log('TravelAI App Initialized');
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function enhanceForms() {
    // Add real-time validation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoadingState(submitBtn);
            }
        });
        
        // Add input validation listeners
        const inputs = form.querySelectorAll('input[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                clearValidationError(this);
            });
        });
    });
    
    // Destination input enhancement
    const destinationInput = document.getElementById('destination');
    if (destinationInput) {
        let timeout;
        destinationInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                suggestDestinations(this.value);
            }, 300);
        });
    }
    
    // Budget input - removed formatting to allow large numbers
    const budgetInput = document.getElementById('budget');
    if (budgetInput) {
        // Remove any formatting restrictions
        budgetInput.addEventListener('input', function() {
            // Only allow numbers
            this.value = this.value.replace(/[^\d]/g, '');
        });
    }
}

function validateForm(form) {
    let isValid = true;
    const requiredInputs = form.querySelectorAll('input[required], select[required]');
    
    requiredInputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    // Specific validation for itinerary form
    if (form.id === 'itineraryForm') {
        const duration = parseInt(form.duration.value);
        const budget = parseFloat(form.budget.value);
        
        if (duration < 1 || duration > 30) {
            showInputError(form.duration, 'Duration must be between 1 and 30 days');
            isValid = false;
        }
        
        if (budget < 1000) {
            showInputError(form.budget, 'Budget must be at least ₹1,000');
            isValid = false;
        }
        
        // Check if at least one interest is selected
        const interests = form.querySelectorAll('input[name="interests"]:checked');
        if (interests.length === 0) {
            showAlert('Please select at least one travel interest', 'warning');
        }
    }
    
    return isValid;
}

function validateInput(input) {
    const value = input.value.trim();
    
    if (input.hasAttribute('required') && !value) {
        showInputError(input, 'This field is required');
        return false;
    }
    
    if (input.type === 'email' && value && !isValidEmail(value)) {
        showInputError(input, 'Please enter a valid email address');
        return false;
    }
    
    if (input.type === 'number' && value) {
        const num = parseFloat(value);
        const min = input.getAttribute('min');
        const max = input.getAttribute('max');
        
        if (min && num < parseFloat(min)) {
            showInputError(input, `Minimum value is ${min}`);
            return false;
        }
        
        if (max && num > parseFloat(max)) {
            showInputError(input, `Maximum value is ${max}`);
            return false;
        }
    }
    
    clearValidationError(input);
    return true;
}

function showInputError(input, message) {
    clearValidationError(input);
    
    input.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
}

function clearValidationError(input) {
    input.classList.remove('is-invalid');
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showLoadingState(button) {
    const originalContent = button.innerHTML;
    button.dataset.originalContent = originalContent;
    
    const loadingSpinner = '<i class="fas fa-spinner fa-spin me-2"></i>';
    const loadingText = button.dataset.loadingText || 'Processing...';
    
    button.innerHTML = loadingSpinner + loadingText;
    button.disabled = true;
    
    // Auto-restore after 30 seconds (fallback)
    setTimeout(() => {
        if (button.disabled) {
            restoreButtonState(button);
        }
    }, 30000);
}

function restoreButtonState(button) {
    if (button.dataset.originalContent) {
        button.innerHTML = button.dataset.originalContent;
        button.disabled = false;
        delete button.dataset.originalContent;
    }
}

function suggestDestinations(query) {
    if (!query || query.length < 2) return;
    
    // Popular Indian destinations for suggestions
    const destinations = [
        'Goa', 'Kerala', 'Rajasthan', 'Himachal Pradesh', 'Uttarakhand',
        'Kashmir', 'Tamil Nadu', 'Karnataka', 'Maharashtra', 'Gujarat',
        'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata',
        'Jaipur', 'Udaipur', 'Agra', 'Varanasi', 'Rishikesh',
        'Manali', 'Shimla', 'Dharamshala', 'Leh Ladakh', 'Andaman',
        'Ooty', 'Munnar', 'Coorg', 'Hampi', 'Khajuraho'
    ];
    
    const filtered = destinations.filter(dest => 
        dest.toLowerCase().includes(query.toLowerCase())
    );
    
    if (filtered.length > 0) {
        showDestinationSuggestions(filtered.slice(0, 5));
    }
}

function showDestinationSuggestions(suggestions) {
    const input = document.getElementById('destination');
    if (!input) return;
    
    // Remove existing suggestions
    const existingSuggestions = document.getElementById('destination-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    // Create suggestions dropdown
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.id = 'destination-suggestions';
    suggestionsDiv.className = 'destination-suggestions';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = suggestion;
        item.addEventListener('click', () => {
            input.value = suggestion;
            suggestionsDiv.remove();
        });
        suggestionsDiv.appendChild(item);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestionsDiv);
    
    // Remove suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.remove();
        }
    }, { once: true });
}

function formatBudgetInput(input) {
    // Function removed - budget input now accepts raw numbers without formatting
}

function animateProgress() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = width;
        }, 200);
    });
}

function enableFormAutoSave() {
    const form = document.getElementById('itineraryForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Load saved data
        const savedValue = localStorage.getItem(`autosave_${input.name}`);
        if (savedValue && input.type !== 'checkbox') {
            input.value = savedValue;
        } else if (savedValue && input.type === 'checkbox') {
            input.checked = savedValue === 'true';
        }
        
        // Save on change
        input.addEventListener('change', function() {
            if (this.type === 'checkbox') {
                localStorage.setItem(`autosave_${this.name}`, this.checked);
            } else {
                localStorage.setItem(`autosave_${this.name}`, this.value);
            }
        });
    });
    
    // Clear autosave on successful form submission
    form.addEventListener('submit', function() {
        inputs.forEach(input => {
            localStorage.removeItem(`autosave_${input.name}`);
        });
    });
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Checkpoint completion handler
function handleCheckpointCompletion(checkpointId) {
    const form = document.querySelector(`form[action*="${checkpointId}"]`);
    if (form) {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Marking Complete...';
                button.disabled = true;
            }
        });
    }
}

// Real-time clock for tracking page
function updateTrackingTime() {
    const timeElements = document.querySelectorAll('.current-time');
    timeElements.forEach(element => {
        element.textContent = new Date().toLocaleTimeString();
    });
}

// Update time every second on tracking page
if (window.location.pathname.includes('/tracking/')) {
    setInterval(updateTrackingTime, 1000);
}

// Destination suggestions styling
const style = document.createElement('style');
style.textContent = `
    .destination-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #dee2e6;
        border-top: none;
        border-radius: 0 0 0.375rem 0.375rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .suggestion-item {
        padding: 0.5rem 0.75rem;
        cursor: pointer;
        border-bottom: 1px solid #f8f9fa;
    }
    
    .suggestion-item:hover {
        background-color: hsl(var(--primary) / 0.1);
        color: hsl(var(--primary));
    }
    
    .suggestion-item:last-child {
        border-bottom: none;
    }
`;
document.head.appendChild(style);

function initializeDateValidation() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;
        
        startDateInput.addEventListener('change', function() {
            const startDate = new Date(this.value);
            const minEndDate = new Date(startDate);
            minEndDate.setDate(minEndDate.getDate() + 1);
            endDateInput.min = minEndDate.toISOString().split('T')[0];
            
            if (endDateInput.value && new Date(endDateInput.value) <= startDate) {
                endDateInput.value = minEndDate.toISOString().split('T')[0];
            }
        });
        
        endDateInput.addEventListener('change', function() {
            const endDate = new Date(this.value);
            const startDate = new Date(startDateInput.value);
            
            if (startDate && endDate <= startDate) {
                showAlert('End date must be after start date', 'warning');
                this.value = '';
            }
        });
    }
}

// Weather notification system
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showAlert('Weather alerts enabled for your trips', 'success');
            }
        });
    }
}

function showWeatherAlert(destination, weatherData) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(`Weather Alert: ${destination}`, {
            body: `${weatherData.description}. Temperature: ${weatherData.temp}°C`,
            icon: '/static/images/weather-icon.png',
            badge: '/static/images/app-icon.png'
        });
        
        notification.onclick = function() {
            window.focus();
            this.close();
        };
    }
}

// Check weather for upcoming trips
async function checkWeatherAlerts() {
    try {
        const response = await fetch('/api/weather-alerts');
        const alerts = await response.json();
        
        alerts.forEach(alert => {
            if (alert.severity === 'high') {
                showWeatherAlert(alert.destination, alert.weather);
            }
        });
    } catch (error) {
        console.log('Weather service unavailable');
    }
}

// Initialize weather alerts on page load
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').then(registration => {
        console.log('Service Worker registered');
    });
}

// Check for weather alerts every hour
setInterval(checkWeatherAlerts, 3600000);

// Initialize notification permissions check on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if notifications are already granted
    if ('Notification' in window && Notification.permission === 'granted') {
        const btn = document.getElementById('enableNotifications');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-check me-1"></i>Notifications Enabled';
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-success');
            btn.disabled = true;
            // Start checking for weather alerts automatically
            checkWeatherAlerts();
        }
    }
});

// Export functions for global access
window.TravelAI = {
    showAlert,
    validateForm,
    handleCheckpointCompletion,
    suggestDestinations,
    requestNotificationPermission,
    checkWeatherAlerts
};
