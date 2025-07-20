import os
import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import cv2

# U2NET model definition (from official repo, simplified for inference)
class REBNCONV(nn.Module):
    def __init__(self, in_ch=3, out_ch=3, dirate=1):
        super(REBNCONV, self).__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, 3, padding=1*dirate, dilation=1*dirate)
        self.bn = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU(inplace=True)
    def forward(self, x):
        hx = x
        xout = self.relu(self.bn(self.conv(hx)))
        return xout

class U2NET(nn.Module):
    # ... (full model code omitted for brevity, use official repo)
    def __init__(self, in_ch=3, out_ch=1):
        super(U2NET, self).__init__()
        # ... (model layers)
        # For brevity, please copy the full U2NET class from the official repo:
        # https://github.com/xuebinqin/U-2-Net/blob/master/model/u2net.py
        pass
    def forward(self, x):
        # ...
        pass

# Helper to load the model
_model = None
def load_model():
    global _model
    if _model is None:
        from u2net.model.u2net import U2NETP # You need to copy u2net.py from the official repo to model/u2net.py
        model_path = os.path.join(os.path.dirname(__file__), 'u2netp.pth')
        net = U2NETP(3,1)
        net.load_state_dict(torch.load(model_path, map_location='cpu'))
        net.eval()
        _model = net
    return _model

def preprocess_image(pil_image):
    # Resize to 320x320, normalize, convert to tensor
    im = pil_image.convert('RGB').resize((320,320), Image.BILINEAR)
    im = np.array(im).astype(np.float32)/255.0
    im = (im - 0.485) / 0.229  # simple normalization
    im = np.transpose(im, (2,0,1))
    im = torch.from_numpy(im).unsqueeze(0).float()
    return im

def run_u2net(pil_image):
    model = load_model()
    inp = preprocess_image(pil_image)
    with torch.no_grad():
        d1 = model(inp)[0]  # U2NET returns a tuple, d1 is the main output
        pred = d1.squeeze().cpu().numpy()
        pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
        mask = (pred*255).astype(np.uint8)
        mask = cv2.resize(mask, pil_image.size, interpolation=cv2.INTER_LINEAR)
        return Image.fromarray(mask) 