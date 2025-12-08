from app.utils.logger import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = setup_logging(self.__class__.__name__)
