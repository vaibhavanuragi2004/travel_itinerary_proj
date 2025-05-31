from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import TravelItinerary, Checkpoint
from ai_service import generate_travel_itinerary
import json
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_itinerary', methods=['POST'])
def generate_itinerary():
    try:
        # Get form data
        destination = request.form.get('destination', '').strip()
        duration = int(request.form.get('duration', 0))
        budget = float(request.form.get('budget', 0))
        interests = request.form.getlist('interests')
        
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
            budget=budget
        )
        itinerary.set_interests_list(interests)
        itinerary.set_itinerary_data(itinerary_data)
        
        db.session.add(itinerary)
        db.session.flush()  # Get the ID
        
        # Create checkpoints
        for day_data in itinerary_data.get('days', []):
            day_num = day_data.get('day', 1)
            for activity in day_data.get('activities', []):
                checkpoint = Checkpoint(
                    itinerary_id=itinerary.id,
                    day=day_num,
                    time=activity.get('time', '09:00'),
                    location=activity.get('location', ''),
                    activity=activity.get('description', ''),
                    estimated_cost=activity.get('cost', 0.0)
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

@app.route('/tracking/<int:itinerary_id>')
def tracking(itinerary_id):
    itinerary = TravelItinerary.query.get_or_404(itinerary_id)
    checkpoints = Checkpoint.query.filter_by(itinerary_id=itinerary_id).order_by(Checkpoint.day, Checkpoint.time).all()
    
    return render_template('tracking.html', itinerary=itinerary, checkpoints=checkpoints)

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

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
