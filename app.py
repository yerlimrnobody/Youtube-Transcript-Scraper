import requests
import re
import json
import xml.etree.ElementTree as ET

def format_time(seconds):
    """
    Converts time in seconds to a human-readable format (HH:MM:SS).
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_duration(seconds):
    """
    Converts duration in seconds to a human-readable format (SS.xx) without milliseconds.
    """
    return f"{seconds:.2f}"

def get_transcript(video_url, language_code):
    video_id = extract_video_id(video_url)
    html = fetch_video_html(video_id)
    player_response = extract_player_response(html)
    captions = get_captions(player_response)
    print(captions)
    
    if not captions:
        print("No captions available for this video.")
        return

    print("Available captions:")
    for caption in captions:
        print(f"Language: {caption['languageCode']}, Name: {caption.get('name', {}).get('simpleText', 'Unknown')}")

    # Example: Trying with English automatic captions
    selected_caption = find_caption_track(captions, language_code)
    if selected_caption:
        transcript = fetch_and_parse_transcript(selected_caption['baseUrl'])
        for entry in transcript:
            start_time = format_time(float(entry['start']))
            duration = format_duration(float(entry['duration']))
            print(f"{start_time} - {duration}: {entry['text']}")
    else:
        print(f"No captions found for language code '{language_code}'.")

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def fetch_video_html(video_id):
    """
    Fetches the HTML content of the YouTube video page.
    """
    url = f'https://www.youtube.com/watch?v={video_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    response = requests.get(url, headers=headers)
    return response.text

def extract_player_response(html):
    """
    Extracts the player response JSON from the HTML content.
    """
    regex = r'var ytInitialPlayerResponse = ({.*?});'
    match = re.search(regex, html)
    if match:
        json_data = match.group(1)
        return json.loads(json_data)
    else:
        # Try alternative pattern
        regex = r'ytInitialPlayerResponse\s*=\s*({.*?});'
        match = re.search(regex, html)
        if match:
            json_data = match.group(1)
            return json.loads(json_data)
    return None

def get_captions(player_response):
    """
    Retrieves the captions tracks from the player response.
    """
    try:
        captions = player_response['captions']['playerCaptionsTracklistRenderer']['captionTracks']
        return captions
    except KeyError:
        return None

def find_caption_track(captions, language_code):
    """
    Finds the caption track matching the desired language code.
    """
    for caption in captions:
        if caption['languageCode'] == language_code:
            return caption
    return None

def fetch_and_parse_transcript(captions_url):
    """
    Fetches the captions XML and parses it into a transcript.
    """
    response = requests.get(captions_url)
    if response.status_code != 200:
        return None

    root = ET.fromstring(response.content)
    transcript = []
    for elem in root.findall('.//text'):
        start = elem.attrib.get('start')
        dur = elem.attrib.get('dur')
        text = elem.text or ''
        transcript.append({
            'start': start,
            'duration': dur,
            'text': text.replace('\n', ' ')
        })
    return transcript

# Example usage
if __name__ == "__main__":
    video_url = input("URL : ")
    language_code = input("Pls Enter Video Language Code. Ex: en for Englist : ")
    get_transcript(video_url, language_code)