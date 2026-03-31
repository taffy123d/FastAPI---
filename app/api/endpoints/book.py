"""
图书模块API接口
实现图书完整的增删改查（CRUD），演示路由、依赖、数据校验核心用法
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import os
import shutil

# 导入数据库依赖
from app.database.db import get_db
# 导入ORM模型
from app.models.book import Book
# 导入Pydantic模型
from app.schemas.book import BookCreate, BookUpdate, BookResponse

from app.utils.file_scanner import (
    get_all_pdf_files,
    BOOK_PDF_DIR,
    pdf_exists,
    delete_pdf_file,  # 新增
    rename_pdf_file   # 新增
)

# 创建子路由实例
# prefix：该模块所有接口的URL前缀，自动拼接
# tags：接口文档中的分类标签，自动分组
router = APIRouter(
    prefix="/books",
    tags=["图书管理接口"]
)

# 1. 查询所有图书
@router.get("/", response_model=list[BookResponse], summary="获取所有图书列表（支持搜索）")
async def get_all_books(
    keyword: str | None = None,  # 新增：搜索关键词
    db: AsyncSession = Depends(get_db)
):
    """
    查询数据库中所有的图书数据
    - keyword：可选，按书名模糊搜索
    """
    query = select(Book)
    
    # 如果有搜索关键词，添加 where 条件
    if keyword:
        query = query.where(Book.title.contains(keyword))
    
    result = await db.execute(query)
    books = result.scalars().all()
    return books

# 2. 根据ID查询单本图书
@router.get("/{book_id}", response_model=BookResponse, summary="根据ID查询图书详情")
async def get_book_by_id(
    book_id: int,  # 路径参数，自动校验为整数
    db: AsyncSession = Depends(get_db)
):
    """
    根据图书ID查询单本图书详情
    - book_id：图书主键ID
    - 404错误：图书不存在时返回
    """
    # 根据ID查询图书
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    # 图书不存在，抛出404异常
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{book_id}的图书不存在"
        )
    return book

# 3. 创建新图书
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, summary="创建新图书")
async def create_book(
    book_data: BookCreate,  # 请求体，自动按照BookCreate模型校验
    db: AsyncSession = Depends(get_db)
):
    """
    创建一本新的图书
    - book_data：符合BookCreate模型的JSON请求体
    - 400错误：图书名称已存在时返回
    - 201状态码：创建成功返回（资源创建成功标准状态码）
    """
    # 检查图书名称是否已存在，避免重复
    result = await db.execute(select(Book).where(Book.title == book_data.title))
    existing_book = result.scalar_one_or_none()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"图书《{book_data.title}》已存在"
        )

    # 创建ORM对象
    new_book = Book(**book_data.model_dump())
    # 添加到数据库会话
    db.add(new_book)
    # 提交事务
    await db.commit()
    # 刷新对象，获取数据库生成的ID
    await db.refresh(new_book)

    return new_book

# 4. 更新图书信息
@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )

    # 【新增】处理 PDF 文件名变更
    old_filename = book.filename
    new_filename = book_data.filename
    
    if old_filename != new_filename:
        # 如果传了新文件名，检查文件是否存在
        if new_filename and not pdf_exists(new_filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF 文件 {new_filename} 不存在"
            )
        
        # 如果只是想“取消关联”，不删除文件
        # 如果是“换一个文件”，也不删除旧文件（防止误删）
        # 如果你想“改文件名”，可以在前端加一个单独的“重命名文件”功能
        # 这里我们只做数据库字段更新，不自动重命名物理文件（防止逻辑混乱）
        pass

    # 更新字段
    update_data = book_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    return book

# 5. 删除图书
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 【新增】如果有关联 PDF，同时删除文件
    if book.filename:
        delete_pdf_file(book.filename)
    
    # 删除数据库记录
    await db.delete(book)
    await db.commit()
    
    return

# 【新增】上传 PDF 文件
@router.post("/upload", summary="上传PDF文件")
async def upload_pdf(file: UploadFile = File(...)):
    """
    上传 PDF 文件到 static/book 目录
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持上传 PDF 文件"
        )
    
    # 确保目录存在
    if not os.path.exists(BOOK_PDF_DIR):
        os.makedirs(BOOK_PDF_DIR)
    
    file_path = os.path.join(BOOK_PDF_DIR, file.filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "message": "上传成功"}


# 【新增】扫描文件夹并同步到数据库
@router.post("/scan-folder", summary="扫描PDF文件夹并同步数据库")
async def scan_and_sync(db: AsyncSession = Depends(get_db)):
    """
    扫描 static/book 目录，自动根据 PDF 文件名创建图书记录
    文件名格式：书名_作者.pdf 或 书名.pdf
    """
    pdf_files = get_all_pdf_files()
    
    # 查询数据库中已有的图书
    result = await db.execute(select(Book))
    existing_books = {book.filename: book for book in result.scalars().all() if book.filename}
    
    added_count = 0
    
    for filename in pdf_files:
        if filename not in existing_books:
            # 解析文件名：假设格式为 "书名_作者.pdf" 或 "书名.pdf"
            name_without_ext = filename[:-4]  # 去掉 .pdf
            
            if "_" in name_without_ext:
                title, author = name_without_ext.split("_", 1)
            else:
                title = name_without_ext
                author = "未知作者"
            
            # 创建新图书
            new_book = Book(
                title=title,
                author=author,
                price=0.0,
                description="自动扫描添加",
                filename=filename
            )
            db.add(new_book)
            added_count += 1
    
    await db.commit()
    
    return {
        "message": f"扫描完成，新增 {added_count} 本图书",
        "total_pdf": len(pdf_files),
        "added": added_count
    }




# 【修改】创建图书时支持关联 PDF
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db)
):
    # 如果传了 filename，检查文件是否存在
    if book_data.filename and not pdf_exists(book_data.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF 文件 {book_data.filename} 不存在，请先上传"
        )
    
    result = await db.execute(select(Book).where(Book.title == book_data.title))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"图书《{book_data.title}》已存在"
        )
    
    new_book = Book(**book_data.model_dump())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    
    return new_book


# 在 app/api/endpoints/book.py 最后添加

# 【新增】获取所有已上传的 PDF 文件列表
@router.get("/pdfs/list", summary="获取已上传的PDF文件列表")
async def get_pdf_list():
    """
    获取 static/book 目录下所有 PDF 文件名
    """
    from app.utils.file_scanner import get_all_pdf_files
    pdf_files = get_all_pdf_files()
    return {"pdfs": pdf_files}


# 【新增】重命名 PDF 文件
@router.post("/rename-pdf", summary="重命名PDF文件")
async def rename_pdf(
    old_filename: str,
    new_filename: str,
    db: AsyncSession = Depends(get_db)
):
    """
    重命名 PDF 文件，同时更新数据库中所有关联的图书记录
    """
    # 1. 安全检查
    if not old_filename or not new_filename:
        raise HTTPException(400, "文件名不能为空")
    
    if not new_filename.lower().endswith(".pdf"):
        raise HTTPException(400, "新文件名必须以 .pdf 结尾")
    
    # 2. 执行重命名
    if not rename_pdf_file(old_filename, new_filename):
        raise HTTPException(400, "重命名失败，请检查文件是否存在")
    
    # 3. 更新数据库中所有关联的图书
    result = await db.execute(select(Book).where(Book.filename == old_filename))
    books = result.scalars().all()
    
    for book in books:
        book.filename = new_filename
    
    await db.commit()
    
    return {
        "message": "重命名成功",
        "old_filename": old_filename,
        "new_filename": new_filename,
        "updated_books": len(books)
    }