import os
import shutil
import time
import ctypes
import imagehash
from PIL import Image, UnidentifiedImageError

# -------------------------- 配置参数 (按需修改) --------------------------
SOURCE_FOLDER = r"D:\img"                          # 原始图片库目录
TARGET_FOLDER = r"D:\img_todo\all_img_result"     # 去重后图片输出目录
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')  # 支持的图片格式
MIN_PIXEL_COUNT = 1000                              # 最小像素数阈值（宽或高小于此值的图片将被过滤）
RETRY_TIMES = 5                                     # 文件操作失败重试次数
RETRY_DELAY = 2                                     # 重试间隔（秒）
HASH_SIZE = 8                                       # 哈希计算尺寸（8-16之间选择，影响去重精度）


# -------------------------- 系统级辅助函数 --------------------------
def release_file_cache():
    """Windows系统-释放文件缓存/句柄，非Windows系统无影响"""
    try:
        if os.name == "nt":
            ctypes.windll.kernel32.SetErrorMode(0x0001)
            ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
    except Exception as e:
        print(f"⚠️ 释放文件缓存失败: {e}")


def remove_readonly_attr(file_path):
    """跨平台移除文件只读属性"""
    if os.path.exists(file_path):
        try:
            if os.name == "nt":
                ctypes.windll.kernel32.SetFileAttributesW(file_path, 128)  # Windows移除只读
            else:
                os.chmod(file_path, 0o777)  # 类Unix系统
        except Exception as e:
            print(f"⚠️ 移除只读属性失败 {file_path}: {e}")


# -------------------------- 核心图片处理函数 --------------------------
def get_image_info(img_path):
    """获取图片的哈希值和尺寸信息"""
    img = None
    try:
        img = Image.open(img_path)
        # 计算感知哈希值
        phash = str(imagehash.phash(img.convert('L'), hash_size=HASH_SIZE))
        # 获取图片尺寸
        width, height = img.size
        return phash, (width, height)
    except UnidentifiedImageError:
        print(f"❌ 无法识别图片: {os.path.basename(img_path)}")
        return None, None
    except Exception as e:
        print(f"❌ 处理图片失败 {os.path.basename(img_path)}: {e}")
        return None, None
    finally:
        if img:
            img.close()
            del img
        release_file_cache()


def safe_copy_file(src_path, dst_path):
    """安全复制文件，处理权限和重试逻辑"""
    remove_readonly_attr(src_path)
    
    # 复制文件（带重试）
    for retry in range(RETRY_TIMES):
        try:
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            if retry < RETRY_TIMES - 1:
                print(f"⚠️ 复制失败 {os.path.basename(src_path)}，重试中... ({retry+1}/{RETRY_TIMES})")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ 复制失败 {os.path.basename(src_path)}: {e}")
                return False


def delete_source_file(src_path):
    """安全删除源文件，处理权限和重试逻辑"""
    remove_readonly_attr(src_path)
    
    # 删除文件（带重试）
    for retry in range(RETRY_TIMES):
        try:
            release_file_cache()
            os.remove(src_path)
            return True
        except PermissionError:
            if retry < RETRY_TIMES - 1:
                print(f"⚠️ 删除失败 {os.path.basename(src_path)}，文件被占用，重试中... ({retry+1}/{RETRY_TIMES})")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ 删除失败 {os.path.basename(src_path)}: 文件被占用")
                with open(os.path.join(TARGET_FOLDER, "delete_failed.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{src_path}\n")
                return False
        except Exception as e:
            if retry < RETRY_TIMES - 1:
                print(f"⚠️ 删除失败 {os.path.basename(src_path)}，重试中... ({retry+1}/{RETRY_TIMES})")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ 删除失败 {os.path.basename(src_path)}: {e}")
                with open(os.path.join(TARGET_FOLDER, "delete_failed.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{src_path}\n")
                return False


# -------------------------- 主函数 --------------------------
def main():
    # 创建目标文件夹
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    
    # 初始化统计变量
    total_files = 0
    processed_files = 0
    duplicate_files = 0
    filtered_files = 0
    moved_files = 0
    error_files = 0
    
    # 存储已处理的图片哈希值
    processed_hashes = set()
    
    print("=" * 60)
    print("📁 图片去重工具")
    print(f"🔍 源文件夹: {SOURCE_FOLDER}")
    print(f"📂 目标文件夹: {TARGET_FOLDER}")
    print(f"🎯 支持格式: {SUPPORTED_FORMATS}")
    print("=" * 60)
    print()
    
    # 遍历源文件夹
    for root, _, files in os.walk(SOURCE_FOLDER):
        print(f"▶ 正在处理文件夹: {root}")
        
        for filename in files:
            # 检查文件格式
            if not filename.lower().endswith(SUPPORTED_FORMATS):
                continue
            
            total_files += 1
            file_path = os.path.join(root, filename)
            
            try:
                # 获取图片信息
                img_hash, (width, height) = get_image_info(file_path)
                
                if img_hash is None:
                    error_files += 1
                    continue
                
                # 过滤小尺寸图片
                if width < MIN_PIXEL_COUNT or height < MIN_PIXEL_COUNT:
                    filtered_files += 1
                    print(f"🔍 过滤小尺寸图片: {filename} ({width}x{height})")
                    continue
                
                # 检查是否重复
                if img_hash in processed_hashes:
                    duplicate_files += 1
                    print(f"🔶 发现重复图片: {filename}")
                    # 可以选择删除重复文件或保留
                    # delete_source_file(file_path)
                    continue
                
                # 处理目标文件命名
                ext = os.path.splitext(filename)[1].lower()
                # 使用哈希值+时间戳命名，避免冲突
                target_filename = f"{img_hash}_{int(time.time())}{ext}"
                target_path = os.path.join(TARGET_FOLDER, target_filename)
                
                # 复制文件到目标文件夹
                if safe_copy_file(file_path, target_path):
                    # 删除源文件
                    delete_source_file(file_path)
                    
                    moved_files += 1
                    processed_hashes.add(img_hash)
                    print(f"✅ 已处理: {filename} → {target_filename}")
                else:
                    error_files += 1
                    
            except Exception as e:
                error_files += 1
                print(f"❌ 处理失败: {filename} - {e}")
                continue
    
    # 生成统计报告
    print()
    print("=" * 60)
    print("📊 去重完成统计报告")
    print("=" * 60)
    print(f"📁 总文件数: {total_files}")
    print(f"✅ 成功去重并移动: {moved_files}")
    print(f"🔶 重复文件数: {duplicate_files}")
    print(f"🔍 过滤小尺寸文件: {filtered_files}")
    print(f"❌ 处理失败文件: {error_files}")
    print(f"💾 已处理哈希值数量: {len(processed_hashes)}")
    print()
    
    # 检查是否有删除失败的文件
    delete_failed_path = os.path.join(TARGET_FOLDER, "delete_failed.txt")
    if os.path.exists(delete_failed_path):
        with open(delete_failed_path, "r", encoding="utf-8") as f:
            failed_count = len(f.readlines())
        print(f"⚠️ 有 {failed_count} 个文件删除失败，详见: {delete_failed_path}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()