git clone <your-repository-url>
cd travelitineraryproj

# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\Activate

# Make sure you have a requirements.txt or dependencies.txt file
pip install -r dependencies.txt

# Install all packages from package.json
npm install

# Build the static assets for production (if you have a build script)
# This step might not be needed for development if Flask serves the raw files
npm run build 

# Get your key from https://console.groq.com/
GROQ_API_KEY="your-groq-api-key"

# Get your key from https://openweathermap.org/
OPENWEATHERMAP_API_KEY="your-openweathermap-api-key"

Run:
python main.py

├── app.py                # Core Flask application setup, configuration, and DB initialization.
├── main.py               # The main entry point to run the application.
├── routes.py             # Defines all URL routes and API endpoints.
├── models.py             # Contains the SQLAlchemy database models (Itinerary, Checkpoint).
├── ai_service.py         # Handles all interactions with the Groq LLM for itinerary generation.
├── agent_coordinator.py  # Orchestrates the multi-agent proactive assistant.
├── chatbot_service.py    # Logic for the travel companion chatbot.
├── budget_optimizer.py   # Rule-based logic for budget breakdown.
├── weather_service.py    # Fetches data from the OpenWeatherMap API.
├── .env                  # (You create this) Stores all secret keys and environment variables.
├── dependencies.txt      # Lists all required Python packages.
├── package.json          # Lists all required Node.js packages.
├── templates/            # Contains all HTML templates for rendering pages.
└── static/               # Contains compiled/static assets like CSS, JS, and images.
