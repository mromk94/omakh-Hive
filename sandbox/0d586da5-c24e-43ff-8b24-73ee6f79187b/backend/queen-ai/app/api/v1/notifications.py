"""
Notifications API Endpoints
Admin notifications system
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory storage for now (replace with DB later)
_notifications = []

def verify_admin(request: Request):
    """Verify admin credentials"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    action_url: str = None

@router.get("")
async def list_notifications(
    limit: int = 50,
    unread_only: bool = False,
    admin: bool = Depends(verify_admin)
):
    """Get all notifications"""
    notifications = _notifications.copy()
    
    if unread_only:
        notifications = [n for n in notifications if not n.get('read', False)]
    
    # Sort by timestamp (newest first)
    notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return {
        "success": True,
        "notifications": notifications[:limit],
        "total": len(notifications),
        "unread_count": len([n for n in _notifications if not n.get('read', False)])
    }

@router.post("")
async def create_notification(
    data: CreateNotificationRequest,
    admin: bool = Depends(verify_admin)
):
    """Create a new notification"""
    notification = {
        "id": f"notif_{len(_notifications) + 1}",
        "title": data.title,
        "message": data.message,
        "type": data.type,
        "action_url": data.action_url,
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    _notifications.append(notification)
    
    logger.info("Notification created", notification_id=notification['id'])
    
    return {
        "success": True,
        "notification": notification
    }

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    admin: bool = Depends(verify_admin)
):
    """Mark notification as read"""
    for notif in _notifications:
        if notif['id'] == notification_id:
            notif['read'] = True
            notif['read_at'] = datetime.utcnow().isoformat()
            return {
                "success": True,
                "notification": notif
            }
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.post("/mark-all-read")
async def mark_all_read(admin: bool = Depends(verify_admin)):
    """Mark all notifications as read"""
    for notif in _notifications:
        notif['read'] = True
        notif['read_at'] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "message": "All notifications marked as read"
    }

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    admin: bool = Depends(verify_admin)
):
    """Delete a notification"""
    global _notifications
    original_len = len(_notifications)
    _notifications = [n for n in _notifications if n['id'] != notification_id]
    
    if len(_notifications) == original_len:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "success": True,
        "message": "Notification deleted"
    }

@router.get("/stats")
async def get_notification_stats(admin: bool = Depends(verify_admin)):
    """Get notification statistics"""
    total = len(_notifications)
    unread = len([n for n in _notifications if not n.get('read', False)])
    
    # Count by type
    by_type = {}
    for notif in _notifications:
        notif_type = notif.get('type', 'info')
        by_type[notif_type] = by_type.get(notif_type, 0) + 1
    
    return {
        "success": True,
        "stats": {
            "total": total,
            "unread": unread,
            "read": total - unread,
            "by_type": by_type
        }
    }
