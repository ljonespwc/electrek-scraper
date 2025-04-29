# electrek_scraper/utils/sentiment_service.py
import os
import requests
import json
import random
from datetime import datetime

class SentimentService:
    def __init__(self):
        """Initialize the sentiment service using GPT-4o"""
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        # Ensure we have an API key
        if not self.openai_api_key:
            print("WARNING: No OpenAI API key found. Sentiment analysis will not work.")
    
    def calculate_sentiment(self, text):
        """Calculate sentiment score between -1 and 1 using GPT-4o"""
        if not text or not self.openai_api_key:
            return 0.0
            
        try:
            # Prepare the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            # Example headlines with scores to provide context for the model
            examples = [
                {"headline": "Tesla breaks another delivery record", "score": 0.8},
                {"headline": "New promising battery startup emerges", "score": 0.6},
                {"headline": "Ford launches new electric vehicle", "score": 0.5},
                {"headline": "EV sales continue to grow", "score": 0.4},
                {"headline": "Legacy automaker announces tentative EV plans", "score": 0.0},
                {"headline": "Oil company reveals 'commitment' to green energy", "score": -0.3},
                {"headline": "Another EV startup promises 'revolutionary' technology", "score": -0.5},
                {"headline": "Traditional automaker continues to delay EV plans", "score": -0.7},
                {"headline": "This company is killing the EV revolution", "score": -0.9}
            ]
            
            # Randomly select 5 examples to include in each request for variety
            selected_examples = random.sample(examples, 5)
            examples_text = "\n".join([f"Headline: {e['headline']}\nScore: {e['score']}" for e in selected_examples])
            
            # Create a detailed prompt that encourages more variance
            system_message = """You are analyzing headlines from electrek.co, a website covering electric vehicles and green energy.

Your task is to rate the true sentiment of headlines on a scale from -1.0 (extremely negative) to 1.0 (extremely positive). 

IMPORTANT GUIDELINES:
1. Use the FULL RANGE from -1.0 to 1.0, not just values near zero
2. Recognize sarcasm and subtle criticism - these should be rated as negative
3. Headlines that express skepticism about hyped claims should be negative
4. Headlines about delays, problems, or failures should be strongly negative
5. Headlines about legitimate breakthroughs should be strongly positive
6. Neutral headlines about factual events should be near zero

DO NOT play it safe by rating everything between -0.3 and 0.3.
DO provide varied scores that reflect the true sentiment intensity.

ONLY respond with a single decimal number between -1.0 and 1.0.
Do not include any explanation or text."""

            # Use the few-shot learning with examples
            user_message = f"Here are some examples of correctly scored headlines:\n\n{examples_text}\n\nNow score this headline:\n\nHeadline: {text}\n\nScore (ONLY a number between -1.0 and 1.0):"
            
            # Prepare the API call
            data = {
                "model": "gpt-4o",  # Use the latest GPT-4o model
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,  # Increased temperature for more variability
                "max_tokens": 10     # We only need a number
            }
            
            # Make the API call
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            # Process the response
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Extract the numeric score
                try:
                    # Find the first numeric value in the response
                    import re
                    number_matches = re.findall(r'-?\d+\.?\d*', content)
                    if number_matches:
                        score = float(number_matches[0])
                        # Ensure it's in the -1 to 1 range
                        return max(min(score, 1.0), -1.0)
                    else:
                        print(f"Could not extract a numeric score from: '{content}'")
                        return 0.0
                except ValueError:
                    print(f"Could not parse GPT response as a float: '{content}'")
                    return 0.0
            else:
                error_msg = f"Error in GPT sentiment analysis: {response.status_code}"
                if response.text:
                    try:
                        error_json = response.json()
                        if 'error' in error_json:
                            error_msg += f" - {error_json['error']['message']}"
                    except:
                        error_msg += f" - {response.text[:100]}..."
                        
                print(error_msg)
                return 0.0
                
        except Exception as e:
            print(f"Exception in GPT sentiment analysis: {str(e)}")
            return 0.0
    
    def get_sentiment_category(self, score):
        """Convert numerical score to category with more granular categories"""
        if score is None:
            return 'neutral'
            
        if score >= 0.7:
            return 'very positive'
        if score >= 0.3:
            return 'positive'
        if score >= 0.1:
            return 'slightly positive'
        if score <= -0.7:
            return 'very negative'
        if score <= -0.3:
            return 'negative'
        if score <= -0.1:
            return 'slightly negative'
            
        return 'neutral'
    
    def get_sentiment_color(self, score):
        """Return a color hex code for the sentiment score"""
        if score is None:
            return '#6c757d'  # gray for neutral
            
        if score >= 0.7:
            return '#28a745'  # strong green
        if score >= 0.3:
            return '#5cb85c'  # medium green
        if score >= 0.1:
            return '#8bc34a'  # light green
        if score <= -0.7:
            return '#dc3545'  # strong red
        if score <= -0.3:
            return '#e74c3c'  # medium red
        if score <= -0.1:
            return '#f08080'  # light red
            
        return '#6c757d'  # gray for neutral