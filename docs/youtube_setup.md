# YouTube API Setup Guide

This guide explains how to set up YouTube Data API v3 for playlist creation functionality.

## Prerequisites

1. **Google Account**: You need a Google account
2. **Google Cloud Project**: Create or use an existing project

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project details:
   - **Project Name**: `Spotify YouTube Converter` (or any name you prefer)
   - **Organization**: Leave as default or select your organization
5. Click "Create"

### 2. Enable YouTube Data API v3

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on "YouTube Data API v3"
4. Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields:
     - **App Name**: `Spotify YouTube Converter`
     - **User Support Email**: Your email
     - **Developer Contact Email**: Your email
   - Add scopes: `https://www.googleapis.com/auth/youtube`
   - Add test users (your email) if needed
4. Create OAuth 2.0 Client ID:
   - **Application Type**: Web application
   - **Name**: `Spotify YouTube Converter`
   - **Authorized Redirect URIs**: Add `http://localhost:8501`
5. Click "Create"
6. Copy your **Client ID** and **Client Secret**

### 4. Configure Environment Variables

Add your YouTube credentials to the `.env` file:

```env
YOUTUBE_CLIENT_ID=your_actual_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_actual_youtube_client_secret_here
```

## OAuth Flow

The application uses OAuth 2.0 flow for YouTube authentication:

1. **First Time**: User clicks "Create YouTube Playlist"
2. **Redirect**: Browser opens Google OAuth consent screen
3. **Authorization**: User grants permission to create playlists
4. **Callback**: Google redirects back to the app with authorization code
5. **Token Exchange**: App exchanges code for access token
6. **Playlist Creation**: App creates playlist using the access token

## Scopes Required

The application requests these YouTube API scopes:

- `https://www.googleapis.com/auth/youtube` - Manage YouTube account
- `https://www.googleapis.com/auth/youtube.force-ssl` - Manage YouTube account (HTTPS)

## Quota and Limits

YouTube Data API v3 has quotas and limits:

- **Daily Quota**: 10,000 units per day (default)
- **Playlist Creation**: 50 units per playlist
- **Video Search**: 100 units per search
- **Rate Limits**: 100 requests per 100 seconds per user

### Quota Usage Estimation

For a typical playlist with 20 songs:
- Create playlist: 50 units
- Add 20 videos: 20 × 50 = 1,000 units
- **Total**: ~1,050 units per playlist

You can create approximately 9-10 playlists per day with the default quota.

## Testing the Setup

Test your YouTube API setup:

```python
from services.youtube_playlist import YouTubePlaylistService

# This will trigger OAuth flow
service = YouTubePlaylistService()

# Test creating a playlist (will open browser for auth)
playlist_url = service.create_playlist(
    name="Test Playlist",
    description="Test playlist from API",
    video_ids=["dQw4w9WgXcQ"]  # Rick Roll for testing
)

print(f"Created playlist: {playlist_url}")
```

## Troubleshooting

### Common Issues

1. **"OAuth consent screen not configured"**
   - Complete the OAuth consent screen setup
   - Add your email as a test user

2. **"Redirect URI mismatch"**
   - Ensure `http://localhost:8501` is in authorized redirect URIs
   - Check for typos (http vs https, port number)

3. **"Insufficient permissions"**
   - Verify the correct scopes are requested
   - Re-authorize the application

4. **"Quota exceeded"**
   - Check your API usage in Google Cloud Console
   - Wait for quota reset (daily) or request quota increase

5. **"Invalid client credentials"**
   - Verify Client ID and Client Secret are correct
   - Ensure no extra spaces or characters

### Production Deployment

For production deployment:

1. **Update Redirect URI**: Change from `localhost` to your domain
2. **OAuth Consent Screen**: Submit for verification if needed
3. **Quota Increase**: Request higher quota limits if needed
4. **Environment Variables**: Securely store credentials

### Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate credentials** periodically
4. **Monitor API usage** for unusual activity
5. **Use HTTPS** in production

## API Documentation

For more details, see the official documentation:

- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [OAuth 2.0 for Web Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [API Quotas and Limits](https://developers.google.com/youtube/v3/getting-started#quota)

## Getting Help

If you encounter issues:

1. Check the Google Cloud Console for error messages
2. Review the OAuth consent screen configuration
3. Verify API quotas and usage
4. Test with a simple API call first
5. Check the [YouTube API support forum](https://support.google.com/youtube/topic/9257891)
