from fastapi import APIRouter, Depends

from app.core.biz_constants import BizMsg
from app.model import Result
from app.model.dto.common import BatchDelete
from app.model.dto.timeline import TimelineCreate, TimelineUpdate
from app.model.entity import Timeline
from app.model.vo.common import CreateResponse
from app.services import TimelineService, get_timeline_service


router = APIRouter(prefix="/timeline", tags=["管理端时间轴接口"])


@router.get("", response_model=Result[list[Timeline]])
async def get_timeline(
    service: TimelineService = Depends(get_timeline_service),
) -> Result[list[Timeline]]:
    """获取时间轴事件列表"""
    timeline_events = await service.list_all()
    return Result.success(timeline_events)


@router.post("", response_model=Result[CreateResponse])
async def create_timeline(
    timeline_event: TimelineCreate,
    service: TimelineService = Depends(get_timeline_service),
):
    """创建时间轴事件"""
    obj_id = await service.create(timeline_event)
    return Result.success(CreateResponse(id=obj_id))


@router.put("/{id}", response_model=Result[None])
async def update_timeline(
    id: int,
    timeline_update: TimelineUpdate,
    service: TimelineService = Depends(get_timeline_service),
) -> Result[None]:
    """更新时间轴事件"""
    is_update = await service.update(id, timeline_update)
    if not is_update:
        return Result.failure(BizMsg.DB_RECORD_NOT_FOUND)
    return Result.success()


@router.delete("/batch", response_model=Result[None])
async def delete_timeline_batch(
    batch_delete: BatchDelete,
    service: TimelineService = Depends(get_timeline_service),
) -> Result[None]:
    """批量删除时间轴事件"""
    is_delete = await service.deleteByIds(batch_delete.ids)
    if not is_delete:
        return Result.failure(BizMsg.DB_RECORD_NOT_FOUND)
    return Result.success()


@router.delete("/{id}", response_model=Result[None])
async def delete_timeline(
    id: int,
    service: TimelineService = Depends(get_timeline_service),
) -> Result[None]:
    """删除时间轴事件"""
    is_delete = await service.deleteById(id)
    if not is_delete:
        return Result.failure(BizMsg.DB_RECORD_NOT_FOUND)
    return Result.success()


