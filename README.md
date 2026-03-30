# FastAPI 学习项目 - 图书管理系统

大学生自学 FastAPI 入门打造的完整学习项目，覆盖路由分发、接口文档、数据库集成、模板渲染等核心知识点，工程化结构设计，代码全注释，极简业务逻辑，让你快速掌握 FastAPI 的核心用法。

## 功能特性

- ✅ **路由分发与模块化开发**：按业务模块拆分接口，实现代码解耦
- ✅ **自动生成交互式接口文档**：Swagger UI + ReDoc 双文档支持
- ✅ **Request 对象全用法演示**：获取请求的所有信息
- ✅ **静态文件挂载与访问**：支持 CSS、图片、JS 等静态资源
- ✅ **Jinja2 模板渲染**：包含模板继承、变量渲染、循环等
- ✅ **SQLite 数据库集成**：使用 SQLAlchemy 2.0 异步 ORM
- ✅ **Pydantic 数据校验**：自动请求体校验与响应格式化
- ✅ **依赖注入系统**：实现数据库会话等依赖的自动管理
- ✅ **完整 CRUD 接口**：图书的增删改查全流程演示

## 技术栈

- **Web 框架**：FastAPI
- **数据库**：SQLite（文件型数据库，无需额外安装）
- **ORM**：SQLAlchemy 2.0（异步）
- **模板引擎**：Jinja2
- **ASGI 服务器**：Uvicorn
- **包管理工具**：uv

## 项目结构

```
fastapi_learn_project/
├── app/                          # 项目核心代码包
│   ├── __init__.py
│   ├── main.py                   # 项目入口
│   ├── core/                     # 全局配置
│   │   ├── __init__.py
│   │   └── config.py             # 项目常量与配置
│   ├── database/                 # 数据库相关
│   │   ├── __init__.py
│   │   └── db.py                 # 数据库连接与会话管理
│   ├── models/                   # ORM 模型
│   │   ├── __init__.py
│   │   └── book.py               # 图书表模型
│   ├── schemas/                  # Pydantic 模型
│   │   ├── __init__.py
│   │   └── book.py               # 图书数据模型
│   ├── api/                      # 路由分发
│   │   ├── __init__.py
│   │   ├── api_v1.py             # 路由汇总注册
│   │   └── endpoints/            # 业务接口
│   │       ├── __init__.py
│   │       ├── book.py           # 图书 CRUD 接口
│   │       └── common.py         # 通用接口
│   ├── templates/                # Jinja2 模板
│   │   ├── base.html             # 基础模板
│   │   ├── index.html            # 首页
│   │   └── book_list.html        # 图书列表页
│   └── static/                   # 静态文件
│       └── css/
│           └── style.css         # 页面样式
├── .gitignore
├── pyproject.toml                # uv 项目配置文件
└── README.md                     # 项目说明文档
```

## 快速开始

### 前置要求

- Python 3.8+
- uv 包管理工具（如果未安装，可通过以下命令安装）：
  ```bash
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  
  # Mac/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 安装与运行

1. **克隆/下载项目**
   ```bash
   cd fastapi_learn_project
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   # uv 会自动创建虚拟环境并安装 pyproject.toml 中的依赖
   uv sync
   ```

3. **启动开发服务器**
   ```bash
   # 使用 uv 运行 uvicorn
   uv run uvicorn app.main:app --reload
   ```

4. **访问项目**
   启动成功后，在浏览器中访问以下地址：
   - 项目首页：http://127.0.0.1:8000
   - 交互式接口文档：http://127.0.0.1:8000/docs
   - ReDoc 规范文档：http://127.0.0.1:8000/redoc
   - 图书列表页：http://127.0.0.1:8000/book-list

## 使用指南

### 1. 接口调试
访问 `http://127.0.0.1:8000/docs`，在 Swagger UI 中可以直接调试所有接口：
- 点击任意接口展开详情
- 点击「Try it out」
- 填写参数后点击「Execute」发送请求
- 查看响应结果

### 2. 学习顺序建议
1. 先启动项目，访问首页和接口文档，熟悉整体功能
2. 从 `app/main.py` 开始，理解项目入口和全局配置
3. 学习 `app/api/endpoints/` 下的接口，掌握路由和 CRUD 操作
4. 研究 `app/schemas/` 和 `app/models/`，理解 Pydantic 和 ORM 模型
5. 查看 `app/database/db.py`，掌握数据库连接和依赖注入
6. 最后了解模板渲染和静态文件的使用

## uv 常用命令

```bash
# 安装依赖
uv add <package_name>

# 安装开发依赖
uv add --dev <package_name>

# 移除依赖
uv remove <package_name>

# 同步依赖（安装 pyproject.toml 中的所有依赖）
uv sync

# 运行 Python 脚本
uv run python <script.py>

# 运行项目命令
uv run uvicorn app.main:app --reload

# 查看已安装的依赖
uv pip list
```

## 学习路线

1. **路由与请求处理**：学习路径参数、查询参数、请求体
2. **数据校验**：掌握 Pydantic 模型的使用
3. **数据库操作**：学习 SQLAlchemy ORM 的异步 CRUD
4. **依赖注入**：理解 FastAPI 的依赖系统
5. **模板渲染**：掌握 Jinja2 模板的使用
6. **接口文档**：利用自动生成的文档辅助开发

## 贡献

欢迎提交 Issue 和 Pull Request！
