from pydantic import BaseModel


class Message(BaseModel):
    """Модель для простых текстовых ответов"""
    message: str
    