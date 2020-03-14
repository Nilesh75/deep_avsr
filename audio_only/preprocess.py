import os
from tqdm import tqdm

from config import args
from utils.preprocessing import preprocess_sample



#walking through the data directory and obtaining a list of all files in the dataset
filesList = list()
for root, dirs, files in os.walk(args["DATA_DIRECTORY"]):
    for file in files:
        if file.endswith(".mp4"):
            filesList.append(os.path.join(root, file[:-4]))

#Preprocessing each sample
print("\nNumber of data samples to be processed = %d\n" %(len(filesList)))
print("\nStarting preprocessing ....\n")

for file in tqdm(filesList):
    preprocess_sample(file)

print("\nPreprocessing Done.\n")