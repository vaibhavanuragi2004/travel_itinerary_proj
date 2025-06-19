import React, { useState, useEffect } from 'react';

const ItineraryForm = () => {
    const [formData, setFormData] = useState({
        destination: '',
        start_date: '',
        end_date: '',
        budget: '',
        interests: []
    });
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    const interestOptions = [
        'Adventure', 'Culture', 'Food', 'Nature', 'History', 
        'Shopping', 'Nightlife', 'Photography', 'Spiritual', 'Beach'
    ];

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        
        if (name === 'destination' && value.length > 2) {
            fetchDestinationSuggestions(value);
        }
    };

    const handleInterestChange = (interest) => {
        setFormData(prev => ({
            ...prev,
            interests: prev.interests.includes(interest)
                ? prev.interests.filter(i => i !== interest)
                : [...prev.interests, interest]
        }));
    };

    const fetchDestinationSuggestions = async (query) => {
        try {
            // This would typically call your Flask API endpoint
            // For now, we'll use a simple filter of popular destinations
            const popularDestinations = [
                'Mumbai, India', 'Delhi, India', 'Bangalore, India', 'Goa, India',
                'Kerala, India', 'Rajasthan, India', 'Himachal Pradesh, India',
                'Tamil Nadu, India', 'Karnataka, India', 'Punjab, India'
            ];
            
            const filtered = popularDestinations.filter(dest => 
                dest.toLowerCase().includes(query.toLowerCase())
            );
            setSuggestions(filtered.slice(0, 5));
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    };

    const validateForm = () => {
        const newErrors = {};
        
        if (!formData.destination.trim()) {
            newErrors.destination = 'Destination is required';
        }
        
        if (!formData.start_date) {
            newErrors.start_date = 'Start date is required';
        }
        
        if (!formData.end_date) {
            newErrors.end_date = 'End date is required';
        }
        
        if (formData.start_date && formData.end_date && 
            new Date(formData.start_date) >= new Date(formData.end_date)) {
            newErrors.end_date = 'End date must be after start date';
        }
        
        if (!formData.budget || formData.budget <= 0) {
            newErrors.budget = 'Please enter a valid budget';
        }
        
        if (formData.interests.length === 0) {
            newErrors.interests = 'Please select at least one interest';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        setLoading(true);
        
        try {
            const response = await fetch('/generate_itinerary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    ...formData,
                    interests: formData.interests
                })
            });
            
            if (response.redirected) {
                window.location.href = response.url;
            } else if (response.ok) {
                // Handle successful response
                const result = await response.text();
                if (result.includes('/itinerary/')) {
                    window.location.href = result;
                } else {
                    window.location.reload();
                }
            } else {
                throw new Error('Failed to generate itinerary');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate itinerary. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="row justify-content-center">
            <div className="col-lg-8">
                <div className="card border-0 shadow-lg">
                    <div className="card-body p-5">
                        <h3 className="text-center mb-4 text-primary">Plan Your Perfect Trip</h3>
                        
                        <form onSubmit={handleSubmit}>
                            {/* Destination Input */}
                            <div className="mb-4 position-relative">
                                <label className="form-label fw-bold">
                                    <i className="fas fa-map-marker-alt me-2 text-primary"></i>
                                    Where do you want to go?
                                </label>
                                <input
                                    type="text"
                                    name="destination"
                                    className={`form-control form-control-lg ${errors.destination ? 'is-invalid' : ''}`}
                                    placeholder="Enter your dream destination..."
                                    value={formData.destination}
                                    onChange={handleInputChange}
                                    autoComplete="off"
                                />
                                {errors.destination && (
                                    <div className="invalid-feedback">{errors.destination}</div>
                                )}
                                
                                {/* Suggestions Dropdown */}
                                {suggestions.length > 0 && (
                                    <div className="position-absolute w-100 bg-white border rounded shadow-sm mt-1" style={{zIndex: 1000}}>
                                        {suggestions.map((suggestion, index) => (
                                            <div
                                                key={index}
                                                className="p-3 border-bottom cursor-pointer suggestion-item"
                                                onClick={() => {
                                                    setFormData(prev => ({ ...prev, destination: suggestion }));
                                                    setSuggestions([]);
                                                }}
                                                style={{cursor: 'pointer'}}
                                            >
                                                <i className="fas fa-map-marker-alt me-2 text-muted"></i>
                                                {suggestion}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Date Inputs */}
                            <div className="row mb-4">
                                <div className="col-md-6">
                                    <label className="form-label fw-bold">
                                        <i className="fas fa-calendar-alt me-2 text-primary"></i>
                                        Start Date
                                    </label>
                                    <input
                                        type="date"
                                        name="start_date"
                                        className={`form-control form-control-lg ${errors.start_date ? 'is-invalid' : ''}`}
                                        value={formData.start_date}
                                        onChange={handleInputChange}
                                        min={new Date().toISOString().split('T')[0]}
                                    />
                                    {errors.start_date && (
                                        <div className="invalid-feedback">{errors.start_date}</div>
                                    )}
                                </div>
                                <div className="col-md-6">
                                    <label className="form-label fw-bold">
                                        <i className="fas fa-calendar-check me-2 text-primary"></i>
                                        End Date
                                    </label>
                                    <input
                                        type="date"
                                        name="end_date"
                                        className={`form-control form-control-lg ${errors.end_date ? 'is-invalid' : ''}`}
                                        value={formData.end_date}
                                        onChange={handleInputChange}
                                        min={formData.start_date || new Date().toISOString().split('T')[0]}
                                    />
                                    {errors.end_date && (
                                        <div className="invalid-feedback">{errors.end_date}</div>
                                    )}
                                </div>
                            </div>

                            {/* Budget Input */}
                            <div className="mb-4">
                                <label className="form-label fw-bold">
                                    <i className="fas fa-rupee-sign me-2 text-primary"></i>
                                    Budget (INR)
                                </label>
                                <input
                                    type="number"
                                    name="budget"
                                    className={`form-control form-control-lg ${errors.budget ? 'is-invalid' : ''}`}
                                    placeholder="Enter your budget in ₹"
                                    value={formData.budget}
                                    onChange={handleInputChange}
                                    min="1000"
                                />
                                {errors.budget && (
                                    <div className="invalid-feedback">{errors.budget}</div>
                                )}
                            </div>

                            {/* Interests Selection */}
                            <div className="mb-4">
                                <label className="form-label fw-bold">
                                    <i className="fas fa-heart me-2 text-primary"></i>
                                    What interests you?
                                </label>
                                <div className="row g-2">
                                    {interestOptions.map((interest) => (
                                        <div key={interest} className="col-md-6 col-lg-4">
                                            <div
                                                className={`interest-card p-3 text-center border rounded cursor-pointer transition ${
                                                    formData.interests.includes(interest) 
                                                        ? 'border-primary bg-primary text-white' 
                                                        : 'border-light bg-light'
                                                }`}
                                                onClick={() => handleInterestChange(interest)}
                                                style={{cursor: 'pointer'}}
                                            >
                                                <i className={`fas fa-${getInterestIcon(interest)} mb-2`}></i>
                                                <div>{interest}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                {errors.interests && (
                                    <div className="text-danger mt-2">{errors.interests}</div>
                                )}
                            </div>

                            {/* Submit Button */}
                            <div className="text-center">
                                <button
                                    type="submit"
                                    className="btn btn-primary btn-lg px-5"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm me-2"></span>
                                            Generating Your Perfect Trip...
                                        </>
                                    ) : (
                                        <>
                                            <i className="fas fa-magic me-2"></i>
                                            Generate My Itinerary
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Helper function to get icons for interests
const getInterestIcon = (interest) => {
    const icons = {
        'Adventure': 'mountain',
        'Culture': 'theater-masks',
        'Food': 'utensils',
        'Nature': 'leaf',
        'History': 'landmark',
        'Shopping': 'shopping-bag',
        'Nightlife': 'moon',
        'Photography': 'camera',
        'Spiritual': 'om',
        'Beach': 'umbrella-beach'
    };
    return icons[interest] || 'star';
};

export default ItineraryForm;