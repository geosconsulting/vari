import os
import tempfile

import kornia.augmentation as K
import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from torchgeo.datasets import EuroSAT100
from torchgeo.models import ResNet18_Weights, resnet18

torch.manual_seed(0)


root = os.path.join(tempfile.gettempdir(), "eurosat100")
dataset = EuroSAT100(root, download=True)

for i in torch.randint(len(dataset), (10,)):
    sample = dataset[i]
    dataset.plot(sample)
