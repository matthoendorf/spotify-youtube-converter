"""
Spotify API service for extracting playlist data.
"""

import os
import re
from typing import Optional
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


class SpotifyService:
    """Service class for interacting with Spotify Web API."""
    
    def __init__(self):
        """Initialize Spotify client with credentials from environment variables."""
        load_dotenv()
        
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET in your .env file."
            )
        
        # Set up client credentials flow
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def extract_playlist_id(self, playlist_url: str) -> str:
        """
        Extract playlist ID from Spotify playlist URL.
        
        Args:
            playlist_url: Spotify playlist URL
            
        Returns:
            Playlist ID string
            
        Raises:
            ValueError: If URL format is invalid
        """
        # Pattern to match Spotify playlist URLs
        pattern = r'https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)'
        match = re.search(pattern, playlist_url)
        
        if not match:
            raise ValueError(f"Invalid Spotify playlist URL: {playlist_url}")
        
        return match.group(1)
    
    def get_playlist_tracks(self, playlist_url: str) -> pd.DataFrame:
        """
        Extract track data from a Spotify playlist.
        
        Args:
            playlist_url: Spotify playlist URL
            
        Returns:
            DataFrame with columns: track_name, artist_name, album_name, spotify_url
        """
        playlist_id = self.extract_playlist_id(playlist_url)
        
        # Get playlist tracks (handle pagination)
        tracks_data = []
        offset = 0
        limit = 100
        
        while True:
            results = self.sp.playlist_tracks(
                playlist_id, 
                offset=offset, 
                limit=limit,
                fields='items(track(name,artists(name),album(name),external_urls.spotify)),next'
            )
            
            for item in results['items']:
                track = item['track']
                
                # Skip if track is None (can happen with local files or unavailable tracks)
                if track is None:
                    continue
                
                # Extract track information
                track_name = track['name']
                artist_name = ', '.join([artist['name'] for artist in track['artists']])
                album_name = track['album']['name']
                spotify_url = track['external_urls']['spotify']
                
                tracks_data.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'album_name': album_name,
                    'spotify_url': spotify_url
                })
            
            # Check if there are more tracks to fetch
            if results['next'] is None:
                break
            
            offset += limit
        
        return pd.DataFrame(tracks_data)
    
    def get_playlist_info(self, playlist_url: str) -> dict:
        """
        Get basic playlist information.
        
        Args:
            playlist_url: Spotify playlist URL
            
        Returns:
            Dictionary with playlist name, description, and track count
        """
        playlist_id = self.extract_playlist_id(playlist_url)
        
        playlist = self.sp.playlist(
            playlist_id, 
            fields='name,description,tracks.total,owner.display_name'
        )
        
        return {
            'name': playlist['name'],
            'description': playlist.get('description', ''),
            'track_count': playlist['tracks']['total'],
            'owner': playlist['owner']['display_name']
        }


def extract_playlist_data(playlist_url: str) -> pd.DataFrame:
    """
    Convenience function to extract playlist data.
    
    Args:
        playlist_url: Spotify playlist URL
        
    Returns:
        DataFrame with track data
    """
    service = SpotifyService()
    return service.get_playlist_tracks(playlist_url)


if __name__ == "__main__":
    # Example usage
    example_url = "https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um?pi=PmIzTgsdTOCAX"
    
    try:
        # Initialize service
        spotify_service = SpotifyService()
        
        # Get playlist info
        print("Getting playlist information...")
        playlist_info = spotify_service.get_playlist_info(example_url)
        print(f"Playlist: {playlist_info['name']}")
        print(f"Owner: {playlist_info['owner']}")
        print(f"Track Count: {playlist_info['track_count']}")
        print(f"Description: {playlist_info['description'][:100]}...")
        print()
        
        # Extract track data
        print("Extracting track data...")
        df = spotify_service.get_playlist_tracks(example_url)
        
        print(f"Successfully extracted {len(df)} tracks")
        print("\nFirst 5 tracks:")
        print(df.head().to_string(index=False))
        
        # Save to CSV for inspection
        df.to_csv('playlist_tracks.csv', index=False)
        print(f"\nData saved to playlist_tracks.csv")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with your Spotify credentials")
        print("2. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        print("3. Registered your app at https://developer.spotify.com/dashboard")
