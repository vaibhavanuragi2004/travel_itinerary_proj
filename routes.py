from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import TravelItinerary, Checkpoint
from ai_service import generate_travel_itinerary
from weather_service import weather_service
import json
from datetime import datetime, timedelta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary():
    try:
        # Get form data
        destination = request.form.get('destination', '').strip()
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        budget = float(request.form.get('budget', 0))
        interests = request.form.getlist('interests')
        
        # Calculate duration from dates
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            duration = (end_date - start_date).days
        else:
            duration = 0
        
        # Validate input
        if not destination or duration <= 0 or budget <= 0:
            flash('Please fill in all required fields with valid values.', 'error')
            return redirect(url_for('index'))
        
        # Generate itinerary using AI
        app.logger.info(f"Generating itinerary for {destination}, {duration} days, budget ₹{budget}")
        itinerary_data = generate_travel_itinerary(destination, duration, budget, interests)
        
        if not itinerary_data:
            flash('Failed to generate itinerary. Please try again.', 'error')
            return redirect(url_for('index'))
        
        # Save to database
        itinerary = TravelItinerary(
            destination=destination,
            duration=duration,
            budget=budget,
            start_date=start_date.date() if start_date_str else None,
            end_date=end_date.date() if end_date_str else None
        )
        itinerary.set_interests_list(interests)
        itinerary.set_itinerary_data(itinerary_data)
        
        db.session.add(itinerary)
        db.session.flush()  # Get the ID
        
        # Create checkpoints
        for day_data in itinerary_data.get('days', []):
            day_num = day_data.get('day', 1)
            for activity in day_data.get('activities', []):
                # Prepare notes with opening hours and tips
                notes_parts = []
                if activity.get('opening_hours'):
                    notes_parts.append(f"opening_hours:{activity.get('opening_hours')}")
                if activity.get('tips'):
                    notes_parts.append(f"tips:{activity.get('tips')}")
                if activity.get('travel_time_to_next'):
                    notes_parts.append(f"travel_time:{activity.get('travel_time_to_next')}")
                if activity.get('transportation_mode'):
                    notes_parts.append(f"transport:{activity.get('transportation_mode')}")
                
                checkpoint = Checkpoint(
                    itinerary_id=itinerary.id,
                    day=day_num,
                    time=activity.get('time', '09:00'),
                    location=activity.get('location', ''),
                    activity=activity.get('description', ''),
                    estimated_cost=activity.get('cost', 0.0),
                    notes=', '.join(notes_parts) if notes_parts else None
                )
                db.session.add(checkpoint)
        
        db.session.commit()
        
        flash('Itinerary generated successfully!', 'success')
        return redirect(url_for('view_itinerary', itinerary_id=itinerary.id))
        
    except ValueError as e:
        flash('Please enter valid numbers for duration and budget.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error generating itinerary: {str(e)}")
        flash('An error occurred while generating your itinerary. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/itinerary/<int:itinerary_id>')
def view_itinerary(itinerary_id):
    itinerary = TravelItinerary.query.get_or_404(itinerary_id)
    checkpoints = Checkpoint.query.filter_by(itinerary_id=itinerary_id).order_by(Checkpoint.day, Checkpoint.time).all()
    
    # Group checkpoints by day
    days_data = {}
    for checkpoint in checkpoints:
        if checkpoint.day not in days_data:
            days_data[checkpoint.day] = []
        days_data[checkpoint.day].append(checkpoint)
    
    # Calculate progress
    total_checkpoints = len(checkpoints)
    completed_checkpoints = len([c for c in checkpoints if c.is_completed])
    progress_percentage = (completed_checkpoints / total_checkpoints * 100) if total_checkpoints > 0 else 0
    
    return render_template('itinerary.html', 
                         itinerary=itinerary, 
                         days_data=days_data,
                         progress_percentage=progress_percentage,
                         total_checkpoints=total_checkpoints,
                         completed_checkpoints=completed_checkpoints)



@app.route('/complete_checkpoint/<int:checkpoint_id>', methods=['POST'])
def complete_checkpoint(checkpoint_id):
    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    
    if not checkpoint.is_completed:
        checkpoint.mark_completed()
        checkpoint.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Checkpoint completed!', 'success')
    
    return redirect(url_for('view_itinerary', itinerary_id=checkpoint.itinerary_id))

@app.route('/my_itineraries')
def my_itineraries():
    itineraries = TravelItinerary.query.order_by(TravelItinerary.created_at.desc()).all()
    return render_template('my_itineraries.html', itineraries=itineraries)

@app.route('/reorder_checkpoints', methods=['POST'])
def reorder_checkpoints():
    try:
        data = request.get_json()
        checkpoint_ids = data.get('checkpoint_ids', [])
        
        if not checkpoint_ids:
            return jsonify({'success': False, 'error': 'No checkpoint IDs provided'})
        
        # Update the order of checkpoints based on their new positions
        for index, checkpoint_id in enumerate(checkpoint_ids):
            checkpoint = Checkpoint.query.get(checkpoint_id)
            if checkpoint:
                # Update the time based on position (assuming 2-hour intervals starting from 9 AM)
                start_hour = 9 + (index * 2)
                new_time = f"{start_hour:02d}:00"
                checkpoint.time = new_time
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Checkpoints reordered successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error reordering checkpoints: {e}")
        return jsonify({'success': False, 'error': 'Failed to reorder checkpoints'})

@app.route('/api/weather-alerts', methods=['GET'])
def get_weather_alerts():
    """API endpoint to get weather alerts for upcoming trips"""
    try:
        alerts = []
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Get all itineraries with start dates in the next 7 days
        upcoming_itineraries = TravelItinerary.query.filter(
            TravelItinerary.start_date >= tomorrow,
            TravelItinerary.start_date <= tomorrow + timedelta(days=7)
        ).all()
        
        for itinerary in upcoming_itineraries:
            if itinerary.start_date:
                weather_alert = weather_service.check_severe_weather(
                    itinerary.destination, 
                    datetime.combine(itinerary.start_date, datetime.min.time())
                )
                
                if weather_alert:
                    alerts.append({
                        'destination': itinerary.destination,
                        'travel_date': itinerary.start_date.isoformat(),
                        'severity': weather_alert['severity'],
                        'weather': {
                            'description': weather_alert['alert_message'],
                            'temp': weather_alert['conditions'][0]['temperature'] if weather_alert['conditions'] else 0
                        }
                    })
        
        return jsonify(alerts)
        
    except Exception as e:
        app.logger.error(f"Error getting weather alerts: {e}")
        return jsonify([])

@app.route('/api/weather/<destination>', methods=['GET'])
def get_destination_weather(destination):
    """Get current weather for a destination"""
    try:
        weather_data = weather_service.get_current_weather(destination)
        if weather_data:
            return jsonify(weather_data)
        else:
            return jsonify({'error': 'Weather data not available'}), 404
    except Exception as e:
        app.logger.error(f"Error getting weather for {destination}: {e}")
        return jsonify({'error': 'Weather service unavailable'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
