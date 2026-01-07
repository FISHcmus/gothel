from pydantic import BaseModel
from typing import Literal


class AssistantRequestDTO(BaseModel):
    """Request DTO for AI assistant suggestion"""
    problemStatement: str
    readingContent: str
    correctEvidence: str
    userSelectedText: str
    userAnswer: int | None
    correctAnswer: int
    options: list[str]
    situation: Literal['wrong_evidence', 'wrong_answer', 'stuck']


class AssistantResponseDTO(BaseModel):
    """Response DTO for AI assistant suggestion"""
    suggestion: str
    emotion: Literal['idle', 'thinking', 'explaining', 'celebrating', 'concerned']
