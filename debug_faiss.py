
import numpy as np
import faiss
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_faiss():
    try:
        dimension = 768  # Gemini embedding dimension is usually 768, but config says 1536?
        # Let's check what the logs said: "Created new FAISS index with dimension 1536"
        # If Gemini returns 768 and we created index with 1536, FAISS will throw error.
        
        # Let's try to simulate what happens in the app
        print("Creating index with dimension 1536...")
        index = faiss.IndexFlatL2(1536)
        
        # Create dummy embeddings
        # Case 1: Matching dimension
        print("Testing with matching dimension (1536)...")
        embeddings_match = np.random.rand(5, 1536).astype(np.float32)
        index.add(embeddings_match)
        print("Success adding matching dimension.")
        
        # Case 2: Mismatch (e.g. 768)
        print("Testing with mismatch dimension (768)...")
        embeddings_mismatch = np.random.rand(5, 768).astype(np.float32)
        try:
            index.add(embeddings_mismatch)
        except Exception as e:
            print(f"Caught expected error for mismatch: {e}")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_faiss()
