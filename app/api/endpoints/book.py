"""
图书模块API接口
实现图书完整的增删改查（CRUD），演示路由、依赖、数据校验核心用法
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 导入数据库依赖
from app.database.db import get_db
# 导入ORM模型
from app.models.book import Book
# 导入Pydantic模型
from app.schemas.book import BookCreate, BookUpdate, BookResponse

# 创建子路由实例
# prefix：该模块所有接口的URL前缀，自动拼接
# tags：接口文档中的分类标签，自动分组
router = APIRouter(
    prefix="/books",
    tags=["图书管理接口"]
)

# 1. 查询所有图书
# @router.get("/", response_model=list[BookResponse], summary="获取所有图书列表")
# async def get_all_books(db: AsyncSession = Depends(get_db)):
#     """
#     查询数据库中所有的图书数据
#     - 返回值：符合BookResponse模型的图书数组
#     """
#     # 执行异步查询
#     result = await db.execute(select(Book))
#     # 提取查询结果
#     books = result.scalars().all()
#     return books

# 修改 app/api/endpoints/book.py 里的 get_all_books

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
@router.put("/{book_id}", response_model=BookResponse, summary="更新图书信息")
async def update_book(
    book_id: int,
    book_data: BookUpdate,  # 更新的请求体，所有字段可选
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID更新图书信息，支持部分更新
    - book_id：要更新的图书ID
    - book_data：仅传入需要修改的字段即可
    - 404错误：图书不存在时返回
    """
    # 查询要更新的图书
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{book_id}的图书不存在"
        )

    # 仅更新传入的字段
    update_data = book_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)

    # 提交事务
    await db.commit()
    # 刷新对象
    await db.refresh(book)

    return book

# 5. 删除图书
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除图书")
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID删除图书
    - book_id：要删除的图书ID
    - 404错误：图书不存在时返回
    - 204状态码：删除成功返回（无内容标准状态码）
    """
    # 查询要删除的图书
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID为{book_id}的图书不存在"
        )

    # 删除图书
    await db.delete(book)
    # 提交事务
    await db.commit()

    return
