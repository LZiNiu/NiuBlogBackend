from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# 定义类型变量
ModelType = TypeVar("ModelType")


class BaseMapper(Generic[ModelType]):
    """
    基础Mapper类，提供通用的增删查改操作
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化BaseMapper
        
        Args:
            model: SQLModel模型类
        """
        self.model = model

    async def create(self, session: AsyncSession, obj: ModelType) -> ModelType:
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

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
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
        statement = select(self.model).where(self.model.id == id)  # type: ignore
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_one(self, session: AsyncSession, **filters) -> Optional[ModelType]:
        """
        根据条件获取首条记录
        """
        statement = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_all(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ModelType]:
        """
        获取记录列表，支持条件、排序与分页
        """
        statement = select(self.model)

        # 条件
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        # 排序：字段前缀 '-' 表示倒序
        if order_by:
            for ob in order_by:
                field = ob.lstrip("-")
                if hasattr(self.model, field):
                    col = getattr(self.model, field)
                    statement = statement.order_by(col.desc() if ob.startswith("-") else col.asc())

        # 偏移与限制
        if offset:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)

        result = await session.execute(statement)
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, id: int, obj_update: dict) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            session: 数据库会话
            id: 要更新记录的ID
            obj_update: 包含更新字段的字典
            
        Returns:
            更新后的对象，如果未找到则返回None
        """
        db_obj = await self.get_by_id(session, id)
        if db_obj:
            for field, value in obj_update.items():
                if hasattr(self.model, field):
                    setattr(db_obj, field, value)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

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
        statement = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        result = await session.execute(statement.limit(1))
        return result.scalars().first() is not None

    async def count(self, session: AsyncSession, **filters) -> int:
        """
        统计符合条件的记录数
        """
        statement = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        result = await session.execute(statement)
        return int(result.scalar() or 0)

    async def paginate(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[dict] = None,
        order_by: Optional[List[str]] = None,
    ) -> tuple[List[ModelType], int]:
        """
        分页查询，返回 (数据列表, 总记录数)
        """
        total = await self.count(session, **(filters or {}))
        offset = (page - 1) * page_size
        items = await self.get_all(session, filters=filters, order_by=order_by, limit=page_size, offset=offset)
        return items, total

    async def get_by_condition(self, session: AsyncSession, **kwargs) -> List[ModelType]:
        """
        根据条件查询记录
        
        Args:
            session: 数据库会话
            **kwargs: 查询条件，例如: username="test", email="test@example.com"
            
        Returns:
            符合条件的记录列表
        """
        statement = select(self.model)
        
        # 添加查询条件
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    def select_fields(sqlalchemy_model: type, fields: type[BaseModel] | dict[str, Any]):
        """
        根据 Pydantic 模型的字段定义，从 SQLModel 类中选择对应的列

        :param sqlalchemy_model: SQLAlchemy 模型类
        :param fields: Pydantic 模型或字段名字典
        :return: SQLAlchemy 的 Select 语句
        """
        if isinstance(fields, dict):
            field_names = list(fields)
        else:
            field_names = list(fields.model_fields.keys())
        
        # 获取 SQLModel 的列
        # 根据字段名选择 SQLModel 的列
        selected_columns = []
        for field_name in field_names:
            col = getattr(sqlalchemy_model, field_name, None)
            if col is None:
                raise ValueError(f"Field '{field_name}' not found in model '{sqlalchemy_model.__name__}'")
            selected_columns.append(col)
        return select(*selected_columns)
