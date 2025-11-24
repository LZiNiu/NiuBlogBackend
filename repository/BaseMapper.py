from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select, update, Column
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from model.common import Base

# 定义类型变量
TableType = TypeVar("TableType", bound=Base)
EntityType = TypeVar("EntityType", bound=BaseModel)


class BaseMapper(Generic[TableType]):
    """
    基础Mapper类，提供通用的增删查改操作
    """

    def __init__(self, entity_model: Type[TableType]):
        """
        初始化BaseMapper
        
        Args:
            model: Orm模型类
        """
        self.entity_model = entity_model

    async def create(self, session: AsyncSession, obj: TableType) -> EntityType:
        """
        创建新记录
        
        Args:
            session: 数据库会话
            obj: 要创建的对象
            
        Returns:
            创建后的对象
        """
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[EntityType]:
        """
        根据ID获取记录
        
        Args:
            session: 数据库会话
            id: 记录ID
            
        Returns:
            查询到的对象，如果未找到则返回None
        """
        # 假设模型具有'id'字段作为主键
        # 在实际使用中，可以通过约定或额外参数指定主键字段
        statement = select(self.entity_model).where(self.entity_model.id == id)  # type: ignore
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_one(self, session: AsyncSession, 
                            fields: List[Column] | None = None, **filters) -> Optional[EntityType]:
        """
        根据条件获取首条记录
        
        Args:
            session: 数据库会话
            fields: 要查询的字段列表, 如果为None则查询所有字段
            **filters: 查询条件，键为字段名，值为字段值
            
        Returns:
            查询到的对象, 如果未找到则返回None
        """
        if not fields:
            statement = select(self.entity_model)
        else:
            statement = select(self.entity_model).options(load_only(*fields))  # type: ignore
        
        for field, value in filters.items():
            if hasattr(self.entity_model, field):
                statement = statement.where(getattr(self.entity_model, field) == value)
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_all(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[EntityType]:
        """
        获取记录列表，支持条件、排序与分页
        """
        statement = select(self.entity_model)

        # 条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.entity_model, field):
                    statement = statement.where(getattr(self.entity_model, field) == value)

        # 排序：字段前缀 '-' 表示倒序
        if order_by:
            for ob in order_by:
                field = ob.lstrip("-")
                if hasattr(self.entity_model, field):
                    col = getattr(self.entity_model, field)
                    statement = statement.order_by(col.desc() if ob.startswith("-") else col.asc())

        # 偏移与限制
        if offset:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)

        result = await session.execute(statement)
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, id: int, obj_update: dict) -> Optional[EntityType]:
        statement = update(self.entity_model).where(self.entity_model.id == id).values(**obj_update)  # type: ignore
        result = await session.execute(statement)
        await session.commit()
        return result

    async def delete(self, session: AsyncSession, id: int) -> bool:
        """
        删除记录
        
        Args:
            session: 数据库会话
            id: 要删除记录的ID
            
        Returns:
            删除成功返回True，否则返回False
        """
        db_obj = await self.get_by_id(session, id)
        if db_obj:
            await session.delete(db_obj)
            await session.commit()
            return True
        return False

    async def exists(self, session: AsyncSession, **filters) -> bool:
        """
        判断是否存在符合条件的记录
        """
        statement = select(self.entity_model)
        for field, value in filters.items():
            if hasattr(self.entity_model, field):
                statement = statement.where(getattr(self.entity_model, field) == value)
        result = await session.execute(statement.limit(1))
        return result.scalars().first() is not None

    async def count(self, session: AsyncSession, **filters) -> int:
        """
        统计符合条件的记录数
        """
        statement = select(func.count()).select_from(self.entity_model)
        for field, value in filters.items():
            if hasattr(self.entity_model, field):
                statement = statement.where(getattr(self.entity_model, field) == value)
        result = await session.execute(statement)
        return int(result.scalar() or 0)

    async def paginate(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        fields: set[str] | type[BaseModel] | None = None,
        order_by: Optional[List[str]] = None,
    ) -> tuple[list[dict], int]:
        """
        分页查询，返回 (数据列表, 总记录数)
        :param session: 数据库会话
        :param page: 页码
        :param page_size: 每页记录数
        :param fields: 要查询的字段，例如: ["id", "username", "email"]
        :param order_by: 排序字段，例如: ["id", "-username"] 表示按ID升序，按用户名降序
        :return: 分页数据列表和总记录数
        """
        total = await self.count(session)
        offset = (page - 1) * page_size
        stmt = select(*self.select_fields(self.entity_model, fields)).offset(offset).limit(page_size)
        if order_by:
            for ob in order_by:
                field = ob.lstrip("-")
                if hasattr(self.entity_model, field):
                    col: Column = getattr(self.entity_model, field)
                    stmt = stmt.order_by(col.desc() if ob.startswith("-") else col.asc())
        result: Result[Row] = await session.execute(stmt)
        items = [dict(row) for row in result.mappings()]
        return items, total

    async def get_by_condition(self, session: AsyncSession, **kwargs) -> List[EntityType]:
        """
        根据条件查询记录
        
        Args:
            session: 数据库会话
            **kwargs: 查询条件，例如: username="test", email="test@example.com"
            
        Returns:
            符合条件的记录列表
        """
        statement = select(self.entity_model)
        
        # 添加查询条件
        for field, value in kwargs.items():
            if hasattr(self.entity_model, field):
                statement = statement.where(getattr(self.entity_model, field) == value)
        
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    def select_fields(sqlalchemy_model: type[Base], fields: type[BaseModel] | set[str]) -> list[Column]:
        """
        根据 Pydantic 模型的字段定义，从 SQLModel 类中选择对应的列

        :param sqlalchemy_model: SQLAlchemy 模型类
        :param fields: Pydantic 模型或字段名字典
        :return: SQLAlchemy 的 实体列 对象
        """
        if issubclass(fields, BaseModel):
            field_names = set(fields.model_fields.keys())
        else:
            field_names = fields
        # 获取 SQLModel 的列
        # 根据字段名选择 SQLModel 的列
        selected_columns = []
        for field_name in field_names:
            col = getattr(sqlalchemy_model, field_name, None)
            if col is None:
                raise ValueError(f"Field '{field_name}' not found in model '{sqlalchemy_model.__name__}'")
            selected_columns.append(col)
        return selected_columns
