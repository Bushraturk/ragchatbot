# Configuration and Deployment Guide

## Environment Configuration

### Required Environment Variables

All configuration is managed through environment variables in a `.env` file. Create this file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=your_neon_postgres_connection_string

# Vector Database Configuration
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key

# AI Services
GEMINI_API_KEY=your_gemini_api_key
COHERE_API_KEY=your_cohere_api_key

# Application Settings
LLM_MODEL=gemini/gemini-2.0-flash
EMBEDDING_MODEL=embed-english-v3.0

# Debug Settings
DEBUG_MODE=false
```

### Environment File Setup
1. Copy the example environment file: `cp .env.example .env`
2. Edit the `.env` file with your actual API keys and configuration
3. Ensure the file is in the backend directory where main.py is located

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Node.js (for frontend, if needed)

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Initialize the database: The application will create tables automatically at startup
5. Start the server: `uvicorn main:app --reload --port 8000`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Set environment variables in `.env` file:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```
4. Start the development server: `npm start`

## Production Deployment

### Backend Deployment Options

#### Option 1: Deploy to Cloud Platforms
- **Heroku**: Use the Python buildpack with requirements.txt
- **Railway**: Deploy directly from GitHub with environment variables
- **Render**: Python web service with Postgres and environment variables
- **AWS Elastic Beanstalk**: Python application with requirements.txt

#### Option 2: Container Deployment
Create a `Dockerfile` based on Python 3.11:
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
When deploying to production, ensure these security best practices:

1. Never commit the `.env` file to version control
2. Use secrets management in your deployment platform
3. Use SSL/HTTPS for all production traffic
4. Rotate API keys periodically
5. Monitor API usage for unexpected spikes

### Database Migration in Production
The application automatically creates database tables at startup using Alembic or direct table creation. For production environments with larger datasets:

1. Test database operations in staging environment first
2. Backup existing data before updates
3. Monitor for any performance issues with large datasets

## API Gateway and Load Balancer Configuration

### API Gateway Settings
When deploying behind an API gateway:

- Configure timeout values to accommodate long-running requests (up to 60 seconds recommended)
- Enable WebSocket support if needed for real-time features
- Set up proper health check endpoints (`/health`)
- Configure rate limiting per IP/user as needed

### Load Balancer Considerations
- Sticky sessions are not required as the system is stateless
- Ensure proper handling of Server-Sent Events (SSE) in load balancer
- Health check endpoint: `/health`

## Monitoring and Logging

### Logging Configuration
The application logs to standard output, which can be captured by your deployment platform.

#### Log Levels
- INFO: Standard operation events
- WARNING: Potential issues that don't stop execution
- ERROR: Issues that affect functionality

### Health Monitoring
- Health endpoint: `/health` (returns 200 OK when operational)
- Debug endpoint: `/debug/threads` (only available when DEBUG_MODE=true)

### Performance Monitoring
Monitor these key metrics:
- Response times for `/chatkit` endpoint
- Vector database query times
- LLM API response times
- Memory usage during document processing

## Scaling Considerations

### Horizontal Scaling
- The application is stateless and can be scaled horizontally
- Session data is stored in the database, allowing for multiple instances
- Vector database handles concurrent queries efficiently

### Database Scaling
- Neon Postgres scales automatically based on usage
- Consider read replicas for high-traffic applications
- Monitor connection pool usage and adjust as needed

### Vector Database Scaling
- Qdrant Cloud scales automatically based on data size and query load
- Monitor for high latency in semantic search operations

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Loading
- Ensure `.env` file is in the correct directory (same as main.py)
- Verify the file format (no quotes around values unless needed)
- Check file permissions to ensure it's readable

#### 2. Database Connection Issues
- Verify the DATABASE_URL is correctly formatted
- Check that the Neon Postgres instance is accessible
- Confirm that network rules allow connections

#### 3. LLM API Issues
- Verify API keys are correct and have the necessary permissions
- Check that rate limits are not being exceeded
- Ensure the LLM_MODEL variable matches available models

#### 4. SSE Streaming Issues
- Check that reverse proxies are not buffering responses
- Verify that load balancers properly handle Server-Sent Events
- Ensure no middleware is interfering with streaming responses

#### 5. Document Upload Failures
- Check that file size limits are appropriate
- Verify that the file format is supported
- Confirm Cohere API key has embedding permissions

### Debug Mode
Enable DEBUG_MODE=true to access additional endpoints:
- `/debug/threads` - View all stored threads
- Enhanced logging for troubleshooting

## Security Best Practices

### API Key Management
- Store API keys as encrypted environment variables
- Rotate API keys regularly
- Monitor API usage for unusual patterns
- Use separate API keys for development and production

### Input Validation
- The system validates and sanitizes user inputs
- File uploads are validated for supported formats
- Message lengths may be limited by underlying services

### Access Control
- API endpoints don't implement user authentication by default
- Add authentication middleware if needed for your use case
- Consider IP-based rate limiting for public deployments

## Backups and Recovery

### Database Backups
- Set up automated backups for Neon Postgres
- Test backup restoration procedures regularly
- Store backups in geographically separate locations

### Data Export
- The system provides endpoints to export conversation history
- Sessions can be retrieved with `/api/chat/{session_id}`
- All data can be exported using the session management endpoints

## Updates and Maintenance

### Updating Dependencies
1. Update `requirements.txt` with new versions
2. Test in staging environment
3. Deploy to production after testing

### Application Updates
1. Deploy new code to staging environment
2. Test all functionality including:
   - Document upload and processing
   - Chat functionality in both modes
   - Session management
3. Deploy to production during low-traffic periods
4. Monitor logs and performance after deployment

### Rollback Procedures
- Maintain previous versions in your deployment system
- Use database migrations that can be rolled back if needed
- Monitor application health after updates