#!/usr/bin/env python3
"""
Script kiểm tra PyTorch CUDA setup
Chạy script này để xác minh PyTorch đã được cài đặt đúng với hỗ trợ CUDA
"""

import sys

def test_pytorch_cuda():
    """Kiểm tra PyTorch và CUDA setup"""
    print("🔍 Kiểm tra PyTorch và CUDA setup...")
    print("=" * 50)
    
    try:
        import torch
        print(f"✅ PyTorch đã được cài đặt: {torch.__version__}")
        
        # Kiểm tra CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"🎮 CUDA có sẵn: {'✅ Có' if cuda_available else '❌ Không'}")
        
        if cuda_available:
            print(f"🚀 CUDA version: {torch.version.cuda}")
            print(f"🔢 Số GPU có sẵn: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                print(f"   GPU {i}: {gpu_name}")
            
            # Test tạo tensor trên GPU
            try:
                test_tensor = torch.randn(3, 3).cuda()
                print("✅ Test tạo tensor trên GPU: Thành công")
                
                # Test tính toán trên GPU
                result = torch.matmul(test_tensor, test_tensor)
                print("✅ Test tính toán trên GPU: Thành công")
                
            except Exception as e:
                print(f"❌ Lỗi khi test GPU: {e}")
                return False
                
        else:
            print("⚠️  PyTorch sẽ chạy trên CPU")
            
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import PyTorch: {e}")
        print("💡 Hãy chạy setup.bat hoặc setup_cuda.bat để cài đặt PyTorch")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False

def main():
    """Hàm chính"""
    print("🤖 Digital Human Server - PyTorch CUDA Test")
    print("=" * 50)
    
    success = test_pytorch_cuda()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Kiểm tra hoàn tất - PyTorch setup OK!")
    else:
        print("❌ Có vấn đề với PyTorch setup")
        print("💡 Hãy chạy setup_cuda.bat để khắc phục")
        sys.exit(1)

if __name__ == "__main__":
    main()

