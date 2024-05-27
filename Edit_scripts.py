import os
from tqdm import tqdm
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from Calculations import *

# def create_video_only_edit(intensities, Output_folder, edit_name = "demo", total_duration = 180, temp_dir = "Temp"):
#     os.makedirs(Output_folder, exist_ok=True)
#     temp_video_paths = []
#     accumulated_duration = 0

#     for i in intensities:
#         clip_path = f"{temp_dir}/cut{i[0]}.mp4"
#         if os.path.exists(clip_path):
#             clip = VideoFileClip(clip_path)
#             remaining_duration = total_duration - accumulated_duration
#             if accumulated_duration + clip.duration > total_duration:
#                 clip = clip.subclip(0, remaining_duration)
#             accumulated_duration += clip.duration
#             temp_filename = f"{temp_dir}/temp_clip_{i[0]}.mp4"
#             clip.write_videofile(temp_filename, codec="libx264", audio_codec="aac", fps=clip.fps)
#             temp_video_paths.append(temp_filename)
#             if accumulated_duration >= total_duration:
#                 break

#     with open("temp_videos.txt", "w") as f:
#         for temp_video_path in temp_video_paths:
#             f.write(f"file '{temp_video_path}'\n")

#     os.system(f"ffmpeg -f concat -safe 0 -i temp_videos.txt -c copy {Output_folder+'/'+edit_name}.mp4")

#     os.remove("temp_videos.txt")
#     for temp_video_path in temp_video_paths:
#         os.remove(temp_video_path)

def create_video_only_edit(intensities, Output_folder, edit_name="demo", total_duration=180, temp_dir="Temp"):
    os.makedirs(Output_folder, exist_ok=True)
    temp_video_paths = []
    accumulated_duration = 0

    for i in intensities:
        clip_path = f"{temp_dir}/cut{i[0]}.mp4"
        if os.path.exists(clip_path):
            clip = VideoFileClip(clip_path)
            fps = clip.fps  # Save the original fps to maintain consistency
            remaining_duration = total_duration - accumulated_duration
            if accumulated_duration + clip.duration > total_duration:
                clip = clip.subclip(0, remaining_duration)
            accumulated_duration += clip.duration
            temp_filename = f"{temp_dir}/temp_clip_{i[0]}.mp4"
            clip.write_videofile(temp_filename, codec="libx264", audio_codec="aac", fps=fps)
            temp_video_paths.append(temp_filename)
            if accumulated_duration >= total_duration:
                break

    # Concatenate all the temporary video clips
    final_clips = [VideoFileClip(path) for path in temp_video_paths]
    final_video = concatenate_videoclips(final_clips)
    
    # Output the final edited video
    output_path = os.path.join(Output_folder, f"{edit_name}.mp4")
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=fps)



def overlay_videos(BaseVideoPath, OverlayVideoPath, outputfolder = "Temp_edits", output_name = "Demo_overlay"):
    os.makedirs(outputfolder, exist_ok=True)
    output_path = outputfolder + '/' + output_name
    video1_clip = VideoFileClip(OverlayVideoPath)
    video2_clip = VideoFileClip(BaseVideoPath)
    
    # Ensure both clips have the same duration
    min_duration = min(video1_clip.duration, video2_clip.duration)
    video1_clip = video1_clip.subclip(0, min_duration)
    video2_clip = video2_clip.subclip(0, min_duration)
    
    # Loop over frames, blend and save
    frame_width = video1_clip.size[0]
    frame_height = video1_clip.size[1]
    fps = video1_clip.fps
    
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
    
    for t in tqdm(np.arange(0, min_duration, 1/fps)):
        frame1 = video1_clip.get_frame(t)
        frame2 = video2_clip.get_frame(t)
        
        frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)
        frame2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2BGR)
        
        frame1 = frame1.astype(np.float32) / 255
        frame2 = frame2.astype(np.float32) / 255
        
        blended_frame = screen_blend(frame1, frame2)
        blended_frame = (blended_frame * 255).astype(np.uint8)
        
        out.write(blended_frame)
    
    out.release()
    print("The videos have been overlaid and saved to", output_path)


def merge_audio_with_video(BaseVideoPath, AudioFilePath, OutputFolder, Output_name, duration = np.inf):
    os.makedirs(OutputFolder, exist_ok=True)
    video_clip = VideoFileClip(BaseVideoPath)
    audio_clip = AudioFileClip(AudioFilePath)

    min_duration = min(video_clip.duration, audio_clip.duration, duration)
    video_clip = video_clip.subclip(0, min_duration)
    audio_clip = audio_clip.subclip(0, min_duration)

    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(OutputFolder+'/'+Output_name+".mp4", codec='libx264', audio_codec='aac')
    print(f"The videos and audios have been merged and saved to {OutputFolder+'/'+Output_name}.mp4")