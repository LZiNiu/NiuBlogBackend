from fastapi import APIRouter, Depends

from app.model import Result
from app.model.entity import Timeline
from app.services import TimelineService, get_timeline_service


router = APIRouter(prefix="/timeline", tags=["用户端时间轴接口"])


@router.get("", response_model=Result[list[Timeline]])
async def get_timeline(
    service: TimelineService = Depends(get_timeline_service),
) -> Result[list[Timeline]]:
    """获取时间轴事件列表"""
    timeline_events = await service.list_all()
    return Result.success(timeline_events)


