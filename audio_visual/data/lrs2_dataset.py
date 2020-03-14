import torch
from torch.utils.data import Dataset
from scipy.io import wavfile
import numpy as np

from .utils import prepare_pretrain_input
from .utils import prepare_main_input


class LRS2Pretrain(Dataset):
       
    """    
    A custom dataset class for the LRS2 pretrain dataset.
    """

    def __init__(self, datadir, numWords, charToIx, stepSize, audioParams, videoParams, noiseParams):
        super(LRS2Pretrain, self).__init__()
        with open(datadir + "/pretrain.txt", "r") as f:
            lines = f.readlines()
        self.datalist = [datadir + "/pretrain/" + line.strip() for line in lines]
        self.numWords = numWords
        self.charToIx = charToIx
        self.stepSize = stepSize
        self.audioParams = audioParams
        self.videoParams = videoParams
        _, self.noise = wavfile.read(noiseParams["noiseFile"])
        self.noiseProb = noiseParams["noiseProb"]
        self.noiseSNR = noiseParams["noiseSNR"]
        return
        

    def __getitem__(self, index):
        #index goes from 0 to stepSize-1
        #dividing the dataset into partitions of size equal to stepSize and selecting a random partition
        #fetch the sample at position 'index' in this randomly selected partition
        base = self.stepSize * np.arange(int(len(self.datalist)/self.stepSize)+1)
        ixs = base + index
        ixs = ixs[ixs < len(self.datalist)]
        index = np.random.choice(ixs)
        
        #passing the sample files and the target file paths to the prepare function to obtain the input tensors
        audioFile = self.datalist[index] + ".wav"
        visualFeaturesFile = self.datalist[index] + ".npy"
        targetFile = self.datalist[index] + ".txt"
        if np.random.choice([True, False], p=[self.noiseProb, 1-self.noiseProb]):
            noise = self.noise
        else:
            noise = None
        inp, trgt, inpLen, trgtLen = prepare_pretrain_input(audioFile, visualFeaturesFile, targetFile, noise, self.numWords, 
                                                            self.charToIx, self.noiseSNR, self.audioParams, self.videoParams)
        return inp, trgt, inpLen, trgtLen


    def __len__(self):
        #each iteration covers only a random subset of all the training samples whose size is given by the step size
        return self.stepSize




class LRS2Main(Dataset):

    """
    A custom dataset class for the LRS2 main (includes train, val, test) dataset
    """
    
    def __init__(self, dataset, datadir, charToIx, stepSize, audioParams, videoParams, noiseParams):
        super(LRS2Main, self).__init__()
        with open(datadir + "/" + dataset + ".txt", "r") as f:
            lines = f.readlines()
        self.datalist = [datadir + "/main/" + line.strip().split(" ")[0] for line in lines]
        self.charToIx = charToIx
        self.dataset = dataset
        self.stepSize = stepSize
        self.audioParams = audioParams
        self.videoParams = videoParams
        if noiseParams["noiseFile"] != None:
            _, self.noise = wavfile.read(noiseParams["noiseFile"])
        else:
            self.noise = None
        self.noiseSNR = noiseParams["noiseSNR"]
        self.noiseProb = noiseParams["noiseProb"]
        return
        

    def __getitem__(self, index):
        #using the same procedure as in pretrain dataset class only for the train dataset
        if self.dataset == "train":
            base = self.stepSize * np.arange(int(len(self.datalist)/self.stepSize)+1)
            ixs = base + index
            ixs = ixs[ixs < len(self.datalist)]
            index = np.random.choice(ixs)

        #passing the sample files and the target file paths to the prepare function to obtain the input tensors 
        audioFile = self.datalist[index] + ".wav"
        visualFeaturesFile = self.datalist[index] + ".npy"
        targetFile = self.datalist[index] + ".txt"
        if np.random.choice([True, False], p=[self.noiseProb, 1-self.noiseProb]):
            noise = self.noise
        else:
            noise = None
        inp, trgt, inpLen, trgtLen = prepare_main_input(audioFile, visualFeaturesFile, targetFile, noise, self.charToIx, 
                                                        self.noiseSNR, self.audioParams, self.videoParams)
        return inp, trgt, inpLen, trgtLen


    def __len__(self):
        #using step size only for train dataset and not for val and test datasets because
        #the size of val and test datasets is smaller than step size and we generally want to validate and test 
        #on the complete dataset
        if self.dataset == "train":
            return self.stepSize
        else:
            return len(self.datalist)

