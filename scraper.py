# scraper.py
import requests
import os
API_KEY = os.environ.get("YOUTUBE_API_KEY")

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return None

def scrape_comments(video_url, max_comments=100):
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")

    # Get video title
    video_title = "Unknown Video"
    channel_name = "Unknown Channel"
    video_api_url = "https://www.googleapis.com/youtube/v3/videos"
    video_params = {
        "part": "snippet",
        "id": video_id,
        "key": API_KEY
    }

    video_response = requests.get(video_api_url, params=video_params)
    if video_response.status_code == 200:
        video_data = video_response.json()
        items = video_data.get("items")
        if items:
            video_title = items[0]["snippet"]["title"]
            channel_name = items[0]["snippet"]["channelTitle"]
    else:
        print("Warning: Could not fetch video title")

    # Get comments
    comment_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    comment_params = {
        "part": "snippet",
        "videoId": video_id,
        "key": API_KEY,
        "maxResults": 100,
        "textFormat": "plainText"
    }

    response = requests.get(comment_url, params=comment_params)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    comments = []
    data = response.json()
    for item in data.get("items", []):
        top_comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(top_comment)
        if len(comments) >= max_comments:
            break

    return video_id, comments, video_title, channel_name