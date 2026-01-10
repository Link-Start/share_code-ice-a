import os
import shutil
import platform
import torch
from ultralytics import YOLO

# ======================== 核心参数配置（请根据自己的路径修改！！！） ========================
SOURCE_IMG_DIR = r"D:\img_todo\all_img_result"  # 去重后的图片源文件夹
HAVE_FACE_DIR = r"D:\img_todo\good"            # 检测出有人脸的图片输出目录
NO_FACE_DIR = r"D:\img_todo\bad"              # 无有效人脸的图片输出目录
CONF_THRESHOLD = 0.9                           # 置信度阈值，大于等于90%才判定为人脸
MODEL_PATH = 'face.pt'          # YOLOv8人脸检测模型路径
# ========================================================================================


def detect_device():
    """
    自动检测并选择最佳运行设备
    返回：设备字符串 (cpu/mps/0)
    """
    print("🔍 正在检测可用计算设备...")
    
    # 检查操作系统类型
    system = platform.system()
    print(f"💻 操作系统: {system}")
    
    # 优先检查Mac设备（MPS）
    if system == "Darwin":  # macOS
        if torch.backends.mps.is_available():
            print("✅ 检测到Mac MPS GPU，将使用MPS加速")
            return "mps"
        else:
            print("⚠️  Mac MPS不可用，将使用CPU")
            return "cpu"
    
    # 检查CUDA GPU（Windows/Linux）
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ 检测到CUDA GPU ({gpu_count}个): {gpu_name}")
        print(f"   CUDA版本: {torch.version.cuda}")
        return 0  # 使用第一个GPU
    
    # 所有GPU都不可用时，使用CPU
    print("⚠️  未检测到可用GPU，将使用CPU")
    return "cpu"


def main():
    """
    人脸检测主函数：对去重后的图片进行批量人脸检测
    输出：包含人脸的图片集合（保存在HAVE_FACE_DIR目录）
    """
    # 创建目标文件夹（如果不存在则自动创建）
    os.makedirs(HAVE_FACE_DIR, exist_ok=True)
    os.makedirs(NO_FACE_DIR, exist_ok=True)

    # 自动检测最佳运行设备
    device = detect_device()
    
    # 加载YOLOv8人脸检测专用预训练模型
    print(f"\n🚀 正在加载人脸检测模型: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ 模型加载成功: {model.model.__class__.__name__}")
        print(f"🔧 当前使用设备: {device}")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 定义需要处理的图片后缀（常用格式全覆盖）
    SUPPORT_IMG_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff']

    # 遍历源文件夹下的所有文件
    img_count = 0
    have_face_count = 0
    
    print(f"\n📁 开始处理图片文件夹: {SOURCE_IMG_DIR}")
    print(f"🎯 人脸检测置信度阈值: {CONF_THRESHOLD * 100:.0f}%")
    print(f"📂 有人脸图片输出目录: {HAVE_FACE_DIR}")
    print(f"📂 无有效人脸图片输出目录: {NO_FACE_DIR}")
    print("=" * 60)

    try:
        for file_name in os.listdir(SOURCE_IMG_DIR):
            # 获取文件完整路径和后缀
            file_path = os.path.join(SOURCE_IMG_DIR, file_name)
            file_suffix = os.path.splitext(file_name)[1].lower()

            # 只处理图片文件
            if file_suffix not in SUPPORT_IMG_FORMATS:
                continue

            img_count += 1
            print(f"\n📷 正在检测第{img_count}张图片: {file_name}")

            try:
                # 执行人脸检测：核心推理，只返回置信度≥CONF_THRESHOLD的结果
                results = model(file_path, conf=CONF_THRESHOLD, device=device, verbose=False)

                # 获取当前图片的检测结果：人脸标签+置信度
                det_boxes = results[0].boxes  # 检测到的目标框集合
                detect_info = []
                for box in det_boxes:
                    cls_name = model.names[int(box.cls)]  # 检测的标签名称（人脸模型只有一个标签：face）
                    conf_score = round(float(box.conf), 4)  # 置信度，保留4位小数
                    detect_info.append(f"{cls_name} - {conf_score * 100:.2f}%")

                # 打印每张图片的所有检测标签及置信度
                if detect_info:
                    print(f"🔍 检测到的标签及置信度: {detect_info}")
                else:
                    print(f"🔍 检测到的标签及置信度: 无符合条件的检测结果")

                # 核心判断逻辑：置信度≥90% 才判定有人脸
                if len(det_boxes) > 0:
                    # 有人脸：移动到有人脸文件夹
                    dest_path = os.path.join(HAVE_FACE_DIR, file_name)
                    shutil.move(file_path, dest_path)
                    print(f"✅ 判定结果：置信度≥90%，检测到人脸 → 已移动至 {os.path.basename(HAVE_FACE_DIR)}")
                    have_face_count += 1
                else:
                    # 无人脸/置信度不足90%：移动到无人脸文件夹
                    dest_path = os.path.join(NO_FACE_DIR, file_name)
                    shutil.move(file_path, dest_path)
                    print(f"🔶 判定结果：无有效人脸（置信度<90%）→ 已移动至 {os.path.basename(NO_FACE_DIR)}")

            except Exception as e:
                # 异常处理：单张图片出错不影响整体批量处理
                print(f"⚠️  图片 {file_name} 处理失败: {str(e)} → 跳过该图片")
                continue

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序执行")
    except Exception as e:
        print(f"\n\n❌ 程序执行出错: {e}")
    finally:
        # 批量处理完成，打印统计信息
        print("\n" + "=" * 60)
        print("📊 人脸检测完成统计报告")
        print("=" * 60)
        print(f"📁 总共检测图片数量: {img_count} 张")
        print(f"✅ 检测出有人脸(置信度≥90%)的图片数量: {have_face_count} 张")
        print(f"🔶 无有效人脸的图片数量: {img_count - have_face_count} 张")
        print(f"📂 有人脸图片保存路径: {HAVE_FACE_DIR}")
        print(f"📂 无有效人脸图片保存路径: {NO_FACE_DIR}")
        print("=" * 60)


if __name__ == "__main__":
    main()