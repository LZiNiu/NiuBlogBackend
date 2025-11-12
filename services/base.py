from utils.logger import setup_logging
from sqlmodel import Session


class BaseService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = setup_logging(self.__class__.__name__)
