# from typing import List, Tuple
#
# from sqlalchemy import Select, select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from model.orm.models import Comment
# from .BaseMapper import BaseMapper
#
#
# class CommentMapper(BaseMapper[Comment]):
#     def __init__(self):
#         super().__init__(Comment)
#
#     async def list_by_post(self, session: AsyncSession, post_id: int, page: int, size: int) -> Tuple[List[Comment], int]:
#         total_stmt = select(Comment.id).where(Comment.post_id == post_id)
#         total = len((await session.execute(total_stmt)).scalars().all())
#         stmt: Select = (
#             select(Comment)
#             .where(Comment.post_id == post_id)
#             .order_by(Comment.created_at.desc())
#             .offset((page - 1) * size)
#             .limit(size)
#         )
#         result = await session.execute(stmt)
#         items = list(result.scalars().all())
#         return items, total
#
#     async def create_comment(self, session: AsyncSession, post_id: int, data: dict) -> int:
#         obj = Comment(post_id=post_id, **data)
#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)
#         return obj.id
