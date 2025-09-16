"""
Audio Utilities - Các tiện ích xử lý âm thanh
Hỗ trợ nhiều định dạng âm thanh và chuyển đổi cho Audio2Face
"""

import os
import librosa
import soundfile as sf
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from typing import Union, Optional, Dict, Any
import logging
import warnings

# Tắt warnings không cần thiết
warnings.filterwarnings("ignore", category=UserWarning)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioFormatConverter:
    """Class chuyển đổi định dạng âm thanh"""
    
    # Các thông số chuẩn cho Audio2Face
    A2F_SAMPLE_RATE = 16000
    A2F_BITS_PER_SAMPLE = 16
    A2F_CHANNELS = 1
    A2F_FORMAT = 'WAV'
    
    # Các định dạng được hỗ trợ
    SUPPORTED_INPUT_FORMATS = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac', '.wma']
    SUPPORTED_OUTPUT_FORMATS = ['.wav']
    
    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_audio_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết về file âm thanh
        
        Args:
            file_path: Đường dẫn file âm thanh
            
        Returns:
            Dict: Thông tin file âm thanh
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {file_path}")
        
        try:
            # Sử dụng soundfile để lấy metadata
            info = sf.info(str(file_path))
            
            audio_info = {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'subtype': info.subtype,
                'format': info.format,
                'frames': info.frames,
                'bit_depth': getattr(info.subtype_info, 'bit_depth', 'unknown') if hasattr(info, 'subtype_info') else 'unknown'
            }
            
            logger.info(f"Audio info: {audio_info}")
            return audio_info
            
        except Exception as e:
            logger.error(f"Lỗi khi đọc thông tin file {file_path}: {e}")
            raise
    
    def is_a2f_compatible(self, file_path: Union[str, Path]) -> bool:
        """
        Kiểm tra file có tương thích với Audio2Face không
        
        Args:
            file_path: Đường dẫn file âm thanh
            
        Returns:
            bool: True nếu tương thích
        """
        try:
            info = self.get_audio_info(file_path)
            
            # Kiểm tra các điều kiện tương thích
            compatible = (
                info['sample_rate'] == self.A2F_SAMPLE_RATE and
                info['channels'] == self.A2F_CHANNELS and
                info['format'] == 'WAV' and
                info['subtype'] in ['PCM_16', 'PCM_24', 'PCM_32']
            )
            
            logger.info(f"File tương thích với A2F: {compatible}")
            return compatible
            
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra tương thích: {e}")
            return False
    
    def convert_to_a2f_format(self, input_path: Union[str, Path], output_path: Union[str, Path] = None) -> str:
        """
        Chuyển đổi file âm thanh sang định dạng tương thích với Audio2Face
        
        Args:
            input_path: Đường dẫn file input
            output_path: Đường dẫn file output (tùy chọn)
            
        Returns:
            str: Đường dẫn file output
        """
        input_path = Path(input_path)
        
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_a2f.wav"
        else:
            output_path = Path(output_path)
        
        logger.info(f"Chuyển đổi file: {input_path} -> {output_path}")
        
        try:
            # Kiểm tra nếu file đã tương thích
            if self.is_a2f_compatible(input_path):
                logger.info("File đã tương thích với A2F, copy sang vị trí mới")
                import shutil
                shutil.copy2(input_path, output_path)
                return str(output_path)
            
            # Load audio với librosa
            audio_data, original_sr = librosa.load(
                str(input_path),
                sr=None,
                mono=False
            )
            
            logger.info(f"Loaded: {audio_data.shape}, {original_sr}Hz")
            
            # Chuyển sang mono nếu cần
            if len(audio_data.shape) > 1:
                audio_data = librosa.to_mono(audio_data)
                logger.info("Converted to mono")
            
            # Resample về 16kHz
            if original_sr != self.A2F_SAMPLE_RATE:
                audio_data = librosa.resample(
                    audio_data,
                    orig_sr=original_sr,
                    target_sr=self.A2F_SAMPLE_RATE
                )
                logger.info(f"Resampled to {self.A2F_SAMPLE_RATE}Hz")
            
            # Normalize
            audio_data = librosa.util.normalize(audio_data)
            
            # Chuyển sang 16-bit integer
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Lưu file WAV
            wavfile.write(str(output_path), self.A2F_SAMPLE_RATE, audio_data)
            
            logger.info(f"Conversion completed: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Lỗi khi chuyển đổi: {e}")
            raise
    
    def batch_convert(self, input_dir: Union[str, Path], output_dir: Union[str, Path] = None) -> list:
        """
        Chuyển đổi hàng loạt các file âm thanh
        
        Args:
            input_dir: Thư mục chứa file input
            output_dir: Thư mục output (tùy chọn)
            
        Returns:
            list: Danh sách file đã chuyển đổi
        """
        input_dir = Path(input_dir)
        
        if output_dir is None:
            output_dir = input_dir / "a2f_converted"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        converted_files = []
        
        # Tìm tất cả file âm thanh
        for ext in self.SUPPORTED_INPUT_FORMATS:
            for file_path in input_dir.glob(f"*{ext}"):
                try:
                    output_file = output_dir / f"{file_path.stem}_a2f.wav"
                    result = self.convert_to_a2f_format(file_path, output_file)
                    converted_files.append(result)
                    logger.info(f"Converted: {file_path.name} -> {output_file.name}")
                except Exception as e:
                    logger.error(f"Lỗi khi chuyển đổi {file_path}: {e}")
        
        logger.info(f"Đã chuyển đổi {len(converted_files)} files")
        return converted_files

def quick_convert(input_path: Union[str, Path], output_path: Union[str, Path] = None) -> str:
    """
    Hàm tiện ích để chuyển đổi nhanh file âm thanh
    
    Args:
        input_path: Đường dẫn file input
        output_path: Đường dẫn file output (tùy chọn)
        
    Returns:
        str: Đường dẫn file output
    """
    converter = AudioFormatConverter()
    return converter.convert_to_a2f_format(input_path, output_path)

def check_audio_compatibility(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Kiểm tra tương thích của file âm thanh với Audio2Face
    
    Args:
        file_path: Đường dẫn file âm thanh
        
    Returns:
        Dict: Thông tin tương thích
    """
    converter = AudioFormatConverter()
    
    try:
        info = converter.get_audio_info(file_path)
        compatible = converter.is_a2f_compatible(file_path)
        
        return {
            'file_path': str(file_path),
            'compatible': compatible,
            'audio_info': info,
            'requirements': {
                'sample_rate': f"{converter.A2F_SAMPLE_RATE}Hz",
                'channels': converter.A2F_CHANNELS,
                'format': converter.A2F_FORMAT,
                'bit_depth': f"{converter.A2F_BITS_PER_SAMPLE}-bit"
            }
        }
    except Exception as e:
        return {
            'file_path': str(file_path),
            'compatible': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test với file hiện có
    test_file = "results/audio/Jade_Voice_Intro.wav"
    
    if os.path.exists(test_file):
        print("=== Kiểm tra tương thích ===")
        compatibility = check_audio_compatibility(test_file)
        print(f"Tương thích: {compatibility['compatible']}")
        print(f"Thông tin: {compatibility.get('audio_info', {})}")
        
        if not compatibility['compatible']:
            print("\n=== Chuyển đổi file ===")
            try:
                output_file = quick_convert(test_file)
                print(f"File đã chuyển đổi: {output_file}")
            except Exception as e:
                print(f"Lỗi: {e}")
    else:
        print(f"File test không tồn tại: {test_file}")
