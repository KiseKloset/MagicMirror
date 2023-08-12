<div align="center">
<h1>Magic Mirror 🪞</h1>
<br>
Magic Mirror 🪞 is an Virtual Try-on Augmented Reality (AR) application that can run on a local machine
</div>
<br>

## <div align="center">📝 Documentation</div>
### 🧰 Install
Clone this repo and install with `conda` (we provide script `install.sh`).
```
git clone https://github.com/KiseKloset/MagicMirror.git
cd MagicMirror

# Install
conda create -n magic-mirror python=3.10
conda activate magic-mirror
bash install.sh
```
*Note: `install.sh` install the environment for devices with GPU (need to install cudatoolkit). If you want to run with CPU, you can skip cudatoolkit and you need to change the version of [torch](https://pytorch.org/) in `requirements.txt` to the corresponding CPU version.*

Download pretrained checkpoints. Currently, we support 2 separate CPU and GPU versions. You just need to download the checkpoints corresponding to your device.
- CPU:
```
gdown 1tCZ5Y31F-7IXMiiP1UW33C35speUkA4L -O model/tryon/dmvton/mobile_warp.pt
gdown 1eriBnHZkrkrGwrzWbn4z_N8uIxFf5gT6 -O model/tryon/dmvton/mobile_gen.pt
```
- GPU
```
gdown 1KJNKjqBeUF9CLcCRFyjONmKzcqjNgj9z -O model/tryon/dmvton_cuda/mobile_warp.pt
gdown 1TP2OiEixy1WEjbJsdDYGL-214v_zkqUV -O model/tryon/dmvton_cuda/mobile_gen.pt
```


### 👨‍💻 Run
```
python App.py
```

## <div align="center">✔️ TODO</div>
- [ ] Optimize gesture control