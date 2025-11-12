from sqlmodel import SQLModel


class Article(SQLModel, table=True):
    pass