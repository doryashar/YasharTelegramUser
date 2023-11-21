## 1
import cv2
import os
import numpy as np
from skimage import metrics

def structural_similarity(image1, image2):
    
    if os.path.exists(image1):
        image1 = cv2.imread(image1)
    else: #TODO: if isinstance(image1, bytes)
        jpg_as_np = np.frombuffer(image1, dtype=np.uint8)
        image1 = cv2.imdecode(jpg_as_np, flags=1)
    
    if os.path.exists(image2):
        image2 = cv2.imread(image2)
    else: #TODO: if isinstance(image1, bytes)
        jpg_as_np = np.frombuffer(image2, dtype=np.uint8)
        image2 = cv2.imdecode(jpg_as_np, flags=1)
    
    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]), interpolation = cv2.INTER_AREA)
    # print(image1.shape, image2.shape)
    # Convert images to grayscale
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # Calculate SSIM
    ssim_score = metrics.structural_similarity(image1_gray, image2_gray, full=True)
    return round(ssim_score[0], 2)

# for first in [112]:
#     for second in range(6):
#         image1 = f'./media/{first}.jpg'
#         image2 = f'./media/{second+111}.jpg'
#         if image1 == image2:
#             continue
#         print(f'{image1} / {image2}')
#         firstcompare(image1, image2)
"""
## 2
import cv2
# Load images
image1 = cv2.imread(image1)
image2 = cv2.imread(image2)
hist_img1 = cv2.calcHist([image1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
hist_img1[255, 255, 255] = 0 #ignore all white pixels
cv2.normalize(hist_img1, hist_img1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
hist_img2 = cv2.calcHist([image2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
hist_img2[255, 255, 255] = 0  #ignore all white pixels
cv2.normalize(hist_img2, hist_img2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
# Find the metric value
metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_CORREL)
print(f"Similarity Score: ", round(metric_val, 2))
# Similarity Score: 0.94


## 3
# !pip install git+https://github.com/openai/CLIP.git
# !pip install open_clip_torch
# !pip install sentence_transformers

import torch
import open_clip
import cv2
from sentence_transformers import util
from PIL import Image
# image processing model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-16-plus-240', pretrained="laion400m_e32")
model.to(device)
def imageEncoder(img):
    img1 = Image.fromarray(img).convert('RGB')
    img1 = preprocess(img1).unsqueeze(0).to(device)
    img1 = model.encode_image(img1)
    return img1
def generateScore(image1, image2):
    test_img = cv2.imread(image1, cv2.IMREAD_UNCHANGED)
    data_img = cv2.imread(image2, cv2.IMREAD_UNCHANGED)
    img1 = imageEncoder(test_img)
    img2 = imageEncoder(data_img)
    cos_scores = util.pytorch_cos_sim(img1, img2)
    score = round(float(cos_scores[0][0])*100, 2)
    return score
print(f"similarity Score: ", round(generateScore(image1, image2), 2))
#similarity Score: 76.77

"""