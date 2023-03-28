import youtube_dl
import speech_recognition as sr
import time
import yt_dlp
import os
import shutil
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

def add_ffmpeg_to_path():
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        current_path = os.environ['PATH']
        if ffmpeg_dir not in current_path:
            os.environ['PATH'] = f"{ffmpeg_dir};{current_path}"

def download_audio(youtube_url):
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav', 'preferredquality': '192',}], 'outtmpl': 'audio.%(ext)s'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    print("Download complete.")

def transcribe_audio():
    r = sr.Recognizer()
    block_length = 10  # duration of each block in seconds
    #total_duration = 39 * 60  # total duration in seconds (27 minutes) - for matches that start at 12 mins
    total_duration = 34 * 60  # total duration in seconds (27 minutes) - for matches that start at 8 mins

    # Keywords related to attacking and scoring
    attacking_keywords = [
    'attack', 'shot', 'shoot', 'chance', 'goal', 'score', 'cross', 'corner', 'opportunity',
    'header', 'free kick', 'penalty', 'assist', 'counterattack', 'break', 'through ball',
    'one-on-one', 'foul', 'possession', 'build-up', 'dangerous', 'in the box', 'finish',
    'goal-bound', 'strike', 'long range', 'volley', 'target', 'pressure', 'offensive',
    'forward', 'clearance', 'threat', 'onside', 'danger', 'goalkeeper save', 'blocked shot',
    'whistle', 'set piece', 'goal line', 'goalmouth', 'scramble', 'last-ditch',
    'tackle', 'rebound', 'narrowly wide', 'post', 'crossbar', 'woodwork', 'close call'
]

    # Initialize the attacking intensity score
    attacking_intensity = 0

    for start_time in range(8 * 60, total_duration, block_length):#- for matches that start at 8 mins
    #for start_time in range(12 * 60, total_duration, block_length):#- for matches that start at 12 mins
        if start_time < total_duration:  # Update the loop condition
            with sr.AudioFile("audio.wav") as audio_file:
                try:
                    # Record the audio for the current block
                    audio_data = r.record(audio_file, offset=start_time, duration=block_length)

                    # Transcribe the audio data
                    response = r.recognize_google(audio_data, show_all=True)
                    if response and response.get('alternative'):
                        text = response['alternative'][0]['transcript']

                        # Calculate the attacking intensity for the current block
                        block_intensity = sum([1 for keyword in attacking_keywords if keyword in text.lower()])

                        # Find the keywords present in the text
                        found_keywords = [keyword for keyword in attacking_keywords if keyword in text.lower()]

                        # Update the total attacking intensity score
                        attacking_intensity += block_intensity


                        if block_intensity >= 1:
                            print(f"Attacking intensity at {start_time} seconds:", block_intensity)
                            print(f"Keywords found at {start_time} seconds:", ', '.join(found_keywords))    

                    else:
                        print(f"Could not understand audio at {start_time} seconds")
                except sr.UnknownValueError:
                    print(f"Could not understand audio at {start_time} seconds")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service at {start_time} seconds; {e}")
                except Exception as e:
                    print("Error occurred:", e)

    print("Total attacking intensity:", attacking_intensity)


def main():
    youtube_url = "https://www.youtube.com/watch?v=qIV_ZE8ZI7Q"

    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(youtube_url, download=False)
        video_title = video_info.get('title', None)
    
    if video_title is not None:
        team_names = video_title.split(" vs ")
        print("Team names:", team_names)
    else:
        print("Could not fetch video title")

    download_audio(youtube_url)
    transcribe_audio()

if __name__ == "__main__":
    main()
