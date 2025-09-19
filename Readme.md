python -m venv .venv

pip install -r pre-requirements.txt
pip install -r requirements.txt
pip install "models/audio2face/proto/sample_wheel/nvidia_ace-1.0.0-py3-none-any.whl"
