import pytest
import json
from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    OLLAMA_HOST = "http://localhost:11434"
    DEFAULT_MODEL = "test-model"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_page(client):
    """Test that index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'llot' in response.data
    assert b'local llm ollama translator' in response.data


def test_favicon_routes(client):
    """Test that favicon routes work."""
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.mimetype == 'image/x-icon'
    
    response = client.get('/favicon.svg')
    assert response.status_code == 200
    assert response.mimetype == 'image/svg+xml'


def test_manifest_json(client):
    """Test web app manifest."""
    response = client.get('/manifest.json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    
    data = json.loads(response.data)
    assert data['name'] == 'llot - local llm ollama translator'
    assert data['short_name'] == 'llot'


def test_api_translate_empty_text(client):
    """Test translation API with empty text."""
    response = client.post('/api/translate', 
                          json={'source_text': ''})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['error'] == 'EMPTY'
    assert data['translated'] == ''


def test_api_history_save_empty(client):
    """Test history save with empty data."""
    response = client.post('/api/history/save', 
                          json={'source_text': '', 'translated': ''})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['ok'] is False
    assert data['error'] == 'EMPTY'


def test_api_alternatives_empty(client):
    """Test alternatives API with empty data."""
    response = client.post('/api/alternatives', 
                          json={'source_text': '', 'current_translation': '', 'clicked_word': ''})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['alternatives'] == []