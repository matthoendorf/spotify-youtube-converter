"""
Image cache utility for downloading and storing YouTube thumbnails locally.
"""

import os
import hashlib
import requests
from pathlib import Path
from typing import Optional
import time


class ImageCache:
    """Utility class for caching images locally."""
    
    def __init__(self, cache_dir: str = "data/thumbnails"):
        """
        Initialize image cache.
        
        Args:
            cache_dir: Directory to store cached images
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Request session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _get_cache_filename(self, url: str, extension: str = "jpg") -> str:
        """
        Generate a unique filename for the cached image.
        
        Args:
            url: Image URL
            extension: File extension
            
        Returns:
            Filename for cached image
        """
        # Create hash of URL for unique filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.{extension}"
    
    def _detect_image_format(self, url: str, content_type: str = None) -> str:
        """
        Detect image format from URL or content type.
        
        Args:
            url: Image URL
            content_type: HTTP content type header
            
        Returns:
            File extension (jpg, png, webp)
        """
        # Check content type first
        if content_type:
            if 'jpeg' in content_type or 'jpg' in content_type:
                return 'jpg'
            elif 'png' in content_type:
                return 'png'
            elif 'webp' in content_type:
                return 'webp'
        
        # Fallback to URL extension
        if '.png' in url.lower():
            return 'png'
        elif '.webp' in url.lower():
            return 'webp'
        else:
            return 'jpg'  # Default for YouTube thumbnails
    
    def get_cached_image(self, url: str) -> Optional[str]:
        """
        Get cached image path, downloading if necessary.
        
        Args:
            url: Image URL to cache
            
        Returns:
            Local file path if successful, None if failed
        """
        if not url:
            return None
        
        try:
            # Check if already cached (try different extensions)
            for ext in ['jpg', 'png', 'webp']:
                filename = self._get_cache_filename(url, ext)
                cache_path = self.cache_dir / filename
                if cache_path.exists():
                    return str(cache_path)
            
            # Download the image
            print(f"Downloading thumbnail: {url}")
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Detect format
            content_type = response.headers.get('content-type', '')
            extension = self._detect_image_format(url, content_type)
            
            # Save to cache
            filename = self._get_cache_filename(url, extension)
            cache_path = self.cache_dir / filename
            
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Cached thumbnail: {cache_path}")
            return str(cache_path)
            
        except Exception as e:
            print(f"Failed to cache image {url}: {e}")
            return None
    
    def get_cached_image_batch(self, urls: list) -> dict:
        """
        Cache multiple images in batch.
        
        Args:
            urls: List of image URLs
            
        Returns:
            Dictionary mapping URLs to local paths (or None if failed)
        """
        results = {}
        
        for i, url in enumerate(urls):
            if url:
                print(f"Caching image {i+1}/{len(urls)}")
                results[url] = self.get_cached_image(url)
                
                # Small delay to be respectful to the server
                time.sleep(0.1)
            else:
                results[url] = None
        
        return results
    
    def clear_cache(self, max_age_days: int = 30):
        """
        Clear old cached images.
        
        Args:
            max_age_days: Remove images older than this many days
        """
        if not self.cache_dir.exists():
            return
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        removed_count = 0
        
        for file_path in self.cache_dir.iterdir():
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        removed_count += 1
                    except Exception as e:
                        print(f"Failed to remove {file_path}: {e}")
        
        print(f"Removed {removed_count} old cached images")
    
    def get_cache_info(self) -> dict:
        """
        Get information about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_dir.exists():
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'cache_dir': str(self.cache_dir)
            }
        
        total_files = 0
        total_size = 0
        
        for file_path in self.cache_dir.iterdir():
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }


# Global cache instance
_image_cache = None

def get_image_cache() -> ImageCache:
    """Get the global image cache instance."""
    global _image_cache
    if _image_cache is None:
        _image_cache = ImageCache()
    return _image_cache


def cache_image(url: str) -> Optional[str]:
    """
    Convenience function to cache a single image.
    
    Args:
        url: Image URL
        
    Returns:
        Local file path or None
    """
    cache = get_image_cache()
    return cache.get_cached_image(url)


def cache_images_batch(urls: list) -> dict:
    """
    Convenience function to cache multiple images.
    
    Args:
        urls: List of image URLs
        
    Returns:
        Dictionary mapping URLs to local paths
    """
    cache = get_image_cache()
    return cache.get_cached_image_batch(urls)


if __name__ == "__main__":
    # Test the image cache
    cache = ImageCache()
    
    # Test with a sample YouTube thumbnail
    test_url = "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"
    
    print("Testing image cache...")
    cached_path = cache.get_cached_image(test_url)
    
    if cached_path:
        print(f"✅ Successfully cached: {cached_path}")
    else:
        print("❌ Failed to cache image")
    
    # Show cache info
    info = cache.get_cache_info()
    print(f"Cache info: {info}")
