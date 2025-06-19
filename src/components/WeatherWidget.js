import React, { useState, useEffect } from 'react';

const WeatherWidget = ({ destination }) => {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (destination) {
            fetchWeather();
        }
    }, [destination]);

    const fetchWeather = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/weather/${encodeURIComponent(destination)}`);
            
            if (response.ok) {
                const data = await response.json();
                setWeather(data);
                setError(null);
            } else {
                throw new Error('Weather data unavailable');
            }
        } catch (err) {
            setError(err.message);
            setWeather(null);
        } finally {
            setLoading(false);
        }
    };

    const getWeatherIcon = (condition) => {
        const iconMap = {
            'clear': 'sun',
            'clouds': 'cloud',
            'rain': 'cloud-rain',
            'snow': 'snowflake',
            'thunderstorm': 'bolt',
            'drizzle': 'cloud-drizzle',
            'mist': 'smog',
            'fog': 'smog'
        };
        return iconMap[condition.toLowerCase()] || 'cloud';
    };

    const getTemperatureColor = (temp) => {
        if (temp > 35) return 'text-danger';
        if (temp > 25) return 'text-warning';
        if (temp > 15) return 'text-success';
        return 'text-info';
    };

    if (loading) {
        return (
            <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                    <div className="spinner-border spinner-border-sm text-primary"></div>
                    <p className="mt-2 mb-0 text-muted">Loading weather...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card border-0 shadow-sm">
                <div className="card-body text-center">
                    <i className="fas fa-exclamation-triangle text-warning mb-2"></i>
                    <p className="mb-2 text-muted">Weather data unavailable</p>
                    <button 
                        className="btn btn-outline-primary btn-sm"
                        onClick={fetchWeather}
                    >
                        <i className="fas fa-redo me-1"></i>Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!weather) {
        return null;
    }

    return (
        <div className="card border-0 shadow-sm">
            <div className="card-header bg-primary text-white">
                <h6 className="mb-0">
                    <i className="fas fa-cloud-sun me-2"></i>
                    Current Weather
                </h6>
            </div>
            <div className="card-body">
                <div className="row align-items-center">
                    <div className="col-6">
                        <div className="text-center">
                            <i className={`fas fa-${getWeatherIcon(weather.weather[0].main)} fa-2x text-primary mb-2`}></i>
                            <div className={`h4 mb-0 ${getTemperatureColor(weather.main.temp)}`}>
                                {Math.round(weather.main.temp)}°C
                            </div>
                            <small className="text-muted">{weather.weather[0].description}</small>
                        </div>
                    </div>
                    <div className="col-6">
                        <div className="weather-details">
                            <div className="d-flex justify-content-between align-items-center mb-1">
                                <small className="text-muted">Feels like</small>
                                <small className="fw-bold">{Math.round(weather.main.feels_like)}°C</small>
                            </div>
                            <div className="d-flex justify-content-between align-items-center mb-1">
                                <small className="text-muted">Humidity</small>
                                <small className="fw-bold">{weather.main.humidity}%</small>
                            </div>
                            <div className="d-flex justify-content-between align-items-center mb-1">
                                <small className="text-muted">Wind</small>
                                <small className="fw-bold">{weather.wind?.speed || 0} m/s</small>
                            </div>
                            {weather.visibility && (
                                <div className="d-flex justify-content-between align-items-center">
                                    <small className="text-muted">Visibility</small>
                                    <small className="fw-bold">{(weather.visibility / 1000).toFixed(1)} km</small>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
                
                {/* Weather Alerts */}
                {weather.alerts && weather.alerts.length > 0 && (
                    <div className="mt-3 alert alert-warning alert-sm">
                        <i className="fas fa-exclamation-triangle me-2"></i>
                        <small>{weather.alerts[0].description}</small>
                    </div>
                )}
                
                <div className="mt-3 text-center">
                    <button 
                        className="btn btn-outline-primary btn-sm"
                        onClick={fetchWeather}
                    >
                        <i className="fas fa-sync-alt me-1"></i>Refresh
                    </button>
                </div>
            </div>
        </div>
    );
};

export default WeatherWidget;