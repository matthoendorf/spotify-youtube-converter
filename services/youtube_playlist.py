"""
YouTube Playlist creation service using YouTube Data API v3.
"""

import os
import json
import pickle
from typing import List, Dict, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import streamlit as st


class YouTubePlaylistService:
    """Service class for creating YouTube playlists."""
    
    def __init__(self):
        """Initialize YouTube API client."""
        load_dotenv()
        
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "YouTube credentials not found. Please set YOUTUBE_CLIENT_ID and "
                "YOUTUBE_CLIENT_SECRET in your .env file."
            )
        
        self.scopes = ['https://www.googleapis.com/auth/youtube']
        self.redirect_uri = 'http://localhost:8501'  # Default Streamlit port
        self.credentials = None
        self.youtube = None
        
        # Try to load existing credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load existing credentials from file."""
        token_file = 'youtube_token.pickle'
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.credentials = pickle.load(token)
        
        # Refresh credentials if needed
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self._save_credentials()
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                self.credentials = None
        
        if self.credentials and self.credentials.valid:
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def _save_credentials(self):
        """Save credentials to file."""
        with open('youtube_token.pickle', 'wb') as token:
            pickle.dump(self.credentials, token)
    
    def get_auth_url(self) -> str:
        """
        Get the authorization URL for OAuth flow.
        
        Returns:
            Authorization URL for user to visit
        """
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store flow for later use
        self._flow = flow
        return auth_url
    
    def authenticate_with_code(self, auth_code: str) -> bool:
        """
        Complete authentication with authorization code.
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            True if authentication successful
        """
        try:
            if not hasattr(self, '_flow'):
                raise ValueError("No authentication flow found. Call get_auth_url() first.")
            
            self._flow.fetch_token(code=auth_code)
            self.credentials = self._flow.credentials
            self._save_credentials()
            
            # Build YouTube service
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.credentials is not None and self.credentials.valid
    
    def create_playlist(self, title: str, description: str = "", privacy_status: str = "private") -> Optional[Dict]:
        """
        Create a new YouTube playlist.
        
        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: 'private', 'public', or 'unlisted'
            
        Returns:
            Playlist information dict or None if failed
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Please authenticate first.")
        
        try:
            playlist_body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'defaultLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            playlist_response = self.youtube.playlists().insert(
                part='snippet,status',
                body=playlist_body
            ).execute()
            
            return playlist_response
            
        except HttpError as e:
            print(f"Error creating playlist: {e}")
            return None
    
    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """
        Add a video to a playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            video_id: YouTube video ID
            
        Returns:
            True if successful
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Please authenticate first.")
        
        try:
            playlist_item_body = {
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
            
            self.youtube.playlistItems().insert(
                part='snippet',
                body=playlist_item_body
            ).execute()
            
            return True
            
        except HttpError as e:
            print(f"Error adding video {video_id} to playlist: {e}")
            return False
    
    def create_playlist_from_tracks(self, 
                                  playlist_name: str, 
                                  tracks_df: pd.DataFrame,
                                  confidence_threshold: float = 0.7,
                                  description: str = "") -> Dict:
        """
        Create a YouTube playlist from track data.
        
        Args:
            playlist_name: Name for the new playlist
            tracks_df: DataFrame with track data including youtube_video_id
            confidence_threshold: Minimum confidence to include tracks
            description: Playlist description
            
        Returns:
            Dictionary with creation results
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Please authenticate first.")
        
        # Filter tracks by confidence and availability
        valid_tracks = tracks_df[
            (tracks_df['match_confidence'] >= confidence_threshold) & 
            (tracks_df['youtube_video_id'] != '') & 
            (tracks_df['youtube_video_id'].notna())
        ]
        
        if len(valid_tracks) == 0:
            return {
                'success': False,
                'error': 'No valid tracks found to add to playlist',
                'tracks_attempted': 0,
                'tracks_added': 0,
                'tracks_skipped': len(tracks_df)
            }
        
        # Create the playlist
        playlist_desc = description or f"Created from Spotify playlist with {len(valid_tracks)} tracks"
        playlist = self.create_playlist(playlist_name, playlist_desc, 'private')
        
        if not playlist:
            return {
                'success': False,
                'error': 'Failed to create playlist',
                'tracks_attempted': 0,
                'tracks_added': 0,
                'tracks_skipped': len(tracks_df)
            }
        
        playlist_id = playlist['id']
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        # Add tracks to playlist
        tracks_added = 0
        tracks_failed = []
        
        for _, track in valid_tracks.iterrows():
            video_id = track['youtube_video_id']
            if self.add_video_to_playlist(playlist_id, video_id):
                tracks_added += 1
            else:
                tracks_failed.append({
                    'track_name': track['track_name'],
                    'artist_name': track['artist_name'],
                    'video_id': video_id
                })
        
        return {
            'success': True,
            'playlist_id': playlist_id,
            'playlist_url': playlist_url,
            'playlist_name': playlist_name,
            'tracks_attempted': len(valid_tracks),
            'tracks_added': tracks_added,
            'tracks_failed': len(tracks_failed),
            'tracks_skipped': len(tracks_df) - len(valid_tracks),
            'failed_tracks': tracks_failed,
            'confidence_threshold': confidence_threshold
        }
    
    def get_user_info(self) -> Optional[Dict]:
        """Get authenticated user's channel information."""
        if not self.is_authenticated():
            return None
        
        try:
            response = self.youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            if response['items']:
                return response['items'][0]['snippet']
            return None
            
        except HttpError as e:
            print(f"Error getting user info: {e}")
            return None


def create_youtube_playlist_streamlit(tracks_df: pd.DataFrame, 
                                    playlist_name: str,
                                    confidence_threshold: float = 0.7) -> Dict:
    """
    Streamlit-specific function to create YouTube playlist with UI integration.
    
    Args:
        tracks_df: DataFrame with track data
        playlist_name: Name for the playlist
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        Creation results dictionary
    """
    # Initialize service
    try:
        service = YouTubePlaylistService()
    except ValueError as e:
        return {
            'success': False,
            'error': str(e),
            'tracks_attempted': 0,
            'tracks_added': 0,
            'tracks_skipped': len(tracks_df)
        }
    
    # Check authentication
    if not service.is_authenticated():
        # Need to authenticate
        st.warning("🔐 YouTube authentication required")
        
        # Get auth URL
        auth_url = service.get_auth_url()
        
        st.markdown(f"**Step 1:** [Click here to authenticate with YouTube]({auth_url})")
        st.markdown("**Step 2:** After authentication, copy the authorization code from the redirect URL")
        st.info("💡 **Tip:** The redirect will open in the same tab. After authentication, you'll see a URL with `code=...` - copy that code and paste it below.")
        
        auth_code = st.text_input(
            "Enter authorization code:",
            placeholder="Paste the code from the redirect URL",
            help="After clicking the link above, you'll be redirected to a URL with a 'code' parameter. Copy that code here."
        )
        
        if auth_code:
            with st.spinner("Authenticating..."):
                if service.authenticate_with_code(auth_code):
                    st.success("✅ Authentication successful!")
                    st.rerun()  # Refresh the app
                else:
                    st.error("❌ Authentication failed. Please try again.")
                    return {
                        'success': False,
                        'error': 'Authentication failed',
                        'tracks_attempted': 0,
                        'tracks_added': 0,
                        'tracks_skipped': len(tracks_df)
                    }
        
        return {
            'success': False,
            'error': 'Authentication required',
            'tracks_attempted': 0,
            'tracks_added': 0,
            'tracks_skipped': len(tracks_df)
        }
    
    # User is authenticated, create playlist
    with st.spinner(f"Creating YouTube playlist '{playlist_name}'..."):
        result = service.create_playlist_from_tracks(
            playlist_name=playlist_name,
            tracks_df=tracks_df,
            confidence_threshold=confidence_threshold
        )
    
    return result


if __name__ == "__main__":
    # Test the service
    print("🎵 Testing YouTube Playlist Creation Service")
    print("=" * 60)
    
    try:
        service = YouTubePlaylistService()
        
        if not service.is_authenticated():
            print("🔐 Authentication required")
            auth_url = service.get_auth_url()
            print(f"Visit this URL to authenticate: {auth_url}")
            
            auth_code = input("Enter authorization code: ")
            if service.authenticate_with_code(auth_code):
                print("✅ Authentication successful!")
            else:
                print("❌ Authentication failed")
                exit(1)
        
        # Get user info
        user_info = service.get_user_info()
        if user_info:
            print(f"👤 Authenticated as: {user_info['title']}")
        
        # Test playlist creation
        test_playlist = service.create_playlist(
            title="Test Music League Playlist",
            description="Test playlist created by Music League Helper"
        )
        
        if test_playlist:
            playlist_id = test_playlist['id']
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"✅ Test playlist created: {playlist_url}")
        else:
            print("❌ Failed to create test playlist")
        
    except Exception as e:
        print(f"❌ Error: {e}")
