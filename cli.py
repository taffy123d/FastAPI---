#!/usr/bin/env python3
"""
图书管理系统 CLI 工具

通过 FastAPI 接口管理图书和 PDF 文件。
支持上传、下载、删除、查询图书以及扫描 PDF 文件夹。

使用方法：
    python cli.py [全局选项] 命令 [命令选项]

示例：
    python cli.py query --keyword "数学"
    python cli.py upload --file "book.pdf"
    python cli.py download --book-id 1 --output "./downloads/"
"""

import argparse
import sys
import os
import json
import subprocess
from typing import Optional, List, Dict, Any
from pathlib import Path

# 尝试导入 requests，如果失败则提供安装指引
try:
    import requests
except ImportError:
    print("错误: 需要 requests 库但未安装")
    print("请使用以下命令安装:")
    print("  uv add requests")
    print("或")
    print("  pip install requests")
    sys.exit(1)

# 默认 API 基础 URL，支持环境变量覆盖
DEFAULT_BASE_URL = os.getenv('BOOK_API_BASE_URL', 'http://127.0.0.1:8000')
API_PREFIX = "/api/v1"

# 配置文件路径
CONFIG_DIR = Path('.book_cli')
CONFIG_FILE = CONFIG_DIR / 'config.json'


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_base_url_from_config() -> Optional[str]:
    """从配置文件中获取基础 URL"""
    config = load_config()
    return config.get('base_url')


def set_base_url_to_config(base_url: str) -> None:
    """将基础 URL 保存到配置文件"""
    config = load_config()
    config['base_url'] = base_url
    save_config(config)


def determine_base_url(cmdline_url: Optional[str] = None) -> str:
    """根据优先级确定基础 URL

    优先级顺序：
    1. 命令行参数 (cmdline_url)
    2. 配置文件中的 base_url
    3. 环境变量 BOOK_API_BASE_URL
    4. 默认值 http://127.0.0.1:8000

    Args:
        cmdline_url: 命令行传入的 base_url 参数，如果为 None 则表示未指定

    Returns:
        最终使用的基础 URL
    """
    # 1. 命令行参数优先
    if cmdline_url is not None:
        return cmdline_url

    # 2. 配置文件
    config_url = get_base_url_from_config()
    if config_url:
        return config_url

    # 3. 环境变量
    env_url = os.getenv('BOOK_API_BASE_URL')
    if env_url:
        return env_url

    # 4. 默认值
    return 'http://127.0.0.1:8000'


class BookCLI:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        """初始化 CLI 工具

        Args:
            base_url: FastAPI 服务器地址，例如 http://127.0.0.1:8000
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}{API_PREFIX}"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求到 API

        Args:
            method: HTTP 方法（GET、POST、PUT、DELETE）
            endpoint: API 端点路径，例如 "/books"
            **kwargs: 传递给 requests 的参数

        Returns:
            解析后的 JSON 响应

        Raises:
            SystemExit: 请求失败时退出程序
        """
        url = f"{self.api_base}{endpoint}"

        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()

            # 对于 204 No Content 响应，返回空字典
            if response.status_code == 204:
                return {}

            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"错误: 无法连接到服务器 {url}")
            print("请确保 FastAPI 服务器正在运行（使用 `uv run uvicorn app.main:app --reload`）")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"API 错误: {e}")
            if response.status_code == 404:
                print("资源未找到，请检查 ID 是否正确")
            elif response.status_code == 400:
                print("请求参数错误")
            try:
                error_detail = response.json().get('detail', '未知错误')
                print(f"详细信息: {error_detail}")
            except:
                pass
            sys.exit(1)
        except Exception as e:
            print(f"未知错误: {e}")
            sys.exit(1)

    def upload(self, file_path: str) -> None:
        """上传 PDF 文件到服务器

        Args:
            file_path: 本地 PDF 文件路径
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"错误: 文件不存在 {file_path}")
            sys.exit(1)

        if file_path.suffix.lower() != '.pdf':
            print("错误: 只支持 PDF 文件")
            sys.exit(1)

        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            response = self._make_request('POST', '/books/upload', files=files)

        print(f"上传成功: {response.get('filename')}")
        print(f"消息: {response.get('message')}")

    def download(self, book_id: Optional[int] = None, filename: Optional[str] = None,
                 output_dir: str = '.') -> None:
        """下载 PDF 文件

        Args:
            book_id: 图书 ID（优先使用）
            filename: PDF 文件名（如果未提供 book_id）
            output_dir: 下载文件保存目录
        """
        if book_id:
            # 获取图书信息以获取文件名
            book_info = self._make_request('GET', f'/books/{book_id}')
            filename = book_info.get('filename')
            if not filename:
                print(f"错误: 图书 ID {book_id} 没有关联的 PDF 文件")
                sys.exit(1)

        if not filename:
            print("错误: 必须提供 book_id 或 filename")
            sys.exit(1)

        # 构建 PDF 文件的静态 URL
        pdf_url = f"{self.base_url}/static/book/{filename}"

        try:
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"下载成功: {output_path}")
            print(f"文件大小: {output_path.stat().st_size} 字节")

        except requests.exceptions.HTTPError:
            print(f"错误: 无法下载文件 {filename}")
            print(f"请检查文件是否存在: {pdf_url}")
            sys.exit(1)
        except Exception as e:
            print(f"下载失败: {e}")
            sys.exit(1)

    def delete(self, book_id: int) -> None:
        """删除图书及其关联的 PDF 文件

        Args:
            book_id: 要删除的图书 ID
        """
        # 先获取图书信息，显示确认信息
        book_info = self._make_request('GET', f'/books/{book_id}')

        print("即将删除以下图书:")
        print(f"  ID: {book_info.get('id')}")
        print(f"  书名: {book_info.get('title')}")
        print(f"  作者: {book_info.get('author')}")
        if book_info.get('filename'):
            print(f"  关联PDF: {book_info.get('filename')} (将同时删除)")

        confirm = input("确认删除？(输入 'yes' 确认): ")
        if confirm.lower() != 'yes':
            print("取消删除")
            return

        self._make_request('DELETE', f'/books/{book_id}')
        print("删除成功")

    def query(self, keyword: Optional[str] = None, book_id: Optional[int] = None) -> None:
        """查询图书信息

        Args:
            keyword: 搜索关键词（模糊匹配书名）
            book_id: 查询特定图书的详细信息
        """
        if book_id:
            # 查询单本图书
            book_info = self._make_request('GET', f'/books/{book_id}')

            print("=" * 60)
            print(f"图书详情 (ID: {book_info.get('id')})")
            print("=" * 60)
            print(f"书名: {book_info.get('title')}")
            print(f"作者: {book_info.get('author')}")
            print(f"价格: ¥{book_info.get('price', 0):.2f}")
            print(f"描述: {book_info.get('description', '无')}")
            if book_info.get('filename'):
                pdf_url = f"{self.base_url}/static/book/{book_info.get('filename')}"
                print(f"PDF文件: {book_info.get('filename')}")
                print(f"在线预览: {pdf_url}")
            else:
                print("PDF文件: 未关联")
            print()
        else:
            # 查询图书列表
            params = {}
            if keyword:
                params['keyword'] = keyword

            response = self._make_request('GET', '/books', params=params)
            books = response if isinstance(response, list) else []

            if not books:
                if keyword:
                    print(f"没有找到包含 '{keyword}' 的图书")
                else:
                    print("数据库中没有图书")
                return

            print(f"找到 {len(books)} 本图书:")
            print("-" * 80)
            for book in books:
                pdf_info = f"📎 {book.get('filename')}" if book.get('filename') else "无"
                print(f"ID: {book.get('id'):3d} | {book.get('title'):30s} | "
                      f"{book.get('author'):15s} | ¥{book.get('price', 0):6.2f} | {pdf_info}")
            print("-" * 80)

    def scan(self) -> None:
        """扫描 PDF 文件夹并同步到数据库"""
        response = self._make_request('POST', '/books/scan-folder')

        print("扫描结果:")
        print(f"  扫描完成: {response.get('message')}")
        print(f"  PDF文件总数: {response.get('total_pdf')}")
        print(f"  新增图书: {response.get('added')}")

    def list_pdfs(self) -> None:
        """列出所有已上传的 PDF 文件"""
        response = self._make_request('GET', '/books/pdfs/list')
        pdfs = response.get('pdfs', [])

        if not pdfs:
            print("没有找到 PDF 文件")
            return

        print(f"找到 {len(pdfs)} 个 PDF 文件:")
        for i, pdf in enumerate(pdfs, 1):
            pdf_url = f"{self.base_url}/static/book/{pdf}"
            print(f"{i:3d}. {pdf}")
            print(f"     下载链接: {pdf_url}")


def main():
    parser = argparse.ArgumentParser(
        description="图书管理系统 CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s query --keyword "数学"
  %(prog)s upload --file "book.pdf"
  %(prog)s download --book-id 1 --output "./downloads/"
  %(prog)s delete --book-id 1
  %(prog)s scan
  %(prog)s list-pdfs
  %(prog)s config set-base-url http://localhost:8000
  %(prog)s config get-base-url

使用 %(prog)s <命令> --help 查看具体命令的帮助信息。
        """
    )

    # 全局选项
    parser.add_argument(
        '--base-url',
        default=DEFAULT_BASE_URL,
        help=f"FastAPI 服务器地址 (默认: {DEFAULT_BASE_URL})"
    )

    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # upload 命令
    upload_parser = subparsers.add_parser('upload', help='上传 PDF 文件')
    upload_parser.add_argument('--file', required=True, help='PDF 文件路径')

    # download 命令
    download_parser = subparsers.add_parser('download', help='下载 PDF 文件')
    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument('--book-id', type=int, help='图书 ID')
    download_group.add_argument('--filename', help='PDF 文件名')
    download_parser.add_argument('--output', default='.', help='下载目录 (默认: 当前目录)')

    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除图书')
    delete_parser.add_argument('--book-id', type=int, required=True, help='要删除的图书 ID')

    # query 命令
    query_parser = subparsers.add_parser('query', help='查询图书')
    query_group = query_parser.add_mutually_exclusive_group()
    query_group.add_argument('--keyword', help='搜索关键词（模糊匹配书名）')
    query_group.add_argument('--book-id', type=int, help='查询特定图书的详细信息')

    # scan 命令
    subparsers.add_parser('scan', help='扫描 PDF 文件夹并同步到数据库')

    # list-pdfs 命令
    subparsers.add_parser('list-pdfs', help='列出所有已上传的 PDF 文件')

    # config 命令
    config_parser = subparsers.add_parser('config', help='配置 CLI 工具')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='配置命令')

    # config set-base-url 命令
    set_url_parser = config_subparsers.add_parser('set-base-url', help='设置默认的基础 URL')
    set_url_parser.add_argument('url', help='FastAPI 服务器地址，例如 http://127.0.0.1:8000')

    # config get-base-url 命令
    config_subparsers.add_parser('get-base-url', help='显示当前配置的基础 URL')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 处理 config 命令（不需要连接服务器）
    if args.command == 'config':
        if not args.config_command:
            config_parser.print_help()
            sys.exit(1)
        if args.config_command == 'set-base-url':
            set_base_url_to_config(args.url)
            print(f"已设置基础 URL: {args.url}")
            print("注意：此配置将在未使用 --base-url 选项时生效")
        elif args.config_command == 'get-base-url':
            url = get_base_url_from_config()
            if url:
                print(f"当前配置的基础 URL: {url}")
            else:
                print("未配置基础 URL，使用优先级：环境变量 BOOK_API_BASE_URL 或默认值")
                env_url = os.getenv('BOOK_API_BASE_URL')
                if env_url:
                    print(f"环境变量 BOOK_API_BASE_URL: {env_url}")
                else:
                    print(f"默认值: http://127.0.0.1:8000")
        sys.exit(0)

    # 确定最终使用的基础 URL
    # 如果用户通过 --base-url 指定了值，则优先使用
    # 否则使用配置文件中保存的值，再否则使用环境变量或默认值
    # 检查用户是否在命令行中提供了 --base-url 选项
    base_url_provided = any(arg.startswith('--base-url') for arg in sys.argv)
    if base_url_provided:
        # 用户明确指定了 --base-url，直接使用
        final_base_url = args.base_url
    else:
        # 用户未通过命令行指定 --base-url，使用优先级判断
        final_base_url = determine_base_url(None)

    # 创建 CLI 实例
    cli = BookCLI(final_base_url)

    # 执行命令
    if args.command == 'upload':
        cli.upload(args.file)
    elif args.command == 'download':
        cli.download(args.book_id, args.filename, args.output)
    elif args.command == 'delete':
        cli.delete(args.book_id)
    elif args.command == 'query':
        cli.query(args.keyword, args.book_id)
    elif args.command == 'scan':
        cli.scan()
    elif args.command == 'list-pdfs':
        cli.list_pdfs()


if __name__ == '__main__':
    main()