# 图书管理系统 CLI 工具使用文档

CLI 工具提供了命令行接口来管理图书和 PDF 文件，通过 FastAPI 接口进行操作。

## 安装要求

### 1. 安装 Python 依赖

CLI 工具需要 `requests` 库来发送 HTTP 请求。如果尚未安装，可以使用以下命令安装：

```bash
# 使用 uv（推荐）
uv add requests

# 或使用 pip
pip install requests
```

### 2. 启动 FastAPI 服务器

在使用 CLI 之前，需要启动 FastAPI 服务器：

```bash
# 在项目根目录执行
uv run uvicorn app.main:app --reload
```

服务器启动后，默认地址为 `http://127.0.0.1:8000`。

## CLI 工具基本用法

```bash
# 查看帮助信息
python cli.py --help

# 查看具体命令的帮助
python cli.py <command> --help
```

### 全局选项

- `--base-url`: 指定 FastAPI 服务器地址（默认: `http://127.0.0.1:8000`）

```bash
# 示例：连接到不同端口的服务器
python cli.py --base-url http://localhost:8080 query
```

### 配置文件

CLI 工具支持配置文件，用于保存默认的基础 URL，避免每次使用时都需要指定 `--base-url` 选项。

配置文件位于：`~/.book_cli/config.json`

**配置优先级（从高到低）：**
1. 命令行选项 `--base-url`
2. 配置文件中的 `base_url` 设置
3. 环境变量 `BOOK_API_BASE_URL`
4. 默认值 `http://127.0.0.1:8000`

**配置管理命令：**
- `config set-base-url <url>`: 设置默认基础 URL
- `config get-base-url`: 查看当前配置的基础 URL

**示例：**
```bash
# 设置默认服务器地址
python cli.py config set-base-url http://localhost:8000

# 查看当前配置
python cli.py config get-base-url

# 使用配置文件中的地址查询图书（无需 --base-url）
python cli.py query
```

## 命令详解

### 1. 查询图书 (`query`)

查询图书列表或查看图书详情。

```bash
# 查询所有图书
python cli.py query

# 按关键词搜索图书
python cli.py query --keyword "数学"

# 查看特定图书的详细信息
python cli.py query --book-id 1
```

**输出示例：**
```
找到 3 本图书:
--------------------------------------------------------------------------------
ID:   1 | 代数学方法                  | 李文威           | ¥  0.00 | 📎 代数学方法(第一卷) 基础架构 (李文威) (Z-Library).pdf
ID:   2 | 矩阵论                      | 戴华             | ¥  0.00 | 📎 矩阵论 (戴华) (Z-Library).pdf
ID:   3 | 计算机组成原理              | 唐朔飞           | ¥  0.00 | 📎 计算机组成原理第3版 (唐朔飞) (Z-Library).pdf
--------------------------------------------------------------------------------
```

### 2. 上传 PDF 文件 (`upload`)

上传 PDF 文件到服务器。

```bash
# 上传单个 PDF 文件
python cli.py upload --file "路径/到/文件.pdf"
```

**注意事项：**
- 只支持 PDF 格式文件
- 文件将被保存到 `app/static/book/` 目录
- 上传后可通过 `list-pdfs` 命令查看

### 3. 下载 PDF 文件 (`download`)

下载图书关联的 PDF 文件。

```bash
# 通过图书 ID 下载
python cli.py download --book-id 1 --output "./downloads/"

# 通过文件名下载
python cli.py download --filename "矩阵论 (戴华) (Z-Library).pdf" --output "."
```

**参数说明：**
- `--book-id`: 图书 ID（优先使用，会自动获取关联的文件名）
- `--filename`: 直接指定 PDF 文件名
- `--output`: 下载目录（默认: 当前目录）

### 4. 删除图书 (`delete`)

删除图书及其关联的 PDF 文件。

```bash
# 删除指定图书
python cli.py delete --book-id 1
```

**安全机制：**
- 删除前会显示图书信息并要求确认
- 如果图书关联了 PDF 文件，该文件也会被删除
- 输入 `yes` 确认删除，其他输入取消操作

### 5. 扫描 PDF 文件夹 (`scan`)

扫描 `app/static/book/` 目录中的 PDF 文件，并自动创建图书记录。

```bash
# 扫描并同步到数据库
python cli.py scan
```

**功能说明：**
- 自动解析文件名格式：`书名_作者.pdf` 或 `书名.pdf`
- 只创建数据库中不存在的图书记录
- 不会删除已存在的记录

### 6. 列出 PDF 文件 (`list-pdfs`)

查看所有已上传的 PDF 文件。

```bash
# 列出所有 PDF 文件
python cli.py list-pdfs
```

**输出示例：**
```
找到 3 个 PDF 文件:
  1. 代数学方法(第一卷) 基础架构 (李文威) (Z-Library).pdf
     下载链接: http://127.0.0.1:8000/static/book/代数学方法(第一卷) 基础架构 (李文威) (Z-Library).pdf
  2. 矩阵论 (戴华) (Z-Library).pdf
     下载链接: http://127.0.0.1:8000/static/book/矩阵论 (戴华) (Z-Library).pdf
  3. 计算机组成原理第3版 (唐朔飞) (Z-Library).pdf
     下载链接: http://127.0.0.1:8000/static/book/计算机组成原理第3版 (唐朔飞) (Z-Library).pdf
```

### 7. 配置 CLI 工具 (`config`)

管理 CLI 工具的配置，包括默认基础 URL。

#### 子命令

**set-base-url**：设置默认基础 URL
```bash
# 设置默认服务器地址
python cli.py config set-base-url http://localhost:8000
```

**get-base-url**：查看当前配置的基础 URL
```bash
# 查看当前配置
python cli.py config get-base-url
```

**功能说明：**
- 配置保存在 `~/.book_cli/config.json` 文件中
- 设置后，在未使用 `--base-url` 选项时会自动使用配置的地址
- 使用 `config get-base-url` 可以查看当前的配置值，以及环境变量和默认值信息

## 使用示例

### 完整工作流程

```bash
# 1. 启动服务器（在另一个终端）
uv run uvicorn app.main:app --reload

# 2. 查询现有图书
python cli.py query

# 3. 上传新图书的 PDF
python cli.py upload --file "新书.pdf"

# 4. 扫描文件夹，自动创建图书记录
python cli.py scan

# 5. 查看新增的图书
python cli.py query --keyword "新书"

# 6. 下载图书的 PDF
python cli.py download --book-id 5 --output "./my_books/"

# 7. 删除不需要的图书
python cli.py delete --book-id 3
```

### 批量操作示例

```bash
# 批量上传多个 PDF 文件（使用 shell 循环）
for pdf in ./books/*.pdf; do
    python cli.py upload --file "$pdf"
done

# 扫描并同步
python cli.py scan

# 导出所有 PDF 文件
python cli.py list-pdfs | grep "下载链接" | awk '{print $2}' > pdf_urls.txt
```

## 故障排除

### 常见问题

1. **连接失败：无法连接到服务器**
   ```
   错误: 无法连接到服务器 http://127.0.0.1:8000/api/v1/books
   请确保 FastAPI 服务器正在运行（使用 `uv run uvicorn app.main:app --reload`）
   ```
   **解决方案：** 启动 FastAPI 服务器。

2. **API 错误：404 资源未找到**
   ```
   API 错误: 404 Client Error: Not Found for url: ...
   资源未找到，请检查 ID 是否正确
   ```
   **解决方案：** 检查图书 ID 是否正确，使用 `query` 命令查看可用图书。

3. **API 错误：400 请求参数错误**
   ```
   API 错误: 400 Client Error: Bad Request for url: ...
   请求参数错误
   ```
   **解决方案：** 检查命令参数是否正确，确保 PDF 文件格式正确。

4. **导入错误：No module named 'requests'**
   ```
   ModuleNotFoundError: No module named 'requests'
   ```
   **解决方案：** 安装 requests 库：`uv add requests`

### 调试模式

要查看详细的 HTTP 请求信息，可以修改 `cli.py` 文件，在 `_make_request` 方法中添加调试输出：

```python
def _make_request(self, method: str, endpoint: str, **kwargs):
    url = f"{self.api_base}{endpoint}"
    print(f"调试: {method} {url}")  # 添加这行
    # ... 其余代码
```

## API 接口对应关系

CLI 命令与 FastAPI 接口的对应关系：

| CLI 命令 | HTTP 方法 | API 端点 | 功能说明 |
|----------|-----------|----------|----------|
| `query` | GET | `/api/v1/books` | 查询图书列表 |
| `query --book-id` | GET | `/api/v1/books/{id}` | 查询图书详情 |
| `upload` | POST | `/api/v1/books/upload` | 上传 PDF 文件 |
| `delete` | DELETE | `/api/v1/books/{id}` | 删除图书 |
| `scan` | POST | `/api/v1/books/scan-folder` | 扫描 PDF 文件夹 |
| `list-pdfs` | GET | `/api/v1/books/pdfs/list` | 列出 PDF 文件 |

## 进阶使用

### 配置管理

CLI 工具支持多种配置方式，优先级从高到低如下：

1. **命令行选项** `--base-url`
2. **配置文件** `~/.book_cli/config.json` 中的 `base_url` 设置
3. **环境变量** `BOOK_API_BASE_URL`
4. **默认值** `http://127.0.0.1:8000`

#### 环境变量配置

可以设置环境变量来指定默认服务器地址：

```bash
# 设置环境变量（Linux/macOS）
export BOOK_API_BASE_URL="http://localhost:8000"

# 设置环境变量（Windows PowerShell）
$env:BOOK_API_BASE_URL="http://localhost:8000"

# CLI 会自动使用环境变量
python cli.py query
```

#### 配置文件配置

可以使用 `config` 命令管理配置文件：

```bash
# 设置默认服务器地址
python cli.py config set-base-url http://localhost:8000

# 查看当前配置
python cli.py config get-base-url
```

配置文件位置：`~/.book_cli/config.json`

### 脚本集成

### 脚本集成

将 CLI 工具集成到其他脚本中：

```python
#!/usr/bin/env python3
import subprocess
import sys

def upload_pdfs_from_directory(directory: str):
    """批量上传目录中的所有 PDF 文件"""
    import glob
    
    for pdf_file in glob.glob(f"{directory}/*.pdf"):
        print(f"上传: {pdf_file}")
        result = subprocess.run([
            sys.executable, 'cli.py', 'upload', '--file', pdf_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  成功: {result.stdout}")
        else:
            print(f"  失败: {result.stderr}")

if __name__ == "__main__":
    upload_pdfs_from_directory("./books")
```

## 贡献与反馈

如果发现 bug 或有功能建议，请通过以下方式反馈：

1. 检查现有问题
2. 提交新的 issue
3. 提出改进建议

**注意：** 使用 CLI 工具前请确保已备份重要数据，删除操作不可恢复。