import glob
import torchvision.transforms as transforms
import numpy as np
import cv2


from pathlib import Path
from PIL import Image


CLOTHES_PATH = Path("samples/clothes")
EDGES_PATH = Path("samples/edges")


def get_transform(method=Image.BICUBIC, normalize=True):
    transform_list = []

    base = float(2 ** 4)
    transform_list.append(transforms.Lambda(lambda img: __make_power_2(img, base, method)))

    transform_list += [transforms.ToTensor()]

    if normalize:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5),
                                                (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)


def __make_power_2(img, base, method=Image.BICUBIC):
    try:
        ow, oh = img.size # PIL
    except:
        oh, ow = img.shape # numpy          
    h = int(round(oh / base) * base)
    w = int(round(ow / base) * base)
    if (h == oh) and (w == ow):
        return img
    return img.resize((w, h), method)


class TryOn:
    def __init__(self, device, img_size=(192, 256)):
        self.device = device
        self.img_size = img_size
        self.load_transforms()
        self.load_samples()
        self.load_models()

    
    def load_transforms(self):
        self.transform = get_transform()
        self.transform_e = get_transform(method=Image.NEAREST, normalize=False)


    def load_samples(self):
        names = [Path(i).name for i in glob.glob(str(CLOTHES_PATH / "*.jpg"))]
        
        self.samples = {}
        for name in names:
            self.samples[name] = {
                "clothes" : self.transform(Image.open(CLOTHES_PATH / name)).to(self.device).unsqueeze(0),
                "edges": self.transform_e(Image.open(EDGES_PATH / name)).to(self.device).unsqueeze(0)
            }


    def load_models(self):
        print(self.device)
        if self.device == "cpu":
            from .dmvton.dmvton import DMVTON
            self.model = DMVTON()

        elif self.device.startswith("cuda"):
            from .dmvton_cuda.dmvton import DMVTON
            self.model = DMVTON() 

        self.model.model.to(self.device)
        self.model.model.eval()


    def __call__(self, frame: np.ndarray, clothes_name: str):
        if clothes_name not in self.samples:
            return frame

        # cropped_result, img = self.preprocess_frame(frame)   
        img = frame
        
        person = self.transform(Image.fromarray(img)).to(self.device).unsqueeze(0)
        clothes = self.samples[clothes_name]["clothes"]
        edges = self.samples[clothes_name]["edges"]

        torch_out = self.model(person, clothes, edges)[0]
        cv_out = (torch_out.permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
        out = (cv_out * 255).astype(np.uint8)

        # return cropped_result, self.postprocess_frame(frame, out, cropped_result)
        return out


    def preprocess_frame(self, frame):
        if frame is None:
            return None, None
        
        # Crop the image to have same ratio
        if frame.shape[0] * self.img_size[0] < frame.shape[1] * self.img_size[1]:
            height = frame.shape[0]
            width = int(self.img_size[0] * height / self.img_size[1])
        else:
            width = frame.shape[1]
            height = int(self.img_size[1] * width / self.img_size[0])
            
        center = (frame.shape[0] // 2, frame.shape[1] // 2)
        x = center[1] - width // 2
        y = center[0] - height // 2
        out_frame = frame[y : y + height, x : x + width]
        out_frame = cv2.resize(out_frame, (self.img_size[0], self.img_size[1]))

        # Mapping bbox value
        cropped_result = { 't': 0, 'l': 0 }
        cropped_result['t'] += y
        cropped_result['b'] = cropped_result['t'] + height
        cropped_result['l'] += x
        cropped_result['r'] = cropped_result['l'] + width

        return cropped_result, out_frame
    

    def postprocess_frame(self, original_frame, out_frame, cropped_result):
        t, l, b, r = cropped_result['t'], cropped_result['l'], cropped_result['b'], cropped_result['r']
        cropped_output = cv2.resize(out_frame, (r - l, b - t))  
        out = original_frame.copy()
        out[t:b, l:r, :] = cropped_output
        return out
        
