# electrek_scraper/utils/clustering.py
import numpy as np

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
        
    try:
        # Convert to numpy arrays
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        # Calculate dot product
        dot_product = np.dot(vec1, vec2)
        
        # Calculate magnitudes
        mag1 = np.linalg.norm(vec1)
        mag2 = np.linalg.norm(vec2)
        
        # Calculate cosine similarity
        if mag1 > 0 and mag2 > 0:
            return dot_product / (mag1 * mag2)
        else:
            return 0.0
    except Exception as e:
        print(f"Error in cosine similarity: {str(e)}")
        return 0.0