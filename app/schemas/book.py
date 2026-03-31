from pydantic import BaseModel, Field
from typing import Optional


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=100, description="图书名称")
    author: str = Field(min_length=1, max_length=50, description="作者")
    price: float = Field(ge=0, description="图书价格")
    description: Optional[str] = Field(default=None, description="图书简介")
    filename: Optional[str] = Field(default=None, description="PDF文件名")  # 新增


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    filename: Optional[str] = None  # 新增


class BookResponse(BookBase):
    id: int

    model_config = {"from_attributes": True}