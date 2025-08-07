# Deployment Guide

This guide covers various deployment options for the Spotify to YouTube Music Converter.

## Table of Contents

- [Local Development](#local-development)
- [Streamlit Cloud](#streamlit-cloud)
- [Docker Deployment](#docker-deployment)
- [Heroku](#heroku)
- [Railway](#railway)
- [Environment Variables](#environment-variables)
- [Production Considerations](#production-considerations)

## Local Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/matthoendorf/spotify-youtube-converter.git
cd spotify-youtube-converter

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API credentials

# Run the application
streamlit run streamlit_app.py
```

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Run the application
uv run streamlit run streamlit_app.py
```

## Streamlit Cloud

Streamlit Cloud is the easiest way to deploy Streamlit applications.

### Prerequisites

- GitHub repository with your code
- Streamlit Cloud account (free)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Choose branch: `main`
   - Main file path: `streamlit_app.py`

3. **Configure Environment Variables**
   - In the app settings, go to "Secrets"
   - Add your environment variables:
   ```toml
   SPOTIFY_CLIENT_ID = "your_spotify_client_id"
   SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
   YOUTUBE_CLIENT_ID = "your_youtube_client_id"
   YOUTUBE_CLIENT_SECRET = "your_youtube_client_secret"
   ```

4. **Update YouTube Redirect URI**
   - In Google Cloud Console, update the OAuth redirect URI
   - Change from `http://localhost:8501` to your Streamlit Cloud URL
   - Format: `https://your-app-name.streamlit.app`

5. **Deploy**
   - Click "Deploy"
   - Your app will be available at `https://your-app-name.streamlit.app`

## Docker Deployment

### Build Docker Image

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/thumbnails

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build the image
docker build -t spotify-youtube-converter .

# Run the container
docker run -p 8501:8501 \
  -e SPOTIFY_CLIENT_ID=your_spotify_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_spotify_client_secret \
  -e YOUTUBE_CLIENT_ID=your_youtube_client_id \
  -e YOUTUBE_CLIENT_SECRET=your_youtube_client_secret \
  spotify-youtube-converter
```

### Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
      - SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
      - YOUTUBE_CLIENT_ID=${YOUTUBE_CLIENT_ID}
      - YOUTUBE_CLIENT_SECRET=${YOUTUBE_CLIENT_SECRET}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed

### Deployment Steps

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Add Buildpack**
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Create Procfile**
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SPOTIFY_CLIENT_ID=your_spotify_client_id
   heroku config:set SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   heroku config:set YOUTUBE_CLIENT_ID=your_youtube_client_id
   heroku config:set YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Update YouTube Redirect URI**
   - Update OAuth redirect URI to: `https://your-app-name.herokuapp.com`

## Railway

Railway offers simple deployment with automatic builds.

### Deployment Steps

1. **Connect GitHub Repository**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables**
   - In the project dashboard, go to "Variables"
   - Add your environment variables

3. **Configure Build**
   - Railway automatically detects Python projects
   - Ensure your `requirements.txt` is in the root directory

4. **Custom Start Command** (if needed)
   ```bash
   streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. **Update YouTube Redirect URI**
   - Update OAuth redirect URI to your Railway domain

## Environment Variables

### Required Variables

```env
# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# YouTube API
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
```

### Platform-Specific Configuration

#### Streamlit Cloud
Use the secrets management in the dashboard (TOML format).

#### Heroku
```bash
heroku config:set VARIABLE_NAME=value
```

#### Docker
Use environment variables in docker run or docker-compose.yml.

#### Railway
Set variables in the project dashboard.

## Production Considerations

### Security

1. **Environment Variables**
   - Never commit credentials to version control
   - Use platform-specific secret management
   - Rotate credentials regularly

2. **HTTPS**
   - Always use HTTPS in production
   - Update OAuth redirect URIs accordingly

3. **CORS and Security Headers**
   - Configure appropriate security headers
   - Validate all user inputs

### Performance

1. **Caching**
   - Enable Streamlit caching for API calls
   - Use persistent storage for thumbnails

2. **Resource Limits**
   - Monitor memory usage
   - Set appropriate container limits

3. **API Quotas**
   - Monitor YouTube API quota usage
   - Implement rate limiting if needed

### Monitoring

1. **Logging**
   - Configure structured logging
   - Monitor application errors

2. **Health Checks**
   - Implement health check endpoints
   - Monitor application availability

3. **Analytics**
   - Track usage patterns
   - Monitor API quota consumption

### Scaling

1. **Horizontal Scaling**
   - Most platforms support automatic scaling
   - Consider stateless design

2. **Database**
   - For high usage, consider adding a database
   - Cache frequently accessed data

3. **CDN**
   - Use CDN for static assets
   - Consider caching thumbnails externally

## Troubleshooting

### Common Issues

1. **Port Configuration**
   - Ensure the app binds to `0.0.0.0` not `localhost`
   - Use the platform-provided PORT environment variable

2. **OAuth Redirect URIs**
   - Update redirect URIs for each deployment
   - Ensure exact match (http vs https, trailing slashes)

3. **Dependencies**
   - Keep requirements.txt updated
   - Test with the exact Python version used in production

4. **File Permissions**
   - Ensure write permissions for thumbnail cache
   - Consider using temporary directories

### Platform-Specific Issues

#### Streamlit Cloud
- Limited to 1GB RAM
- No persistent file storage
- Automatic sleep after inactivity

#### Heroku
- Ephemeral file system
- Dyno sleep on free tier
- Limited build time

#### Docker
- File permission issues
- Network configuration
- Resource limits

## Getting Help

If you encounter deployment issues:

1. Check platform-specific documentation
2. Review application logs
3. Verify environment variables
4. Test OAuth flows with new redirect URIs
5. Monitor API quota usage

For platform-specific support:
- [Streamlit Cloud Community](https://discuss.streamlit.io/)
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Railway Documentation](https://docs.railway.app/)
- [Docker Documentation](https://docs.docker.com/)
