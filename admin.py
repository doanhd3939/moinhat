"""
Xử lý các lệnh quản trị viên: ban, unban, addadmin, deladmin, hướng dẫn admin.
"""
import time
from utils import ADMINS_LOCK, BAN_LIST, is_admin

ADMIN_GUIDE = (
    "<b>👑 HƯỚNG DẪN QUẢN TRỊ VIÊN</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>CÁC LỆNH QUẢN TRỊ:</b>\n"
    "<code>/ban &lt;user_id&gt; &lt;phút&gt;</code> – Ban user X phút\n"
    "<code>/unban &lt;user_id&gt;</code> – Gỡ ban user\n"
    "<code>/addadmin &lt;user_id&gt;</code> – Thêm admin mới\n"
    "<code>/deladmin &lt;user_id&gt;</code> – Xoá quyền admin\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>LƯU Ý:</b>\n"
    "- Không thể xoá chính mình nếu là admin cuối cùng.\n"
    "- Ban thủ công sẽ ghi đè ban tự động.\n"
    "- /unban sẽ gỡ mọi loại ban.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "<b>Ví dụ:</b>\n"
    "<code>/ban 123456789 10</code> – Ban user 123456789 trong 10 phút\n"
    "<code>/unban 123456789</code> – Gỡ ban user\n"
)

def admin_notify(msg: str) -> str:
    return (
        "<b>👑 QUẢN TRỊ VIÊN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{msg}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

def handle_admin_command(current_user_id: int, admins: set, cmd: str, args: list) -> dict:
    if not is_admin(current_user_id, admins):
        return {"status": "error", "msg": admin_notify("❌ <b>Bạn không có quyền quản trị viên!</b>")}
    if cmd == "/ban":
        if len(args) < 2:
            return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/ban &lt;user_id&gt; &lt;số_phút&gt;</code>")}
        target = int(args[0])
        mins = int(args[1])
        now = time.time()
        was_banned = BAN_LIST.get(target)
        BAN_LIST[target] = {'until': now + mins * 60, 'manual': True}
        if was_banned:
            return {"status": "ok", "msg": admin_notify(f"🔁 <b>Đã cập nhật lại thời gian ban <code>{target}</code> thành <b>{mins} phút</b>.</b>")}
        else:
            return {"status": "ok", "msg": admin_notify(f"🔒 <b>Đã ban <code>{target}</code> trong <b>{mins} phút</b>.</b>")}
    elif cmd == "/unban":
        if len(args) < 1:
            return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/unban &lt;user_id&gt;</code>")}
        target = int(args[0])
        if target in BAN_LIST:
            del BAN_LIST[target]
            return {"status": "ok", "msg": admin_notify(f"🔓 <b>Đã gỡ ban <code>{target}</code>.</b>")}
        return {"status": "ok", "msg": admin_notify(f"ℹ️ <b>User <code>{target}</code> không bị cấm.</b>")}
    elif cmd == "/addadmin":
        if len(args) < 1:
            return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/addadmin &lt;user_id&gt;</code>")}
        target = int(args[0])
        with ADMINS_LOCK:
            admins.add(target)
        return {"status": "ok", "msg": admin_notify(f"✨ <b>Đã thêm admin <code>{target}</code>.</b>")}
    elif cmd == "/deladmin":
        if len(args) < 1:
            return {"status": "error", "msg": admin_notify("❌ <b>Cú pháp đúng:</b> <code>/deladmin &lt;user_id&gt;</code>")}
        target = int(args[0])
        with ADMINS_LOCK:
            if target == current_user_id and len(admins) == 1:
                return {"status": "error", "msg": admin_notify("⚠️ <b>Không thể xoá admin cuối cùng!</b>")}
            admins.discard(target)
        return {"status": "ok", "msg": admin_notify(f"🗑️ <b>Đã xoá quyền admin <code>{target}</code>.</b>")}
    elif cmd == "/adminguide":
        return {"status": "ok", "msg": ADMIN_GUIDE}
    else:
        return {"status": "error", "msg": admin_notify("❌ <b>Lệnh quản trị không hợp lệ!</b>")}
