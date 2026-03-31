import os
from pathlib import Path
from typing import List
from app.core.config import STATIC_DIR

# PDF 文件夹路径
BOOK_PDF_DIR = os.path.join(STATIC_DIR, "book")


def get_all_pdf_files() -> List[str]:
    """扫描 static/book 目录，获取所有 PDF 文件名"""
    if not os.path.exists(BOOK_PDF_DIR):
        os.makedirs(BOOK_PDF_DIR)
        return []
    
    pdf_files = []
    for filename in os.listdir(BOOK_PDF_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_files.append(filename)
    return pdf_files


def get_safe_pdf_path(filename: str) -> str | None:
    """
    【安全】获取 PDF 文件的完整路径
    防止路径遍历攻击（例如 filename = '../../../../etc/passwd'）
    """
    if not filename:
        return None
    
    # 1. 只取文件名部分，去掉路径
    safe_filename = os.path.basename(filename)
    
    # 2. 拼接路径
    file_path = os.path.join(BOOK_PDF_DIR, safe_filename)
    
    # 3. 再次确认最终路径在 BOOK_PDF_DIR 内（双重检查）
    if not os.path.normpath(file_path).startswith(os.path.normpath(BOOK_PDF_DIR)):
        return None
    
    return file_path


def pdf_exists(filename: str) -> bool:
    """检查 PDF 文件是否存在"""
    file_path = get_safe_pdf_path(filename)
    if not file_path:
        return False
    return os.path.exists(file_path)


def delete_pdf_file(filename: str) -> bool:
    """
    【安全】删除 PDF 文件
    返回是否成功
    """
    file_path = get_safe_pdf_path(filename)
    if not file_path or not os.path.exists(file_path):
        return False
    
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def rename_pdf_file(old_filename: str, new_filename: str) -> bool:
    """
    【安全】重命名 PDF 文件
    """
    old_path = get_safe_pdf_path(old_filename)
    new_path = get_safe_pdf_path(new_filename)
    
    if not old_path or not new_path:
        return False
    
    if not os.path.exists(old_path):
        return False
    
    # 如果新文件名已存在，不覆盖
    if os.path.exists(new_path):
        return False
    
    try:
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        print(f"重命名文件失败: {e}")
        return False