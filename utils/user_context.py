from dataclasses import dataclass
from typing import Optional
from contextvars import ContextVar

from model.orm.models import Role


@dataclass
class UserContext:
    user_id: int | str
    username: str
    role: str
    token: str

    @property
    def is_admin(self) -> bool:
        return self.role in [Role.ADMIN.value, Role.SUPER.value]


user_ctx: ContextVar[Optional[UserContext]] = ContextVar("user_ctx", default=None)


def set_user_context(ctx: UserContext) -> None:
    user_ctx.set(ctx)


def get_user_context() -> Optional[UserContext]:
    return user_ctx.get()


def clear_user_context() -> None:
    user_ctx.set(None)