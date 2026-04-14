from fastapi.testclient import TestClient
import sys
import os

# Fix: Ensure the parent directory is in the path so 'from main import app' works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_success():
    # Create a dummy image file in memory
    # CHANGE 'image' to 'file' to match the backend parameter name
    files = {'file': ('test.png', b'fake-image-content', 'image/png')}
    response = client.post("/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    # Validate schema consistency
    assert "situation" in data
    assert "predicted_action" in data
    assert "risk" in data
    assert "recommended_action" in data
    assert "urgency" in data
    assert "confidence" in data

def test_analyze_invalid_file():
    # Upload a text file instead of an image
    # CHANGE 'image' to 'file'
    files = {'file': ('test.txt', b'not-an-image', 'text/plain')}
    response = client.post("/analyze", files=files)
    assert response.status_code == 400
    # Note: If your backend doesn't explicitly catch this and raise 400,
    # it will still return 422. I recommend updating the backend to handle this.
    assert response.json()["detail"] == "Invalid file type. Please upload an image."

def test_analyze_missing_file():
    # No files provided - FastAPI returns 422 Unprocessable Entity for missing required parts
    response = client.post("/analyze")
    assert response.status_code == 422