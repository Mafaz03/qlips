from scenedetect import VideoManager
from moviepy.editor import VideoFileClip, AudioFileClip
from pytube import YouTube
import cv2
import pytube
import numpy as np
import os
from pytube import YouTube
from slugify import slugify
import logging
import ssl


def download_media(url, foldername, resolution, audio=None):
    
    yt = YouTube(url)
    filename = slugify(yt.title)

    resolution_map = {
        "1080p": "1080p",
        "720p": "720p",
        "480p": "480p",
        "360p": "360p",
        "240p": "240p",
        "144p": "144p",
        "4K": "2160p"
    }

    selected_resolution = resolution_map.get(resolution, "1080p")
    
    if audio is None:
        # Download both audio and video
        video_stream = yt.streams.filter(file_extension='mp4', res=selected_resolution).first()
        if not video_stream:
            raise Exception(f"No suitable video stream found for resolution {resolution}")
        video_path = os.path.join(foldername, filename + ".mp4")
        video_stream.download(output_path=foldername, filename=filename + ".mp4")

        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No suitable audio stream found")
        audio_path = os.path.join(foldername, filename + "_audio.mp4")
        audio_stream.download(output_path=foldername, filename=filename + "_audio.mp4")
        
        return video_path, audio_path

    elif audio:
        # Download audio only
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            raise Exception("No suitable audio stream found")
        audio_path = os.path.join(foldername, filename + "_audio.mp4")
        audio_stream.download(output_path=foldername, filename=filename + "_audio.mp4")
        return audio_path

    else:
        # Download video only
        video_stream = yt.streams.filter(file_extension='mp4', res=selected_resolution, only_video=True).first()
        if not video_stream:
            raise Exception(f"No suitable video stream found for resolution {resolution}")
        video_path = os.path.join(foldername, filename + ".mp4")
        video_stream.download(output_path=foldername, filename=filename + ".mp4")
        return video_path

def merge_audio_video(video_path, audio_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

def download_main(urls, foldername, resolution, audio=None):
    os.makedirs(foldername, exist_ok=True)
    if not isinstance(urls, list): urls = [urls]
    for url in urls:
        try:
            if audio is None:
                video_path, audio_path = download_media(url, foldername, resolution, audio)
                print(f"Downloaded video to {video_path} and audio to {audio_path}")

                # Merge audio and video
                merged_path = os.path.join(foldername, slugify(YouTube(url).title) + "_merged.mp4")
                merge_audio_video(video_path, audio_path, merged_path)
                os.remove(foldername + '/' + slugify(YouTube(url).title) + "_audio.mp4")
                os.remove(foldername + '/' + slugify(YouTube(url).title) + ".mp4")
                os.rename(foldername + '/' + slugify(YouTube(url).title) + "_merged.mp4", foldername + '/' + slugify(YouTube(url).title) + ".mp4")
                print(f"Merged video and audio to {merged_path}")

            elif audio:
                audio_path = download_media(url, foldername, resolution, audio)
                print(f"Downloaded audio to {audio_path}")
            else:
                video_path = download_media(url, foldername, resolution, audio)
                print(f"Downloaded video to {video_path}")

        except Exception as e:
            print(f"An error occurred: {e}")


