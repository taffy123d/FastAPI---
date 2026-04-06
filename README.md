# FastAPI 学习项目 - PDF 图书管理系统
专为 FastAPI 入门打造的完整学习项目，现已升级为**完整的 PDF 图书管理系统**！
覆盖**路由分发、接口文档、Request 对象、静态文件、模板渲染、SQLite 数据库、文件上传、PDF 在线预览/下载**等核心知识点。
工程结构清晰、代码注释详尽、业务逻辑极简，专注让你快速掌握 FastAPI 开发全流程。

---
## 新增
- cli工具，暴露cli接口可供调试或agent调用 详见CLI_README.md

## 项目特性
- ✅ 标准工程化目录结构，适合学习与扩展
- ✅ 路由分发与模块化接口管理
- ✅ 自动生成交互式 API 文档（Swagger / ReDoc）
- ✅ Pydantic 数据校验与响应格式化
- ✅ SQLite + SQLAlchemy 异步 ORM 操作
- ✅ Jinja2 模板渲染 + 静态文件支持
- ✅ 完整图书 CRUD 增删改查接口
- ✅ 依赖注入、请求对象、异常处理实战
- ✅ **PDF 文件上传功能**
- ✅ **自动扫描文件夹并同步数据库**
- ✅ **PDF 在线预览（浏览器直接打开）**
- ✅ **PDF 在线下载**
- ✅ **图书与 PDF 文件关联管理**

## 技术栈
- **框架**：FastAPI
- **服务器**：Uvicorn
- **数据库**：SQLite（文件数据库，无需额外安装）
- **ORM**：SQLAlchemy 2.0（异步）
- **模板**：Jinja2
- **包管理**：uv
- **文件上传**：python-multipart

## 项目结构
```
fastapi_learn_project/
├── app/
│   ├── main.py                 # 项目入口，创建 app、注册路由
│   ├── core/
│   │   └── config.py           # 全局配置（数据库、路径、项目信息）
│   ├── database/
│   │   └── db.py               # 数据库引擎、会话、建表函数
│   ├── models/
│   │   └── book.py             # ORM 模型（对应数据库表）
│   ├── schemas/
│   │   └── book.py             # Pydantic 模型（请求校验 + 响应格式）
│   ├── api/
│   │   ├── api_v1.py           # v1 版本路由汇总
│   │   └── endpoints/
│   │       ├── book.py         # 图书 CRUD + PDF 管理接口
│   │       └── common.py       # 通用接口（Request 演示）
│   ├── utils/
│   │   └── file_scanner.py     # PDF 文件扫描工具
│   ├── templates/              # HTML 模板文件
│   └── static/
│       ├── css/
│       └── book/               # PDF 文件存放目录
├── pyproject.toml              # uv 依赖管理
└── README.md
```

---

## 快速启动（uv 包管理）
### 1. 安装依赖
```bash
uv sync
```

### 2. 确保目录存在
在 `app/static/` 下创建 `book` 文件夹（用于存放 PDF）：
```
app/static/book/
```

### 3. 启动项目
```bash
uv run uvicorn app.main:app --reload
```

### 4. 访问地址
- 项目首页：http://127.0.0.1:8000
- **PDF 图书管理页面**：http://127.0.0.1:8000/book-list
- **Swagger 接口文档**：http://127.0.0.1:8000/docs
- ReDoc 接口文档：http://127.0.0.1:8000/redoc

---

# 📖 接口文档详细使用说明（/docs）
打开 `http://127.0.0.1:8000/docs` 即可看到所有接口，支持**在线调试、参数填写、响应查看**。

## 一、通用操作步骤（所有接口一致）
1. 点击任意接口右侧 **「Try it out」**
2. 填写路径参数 / 请求体参数
3. 点击 **「Execute」** 发送请求
4. 查看 **Responses** 中的状态码与返回数据

---

## 二、图书管理接口（/api/v1/books）
### 1. 获取所有图书（支持搜索）
- **方法**：GET
- **路径**：`/api/v1/books/`
- **查询参数**：
  - `keyword`（可选）：按书名模糊搜索
- **作用**：查询数据库中所有图书
- **成功响应**：200

---

### 2. 根据 ID 获取单本图书
- **方法**：GET
- **路径**：`/api/v1/books/{book_id}`
- **参数**：
  - `book_id`：路径参数，图书 ID（数字）
- **成功响应**：200 + 图书信息
- **失败响应**：404 图书不存在

---

### 3. 新增图书
- **方法**：POST
- **路径**：`/api/v1/books/`
- **请求体示例**
```json
{
  "title": "Python快速入门",
  "author": "张三",
  "price": 59.9,
  "description": "适合零基础学习Python",
  "filename": "Python入门_张三.pdf"
}
```
- **必填字段**：`title`、`author`、`price`
- **可选字段**：`description`、`filename`（PDF 文件名）
- **注意**：如果传了 `filename`，该 PDF 文件必须已上传
- **成功响应**：201 Created

---

### 4. 更新图书信息
- **方法**：PUT
- **路径**：`/api/v1/books/{book_id}`
- **路径参数**：`book_id`
- **请求体示例（可只传需要修改的字段）**
```json
{
  "price": 69.9,
  "filename": "新的文件名.pdf"
}
```
- **成功响应**：200
- **失败响应**：404

---

### 5. 删除图书
- **方法**：DELETE
- **路径**：`/api/v1/books/{book_id}`
- **成功响应**：204 No Content

---

## 三、PDF 管理接口（新增）
### 1. 上传 PDF 文件
- **方法**：POST
- **路径**：`/api/v1/books/upload`
- **参数**：`file`（Form Data，文件类型）
- **说明**：上传 PDF 文件到 `app/static/book/` 目录
- **成功响应**：200
  ```json
  {
    "filename": "Python入门_张三.pdf",
    "message": "上传成功"
  }
  ```

---

### 2. 扫描 PDF 文件夹并同步数据库
- **方法**：POST
- **路径**：`/api/v1/books/scan-folder`
- **说明**：
  - 自动扫描 `app/static/book/` 目录
  - 根据 PDF 文件名自动创建图书记录
  - 文件名格式建议：`书名_作者.pdf` 或 `书名.pdf`
- **成功响应**：200
  ```json
  {
    "message": "扫描完成，新增 3 本图书",
    "total_pdf": 5,
    "added": 3
  }
  ```

---

### 3. 获取已上传的 PDF 文件列表
- **方法**：GET
- **路径**：`/api/v1/books/pdfs/list`
- **说明**：获取 `app/static/book/` 目录下所有 PDF 文件名
- **成功响应**：200
  ```json
  {
    "pdfs": [
      "Python入门_张三.pdf",
      "FastAPI教程.pdf"
    ]
  }
  ```

---

## 四、通用接口（/api/v1/common）
### 获取请求信息
- **方法**：GET
- **路径**：`/api/v1/common/request-info`
- **作用**：演示 Request 对象用法

---

## 五、页面接口
### 1. 首页
- GET `/`
- 返回 HTML 首页

### 2. PDF 图书管理页面
- GET `/book-list`
- **功能**：
  - 查看所有图书
  - 按书名搜索
  - 上传 PDF
  - 扫描文件夹
  - 在线预览 PDF
  - 在线下载 PDF
  - 新增/编辑/删除图书

### 3. 新增/编辑图书表单页
- GET `/book-form`
- GET `/book-form?book_id=1`
- **功能**：
  - 录入/修改图书信息
  - 下拉选择已上传的 PDF 文件

---

## 六、PDF 访问地址（直接访问）
- **在线预览**：`http://127.0.0.1:8000/static/book/文件名.pdf`
- **在线下载**：同上，浏览器会自动处理

---

## 七、常见状态码说明
- **200**：请求/查询/修改成功
- **201**：资源创建成功
- **204**：删除成功
- **400**：参数错误/数据重复/PDF 文件不存在
- **404**：资源不存在
- **422**：请求体格式/类型校验失败

---

## 前端使用指南（图书管理页面）
### 1. 上传 PDF
1. 点击右上角 **「📤 上传 PDF」**
2. 选择 PDF 文件
3. 点击「上传」

### 2. 扫描文件夹（自动创建图书）
1. 确保 PDF 已放入 `app/static/book/` 或已通过页面上传
2. 点击 **「📂 扫描文件夹」**
3. 系统自动根据文件名创建图书记录
4. 文件名建议：`书名_作者.pdf`

### 3. 在线预览/下载 PDF
- 点击图书卡片上的 **「👁️ 预览」**：浏览器新标签页打开 PDF
- 点击 **「⬇️ 下载」**：下载 PDF 文件到本地

### 4. 手动关联 PDF
1. 点击「新增图书」或「编辑」
2. 在「关联 PDF 文件」下拉框中选择已上传的 PDF
3. 保存后即可在列表页看到预览/下载按钮

---

## 学习建议
1. 先启动项目，访问 `/book-list` 熟悉 PDF 管理功能
2. 尝试上传一个 PDF，然后扫描文件夹，观察自动创建图书的效果
3. 访问 `/docs` 调试所有接口，理解后端逻辑
4. 对照代码理解：文件上传 → 扫描同步 → 关联管理 → 预览下载
5. 尝试修改代码，比如：删除图书时同时删除 PDF 文件、增加 PDF 封面图等

---

## uv 常用命令
```bash
# 安装依赖
uv sync

# 新增依赖包
uv add 包名

# 启动项目
uv run uvicorn app.main:app --reload

# 查看已安装包
uv pip list
```