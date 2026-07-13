import torch

print("torch:", torch.__version__)
print("hip:", torch.version.hip)
print("cuda available (rocm):", torch.cuda.is_available())

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))