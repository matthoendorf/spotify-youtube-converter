"""
YouTube Music search service for finding tracks from Spotify playlists.
"""

import os
import re
from typing import List, Dict, Optional
import pandas as pd
from ytmusicapi import YTMusic
from dotenv import load_dotenv
from utils.image_cache import cache_image


class YouTubeMusicService:
    """Service class for searching YouTube Music."""
    
    def __init__(self):
        """Initialize YouTube Music client."""
        load_dotenv()
        
        # YTMusic doesn't require authentication for search
        # But you can optionally provide headers for better results
        try:
            self.ytmusic = YTMusic()
        except Exception as e:
            raise ValueError(f"Failed to initialize YouTube Music client: {e}")
    
    def search_track(self, artist: str, track_name: str, limit: int = 5) -> List[Dict]:
        """
        Search for a track on YouTube Music.
        
        Args:
            artist: Artist name
            track_name: Track name
            limit: Maximum number of results to return
            
        Returns:
            List of search results with YouTube Music data
        """
        # Create search query
        query = f"{artist} {track_name}"
        
        try:
            # Search for songs on YouTube Music
            results = self.ytmusic.search(query, filter="songs", limit=limit)
            
            processed_results = []
            for result in results:
                processed_result = {
                    'youtube_title': result.get('title', ''),
                    'youtube_artist': ', '.join([artist['name'] for artist in result.get('artists', [])]),
                    'youtube_album': result.get('album', {}).get('name', '') if result.get('album') else '',
                    'youtube_duration': result.get('duration', ''),
                    'youtube_url': f"https://music.youtube.com/watch?v={result.get('videoId', '')}",
                    'youtube_video_id': result.get('videoId', ''),
                    'youtube_thumbnail': result.get('thumbnails', [{}])[-1].get('url', '') if result.get('thumbnails') else '',
                    'match_confidence': self._calculate_match_confidence(artist, track_name, result)
                }
                processed_results.append(processed_result)
            
            # Sort by match confidence
            processed_results.sort(key=lambda x: x['match_confidence'], reverse=True)
            return processed_results
            
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return []
    
    def _calculate_match_confidence(self, original_artist: str, original_track: str, yt_result: Dict) -> float:
        """
        Calculate a confidence score for how well the YouTube result matches the original track.
        
        Args:
            original_artist: Original artist name
            original_track: Original track name
            yt_result: YouTube Music search result
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        yt_title = yt_result.get('title', '').lower()
        yt_artists = [artist['name'].lower() for artist in yt_result.get('artists', [])]
        
        original_artist_lower = original_artist.lower()
        original_track_lower = original_track.lower()
        
        # Check if track name matches (50% weight)
        if original_track_lower in yt_title:
            score += 0.5
        elif any(word in yt_title for word in original_track_lower.split() if len(word) > 2):
            score += 0.3
        
        # Check if artist matches (40% weight)
        artist_match = False
        for yt_artist in yt_artists:
            if original_artist_lower in yt_artist or yt_artist in original_artist_lower:
                score += 0.4
                artist_match = True
                break
        
        if not artist_match:
            # Check for partial artist matches
            for yt_artist in yt_artists:
                artist_words = original_artist_lower.split()
                if any(word in yt_artist for word in artist_words if len(word) > 2):
                    score += 0.2
                    break
        
        # Bonus for exact matches (10% weight)
        if (original_track_lower == yt_title and 
            any(original_artist_lower == yt_artist for yt_artist in yt_artists)):
            score += 0.1
        
        return min(score, 1.0)
    
    def search_playlist_tracks(self, spotify_df: pd.DataFrame, top_results: int = 3) -> pd.DataFrame:
        """
        Search YouTube Music for all tracks in a Spotify playlist DataFrame.
        
        Args:
            spotify_df: DataFrame with Spotify track data
            top_results: Number of top YouTube results to keep per track
            
        Returns:
            DataFrame with combined Spotify and YouTube Music data
        """
        all_results = []
        
        for idx, row in spotify_df.iterrows():
            print(f"Searching {idx + 1}/{len(spotify_df)}: {row['artist_name']} - {row['track_name']}")
            
            # Search YouTube Music
            yt_results = self.search_track(
                row['artist_name'], 
                row['track_name'], 
                limit=top_results
            )
            
            if yt_results:
                # Take the best match
                best_match = yt_results[0]
                
                # Cache the thumbnail image
                thumbnail_url = best_match['youtube_thumbnail']
                cached_thumbnail_path = None
                if thumbnail_url:
                    print(f"Caching thumbnail for: {best_match['youtube_title']}")
                    cached_thumbnail_path = cache_image(thumbnail_url)
                
                # Combine Spotify and YouTube data
                combined_result = {
                    # Original Spotify data
                    'track_name': row['track_name'],
                    'artist_name': row['artist_name'],
                    'album_name': row['album_name'],
                    'spotify_url': row['spotify_url'],
                    
                    # YouTube Music data
                    'youtube_title': best_match['youtube_title'],
                    'youtube_artist': best_match['youtube_artist'],
                    'youtube_album': best_match['youtube_album'],
                    'youtube_duration': best_match['youtube_duration'],
                    'youtube_url': best_match['youtube_url'],
                    'youtube_video_id': best_match['youtube_video_id'],
                    'youtube_thumbnail': best_match['youtube_thumbnail'],
                    'youtube_thumbnail_local': cached_thumbnail_path,
                    'match_confidence': best_match['match_confidence']
                }
                
                all_results.append(combined_result)
            else:
                # No YouTube results found
                combined_result = {
                    # Original Spotify data
                    'track_name': row['track_name'],
                    'artist_name': row['artist_name'],
                    'album_name': row['album_name'],
                    'spotify_url': row['spotify_url'],
                    
                    # Empty YouTube data
                    'youtube_title': '',
                    'youtube_artist': '',
                    'youtube_album': '',
                    'youtube_duration': '',
                    'youtube_url': '',
                    'youtube_video_id': '',
                    'youtube_thumbnail': '',
                    'youtube_thumbnail_local': None,
                    'match_confidence': 0.0
                }
                
                all_results.append(combined_result)
        
        return pd.DataFrame(all_results)
    
    def get_best_matches(self, spotify_df: pd.DataFrame, confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Get only high-confidence YouTube Music matches for Spotify tracks.
        
        Args:
            spotify_df: DataFrame with Spotify track data
            confidence_threshold: Minimum confidence score to include
            
        Returns:
            DataFrame with only high-confidence matches
        """
        full_results = self.search_playlist_tracks(spotify_df)
        return full_results[full_results['match_confidence'] >= confidence_threshold]


def search_youtube_music(spotify_df: pd.DataFrame, top_results: int = 3) -> pd.DataFrame:
    """
    Convenience function to search YouTube Music for Spotify tracks.
    
    Args:
        spotify_df: DataFrame with Spotify track data
        top_results: Number of top results per track
        
    Returns:
        DataFrame with combined Spotify and YouTube Music data
    """
    service = YouTubeMusicService()
    return service.search_playlist_tracks(spotify_df, top_results)


if __name__ == "__main__":
    # Example usage
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.spotify import extract_playlist_data
    
    print("🎵 Testing YouTube Music Search Integration")
    print("=" * 60)
    
    try:
        # Get Spotify playlist data
        playlist_url = "https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um?pi=PmIzTgsdTOCAX"
        print("📥 Extracting Spotify playlist...")
        spotify_df = extract_playlist_data(playlist_url)
        print(f"✅ Found {len(spotify_df)} Spotify tracks")
        
        # Search YouTube Music (test with first 3 tracks)
        print("\n🔍 Searching YouTube Music...")
        test_df = spotify_df.head(3)  # Test with first 3 tracks
        
        yt_service = YouTubeMusicService()
        combined_df = yt_service.search_playlist_tracks(test_df)
        
        print(f"\n📊 Results:")
        for _, row in combined_df.iterrows():
            print(f"\n🎵 {row['track_name']} - {row['artist_name']}")
            print(f"   🎯 Match Confidence: {row['match_confidence']:.2f}")
            print(f"   📺 YouTube: {row['youtube_title']} - {row['youtube_artist']}")
            print(f"   🔗 URL: {row['youtube_url']}")
        
        # Save results
        combined_df.to_csv('spotify_youtube_matches.csv', index=False)
        print(f"\n💾 Results saved to: spotify_youtube_matches.csv")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed ytmusicapi: pip install ytmusicapi")
        print("2. Your Spotify credentials are set up correctly")
