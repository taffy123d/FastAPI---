# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

### 依赖管理
项目使用 `uv` 进行依赖管理（`pyproject.toml` 和 `uv.lock`）。

- 安装依赖：`uv sync`
- 添加新包：`uv add <package-name>`
- 查看已安装包：`uv pip list`

### 开发服务器
- 启动开发服务器（自动重载）：`uv run uvicorn app.main:app --reload`
- 无重载启动：`uv run uvicorn app.main:app`

### 数据库
- SQLite 数据库文件：`learn.db`（位于项目根目录）
- 数据库表在应用启动时自动创建（通过 `app.database.db.create_tables`）

### 访问地址
- 项目首页：http://127.0.0.1:8000
- 图书管理页面：http://127.0.0.1:8000/book-list
- Swagger API 文档：http://127.0.0.1:8000/docs
- ReDoc API 文档：http://127.0.0.1:8000/redoc

### 命令行工具 (CLI)
项目提供了命令行工具 `cli.py`，用于通过终端管理图书和 PDF 文件。

**安装 CLI 依赖：**
```bash
uv add requests
```

**基本用法：**
```bash
# 查看帮助
python cli.py --help

# 查询图书
python cli.py query --keyword "数学"

# 上传 PDF
python cli.py upload --file "book.pdf"

# 下载 PDF
python cli.py download --book-id 1 --output "./downloads/"

# 删除图书
python cli.py delete --book-id 1

# 扫描 PDF 文件夹
python cli.py scan

# 列出所有 PDF 文件
python cli.py list-pdfs
```

**详细文档：** 参见 [CLI_README.md](CLI_README.md)

## 项目架构

### 技术栈
- **框架**：FastAPI
- **服务器**：Uvicorn
- **数据库**：SQLite（文件数据库）
- **ORM**：SQLAlchemy 2.0（异步）
- **模板引擎**：Jinja2
- **包管理**：uv

### 目录结构
```
app/
├── main.py                 # 应用入口，创建FastAPI实例、挂载静态文件、模板渲染路由
├── core/
│   └── config.py          # 全局配置（数据库URL、项目信息、路径常量）
├── database/
│   └── db.py              # 数据库引擎、会话工厂、表创建函数、依赖注入
├── models/
│   └── book.py            # SQLAlchemy ORM 模型（Book 表）
├── schemas/
│   └── book.py            # Pydantic 模型（请求/响应数据校验）
├── api/
│   ├── api_v1.py          # v1 版本路由汇总（前缀 /api/v1）
│   └── endpoints/
│       ├── book.py        # 图书管理接口（CRUD + PDF 上传/扫描）
│       └── common.py      # 通用接口（请求信息演示）
├── utils/
│   └── file_scanner.py    # PDF 文件扫描工具（安全文件操作）
├── templates/             # Jinja2 HTML 模板
└── static/
    ├── css/               # 样式文件
    ├── js/                # JavaScript 文件
    └── book/              # PDF 文件存储目录
```

### 核心设计模式

#### 1. 配置集中管理
所有常量配置集中在 `app/core/config.py`，包括：
- 项目元数据（名称、版本、描述）
- 数据库连接 URL
- 模板和静态文件路径
- 静态文件 URL 前缀

#### 2. 数据库异步会话管理
- `AsyncSessionLocal` 会话工厂在 `app/database/db.py` 中定义
- 依赖注入函数 `get_db()` 为每个请求提供独立的数据库会话
- 自动提交/回滚，请求结束后自动关闭会话

#### 3. 路由版本化与模块化
- API 版本前缀：`/api/v1`
- 路由汇总：`api_v1.py` 统一注册所有端点路由
- 业务模块分离：图书管理 (`book.py`) 和通用接口 (`common.py`) 分开

#### 4. 数据校验与序列化
- **Pydantic 模型** (`schemas/book.py`)：定义请求/响应数据结构
  - `BookCreate`：创建图书的必需字段
  - `BookUpdate`：更新图书的部分字段（可选）
  - `BookResponse`：响应格式，包含自动生成的 ID
- **ORM 模型** (`models/book.py`)：定义数据库表结构
- 自动转换：FastAPI 自动将 ORM 对象序列化为 Pydantic 响应

#### 5. 静态文件与模板服务
- 静态文件挂载：`/static` URL 前缀指向 `app/static/` 目录
- PDF 文件存储：`app/static/book/` 目录存放上传的 PDF
- 模板渲染：Jinja2 模板位于 `app/templates/`，通过 `templates.TemplateResponse` 渲染

#### 6. 文件操作安全
`app/utils/file_scanner.py` 提供安全的文件操作功能：
- 路径安全检查：防止目录遍历攻击
- PDF 文件存在性检查
- 安全删除和重命名操作
- 自动扫描 PDF 文件夹并同步到数据库

### 关键工作流程

#### 图书管理流程
1. **上传 PDF** → `POST /api/v1/books/upload`
2. **扫描文件夹** → `POST /api/v1/books/scan-folder`（根据文件名自动创建图书）
3. **手动关联**：创建/编辑图书时选择已上传的 PDF 文件
4. **在线预览**：直接访问 `/static/book/文件名.pdf`
5. **删除图书**：如果有关联 PDF，同时删除物理文件

#### 数据库操作流程
1. 路由函数通过 `db: AsyncSession = Depends(get_db)` 注入会话
2. 使用 `select(Book)` 构建查询
3. 执行查询：`await db.execute(query)`
4. 获取结果：`result.scalars().all()` 或 `result.scalar_one_or_none()`
5. 提交事务：`await db.commit()`
6. 刷新对象：`await db.refresh(obj)`（获取数据库生成的值）

### 注意事项

#### 安全性
- 文件上传：检查文件扩展名，仅允许 PDF
- 文件路径：使用 `os.path.basename` 防止路径遍历
- 数据库：使用参数化查询（SQLAlchemy 自动处理）

#### 性能
- 异步操作：所有数据库操作使用异步 SQLAlchemy
- 连接池：SQLAlchemy 引擎默认包含连接池
- 静态文件：FastAPI 静态文件服务适合中小文件

#### 开发便利性
- 自动重载：开发时使用 `--reload` 标志
- SQL 日志：数据库引擎配置 `echo=True`（开发环境）
- 交互式文档：Swagger UI 支持在线测试 API

### 扩展建议
1. **添加测试**：创建 `tests/` 目录，使用 `pytest` 和 `httpx.AsyncClient`
2. **环境配置**：使用环境变量替代硬编码配置（如数据库路径）
3. **错误处理**：自定义异常处理器统一错误响应格式
4. **身份验证**：添加 JWT 或 OAuth2 保护敏感接口
5. **前端优化**：使用现代前端框架（如 Vue.js/React）替换 Jinja2 模板

### 故障排查
- **数据库连接失败**：检查 `learn.db` 文件权限
- **静态文件 404**：确认 `app/static/book/` 目录存在
- **模板渲染错误**：检查模板文件语法和上下文变量
- **文件上传失败**：检查目录权限和磁盘空间