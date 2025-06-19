import React from 'react';
import ReactDOM from 'react-dom/client';
import ItineraryForm from './components/ItineraryForm';
import ItineraryTracker from './components/ItineraryTracker';
import WeatherWidget from './components/WeatherWidget';

// Initialize React components based on page
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure all scripts are loaded
    setTimeout(() => {
        // Itinerary Form Component
        const formContainer = document.getElementById('react-itinerary-form');
        if (formContainer) {
            // Hide loading spinner
            const loadingDiv = document.getElementById('form-loading');
            if (loadingDiv) loadingDiv.style.display = 'none';
            
            // Show fallback form if React fails
            const fallbackForm = document.getElementById('fallback-form');
            
            try {
                const root = ReactDOM.createRoot(formContainer);
                root.render(<ItineraryForm />);
                console.log('React form loaded successfully');
            } catch (error) {
                console.error('React form failed to load:', error);
                if (fallbackForm) {
                    fallbackForm.style.display = 'block';
                    formContainer.style.display = 'none';
                }
            }
        }

        // Itinerary Tracker Component
        const trackerContainer = document.getElementById('react-tracker');
        if (trackerContainer) {
            const itineraryId = trackerContainer.dataset.itineraryId;
            const root = ReactDOM.createRoot(trackerContainer);
            root.render(<ItineraryTracker itineraryId={itineraryId} />);
        }

        // Weather Widget Component
        const weatherContainer = document.getElementById('react-weather');
        if (weatherContainer) {
            const destination = weatherContainer.dataset.destination;
            const root = ReactDOM.createRoot(weatherContainer);
            root.render(<WeatherWidget destination={destination} />);
        }
    }, 100);
});