import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from app import db # Assuming 'app' is your Flask app instance
from models import TravelItinerary

class RecommendationService:
    def __init__(self):
        self.df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.indices = None
        self.load_and_process_data()

    def load_and_process_data(self):
        # --- Step 1: Load and process the base CSV data ---
        try:
            # This is a helper function to correctly parse your specific CSV format
            def process_csv_data(filepath):
                csv_df = pd.read_csv(filepath)
                # Forward-fill the main itinerary info (destination, duration)
                main_cols = ['input__destination', 'input__duration']
                csv_df[main_cols] = csv_df[main_cols].replace('', pd.NA).ffill()
                
                # Drop rows where destination is still empty
                csv_df.dropna(subset=['input__destination'], inplace=True)

                # Aggregate interests for each destination
                destinations = []
                for name, group in csv_df.groupby('input__destination'):
                    # Combine all interest columns and get unique, non-empty values
                    interest_cols = [f'input__interests__00{i}' for i in range(1, 6)]
                    interests = group[interest_cols].values.flatten()
                    unique_interests = [str(i) for i in pd.Series(interests).dropna().unique() if str(i)]
                    
                    destinations.append({
                        'destination': name,
                        'interests_str': ' '.join(unique_interests).lower()
                    })
                return pd.DataFrame(destinations)

            self.df = process_csv_data('tourism_iternary_dataset (1).csv')
            print("Successfully loaded and processed base CSV dataset.")

        except FileNotFoundError:
            print("Warning: tourism_iternary_dataset.csv not found. Recommendations will be limited.")
            self.df = pd.DataFrame(columns=['destination', 'interests_str'])

        # --- Step 2: Feature Engineering with TF-IDF ---
        # Create a TF-IDF Vectorizer to convert text interests into a matrix of numbers
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        
        # Create the TF-IDF matrix
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['interests_str'])
        
        # Create a mapping from destination name to index
        self.indices = pd.Series(self.df.index, index=self.df['destination']).drop_duplicates()

    def get_recommendations(self, user_id=None, top_n=5):
        # --- Step 3: Get user's past travel history from the database ---
        # For this example, we'll assume a single user context. 
        # In a real app, you'd filter by user_id.
        past_itineraries = TravelItinerary.query.order_by(TravelItinerary.created_at.desc()).limit(10).all()
        
        if not past_itineraries:
            # Cold Start: If no history, recommend most popular or diverse options
            return self.df['destination'].head(top_n).tolist()

        past_destinations = [it.destination for it in past_itineraries]
        
        # Find the average profile of the user based on past trips
        user_profile_indices = [self.indices[dest] for dest in past_destinations if dest in self.indices]
        
        if not user_profile_indices:
             return self.df['destination'].head(top_n).tolist()

        # --- Step 4: Calculate Similarity and Generate Recommendations ---
        # Calculate cosine similarity between all destinations
        cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)

        # Get the average similarity of all destinations to the user's past trips
        avg_sim_scores = cosine_sim[user_profile_indices].mean(axis=0)

        # Create a series with similarity scores
        sim_scores_series = pd.Series(avg_sim_scores, index=self.df['destination'])

        # Sort the destinations based on similarity scores
        sim_scores_series = sim_scores_series.sort_values(ascending=False)

        # Filter out destinations the user has already visited
        recommendations = sim_scores_series[~sim_scores_series.index.isin(past_destinations)]

        # Return the top N recommendations
        return recommendations.head(top_n).index.tolist()