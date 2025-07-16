"""
Các hàm tiện ích dùng chung cho dự án.
"""
import threading
import logging
import time
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)

SPAM_COUNTER: Dict[int, list] = {}
BAN_LIST: Dict[int, Dict[str, Any]] = {}
ADMINS_LOCK = threading.Lock()
USER_LOCKS = threading.Lock()
USER_BUTTON_LOCK: Dict[int, bool] = {}

def is_admin(user_id: int, admins: set) -> bool:
    with ADMINS_LOCK:
        return user_id in admins

def pre_check(user_id: int, admins: set) -> Dict[str, Any]:
    """
    Kiểm tra quyền và trạng thái của user trước khi thực hiện tác vụ.
    """
    if is_admin(user_id, admins):
        return {"status": "ok"}
    ban = BAN_LIST.get(user_id)
    if ban and ban['until'] > time.time():
        return {"status": "banned", "msg": "Bạn đang bị cấm."}
    now = time.time()
    cnts = SPAM_COUNTER.setdefault(user_id, [])
    cnts = [t for t in cnts if now - t < 60]
    cnts.append(now)
    SPAM_COUNTER[user_id] = cnts
    if len(cnts) > 3:
        BAN_LIST[user_id] = {'until': now + 300, 'manual': False}
        return {"status": "spam", "msg": "Bạn đã bị tự động ban 5 phút do spam."}
    return {"status": "ok"}

def auto_unban_loop():
    """
    Tự động gỡ ban khi hết thời gian.
    """
    while True:
        now = time.time()
        to_del = []
        for user_id, ban in list(BAN_LIST.items()):
            if ban['until'] <= now:
                to_del.append(user_id)
        for user_id in to_del:
            del BAN_LIST[user_id]
            logging.info(f"Auto unban user {user_id}")
        time.sleep(5)

def setup_auto_unban():
    threading.Thread(target=auto_unban_loop, daemon=True).start()
