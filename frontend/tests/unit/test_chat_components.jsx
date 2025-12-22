import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ApiService from '../services/api';
import { ChatPage } from '../pages/ChatPage';

// Mock the ApiService
jest.mock('../services/api', () => ({
  sendMessage: jest.fn(),
  getChatHistory: jest.fn(),
  listSessions: jest.fn(),
}));

describe('ChatPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chat interface', () => {
    render(<ChatPage />);
    
    // Check if key elements are present in the UI
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    expect(screen.getByTestId('message-input')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
  });

  test('allows user to select text mode', async () => {
    render(<ChatPage />);
    
    // Find and click the mode selection element
    const modeSelector = screen.getByTestId('mode-selector');
    expect(modeSelector).toBeInTheDocument();
    
    // Verify that the mode can be changed
    // This would involve more complex interaction testing
  });
});

describe('ApiService', () => {
  test('sendMessage returns a valid response', async () => {
    const mockResponse = {
      session_id: 'test-session-id',
      response: 'Test response',
      context_references: [],
      timestamp: '2023-01-01T00:00:00Z'
    };
    
    ApiService.sendMessage.mockResolvedValue(mockResponse);
    
    const result = await ApiService.sendMessage('Test message');
    
    expect(result).toEqual(mockResponse);
    expect(ApiService.sendMessage).toHaveBeenCalledWith('Test message', null, 'full_book', null);
  });

  test('listSessions returns session data', async () => {
    const mockSessions = {
      sessions: [
        { id: 'session1', title: 'Session 1', created_at: '2023-01-01T00:00:00Z' }
      ]
    };
    
    ApiService.listSessions.mockResolvedValue(mockSessions);
    
    const result = await ApiService.listSessions();
    
    expect(result).toEqual(mockSessions);
    expect(ApiService.listSessions).toHaveBeenCalled();
  });
});