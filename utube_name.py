import os
import re
import requests as r
from pytubefix import YouTube
import streamlit as st
from urllib.parse import quote_plus as encode
import time  # For simulating download progress

# Path to save the downloaded files
SAVE_PATH = r"C:\Users\Vishal Verma\Downloads\songs"

# Base URL for YouTube search
base = "https://www.youtube.com/results?search_query="

# Function to search YouTube for videos
def search_yt(query: str):
    global base
    query = encode(query)
    url = base + query
    resp = r.get(url)
    pattern = r'videoId":"([^"]+)","thumbnail":{"thumbnails":\[{"url":"[^"]+","width":\d+,"height":\d+},{"url":"[^"]+","width":\d+,"height":\d+\}\]\},"title":\{"runs":\[{\"text":"([^"]+)'
    result = re.findall(pattern, resp.text)
    data = {i: [f"https://www.youtube.com/watch?v={v[0]}", v[1]] for i, v in enumerate(result)}
    return data

# Streamlit app
st.title("YouTube Downloader")
st.write("Search for a YouTube video, select resolution, and download with audio.")

# Input for video search
search_query = st.text_input("Enter the video name:")

# Initialize session state to store search results and video index
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'video_index' not in st.session_state:
    st.session_state.video_index = 0  # Default index

# Reset search results when a new video name is entered
if search_query and search_query != st.session_state.get('last_search_query'):
    st.session_state.search_results = None
    st.session_state.last_search_query = search_query

if search_query:
    # Perform search only if search results are not already stored
    if st.session_state.search_results is None:
        st.session_state.search_results = search_yt(search_query)

    # Display search results
    data = st.session_state.search_results
    
    if data:
        st.write("Search Results:")
        for i, v in enumerate(data.values()):
            st.write(f"{i+1} :-> {v[1]}")
        
        # Control buttons for video index selection
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Minus"):
                if st.session_state.video_index > 0:
                    st.session_state.video_index -= 1

        with col2:
            st.write(f"Selected video: {st.session_state.video_index + 1}")

        with col3:
            if st.button("Plus"):
                if st.session_state.video_index < len(data) - 1:
                    st.session_state.video_index += 1

        # Use the selected video index to fetch the video link
        link = data[st.session_state.video_index][0]
        yt = YouTube(link)

        # Get available resolutions
        available_resolutions = list(set([stream.resolution for stream in yt.streams.filter(file_extension='mp4', only_video=True) if stream.resolution]))

        # Display available resolutions
        st.write("Available resolutions:")
        for i, res in enumerate(available_resolutions, start=1):
            st.write(f"{i}. {res}")
        
        # Input for choosing resolution
        choice = st.number_input("Enter the number corresponding to your preferred resolution:", min_value=1, max_value=len(available_resolutions), value=1, step=1)
        chosen_resolution = available_resolutions[choice - 1]

        if st.button("Download"):
            # Get the video stream with the chosen resolution
            video_stream = yt.streams.filter(file_extension='mp4', resolution=chosen_resolution, only_video=True).first()

            # Get the audio stream (highest quality audio)
            audio_stream = yt.streams.filter(only_audio=True).first()

            # Progress bars for video and audio downloads
            st.write("Downloading video...")
            video_progress = st.progress(0)
            for i in range(100):  # Simulating progress for video download
                time.sleep(0.03)
                video_progress.progress(i + 1)
            video_file = video_stream.download(output_path=SAVE_PATH, filename="temp_vid")
            st.write("Video downloaded.")

            st.write("Downloading audio...")
            audio_progress = st.progress(0)
            for i in range(100):  # Simulating progress for audio download
                time.sleep(0.03)
                audio_progress.progress(i + 1)
            audio_file = audio_stream.download(output_path=SAVE_PATH, filename="temp_aud")
            st.write("Audio downloaded.")

            # Set output file path
            output_file = os.path.join(SAVE_PATH, yt.title + "Mixed.mp4")

            # Combine video and audio using ffmpeg (ensure ffmpeg is installed)
            st.write("Merging video and audio...")
            os.system(f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"')
            st.success('Download complete!')














