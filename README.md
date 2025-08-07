# 🎵 Spotify to YouTube Music Converter

A Streamlit web application that converts Spotify playlists to YouTube Music playlists without requiring Spotify Premium. Perfect for discovering and enjoying music from any public Spotify playlist on YouTube Music!

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Spotify](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)
![YouTube Music](https://img.shields.io/badge/YouTube_Music-FF0000?style=for-the-badge&logo=youtube&logoColor=white)

## ✨ Features

### 🎯 Core Functionality
- **Extract Spotify Playlists** - Get track data from public Spotify playlists (no Premium required)
- **YouTube Music Search** - Find matching tracks on YouTube Music with confidence scoring
- **Automatic Playlist Creation** - Create private YouTube playlists with shareable links
- **Visual Thumbnails** - Display YouTube thumbnails (cached locally to avoid CORS issues)
- **Smart Matching** - Advanced algorithm matches tracks by artist, title, and album

### 🚀 Advanced Features
- **Session State Management** - Data persists across app interactions and OAuth flows
- **Image Caching System** - Local thumbnail storage eliminates browser CORS errors
- **Confidence Scoring** - Adjustable thresholds for match quality (0.0 - 1.0)
- **Multiple Export Formats** - CSV, high-confidence only, YouTube URLs
- **Real-time Progress** - Visual feedback during searches and playlist creation
- **Error Handling** - Comprehensive error messages and troubleshooting guides

## 🎮 Great for Social Music Games

This tool works perfectly with social music games where participants submit songs to themed playlists. It helps you:

1. **Access shared playlists** without Spotify Premium
2. **Discover new music** with visual thumbnails and metadata
3. **Create your own YouTube playlists** from shared submissions
4. **Share playlists** with friends via private YouTube links
5. **Export data** for analysis and record-keeping

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Spotify Developer Account
- Google Cloud Project with YouTube Data API v3

### Quick Start

#### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/matthoendorf/spotify-youtube-converter.git
   cd spotify-youtube-converter
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials (see setup guides below)
   ```

3. **Run with Docker**
   ```bash
   docker-compose up
   ```

4. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Start converting playlists!

#### Option 2: Local Python Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/matthoendorf/spotify-youtube-converter.git
   cd spotify-youtube-converter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials (see setup guides below)
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Start converting playlists!

## 🔧 API Setup

### Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Click "Create an App"
3. Fill in app details (name, description)
4. Copy your **Client ID** and **Client Secret**
5. Add them to your `.env` file

**Note:** No redirect URI needed - we use Client Credentials Flow

### YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Web application"
6. Add `http://localhost:8501` to authorized redirect URIs
7. Copy your **Client ID** and **Client Secret**
8. Add them to your `.env` file

For detailed setup instructions, see:
- [Spotify API Setup](docs/spotify_setup.md)
- [YouTube API Setup](docs/youtube_setup.md)

## 📖 Usage

### Basic Workflow

1. **Enter Spotify Playlist URL**
   - Paste any public Spotify playlist URL
   - Works with any shared playlist!

2. **Extract & Search**
   - App extracts track metadata from Spotify
   - Searches YouTube Music for matching tracks
   - Displays results with thumbnails and confidence scores

3. **Review Results**
   - Browse all matches in the "All Results" tab
   - Filter high-confidence matches
   - View detailed data table

4. **Create YouTube Playlist**
   - Go to "Export" tab
   - Click "Create YouTube Playlist"
   - Authenticate with Google (one-time setup)
   - Get shareable playlist link!

### Advanced Options

- **Confidence Threshold**: Adjust match quality requirements (0.0 - 1.0)
- **Max Results**: Control how many YouTube results to consider per track
- **Thumbnail Display**: Toggle visual thumbnails on/off
- **Export Options**: Download CSV files, URLs, or filtered data

## 🏗️ Architecture

### Project Structure
```
spotify-youtube-converter/
├── streamlit_app.py          # Main Streamlit application
├── services/
│   ├── spotify.py           # Spotify API integration
│   ├── youtube.py           # YouTube Music search
│   └── youtube_playlist.py  # YouTube playlist creation
├── utils/
│   ├── image_cache.py       # Local thumbnail caching
│   └── io.py               # File I/O utilities
├── config/
│   └── settings.py         # Configuration management
├── data/
│   └── thumbnails/         # Cached thumbnail images
└── docs/
    └── spotify_setup.md    # Detailed setup guide
```

### Key Components

- **SpotifyService**: Handles playlist extraction using Client Credentials Flow
- **YouTubeMusicService**: Searches YouTube Music and caches thumbnails
- **YouTubePlaylistService**: Creates playlists using OAuth 2.0
- **ImageCache**: Downloads and stores thumbnails locally
- **Session State Management**: Preserves data across app interactions

## 🔒 Privacy & Security

- **No Premium Required**: Uses Spotify's public API endpoints
- **Local Caching**: Thumbnails stored locally, not shared
- **Private Playlists**: YouTube playlists created as private with shareable links
- **Secure OAuth**: Standard Google OAuth 2.0 flow for YouTube authentication
- **No Data Collection**: App doesn't store or transmit personal data

## 📝 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

### Setup Guides
- [Spotify API Setup](docs/spotify_setup.md) - Complete guide for Spotify Developer setup
- [YouTube API Setup](docs/youtube_setup.md) - Google Cloud and YouTube API configuration

### Deployment
- [Deployment Guide](docs/deployment.md) - Deploy to Streamlit Cloud, Heroku, Docker, and more

### Contributing
- [Contributing Guide](docs/contributing.md) - How to contribute to the project

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/matthoendorf/spotify-youtube-converter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthoendorf/spotify-youtube-converter/discussions)
- **Documentation**: Check the `docs/` folder for detailed guides