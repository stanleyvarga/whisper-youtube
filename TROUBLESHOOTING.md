# AMD GPU Troubleshooting Guide

## Issue: GPU Not Detected in WSL Ubuntu

If you see "CPU (GPU not available)" when using `--gpu` flag, follow these steps:

### 1. Verify PyTorch Installation

Check if PyTorch was installed with ROCm support:

```bash
pip show torch
```

Look for the build info. It should mention ROCm if correctly installed.

### 2. Reinstall PyTorch with ROCm

Uninstall current PyTorch and reinstall with ROCm support:

```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### 3. Test GPU Detection

Run this diagnostic script:

```python
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'Number of GPUs: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
else:
    print('GPU not available. Check ROCm installation.')
```

### 4. Check ROCm Installation in WSL

ROCm installation in WSL can be tricky. Key requirements:

- **ROCm version**: Must be 5.7+ for RDNA 3 (RX 9000 series) support
- **WSL2**: ROCm works better in WSL2 than WSL1
- **Windows GPU passthrough**: Your GPU must be properly exposed to WSL

### 5. Alternative: Use ROCm on Native Linux

If ROCm doesn't work in WSL, consider:
- Installing a dual boot with native Linux (Ubuntu recommended)
- ROCm has better support on native Linux installations
- This would give you the best performance

### 6. Verify System Compatibility

Check if your system can see the GPU:

```bash
# Check if GPU is visible
lspci | grep -i amd

# Check ROCm installation
/opt/rocm/bin/rocminfo

# Check if device is accessible
ls -la /dev/dri/
```

### 7. WSL-Specific Configuration

If using WSL, you may need to configure GPU passthrough:

1. Update WSL to latest version
2. Install AMD ROCm drivers in Windows
3. Ensure WSL can access the GPU

### Expected Output When Working

When properly configured, you should see:

```
🔄 Loading Whisper model 'large-v3' on AMD Radeon RX 9060 XT...
✅ Model loaded on GPU: AMD Radeon RX 9060 XT
```

Instead of:

```
🔄 Loading Whisper model 'large-v3' on CPU (GPU not available)...
✅ Model loaded on CPU
```

### Performance Expectations

- **Without GPU**: large-v3 model at ~0.5-1x real-time
- **With RX 9060 XT**: large-v3 model at ~5-8x real-time (10x faster)

### Getting Help

If you continue to have issues:

1. Check AMD ROCm documentation: https://rocm.docs.amd.com/
2. Verify your specific GPU model is supported
3. Check ROCm GitHub issues for WSL-specific problems

