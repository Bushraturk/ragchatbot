import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add the backend src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.core.store import Store


@pytest.mark.asyncio
async def test_store_initialization():
    """Test that the store initializes correctly"""
    store = Store()
    assert store is not None


@pytest.mark.asyncio
@patch('backend.src.core.store.SessionLocal')
async def test_generate_thread_id(mock_session_local):
    """Test generating a thread ID"""
    store = Store()
    
    # Mock the database session
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    context = {}
    thread_id = store.generate_thread_id(context)
    
    assert thread_id is not None
    assert isinstance(thread_id, str)
    assert thread_id.startswith('thread_')
    assert len(thread_id) > len('thread_')


@pytest.mark.asyncio
@patch('backend.src.core.store.SessionLocal')
async def test_generate_item_id(mock_session_local):
    """Test generating an item ID"""
    store = Store()
    
    # Mock the database session
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    context = {}
    item_id = store.generate_item_id('message', 'test_thread_123', context)
    
    assert item_id is not None
    assert isinstance(item_id, str)
    assert item_id.startswith('message_')
    assert len(item_id) > len('message_')


@pytest.mark.asyncio
@patch('backend.src.core.store.SessionLocal')
async def test_load_thread_new_thread(mock_session_local):
    """Test loading a thread that doesn't exist (should create a new one)"""
    # Mock the database session and thread query
    mock_session = MagicMock()
    mock_thread_query = MagicMock()
    mock_thread_query.filter.return_value.first.return_value = None  # Thread doesn't exist
    mock_session.query.return_value = mock_thread_query
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    store = Store()
    context = {}
    
    thread_data = await store.load_thread('new_thread_123', context)
    
    assert thread_data is not None
    assert 'id' in thread_data
    assert thread_data['id'] == 'new_thread_123'
    assert 'created_at' in thread_data


@pytest.mark.asyncio
@patch('backend.src.core.store.SessionLocal')
async def test_load_thread_existing_thread(mock_session_local):
    """Test loading an existing thread"""
    # Mock the database session and thread query
    mock_session = MagicMock()
    mock_thread_db = MagicMock()
    mock_thread_db.id = 'existing_thread_123'
    mock_thread_db.created_at = '2023-01-01T00:00:00Z'
    mock_thread_db.metadata_ = {'mode': 'full_book'}
    
    mock_thread_query = MagicMock()
    mock_thread_query.filter.return_value.first.return_value = mock_thread_db
    mock_session.query.return_value = mock_thread_query
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    store = Store()
    context = {}
    
    thread_data = await store.load_thread('existing_thread_123', context)
    
    assert thread_data is not None
    assert thread_data['id'] == 'existing_thread_123'
    assert thread_data['metadata'] == {'mode': 'full_book'}


@pytest.mark.asyncio    
@patch('backend.src.core.store.SessionLocal')
async def test_save_thread(mock_session_local):
    """Test saving a thread"""
    # Mock the database session
    mock_session = MagicMock()
    mock_thread_db = MagicMock()
    mock_thread_db.id = 'test_thread_123'
    mock_thread_db.metadata_ = {}
    
    mock_thread_query = MagicMock()
    mock_thread_query.filter.return_value.first.return_value = mock_thread_db
    mock_session.query.return_value = mock_thread_query
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    store = Store()
    context = {}
    
    thread_data = {
        'id': 'test_thread_123',
        'created_at': '2023-01-01T00:00:00Z',
        'metadata': {'mode': 'selected_text'}
    }
    
    await store.save_thread(thread_data, context)
    
    # Verify that commit was called
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch('backend.src.core.store.SessionLocal')
async def test_add_thread_item_new_item(mock_session_local):
    """Test adding a new item to a thread"""
    # Mock the database session
    mock_session = MagicMock()
    
    # Mock the query to return None for existing item (item doesn't exist)
    mock_item_query = MagicMock()
    mock_item_query.filter.return_value.first.return_value = None
    mock_session.query.return_value = mock_item_query
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session_local.return_value.__exit__.return_value = None
    
    store = Store()
    context = {}
    
    item_data = {
        'id': 'test_item_123',
        'type': 'message',
        'role': 'user',
        'content': 'Test content'
    }
    
    await store.add_thread_item('test_thread_123', item_data, context)
    
    # Verify that add and commit were called
    assert mock_session.add.called
    mock_session.commit.assert_called_once()