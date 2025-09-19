import os
import subprocess
from setuptools import setup, find_packages, Command

class InstallEnvironmentCommand(Command):
    description = 'Install complete environment including CUDA and system dependencies'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Cài đặt system dependencies
        subprocess.check_call(['apt-get', 'update'])
        subprocess.check_call([
            'apt-get', 'install', '-y',
            'python3-pip',
            'git',
            'ffmpeg',
            'libsndfile1',
            'nvidia-cuda-toolkit',
            'nvidia-cuda-toolkit-gcc'
        ])

        # Cài đặt PyTorch với CUDA
        subprocess.check_call([
            'pip3', 'install',
            'torch', 'torchvision', 'torchaudio',
            '--index-url', 'https://download.pytorch.org/whl/cu118'
        ])

        # Cài đặt các package cơ bản
        subprocess.check_call([
            'pip3', 'install',
            'transformers==4.56.1',
            'omegaconf>=2.3.0',
            'numpy>=2.0.0,<2.3.0',
            'scipy==1.12.0'
        ])

# Đọc requirements từ file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#") 
        and not line.startswith("git+")
        and not any(pkg in line for pkg in ['torch', 'transformers', 'numpy', 'scipy'])
    ]

# Thêm các git dependencies riêng
git_dependencies = [
    'pytorch3d @ git+https://github.com/facebookresearch/pytorch3d.git',
]

setup(
    name="digital-human-server",
    version="0.1.0",
    author="Minh Nhật",
    author_email="nhatminhho136@gmail.com",
    description="A digital human server with TTS, face and motion generation capabilities",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements + git_dependencies,
    cmdclass={
        'install_env': InstallEnvironmentCommand,
    },
    include_package_data=True,
    package_data={
        "": [
            "configs/*.yml",
            "configs/config_face/*.yml",
            "models/audio2face/proto/sample_wheel/*.whl",
        ],
    },
)

# Post-installation setup
def setup_nvidia_environment():
    cuda_home = os.environ.get('CUDA_HOME')
    if not cuda_home:
        # Tìm CUDA path
        common_cuda_paths = [
            '/usr/local/cuda',
            '/usr/local/cuda-11.8',
            'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8'
        ]
        for path in common_cuda_paths:
            if os.path.exists(path):
                os.environ['CUDA_HOME'] = path
                break

    # Thiết lập các biến môi trường CUDA khác nếu cần
    if cuda_home:
        os.environ['LD_LIBRARY_PATH'] = f"{cuda_home}/lib64:{os.environ.get('LD_LIBRARY_PATH', '')}"

if __name__ == '__main__':
    setup_nvidia_environment()