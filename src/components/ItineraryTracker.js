import React, { useState, useEffect } from 'react';

const ItineraryTracker = ({ itineraryId }) => {
    const [checkpoints, setCheckpoints] = useState([]);
    const [currentLocation, setCurrentLocation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [updates, setUpdates] = useState([]);

    useEffect(() => {
        fetchCheckpoints();
        addUpdate('Tracking system initialized');
        
        // Simulate real-time updates
        const interval = setInterval(() => {
            if (Math.random() > 0.8) {
                const messages = [
                    'GPS signal strong',
                    'Weather conditions favorable',
                    'Traffic is light on your route',
                    'Local recommendations updated'
                ];
                addUpdate(messages[Math.floor(Math.random() * messages.length)]);
            }
        }, 10000);

        return () => clearInterval(interval);
    }, [itineraryId]);

    const fetchCheckpoints = async () => {
        try {
            const response = await fetch(`/api/itinerary/${itineraryId}/checkpoints`);
            if (response.ok) {
                const data = await response.json();
                setCheckpoints(data.checkpoints || []);
                setCurrentLocation(data.next_checkpoint);
            }
        } catch (error) {
            console.error('Error fetching checkpoints:', error);
        } finally {
            setLoading(false);
        }
    };

    const addUpdate = (message) => {
        const newUpdate = {
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            message: message
        };
        setUpdates(prev => [newUpdate, ...prev.slice(0, 4)]);
    };

    const handleLocationUpdate = () => {
        addUpdate('Location updated successfully - GPS coordinates refreshed');
    };

    const getStatusColor = (checkpoint) => {
        if (checkpoint.is_completed) return 'success';
        if (currentLocation && checkpoint.id === currentLocation.id) return 'warning';
        return 'secondary';
    };

    const getStatusIcon = (checkpoint) => {
        if (checkpoint.is_completed) return 'check';
        if (currentLocation && checkpoint.id === currentLocation.id) return 'location-arrow';
        return 'clock';
    };

    if (loading) {
        return (
            <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-3 text-muted">Loading tracking data...</p>
            </div>
        );
    }

    return (
        <div className="row">
            {/* Current Status */}
            <div className="col-12 mb-4">
                <div className="card border-0 shadow-sm">
                    <div className="card-body">
                        <div className="row align-items-center">
                            <div className="col-md-8">
                                <h5 className="mb-2">
                                    <i className="fas fa-map-pin me-2 text-primary"></i>
                                    Current Status
                                </h5>
                                {currentLocation ? (
                                    <div>
                                        <div className="h6 text-primary">Next: {currentLocation.location}</div>
                                        <small className="text-muted">
                                            <i className="fas fa-clock me-1"></i>
                                            Scheduled for {currentLocation.time} on Day {currentLocation.day}
                                        </small>
                                    </div>
                                ) : (
                                    <div className="text-success">
                                        <i className="fas fa-trophy me-2"></i>
                                        Journey Complete!
                                    </div>
                                )}
                            </div>
                            <div className="col-md-4 text-md-end">
                                <button 
                                    className="btn btn-primary"
                                    onClick={handleLocationUpdate}
                                >
                                    <i className="fas fa-crosshairs me-2"></i>
                                    Update Location
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Timeline */}
            <div className="col-lg-8 mb-4">
                <div className="card border-0 shadow-sm">
                    <div className="card-header bg-white">
                        <h5 className="mb-0">
                            <i className="fas fa-route me-2 text-primary"></i>
                            Journey Timeline
                        </h5>
                    </div>
                    <div className="card-body">
                        <div className="timeline">
                            {checkpoints.map((checkpoint, index) => (
                                <div key={checkpoint.id} className="timeline-item">
                                    <div className={`timeline-marker bg-${getStatusColor(checkpoint)}`}>
                                        <i className={`fas fa-${getStatusIcon(checkpoint)} text-white`}></i>
                                    </div>
                                    <div className="timeline-content">
                                        <div className="d-flex justify-content-between align-items-start">
                                            <div>
                                                <h6 className="mb-1">{checkpoint.location}</h6>
                                                <p className="mb-1 text-muted">{checkpoint.activity}</p>
                                                <small className="text-muted">
                                                    Day {checkpoint.day} - {checkpoint.time}
                                                </small>
                                            </div>
                                            {checkpoint.estimated_cost > 0 && (
                                                <span className="badge bg-light text-dark">
                                                    ₹{checkpoint.estimated_cost.toLocaleString()}
                                                </span>
                                            )}
                                        </div>
                                        {checkpoint.is_completed && checkpoint.completed_at && (
                                            <div className="mt-2 p-2 bg-success bg-opacity-10 rounded">
                                                <small className="text-success">
                                                    <i className="fas fa-check-circle me-1"></i>
                                                    Completed on {new Date(checkpoint.completed_at).toLocaleDateString()}
                                                </small>
                                                {checkpoint.notes && (
                                                    <div className="mt-1">
                                                        <small className="text-muted">{checkpoint.notes}</small>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Live Updates */}
            <div className="col-lg-4">
                <div className="card border-0 shadow-sm">
                    <div className="card-header bg-white">
                        <h5 className="mb-0">
                            <i className="fas fa-bell me-2 text-primary"></i>
                            Live Updates
                        </h5>
                    </div>
                    <div className="card-body" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {updates.length === 0 ? (
                            <p className="text-muted text-center">No updates yet</p>
                        ) : (
                            updates.map((update) => (
                                <div key={update.id} className="update-item mb-3 p-2 border-bottom">
                                    <div className="d-flex justify-content-between align-items-start">
                                        <small className="text-primary fw-bold">{update.time}</small>
                                    </div>
                                    <div className="mt-1">
                                        <i className="fas fa-info-circle text-info me-2"></i>
                                        <small>{update.message}</small>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ItineraryTracker;