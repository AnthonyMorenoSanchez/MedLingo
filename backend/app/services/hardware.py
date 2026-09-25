import platform
import shutil
import subprocess

import psutil


def detect():
    memory=psutil.virtual_memory()
    gpu='Not detected; CPU fallback'
    try:
        if platform.system()=='Windows' or shutil.which('powershell.exe'):
            exe='powershell.exe' if platform.system()!='Windows' else 'powershell'
            gpu=subprocess.check_output([exe,'-NoProfile','-Command','(Get-CimInstance Win32_VideoController).Name'],timeout=8,text=True).strip()
        elif shutil.which('lspci'):
            output=subprocess.check_output(['lspci'],timeout=5,text=True)
            gpu='; '.join(line for line in output.splitlines() if 'VGA' in line or '3D controller' in line) or gpu
    except (OSError,subprocess.SubprocessError):
        pass
    total=round(memory.total/2**30,1);available=round(memory.available/2**30,1)
    # Use visible/available memory: WSL may expose less RAM than its Windows host.
    model='qwen3:0.6b' if total<8 or available<3 else 'qwen3:1.7b' if total<14 or available<6 else 'qwen3:4b' if total<28 or available<12 else 'qwen3:8b'
    return {'os':platform.system(),'wsl':'microsoft' in platform.release().lower(),'ram_gb':total,'available_ram_gb':available,'gpu':gpu,'recommended_model':model,'choices':['qwen3:0.6b','qwen3:1.7b','qwen3:4b','qwen3:8b'],'note':'Recommendation prioritizes memory headroom. CPU works without GPU support. RX 5700 XT is not on the ROCm support list; native Windows Vulkan may accelerate it, but is not assumed. WSL memory limits may lower the recommendation.'}
