from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

class InputMessage(BaseModel):
    """定义消息结构"""
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class ChatRequest(BaseModel):
    """定义聊天完成请求体"""
    model: str = Field(..., description="要使用的模型名称，如 'Qwen3-Max'")
    messages: List[InputMessage] = Field(..., description="对话历史消息列表")
    stream: bool = Field(False, description="是否以流式方式返回响应")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)

class OutputMessage(BaseModel):
    name: str
    text: str