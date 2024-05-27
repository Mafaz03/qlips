import pytesseract
from pytesseract import Output
from tqdm import tqdm
import cv2
import os
import matplotlib.pyplot as plt
import numpy as nd
import pandas as pd

def calc_intensities(folder = "Temp", noisify = 3, every = 2, remove_clips_with_text = True ,every_text = 20, confidence = 20):
    """
    every: Finds rate of absolute change between `every` frame of the clip
    every_text: Checks if text is present in `every_text` frame of the clip
    confidence: confidence of text existing
    """
    intensities = {}
    for i, cut in enumerate(tqdm(os.listdir(folder))):
        intensity = []
        cap = cv2.VideoCapture(f"{folder}/{cut}")
        if not cap.isOpened():
            raise Exception("Error opening video file")
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        time_elapsed = 1 / frame_rate 
        count = 0
        while cap.isOpened():
            ret, frame = cap.read(cv2.IMREAD_GRAYSCALE)
            if not ret: break
            if i == 0: height, width = frame.shape[:2]
            frame = cv2.resize(frame, (int(width/noisify), int(height/noisify)), interpolation=cv2.INTER_LINEAR)
            if remove_clips_with_text:
                if count % every_text == 0:
                    data = pytesseract.image_to_data(frame, output_type=Output.DICT)
                    data_text = ''.join(data["text"])
                    if len(data_text) != 0:
                        confidences = data['conf']
                        conf = sum(confidences) / len(confidences)
                        if conf > confidence:
                            print(cut, data_text, conf)
                            os.remove(f"{folder}/{cut}")
                            break
            
            if count % every == 0:
                ret, frame_old = cap.read(cv2.IMREAD_GRAYSCALE)
                if not ret: break
                frame_old = cv2.resize(frame_old, (int(width/noisify), int(height/noisify)), interpolation=cv2.INTER_LINEAR)
            frame_sub = cv2.absdiff(frame_old, frame)
            new_frame = (frame_sub - (255/2))/(255 /2)
            intensity.append(new_frame.sum())
            count += 1
        intensities[int(cut.split('.')[0].removeprefix("cut"))] = sum(intensity)

    intensities_sorted = sorted(intensities.items(), key=lambda x: x[1], reverse=True)
    intensities_sorted = [i for i in intensities_sorted if i[1] != 0]
    intensities_sorted
    return intensities_sorted

def plot_inten(intensities):
    plt.plot([i[-1] for i in intensities])
    plt.xlabel("Clip number")
    plt.ylabel("intensity")
    plt.title("Intensities of Clips in order")
    plt.show()


def screen_blend(A, B):
    return 1 - (1 - A) * (1 - B)

import cv2
import numpy as np

def pad_to_shape(array, target_shape):
    pad_height = target_shape[0] - array.shape[0]
    pad_width = target_shape[1] - array.shape[1]
    
    # Calculate padding for height and width, evenly distributed
    pad_top = pad_height // 2
    pad_bottom = pad_height - pad_top
    pad_left = pad_width // 2
    pad_right = pad_width - pad_left
    
    # Apply padding
    padded_array = np.pad(array, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)), mode='constant')
    return padded_array

def set_to_res(input_video_path, output_video_path=None, target_shapes = [(1080, 1920, 3), (1280, 720, 3), (3840, 2160, 3)], inplace = True):

    if output_video_path is None: output_video_path = input_video_path.split(".mp4")[0] + "_reshaped" + ".mp4"
    cap = cv2.VideoCapture(input_video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if (frame_height, frame_width, 3) not in target_shapes:
        res = (frame_height, frame_width, 3)
        diff = [abs((np.array(res) - np.array(i)).sum()) for i in target_shapes]
        target_shape = target_shapes[diff.index(min(diff))]
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (target_shape[1], target_shape[0]))
        while True:
            ret, frame = cap.read()
            if not ret: break
            padded_frame = pad_to_shape(frame, target_shape)
            out.write(padded_frame)
        print("Video processing complete. The output video is saved as", output_video_path)
        if inplace: os.remove(input_video_path)
        cap.release()
        out.release()
    else:
        target_shape = (frame_height, frame_width, 3)
        print(f"{input_video_path} is already meeting requiremnt")
        pass
    return [target_shape]


def filter_overlapping_scenes(scene_df):
    new = []
    prev_end = 0 
    prev_start = 0 

    for i in range(scene_df.shape[0]):
        start = scene_df.iloc[i]["Scene start"]
        end = scene_df.iloc[i]["Scene end"]
        video_title = int(scene_df.iloc[i]["Video title"])

        if i == 0:
            prev_end = end
            prev_start = start
            new.append([video_title, start, end, end - start])
        else:
            if start >= prev_end or start <= prev_start:
                new.append([video_title, start, end, end - start])
                prev_end = end
                prev_start = start

    filtered_scene_df = pd.DataFrame(new, columns=["Video title", "Scene start", "Scene end", "Duration"])
    return filtered_scene_df

