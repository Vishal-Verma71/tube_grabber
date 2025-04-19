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

# Inject custom CSS for styling
st.markdown(
    """
    <style>
        h1 {
            color: #ff5733;
            font-size: 40px;
            font-weight: bold;
            text-align: center;
        }
        h2 {
            color: #FFFF00;
            font-size: 30px;
            font-weight: bold;
        }
        h3 {
            color: #ff33a8;
            font-size: 18px;
        }
        p {
            color: #27ae60;
            font-size: 18px;
            font-weight: bold;
        }
        .stRadio > label {
            font-size: 18px;
            font-weight: bold;
            color: #d35400;
        }
        div.stButton > button {
            background-color: #3498db;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px;
            width: 220px;
        }
        div.stTextInput > label {
            font-size: 20px;
            font-weight: bold;
            color: darkblue;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# App title
st.markdown("<h1>YouTube Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p>Search for a YouTube video, select resolution, and download it.</p>", unsafe_allow_html=True)

# Input for video search
search_query = st.text_input("🔍 Enter the video name:")

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_video_index' not in st.session_state:
    st.session_state.selected_video_index = None
if 'selected_resolution' not in st.session_state:
    st.session_state.selected_resolution = None  # Store resolution choice

# Reset search results when a new search query is entered
if search_query and search_query != st.session_state.get('last_search_query'):
    st.session_state.search_results = None
    st.session_state.last_search_query = search_query

if search_query:
    if st.session_state.search_results is None:
        st.session_state.search_results = search_yt(search_query)

    data = st.session_state.search_results
    
    if data:
        st.markdown("<h2>🎥 Search Results:</h2>", unsafe_allow_html=True)
        
        # Display radio button choices for video selection
        video_options = {f"{v[1]}": i for i, v in data.items()}  # {title: index}
        selected_video_title = st.radio("🎬 Choose a video:", list(video_options.keys()))

        # Store selected video index
        st.session_state.selected_video_index = video_options[selected_video_title]

        # Get selected video link
        selected_index = st.session_state.selected_video_index
        link = data[selected_index][0]
        yt = YouTube(link, use_oauth=False, allow_oauth_cache=True)

        # Get available resolutions
        available_resolutions = sorted(
            list(set([stream.resolution for stream in yt.streams.filter(file_extension='mp4', only_video=True) if stream.resolution])),
            reverse=True  # Sort from highest to lowest resolution
        )

        # Ensure resolutions are available
        if available_resolutions:
            st.markdown("<h2>📺 Available Resolutions:</h2>", unsafe_allow_html=True)

            # Radio button for resolution selection
            chosen_resolution = st.radio("🎯 Select a resolution:", available_resolutions)

            # Store selected resolution
            st.session_state.selected_resolution = chosen_resolution

            # Download button
            if st.button("📥 Download Now"):
                video_stream = yt.streams.filter(file_extension='mp4', resolution=chosen_resolution, only_video=True).first()
                audio_stream = yt.streams.filter(only_audio=True).first()

                # Simulated progress bars
                st.markdown("<h3>⏳ Wait kar... Video download ho raha hai...</h3>", unsafe_allow_html=True)
                video_progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    video_progress.progress(i + 1)
                video_file = video_stream.download(output_path=SAVE_PATH, filename="temp_vid")
                st.markdown("<h3>✅ Video download ho gaya!</h3>", unsafe_allow_html=True)

                st.markdown("<h3>⏳ Wait kar... Audio download ho raha hai...</h3>", unsafe_allow_html=True)
                audio_progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    audio_progress.progress(i + 1)
                audio_file = audio_stream.download(output_path=SAVE_PATH, filename="temp_aud")
                st.markdown("<h3>✅ Audio bhi download ho gaya!</h3>", unsafe_allow_html=True)

                # Set output file path
                output_file = os.path.join(SAVE_PATH, yt.title + "Mixed.mp4")

                # Merge video and audio using ffmpeg
                st.markdown("<h3>⏳ Bas thoda aur wait... Video aur audio merge ho raha hai...</h3>", unsafe_allow_html=True)
                os.system(f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"')

                st.success("🎉 Download complete ho gaya! Ja sun le aur maje kar! 😎")
        else:
            st.markdown("<h3 style='color: red;'>🚨 No available resolutions found.</h3>", unsafe_allow_html=True)
