"""
Music League Helper - Streamlit App
Extract Spotify playlist data and find tracks on YouTube Music
"""

import streamlit as st
import pandas as pd
import time
from typing import Optional

# Import our services
from services.spotify import SpotifyService, extract_playlist_data
from services.youtube import YouTubeMusicService, search_youtube_music
from services.youtube_playlist import create_youtube_playlist_streamlit

# Page configuration
st.set_page_config(
    page_title="Music League Helper",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit app."""
    
    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'playlist_info' not in st.session_state:
        st.session_state.playlist_info = None
    if 'spotify_df' not in st.session_state:
        st.session_state.spotify_df = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    if 'pending_playlist_creation' not in st.session_state:
        st.session_state.pending_playlist_creation = False
    if 'playlist_creation_data' not in st.session_state:
        st.session_state.playlist_creation_data = None
    
    # Header
    st.title("🎵 Music League Helper")
    st.markdown("Extract Spotify playlist data and find tracks on YouTube Music")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # YouTube Music search settings
        st.subheader("YouTube Music Search")
        search_enabled = st.checkbox("Enable YouTube Music search", value=True)
        confidence_threshold = st.slider(
            "Match confidence threshold", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.7, 
            step=0.1,
            help="Only show YouTube matches above this confidence level"
        )
        max_results_per_track = st.selectbox(
            "Max YouTube results per track",
            options=[1, 3, 5],
            index=0,
            help="Number of YouTube Music results to consider per track"
        )
        
        # Display options
        st.subheader("🖼️ Display Options")
        show_thumbnails = st.checkbox("Show thumbnails", value=True, help="Display YouTube thumbnails in results (cached locally)")
        
        # Export options
        st.subheader("📥 Export Options")
        include_thumbnails_export = st.checkbox("Include thumbnails in CSV export", value=False)
        
        # Info
        st.subheader("ℹ️ About")
        st.info(
            "This tool helps you find Music League playlist tracks on YouTube Music "
            "since you don't have Spotify Premium. Perfect for discovering new music!"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Playlist URL input
        st.subheader("📋 Spotify Playlist")
        playlist_url = st.text_input(
            "Enter Spotify Playlist URL:",
            placeholder="https://open.spotify.com/playlist/...",
            help="Paste the URL of a public Spotify playlist from Music League"
        )
        
        # Example URLs
        with st.expander("📝 Example URLs"):
            st.code("https://open.spotify.com/playlist/21VEt90ZQIRa95rmeFi5Um?pi=PmIzTgsdTOCAX")
            st.caption("Music League playlists are typically public and can be accessed without Premium")
    
    with col2:
        # Quick stats (will be populated after extraction)
        st.subheader("📊 Quick Stats")
        stats_placeholder = st.empty()
        
        # Display placeholder stats
        with stats_placeholder.container():
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Tracks", "—")
                st.metric("YouTube Matches", "—")
            with col_b:
                st.metric("High Confidence", "—")
                st.metric("Success Rate", "—")
    
    # Check if we have existing results to display
    if st.session_state.search_results is not None and st.session_state.playlist_info is not None:
        # Display existing results
        playlist_info = st.session_state.playlist_info
        combined_df = st.session_state.search_results
        
        # Show current playlist info
        st.success(f"✅ Current playlist: **{playlist_info['name']}**")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Owner", playlist_info['owner'])
        with col2:
            st.metric("Total Tracks", playlist_info['track_count'])
        with col3:
            st.metric("Extracted", len(combined_df))
        with col4:
            if st.button("🔄 New Search", use_container_width=True):
                # Clear session state
                st.session_state.search_results = None
                st.session_state.playlist_info = None
                st.session_state.spotify_df = None
                st.rerun()
        
        # Calculate and display stats
        total_tracks = len(combined_df)
        youtube_matches = len(combined_df[combined_df['youtube_url'] != ''])
        high_confidence = len(combined_df[combined_df['match_confidence'] >= confidence_threshold])
        success_rate = (youtube_matches / total_tracks * 100) if total_tracks > 0 else 0
        
        # Update stats
        with stats_placeholder.container():
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Tracks", total_tracks)
                st.metric("YouTube Matches", youtube_matches)
            with col_b:
                st.metric("High Confidence", high_confidence)
                st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Display results
        display_results(combined_df, confidence_threshold, show_thumbnails, include_thumbnails_export, playlist_info)
    
    # Process button (only show if no existing results)
    elif st.button("🚀 Extract & Search", type="primary", use_container_width=True):
        if not playlist_url:
            st.error("Please enter a Spotify playlist URL")
            return
        
        try:
            # Step 1: Extract Spotify data
            with st.spinner("📥 Extracting Spotify playlist data..."):
                spotify_service = SpotifyService()
                
                # Get playlist info
                playlist_info = spotify_service.get_playlist_info(playlist_url)
                
                # Get track data
                spotify_df = spotify_service.get_playlist_tracks(playlist_url)
            
            # Store in session state
            st.session_state.playlist_info = playlist_info
            st.session_state.spotify_df = spotify_df
            
            # Display playlist info
            st.success(f"✅ Found playlist: **{playlist_info['name']}**")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Owner", playlist_info['owner'])
            with col2:
                st.metric("Total Tracks", playlist_info['track_count'])
            with col3:
                st.metric("Extracted", len(spotify_df))
            with col4:
                if playlist_info['description']:
                    st.metric("Has Description", "Yes")
                else:
                    st.metric("Has Description", "No")
            
            # Step 2: YouTube Music search (if enabled)
            if search_enabled and len(spotify_df) > 0:
                with st.spinner(f"🔍 Searching YouTube Music for {len(spotify_df)} tracks..."):
                    # Create YouTube service
                    youtube_service = YouTubeMusicService()
                    
                    # Use the service method that includes caching
                    combined_df = youtube_service.search_playlist_tracks(spotify_df, top_results=max_results_per_track)
                    
                    # Store results in session state
                    st.session_state.search_results = combined_df
                    
                    # Calculate stats
                    total_tracks = len(combined_df)
                    youtube_matches = len(combined_df[combined_df['youtube_url'] != ''])
                    high_confidence = len(combined_df[combined_df['match_confidence'] >= confidence_threshold])
                    success_rate = (youtube_matches / total_tracks * 100) if total_tracks > 0 else 0
                    
                    # Update stats
                    with stats_placeholder.container():
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Tracks", total_tracks)
                            st.metric("YouTube Matches", youtube_matches)
                        with col_b:
                            st.metric("High Confidence", high_confidence)
                            st.metric("Success Rate", f"{success_rate:.1f}%")
                    
                    st.success(f"🎯 Found YouTube Music matches for {youtube_matches}/{total_tracks} tracks")
                    
                    # Display results
                    display_results(combined_df, confidence_threshold, show_thumbnails, include_thumbnails_export, playlist_info)
                    
            else:
                # Only Spotify data - store in session state
                st.session_state.search_results = spotify_df
                display_spotify_only_results(spotify_df, playlist_info)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
            # Show troubleshooting info
            with st.expander("🔧 Troubleshooting"):
                st.write("**Common issues:**")
                st.write("- Make sure the playlist is public")
                st.write("- Check that your Spotify credentials are set up correctly")
                st.write("- Verify the playlist URL format")
                st.write("- Try with a different playlist")
                
                st.write("**Need help?**")
                st.write("Check the setup guide in `docs/spotify_setup.md`")

def display_results(df: pd.DataFrame, confidence_threshold: float, show_thumbnails: bool, include_thumbnails_export: bool, playlist_info: dict):
    """Display the combined Spotify + YouTube Music results."""
    
    # Check if we should force the Export tab to be active
    if st.session_state.pending_playlist_creation or (hasattr(st.session_state, 'force_export_tab') and st.session_state.force_export_tab):
        # Show only the Export tab content when playlist creation is active
        st.subheader("📥 Export & Create Playlist")
        display_export_tab(df, confidence_threshold, include_thumbnails_export, playlist_info)
        return
    
    # Tabs for different views with session state
    tab_names = ["🎵 All Results", "🎯 High Confidence", "📊 Data Table", "📥 Export"]
    
    # Create tabs and get the selected one
    selected_tab = st.tabs(tab_names)
    
    # Tab 1: All Results
    with selected_tab[0]:
        st.subheader("🎵 All Track Matches")
        display_track_cards(df, show_all=True, include_thumbnails=show_thumbnails)
    
    # Tab 2: High Confidence
    with selected_tab[1]:
        st.subheader(f"🎯 High Confidence Matches (≥{confidence_threshold:.1f})")
        high_conf_df = df[df['match_confidence'] >= confidence_threshold]
        
        if len(high_conf_df) > 0:
            display_track_cards(high_conf_df, show_all=False, include_thumbnails=show_thumbnails)
        else:
            st.info("No high-confidence matches found. Try lowering the confidence threshold in the sidebar.")
    
    # Tab 3: Data Table
    with selected_tab[2]:
        st.subheader("📊 Complete Data Table")
        
        # Column selection
        display_columns = st.multiselect(
            "Select columns to display:",
            options=list(df.columns),
            default=['track_name', 'artist_name', 'youtube_title', 'youtube_artist', 'match_confidence', 'youtube_url']
        )
        
        if display_columns:
            st.dataframe(df[display_columns], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
    
    # Tab 4: Export
    with selected_tab[3]:
        st.subheader("📥 Export & Create Playlist")
        
        # YouTube Playlist Creation Section
        st.subheader("🎬 Create YouTube Playlist")
        
        # Check if we have YouTube matches
        youtube_matches = len(df[df['youtube_url'] != ''])
        high_conf_matches = len(df[df['match_confidence'] >= confidence_threshold])
        
        if youtube_matches > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info(f"📊 **{youtube_matches}** YouTube matches found ({high_conf_matches} high confidence)")
                st.write(f"Playlist will be created with tracks having confidence ≥ {confidence_threshold:.1f}")
            
            with col2:
                # Check if playlist creation is in progress
                button_disabled = st.session_state.pending_playlist_creation
                button_text = "⏳ Creating Playlist..." if button_disabled else "🎬 Create YouTube Playlist"
                
                if st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
                    # Set active tab to Export and store playlist creation data
                    st.session_state.active_tab = 3  # Export tab
                    st.session_state.pending_playlist_creation = True
                    st.session_state.playlist_creation_data = {
                        'tracks_df': df,
                        'playlist_name': playlist_info['name'],
                        'confidence_threshold': confidence_threshold
                    }
                    st.rerun()
        
            # Handle pending playlist creation or show results
            if st.session_state.pending_playlist_creation and st.session_state.playlist_creation_data:
                # Create YouTube playlist
                result = create_youtube_playlist_streamlit(
                    tracks_df=st.session_state.playlist_creation_data['tracks_df'],
                    playlist_name=st.session_state.playlist_creation_data['playlist_name'],
                    confidence_threshold=st.session_state.playlist_creation_data['confidence_threshold']
                )
                
                if result['success']:
                    st.success("🎉 YouTube playlist created successfully!")
                    
                    # Clear pending state but keep active tab as Export
                    st.session_state.pending_playlist_creation = False
                    st.session_state.playlist_creation_data = None
                    st.session_state.active_tab = 3  # Stay on Export tab
                    
                    # Display results
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Tracks Added", result['tracks_added'])
                    with col_b:
                        st.metric("Tracks Skipped", result['tracks_skipped'])
                    with col_c:
                        st.metric("Success Rate", f"{(result['tracks_added']/result['tracks_attempted']*100):.1f}%" if result['tracks_attempted'] > 0 else "0%")
                    
                    # Playlist link
                    st.markdown(f"🔗 **[Open Your Playlist]({result['playlist_url']})**")
                    st.caption("Playlist is private but shareable with this link")
                    
                    # Show failed tracks if any
                    if result['tracks_failed'] > 0:
                        with st.expander(f"⚠️ {result['tracks_failed']} tracks failed to add"):
                            for failed_track in result['failed_tracks']:
                                st.write(f"• {failed_track['artist_name']} - {failed_track['track_name']}")
                
                elif result['error'] != 'Authentication required':
                    # Clear pending state on error (except auth required)
                    st.session_state.pending_playlist_creation = False
                    st.session_state.playlist_creation_data = None
                    st.error(f"❌ Failed to create playlist: {result['error']}")
        
        else:
            st.warning("⚠️ No YouTube matches found. Cannot create playlist.")
        
        st.divider()
        
        # File Export Section
        st.subheader("📁 File Export")
        
        # Prepare export data
        export_df = df.copy()
        if not include_thumbnails_export:
            export_df = export_df.drop('youtube_thumbnail', axis=1, errors='ignore')
        
        # CSV download
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"{playlist_info['name'].replace(' ', '_')}_with_youtube.csv",
            mime="text/csv"
        )
        
        # High confidence only
        high_conf_df = export_df[export_df['match_confidence'] >= confidence_threshold]
        if len(high_conf_df) > 0:
            high_conf_csv = high_conf_df.to_csv(index=False)
            st.download_button(
                label="🎯 Download High Confidence Only",
                data=high_conf_csv,
                file_name=f"{playlist_info['name'].replace(' ', '_')}_high_confidence.csv",
                mime="text/csv"
            )
        
        # YouTube URLs only (for playlist creation)
        youtube_urls = export_df[export_df['youtube_url'] != '']['youtube_url'].tolist()
        if youtube_urls:
            urls_text = '\n'.join(youtube_urls)
            st.download_button(
                label="🔗 Download YouTube URLs Only",
                data=urls_text,
                file_name=f"{playlist_info['name'].replace(' ', '_')}_youtube_urls.txt",
                mime="text/plain"
            )

def display_spotify_only_results(df: pd.DataFrame, playlist_info: dict):
    """Display Spotify-only results when YouTube search is disabled."""
    
    st.subheader("📋 Spotify Playlist Tracks")
    
    # Display tracks
    for idx, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{row['track_name']}**")
                st.write(f"👤 {row['artist_name']}")
                st.write(f"💿 {row['album_name']}")
            
            with col2:
                st.link_button("🎵 Open in Spotify", row['spotify_url'])
    
    # Export
    st.subheader("📥 Export")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📄 Download as CSV",
        data=csv,
        file_name=f"{playlist_info['name'].replace(' ', '_')}_spotify_only.csv",
        mime="text/csv"
    )

def display_export_tab(df: pd.DataFrame, confidence_threshold: float, include_thumbnails_export: bool, playlist_info: dict):
    """Display the Export tab content."""
    
    # YouTube Playlist Creation Section
    st.subheader("🎬 Create YouTube Playlist")
    
    # Check if we have YouTube matches
    youtube_matches = len(df[df['youtube_url'] != ''])
    high_conf_matches = len(df[df['match_confidence'] >= confidence_threshold])
    
    if youtube_matches > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"📊 **{youtube_matches}** YouTube matches found ({high_conf_matches} high confidence)")
            st.write(f"Playlist will be created with tracks having confidence ≥ {confidence_threshold:.1f}")
        
        with col2:
            # Check if playlist creation is in progress
            button_disabled = st.session_state.pending_playlist_creation
            button_text = "⏳ Creating Playlist..." if button_disabled else "🎬 Create YouTube Playlist"
            
            if st.button(button_text, type="primary", use_container_width=True, disabled=button_disabled):
                # Store playlist creation data and trigger creation
                st.session_state.pending_playlist_creation = True
                st.session_state.playlist_creation_data = {
                    'tracks_df': df,
                    'playlist_name': playlist_info['name'],
                    'confidence_threshold': confidence_threshold
                }
                st.rerun()
    
        # Handle pending playlist creation or show results
        if st.session_state.pending_playlist_creation and st.session_state.playlist_creation_data:
            # Create YouTube playlist
            result = create_youtube_playlist_streamlit(
                tracks_df=st.session_state.playlist_creation_data['tracks_df'],
                playlist_name=st.session_state.playlist_creation_data['playlist_name'],
                confidence_threshold=st.session_state.playlist_creation_data['confidence_threshold']
            )
            
            if result['success']:
                st.success("🎉 YouTube playlist created successfully!")
                
                # Clear pending state
                st.session_state.pending_playlist_creation = False
                st.session_state.playlist_creation_data = None
                
                # Display results
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Tracks Added", result['tracks_added'])
                with col_b:
                    st.metric("Tracks Skipped", result['tracks_skipped'])
                with col_c:
                    st.metric("Success Rate", f"{(result['tracks_added']/result['tracks_attempted']*100):.1f}%" if result['tracks_attempted'] > 0 else "0%")
                
                # Playlist link
                st.markdown(f"🔗 **[Open Your Playlist]({result['playlist_url']})**")
                st.caption("Playlist is private but shareable with this link")
                
                # Show failed tracks if any
                if result['tracks_failed'] > 0:
                    with st.expander(f"⚠️ {result['tracks_failed']} tracks failed to add"):
                        for failed_track in result['failed_tracks']:
                            st.write(f"• {failed_track['artist_name']} - {failed_track['track_name']}")
                
                # Add button to return to normal tabs
                if st.button("📋 Back to All Results", use_container_width=True):
                    if hasattr(st.session_state, 'force_export_tab'):
                        del st.session_state.force_export_tab
                    st.rerun()
            
            elif result['error'] != 'Authentication required':
                # Clear pending state on error (except auth required)
                st.session_state.pending_playlist_creation = False
                st.session_state.playlist_creation_data = None
                st.error(f"❌ Failed to create playlist: {result['error']}")
    
    else:
        st.warning("⚠️ No YouTube matches found. Cannot create playlist.")
    
    st.divider()
    
    # File Export Section
    st.subheader("📁 File Export")
    
    # Prepare export data
    export_df = df.copy()
    if not include_thumbnails_export:
        export_df = export_df.drop('youtube_thumbnail', axis=1, errors='ignore')
    
    # CSV download
    csv = export_df.to_csv(index=False)
    st.download_button(
        label="📄 Download as CSV",
        data=csv,
        file_name=f"{playlist_info['name'].replace(' ', '_')}_with_youtube.csv",
        mime="text/csv"
    )
    
    # High confidence only
    high_conf_df = export_df[export_df['match_confidence'] >= confidence_threshold]
    if len(high_conf_df) > 0:
        high_conf_csv = high_conf_df.to_csv(index=False)
        st.download_button(
            label="🎯 Download High Confidence Only",
            data=high_conf_csv,
            file_name=f"{playlist_info['name'].replace(' ', '_')}_high_confidence.csv",
            mime="text/csv"
        )
    
    # YouTube URLs only (for playlist creation)
    youtube_urls = export_df[export_df['youtube_url'] != '']['youtube_url'].tolist()
    if youtube_urls:
        urls_text = '\n'.join(youtube_urls)
        st.download_button(
            label="🔗 Download YouTube URLs Only",
            data=urls_text,
            file_name=f"{playlist_info['name'].replace(' ', '_')}_youtube_urls.txt",
            mime="text/plain"
        )

def display_track_cards(df: pd.DataFrame, show_all: bool = True, include_thumbnails: bool = False):
    """Display track results as cards."""
    
    if len(df) == 0:
        st.info("No tracks to display")
        return
    
    for idx, row in df.iterrows():
        with st.container():
            # Create columns for layout
            if include_thumbnails and row.get('youtube_thumbnail_local'):
                col1, col2, col3 = st.columns([1, 4, 2])
                with col1:
                    try:
                        st.image(row['youtube_thumbnail_local'], width=80)
                    except Exception:
                        st.write("🎵")
            else:
                col1, col2, col3 = st.columns([1, 4, 2])
                with col1:
                    st.write("🎵")
            
            with col2:
                # Track info
                st.write(f"**{row['track_name']}**")
                st.write(f"👤 {row['artist_name']} • 💿 {row['album_name']}")
                
                # YouTube match info
                if row['youtube_url']:
                    confidence_color = "🟢" if row['match_confidence'] >= 0.7 else "🟡" if row['match_confidence'] >= 0.4 else "🔴"
                    st.write(f"{confidence_color} **YouTube:** {row['youtube_title']} - {row['youtube_artist']}")
                    if row['youtube_duration']:
                        st.write(f"⏱️ {row['youtube_duration']}")
                else:
                    st.write("❌ No YouTube Music match found")
            
            with col3:
                # Action buttons
                st.link_button("🎵 Spotify", row['spotify_url'], use_container_width=True)
                if row['youtube_url']:
                    st.link_button("📺 YouTube Music", row['youtube_url'], use_container_width=True)
                
                # Match confidence
                if row['youtube_url']:
                    st.metric("Match", f"{row['match_confidence']:.2f}")
        
        st.divider()

if __name__ == "__main__":
    main()
