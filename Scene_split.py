import os
import datetime
import pandas as pd
from scenedetect import VideoManager
from tqdm import tqdm
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def mapper(folder):
    video_title = os.listdir(folder)
    video_title_map = {idx: video_title[idx] for idx in range(len(video_title))}
    video_title_map_rev = {video_title[idx]: idx for idx in range(len(video_title))}
    return video_title_map, video_title_map_rev

def timecode_to_seconds(timecode):
    time_object = datetime.datetime.strptime(timecode, "%H:%M:%S.%f")
    total_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second + time_object.microsecond / 1e6
    return total_seconds

def get_scene_dict(folder):
    video_title = os.listdir(folder)
    scene_dict = {}
    for video in tqdm(video_title):
        video_manager = VideoManager([f"Videos/{video}"])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        scene_dict[video] = scene_list
    return scene_dict

def get_scene_df(scene_dict, folder="Videos", clip: float = None, min_duration=2, max_duration=np.inf):
    video_title_map, video_title_map_rev = mapper(folder)
    rows = []
    
    for title in scene_dict.keys():
        scene_list = scene_dict[title]
        
        for scene in scene_list:
            start_time = timecode_to_seconds(scene[0].get_timecode())
            end_time = timecode_to_seconds(scene[1].get_timecode())
            
            if clip is not None:
                if end_time > clip:
                    duration = start_time + clip - start_time
                    if duration > min_duration and duration < max_duration:
                        row = [video_title_map_rev[title], start_time, start_time + clip]
                        rows.append(row)
                else:
                    duration = end_time - start_time
                    if duration > min_duration and duration < max_duration:
                        row = [video_title_map_rev[title], start_time, end_time]
                        rows.append(row)
            else:
                duration = end_time - start_time
                if duration > min_duration and duration < max_duration:
                    row = [video_title_map_rev[title], start_time, end_time]
                    rows.append(row)

    scene_df = pd.DataFrame(rows).rename(columns={0: "Video title", 1: "Scene start", 2: "Scene end"})
    for i in list(video_title_map.keys()): print(i, ' : ', video_title_map[i])
    scene_df["Duration"] = scene_df["Scene end"] - scene_df["Scene start"]
    return scene_df

def plot_df(df, folder = "Videos"):
    video_title_map, video_title_map_rev = mapper(folder)
    compare = df["Video title"].value_counts()
    compare_title = [video_title_map[i] for i in list(compare.keys())]
    compare_count = compare.values
    plt.bar(compare_title, compare_count)
    plt.show()

def clean_scene_on_duration(scene_df, min_duration = 2, max_duration = np.inf):
    durations = []
    for row in range(len(scene_df)):
        duration = scene_df.iloc[row]["Scene end"] - scene_df.iloc[row]["Scene start"]
        if duration > max_duration or duration < min_duration: durations.append(None)
        else: durations.append(duration)
        
    scene_df["Duration"] = durations
    scene_df_cleaned = scene_df.dropna().reset_index().drop("index", axis=1)
    return scene_df_cleaned

def split_and_store_clip(df, clipstart = 0.2, clipend = 0.2, folder = "Temp", mapfoder = "Videos"):
    video_title_map, video_title_map_rev = mapper(mapfoder)
    os.makedirs(folder, exist_ok=True)
    for i in range(len(df)):
        ffmpeg_extract_subclip(f"Videos/{video_title_map[int(df.iloc[i]['Video title'])]}", 
                            df.iloc[i]["Scene start"]+clipstart, 
                            df.iloc[i]["Scene end"]-clipend, 
                            targetname=f"Temp/cut{i}.mp4")