"""
Chạy Flask API và Telegram Bot BYPASS trên cùng một project.
"""
import threading
import asyncio
import time

from flask import Flask, request, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, FLASK_PORT, ADMIN_IDS
from utils import setup_auto_unban, pre_check, USER_LOCKS, USER_BUTTON_LOCK, is_admin
from admin import handle_admin_command, ADMIN_GUIDE
from bypass import get_bypass_code
from template import BYPASS_TEMPLATE

TASKS = [
    {"label": "Bypass M88", "type": "m88"},
    {"label": "Bypass FB88", "type": "fb88"},
    {"label": "Bypass 188BET", "type": "188bet"},
    {"label": "Bypass W88", "type": "w88"},
    {"label": "Bypass V9BET", "type": "v9bet"},
    {"label": "Bypass BK8", "type": "bk8"},
    {"label": "Bypass VN88", "type": "vn88"},
]
HELP_BUTTON = {"label": "📖 Hướng dẫn / Hỗ trợ", "callback": "help"}

# Flask app
app = Flask(__name__)

@app.route('/bypass', methods=['POST'])
def bypass_api():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'Thiếu dữ liệu'}), 400
    bypass_type = json_data.get('type')
    if not bypass_type:
        return jsonify({'error': 'Thiếu loại bypass'}), 400
    result = get_bypass_code(bypass_type)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Không lấy được mã'}), 400

@app.route('/', methods=['GET'])
def index():
    return render_template_string(BYPASS_TEMPLATE)

def start_flask():
    app.run(host="0.0.0.0", port=FLASK_PORT, threaded=True)

# Telegram bot
async def send_main_menu(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    user = None
    try:
        user = (await context.bot.get_chat(chat_id)).id
    except Exception:
        pass
    keyboard = []
    for i in range(0, len(TASKS), 2):
        line = []
        for task in TASKS[i:i+2]:
            line.append(InlineKeyboardButton(task["label"], callback_data=f"bypass:{task['type']}:{chat_id}"))
        keyboard.append(line)
    keyboard.append([InlineKeyboardButton(HELP_BUTTON["label"], callback_data=f"{HELP_BUTTON['callback']}:{chat_id}")])
    if user is not None and is_admin(user, ADMIN_IDS):
        keyboard.append([InlineKeyboardButton("👑 Hướng dẫn Admin", callback_data=f"adminguide:{chat_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="<b>🔰 CHỌN NHIỆM VỤ BYPASS-BÓNG X:</b>\nBạn có thể tiếp tục chọn nhiệm vụ khác hoặc xem hướng dẫn 👇",
        parse_mode="HTML", reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if ":" in data:
        parts = data.split(":")
        action = parts[0]
        action_type = parts[1] if len(parts) > 1 else None
        action_chat_id = int(parts[-1]) if parts[-1].isdigit() else None
    else:
        action = data
        action_type = None
        action_chat_id = None

    if action_chat_id is not None and user_id != action_chat_id:
        await query.edit_message_text(
            "⛔ <b>Nút này chỉ dành cho bạn!</b>",
            parse_mode="HTML"
        )
        return

    with USER_LOCKS:
        if USER_BUTTON_LOCK.get(user_id, False):
            await query.edit_message_text(
                "⛔ <b>Bạn vừa thao tác, vui lòng chờ kết quả!</b>",
                parse_mode="HTML"
            )
            return
        USER_BUTTON_LOCK[user_id] = True

    if action == "mainmenu":
        await send_main_menu(chat_id, context)
        USER_BUTTON_LOCK[user_id] = False
        return
    if action == "adminguide":
        await query.edit_message_text(
            ADMIN_GUIDE, parse_mode="HTML", disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Quay lại Menu", callback_data=f"mainmenu:{chat_id}")]
            ])
        )
        USER_BUTTON_LOCK[user_id] = False
        return
    if action == HELP_BUTTON["callback"]:
        help_text = (
            "<b>📖 HƯỚNG DẪN SỬ DỤNG BOT BYPASS & HỖ TRỢ</b>\n"
            "• Bypass traffic (lấy mã) cho các loại: <b>M88, FB88, 188BET, W88, V9BET, BK8, VN88</b>.\n"
            "• Giao diện Telegram cực dễ dùng, thao tác nhanh chóng.\n"
            "━━━━━━━━━━━━━\n"
            "<b>2. CÁCH SỬ DỤNG:</b>\n"
            "– Dùng các NÚT NHIỆM VỤ hoặc lệnh <code>/ym &lt;loại&gt;</code>\n"
            "Ví dụ: <code>/ym m88</code> hoặc <code>/ym bk8</code>\n"
            "━━━━━━━━━━━━━\n"
            "<b>5. HỖ TRỢ & LIÊN HỆ:</b>\n"
            "• Admin: <a href='https://t.me/doanhvip1'>@doanhvip12</a> | Nhóm: <a href='https://t.me/doanhvip1'>https://t.me/doanhvip1</a>\n"
            "<i>Chúc bạn thành công! 🚀</i>"
        )
        help_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Quay lại Menu", callback_data=f"mainmenu:{chat_id}")],
            [InlineKeyboardButton("💬 Liên hệ Admin & Nhóm", callback_data=f"help:{chat_id}")]
        ])
        await query.edit_message_text(
            help_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=help_keyboard
        )
        USER_BUTTON_LOCK[user_id] = False
        return

    if action == "bypass":
        type_ = action_type
        check = pre_check(user_id, ADMIN_IDS)
        if check["status"] != "ok":
            await query.edit_message_text(
                f"❌ <b>Lỗi:</b> {check.get('msg', 'Bạn bị giới hạn.')}",
                parse_mode="HTML"
            )
            USER_BUTTON_LOCK[user_id] = False
            return

        # Gửi trạng thái lần đầu
        msg = (
            "⏳ <b>Đã nhận nhiệm vụ!</b>\n"
            "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>75 giây</b>...</i>\n"
            "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
            "<b>Còn lại: <code>75</code> giây...</b>"
        )
        sent = await query.edit_message_text(msg, parse_mode="HTML")

        async def delay_and_reply():
            start_time = time.time()
            result = None
            import requests
            def get_code():
                nonlocal result
                try:
                    resp = requests.post(f"http://localhost:{FLASK_PORT}/bypass", json={"type": type_, "user_id": user_id, "message": f"/ym {type_}"})
                    data = resp.json()
                    if "code" in data or "codes" in data:
                        if "codes" in data:
                            result = f'✅ <b>{type_.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{", ".join(data["codes"])}</code>'
                        else:
                            result = f'✅ <b>{type_.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{data["code"]}</code>'
                    else:
                        result = f'❌ <b>Lỗi:</b> {data.get("error", "Không lấy được mã")}'
                except Exception as e:
                    result = f"❌ <b>Lỗi hệ thống:</b> <code>{e}</code>"
            t = threading.Thread(target=get_code)
            t.start()
            for remain in range(70, 0, -5):
                await asyncio.sleep(5)
                try:
                    await sent.edit_text(
                        "⏳ <b>Đã nhận nhiệm vụ!</b>\n"
                        "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>75 giây</b>...</i>\n"
                        "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
                        f"<b>Còn lại: <code>{remain}</code> giây...</b>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            t.join()
            await asyncio.sleep(max(0, 75 - (time.time() - start_time)))
            await sent.edit_text(
                "<b>🎉 KẾT QUẢ BYPASS</b>\n<b>─────────────────────────────</b>\n"
                + (result if result else "<b>Không lấy được kết quả</b>") +
                "\n<b>─────────────────────────────</b>",
                parse_mode="HTML"
            )
            await send_main_menu(chat_id, context)
            USER_BUTTON_LOCK[user_id] = False
        asyncio.create_task(delay_and_reply())

async def ym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    if message.startswith(('/ban', '/unban', '/addadmin', '/deladmin','/adminguide')):
        parts = message.split()
        result = handle_admin_command(user_id, ADMIN_IDS, parts[0], parts[1:])
        await update.message.reply_html(result["msg"])
        return
    check = pre_check(user_id, ADMIN_IDS)
    if check["status"] != "ok":
        await update.message.reply_html(
            f"❌ <b>Lỗi:</b> {check.get('msg', '')}"
        )
        return
    if not context.args:
        await update.message.reply_html(
            "📌 <b>Hướng dẫn sử dụng:</b>\n<b>/ym &lt;loại&gt;</b>\nVí dụ: <code>/ym m88</code>\n<b>Các loại hợp lệ:</b> <i>m88, fb88, 188bet, w88, v9bet, bk8, vn88</i>"
        )
        return
    type_ = context.args[0].lower()
    sent = await update.message.reply_html(
        "⏳ <b>Đã nhận lệnh!</b>\n"
        "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>75 giây</b>...</i>\n"
        "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
        "<b>Còn lại: <code>75</code> giây...</b>"
    )
    async def delay_and_reply():
        start_time = time.time()
        result = None
        import requests
        def get_code():
            nonlocal result
            try:
                resp = requests.post(f"http://localhost:{FLASK_PORT}/bypass", json={"type": type_, "user_id": user_id, "message": f"/ym {type_}"})
                data = resp.json()
                if "code" in data or "codes" in data:
                    if "codes" in data:
                        result = f'✅ <b>{type_.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{", ".join(data["codes"])}</code>'
                    else:
                        result = f'✅ <b>{type_.upper()}</b> | <b style="color:#32e1b7;">Mã</b>: <code>{data["code"]}</code>'
                else:
                    result = f'❌ <b>Lỗi:</b> {data.get("error", "Không lấy được mã")}'
            except Exception as e:
                result = f"❌ <b>Lỗi hệ thống:</b> <code>{e}</code>"
        t = threading.Thread(target=get_code)
        t.start()
        for remain in range(70, 0, -5):
            await asyncio.sleep(5)
            try:
                await sent.edit_text(
                    "⏳ <b>Đã nhận lệnh!</b>\n"
                    "🤖 <i>Bot đang xử lý yêu cầu của bạn, vui lòng chờ <b>75 giây</b>...</i>\n"
                    "<b>⏱️ Đang lấy mã, xin đừng gửi lệnh mới...</b>\n"
                    f"<b>Còn lại: <code>{remain}</code> giây...</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        t.join()
        await asyncio.sleep(max(0, 75 - (time.time() - start_time)))
        await sent.edit_text(
            "<b>🎉 KẾT QUẢ BYPASS</b>\n<b>─────────────────────────────</b>\n" + (result if result else "<b>Không lấy được kết quả</b>") + "\n<b>─────────────────────────────</b>",
            parse_mode="HTML"
        )
        await send_main_menu(update.effective_chat.id, context)
    asyncio.create_task(delay_and_reply())

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", lambda update, ctx: send_main_menu(update.effective_chat.id, ctx)))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("ym", ym_command))
    application.add_handler(CommandHandler(["ban", "unban", "addadmin", "deladmin", "adminguide"], ym_command))
    application.run_polling()

if __name__ == "__main__":
    setup_auto_unban()
    threading.Thread(target=start_flask, daemon=True).start()
    run_bot()
