import torch
import torch.nn as nn


class IrisNet(nn.Module):
    """
    Simple MLP for Iris classification: 4 features -> 3 classes.
    Normalization stats (mean, std) are baked in as buffers so the
    model is self-contained — no preprocessing needed at inference time.
    """
    mean: torch.Tensor
    std: torch.Tensor

    def __init__(self, mean: list, std: list):
        super().__init__()
        self.register_buffer("mean", torch.tensor(mean, dtype=torch.float32))
        self.register_buffer("std",  torch.tensor(std,  dtype=torch.float32))
        self.fc1 = nn.Linear(4, 16)
        self.fc2 = nn.Linear(16, 3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = (x - self.mean) / self.std
        x = torch.relu(self.fc1(x))
        return self.fc2(x)
