import pytesseract
from pytesseract import Output
from tqdm import tqdm
import cv2
import os
import matplotlib.pyplot as plt

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
    plt.title("Intensities in Clips in order")
    plt.show()

def screen_blend(A, B):
    return 1 - (1 - A) * (1 - B)