"""
项目入口核心文件
"""

from app.database.db import get_db
from app.models.book import Book

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.future import select

# 导入项目配置
from app.core.config import (
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_DESCRIPTION,
    TEMPLATES_DIR,
    STATIC_DIR,
    STATIC_URL
)
# 导入汇总路由
from app.api.api_v1 import api_router
# 导入数据库启动函数与依赖
from app.database.db import create_tables, get_db
from app.models.book import Book

# 1. 创建FastAPI应用实例
app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    description=PROJECT_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 2. 挂载静态文件目录
app.mount(
    STATIC_URL,
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# 3. 初始化Jinja2模板引擎
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 4. 注册汇总路由
app.include_router(api_router)

# 5. 项目启动事件
@app.on_event("startup")
async def startup_event():
    print("===== FastAPI学习项目启动成功 =====")
    await create_tables()
    print("===== 数据库表创建完成 =====")

# 6. 模板渲染接口：项目首页（【关键修复】request 作为第一个参数）
@app.get("/", response_class=HTMLResponse, summary="项目首页-模板渲染演示")
async def index(request: Request):
    """
    演示Jinja2模板渲染基础用法
    """
    # 【核心修复】TemplateResponse 的第一个参数必须是 request
    return templates.TemplateResponse(
        request,  # 【关键】必须放在第一位
        "index.html",
        {
            "project_name": PROJECT_NAME,
            "project_version": PROJECT_VERSION
        }
    )

# 7. 模板渲染接口：图书列表页（【关键修复】request 作为第一个参数）
# 修改 main.py 里的 book_list_page

@app.get("/book-list", response_class=HTMLResponse, summary="图书列表页-模板+数据库演示")
async def book_list_page(
    request: Request,
    keyword: str | None = None,  # 新增：接收搜索关键词
    db: AsyncSession = Depends(get_db)
):
    """
    演示模板渲染与数据库查询结合
    支持按书名搜索
    """
    # 查询图书（支持搜索）
    query = select(Book)
    if keyword:
        query = query.where(Book.title.contains(keyword))
    
    result = await db.execute(query)
    books = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="book_list.html",
        context={
            "books": books,
            "keyword": keyword  # 传给模板，用于回填搜索框
        }
    )


# 在 main.py 最后添加

# 新增/编辑图书页面
@app.get("/book-form", response_class=HTMLResponse, summary="图书表单页")
# 新增/编辑图书页面
@app.get("/book-form", response_class=HTMLResponse, summary="图书表单页")
async def book_form_page(
    request: Request,
    book_id: int | None = None,
    db: AsyncSession = Depends(get_db)  # 直接用依赖注入，不要自己写循环
):
    """
    渲染图书表单页面
    - 如果传了 book_id，就是编辑模式，会先查询图书数据
    - 如果没传，就是新增模式
    """
    book = None
    if book_id:
        # 编辑模式：从数据库查这本书
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()

    # 【关键修复】TemplateResponse 第一个参数必须是 request
    return templates.TemplateResponse(
        request=request,  # 显式传入 request
        name="book_form.html",
        context={
            "book": book,
            "is_edit": book is not None
        }
    )