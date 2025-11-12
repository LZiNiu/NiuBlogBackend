import logging
from sqlmodel import Session


class BaseService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)
