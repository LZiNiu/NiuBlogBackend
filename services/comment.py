from typing import List, Tuple

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dao.CommentMapper import CommentMapper
from core.config import settings
from model.db import get_session
from model.dto.comment import CommentCreateDTO
from utils.auth_utils import get_payload
from model.common import JwtPayload
from model.vo.comment import CommentVO
from services.base import BaseService


def get_comment_mapper() -> CommentMapper:
    return CommentMapper()


class CommentService(BaseService):
    def __init__(self, session: AsyncSession, mapper: CommentMapper):
        super().__init__(session)
        self.mapper = mapper

    async def list_by_post(self, post_id: int, page: int, size: int) -> Tuple[List[CommentVO | dict], int]:
        items, total = await self.mapper.list_by_post(self.session, post_id, page, size)
        return [CommentVO.model_validate(i).model_dump() for i in items], total

    async def create_comment(self, post_id: int, dto: CommentCreateDTO, author_user_id: int) -> int:
        text = dto.content or ""
        for w in settings.SENSITIVE_WORDS:
            if w and w.lower() in text.lower():
                return 0
        data = dto.model_dump()
        data["author_user_id"] = author_user_id
        return await self.mapper.create_comment(self.session, post_id, data)


def get_comment_service(session: AsyncSession = Depends(get_session), mapper: CommentMapper = Depends(get_comment_mapper)) -> CommentService:
    return CommentService(session, mapper)
