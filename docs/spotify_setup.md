# Spotify API Setup Guide

This guide explains how to set up and use the Spotify playlist extraction functionality.

## Prerequisites

1. **Spotify Developer Account**: You need a Spotify account (free is fine)
2. **Spotify App Registration**: Create an app in the Spotify Developer Dashboard

## Setup Steps

### 1. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the details:
   - **App Name**: `Music League Helper` (or any name you prefer)
   - **App Description**: `Tool for extracting playlist data from Music League`
   - **Website**: Leave blank or use `http://localhost`
   - **Redirect URI**: `http://localhost:8080/callback` (not used for Client Credentials flow, but required)
5. Check the boxes for the terms of service
6. Click "Save"

### 2. Get Your Credentials

1. In your app dashboard, click "Settings"
2. Copy your **Client ID**
3. Click "View client secret" and copy your **Client Secret**

### 3. Configure Environment Variables

1. Create a `.env` file in the project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_actual_client_id_here
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
   ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from services.spotify import extract_playlist_data

# Extract playlist data
playlist_url = "https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um"
df = extract_playlist_data(playlist_url)

print(f"Extracted {len(df)} tracks")
print(df.head())
```

### Advanced Usage

```python
from services.spotify import SpotifyService

# Initialize service
service = SpotifyService()

# Get playlist information
playlist_info = service.get_playlist_info(playlist_url)
print(f"Playlist: {playlist_info['name']}")
print(f"Owner: {playlist_info['owner']}")
print(f"Track Count: {playlist_info['track_count']}")

# Get track data
tracks_df = service.get_playlist_tracks(playlist_url)

# Save to CSV
tracks_df.to_csv('my_playlist.csv', index=False)
```

### Test the Setup

Run the test script to verify everything works:

```bash
python test_spotify.py
```

## DataFrame Schema

The extracted data returns a pandas DataFrame with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `track_name` | string | Name of the track |
| `artist_name` | string | Artist name(s), comma-separated for multiple artists |
| `album_name` | string | Album name |
| `spotify_url` | string | Direct Spotify URL to the track |

## Supported URL Formats

The service supports standard Spotify playlist URLs:

- `https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um`
- `https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um?si=abc123`
- `https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um?pi=PmIzTgsdTOCAX`

## Error Handling

The service handles common issues:

- **Invalid URLs**: Raises `ValueError` with clear message
- **Missing credentials**: Raises `ValueError` with setup instructions
- **Private playlists**: May return empty results or raise authentication errors
- **Unavailable tracks**: Skips tracks that are None (local files, region-restricted)
- **Large playlists**: Automatically handles pagination for playlists with 100+ tracks

## Limitations

- **Client Credentials Flow**: Can only access public playlists
- **Rate Limits**: Spotify API has rate limits (usually not an issue for normal usage)
- **Local Files**: Cannot extract data from local files in playlists
- **Region Restrictions**: Some tracks may not be available in all regions

## Troubleshooting

### Common Issues

1. **"Spotify credentials not found"**
   - Make sure your `.env` file exists and has the correct variable names
   - Check that there are no extra spaces around the `=` sign

2. **"Invalid client credentials"**
   - Verify your Client ID and Client Secret are correct
   - Make sure you copied them completely (no truncation)

3. **"Invalid Spotify playlist URL"**
   - Ensure the URL is a Spotify playlist URL (not track, album, or artist)
   - Check that the playlist is public

4. **Empty DataFrame returned**
   - The playlist might be private
   - The playlist might be empty
   - All tracks might be local files or unavailable

### Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify your Spotify app settings
3. Test with a known public playlist
4. Check the [Spotify Web API documentation](https://developer.spotify.com/documentation/web-api/)
