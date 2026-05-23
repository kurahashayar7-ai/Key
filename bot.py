# -*- coding: utf-8 -*-
"""
𝙘𝙤𝙞𝙣𝙨𝙢𝙖𝙧𝙠𝙚𝙩 𝙗𝙤𝙩 ☘️
بۆتی تێلیگرام بۆ بەڕێوەبردنی پاکێجەکان و بانگێشتنامەکان

پێداویستی:
    pip install python-telegram-bot==21.6

بەکارهێنان:
    BOT_TOKEN=xxxxx python bot.py
"""

import os
import json
import secrets
import logging
from urllib.parse import quote

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─────────────── ڕێکخستن ───────────────
BOT_TOKEN    = os.getenv("BOT_TOKEN", "8978760655:AAGTh5zDMxy4aqbc7JWKqvD7v1p2hZDACgk")
MASTER_CODE  = "25062011"
SUPPORT_LINK = "https://t.me/knamo_1"
DATA_FILE    = "bot_data.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("coinsmarket")

# ─────────────── کۆگای JSON ───────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "admins": [],
        "invite_codes": {},
        "packages": [
            {"name": "پاکێجی بنەڕەتی", "price": "10$"},
            {"name": "پاکێجی ناوەند",  "price": "25$"},
            {"name": "پاکێجی VIP",     "price": "50$"},
        ],
        "bots": [],
    }

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DB, f, ensure_ascii=False, indent=2)

DB = load_data()

def is_admin(uid: int) -> bool:
    return uid in DB["admins"]

# ─────────────── ڕووکار ───────────────
WELCOME = (
    "بەخێر بێن بۆ 𝙘𝙤𝙞𝙣𝙨𝙢𝙖𝙧𝙠𝙚𝙩 𝙗𝙤𝙩 ☘️\n"
    "تایبەت بە پەرەپێدانی بۆتی تێلیگرام\n\n"
    "بەشێک هەڵبژێرە 👇"
)

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 پاکێجەکان", callback_data="m:pkgs")],
        [InlineKeyboardButton("🤖 بۆتەکان",   callback_data="m:bots")],
        [InlineKeyboardButton("🔑 کۆدی پاکێج", callback_data="m:code")],
        [InlineKeyboardButton("ℹ️ دەربارە",   callback_data="m:about")],
    ])

def back_home():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="m:home")]])

def packages_kb():
    rows = []
    for i, p in enumerate(DB["packages"]):
        rows.append([InlineKeyboardButton(f"📦 {p['name']} — {p['price']}", callback_data=f"pkg:{i}")])
    rows.append([InlineKeyboardButton("🔑 کۆدی پاکێج", callback_data="m:code")])
    rows.append([InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="m:home")])
    return InlineKeyboardMarkup(rows)

def package_view_kb(idx: int):
    p = DB["packages"][idx]
    msg = f"سڵاو، دەمەوێت {p['name']} ({p['price']}) بکڕم 🌿"
    url = f"{SUPPORT_LINK}?text={quote(msg)}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 کڕینی پاکێج", url=url)],
        [InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="m:pkgs")],
    ])

def bots_kb():
    rows = []
    if not DB["bots"]:
        rows.append([InlineKeyboardButton("— هیچ بۆتێک نییە —", callback_data="noop")])
    for b in DB["bots"]:
        rows.append([InlineKeyboardButton(f"🤖 {b['name']}", url=b["link"])])
        msg = f"سڵاو، دەمەوێت پاکێجی ({b.get('package','—')}) بۆ بۆتی ({b['name']}) بکڕم 🌿"
        url = f"{SUPPORT_LINK}?text={quote(msg)}"
        rows.append([InlineKeyboardButton(f"🛒 کڕینی پاکێج — {b.get('package','—')}", url=url)])
    rows.append([InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="m:home")])
    return InlineKeyboardMarkup(rows)

# ─────────────── پانێڵی ئەدمین ───────────────
def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ دروستکردنی کۆدی بانگێشت", callback_data="a:new")],
        [InlineKeyboardButton("📋 کۆدە دروستکراوەکان",     callback_data="a:list")],
        [InlineKeyboardButton("➕ زیادکردنی بۆت",          callback_data="a:addbot")],
        [InlineKeyboardButton("🗑 سڕینەوەی بۆت",           callback_data="a:delbot")],
        [InlineKeyboardButton("📦 پاکێجەکان",              callback_data="a:pkgs")],
        [InlineKeyboardButton("⬅️ مێنیوی سەرەکی",          callback_data="m:home")],
    ])

def pkg_choice_kb(prefix: str):
    rows = [[InlineKeyboardButton(f"📦 {p['name']}", callback_data=f"{prefix}:{i}")]
            for i, p in enumerate(DB["packages"])]
    rows.append([InlineKeyboardButton("⬅️ پاشگەزبوونەوە", callback_data="a:home")])
    return InlineKeyboardMarkup(rows)

# ─────────────── /start ───────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=main_menu_kb())

# ─────────────── دوگمەکان ───────────────
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data or ""
    uid = q.from_user.id

    if data == "m:home":
        return await q.edit_message_text(WELCOME, reply_markup=main_menu_kb())
    if data == "m:pkgs":
        return await q.edit_message_text("📦 لیستی پاکێجەکان:", reply_markup=packages_kb())
    if data == "m:bots":
        return await q.edit_message_text("🤖 بۆتە بەردەستەکان:", reply_markup=bots_kb())
    if data == "m:about":
        return await q.edit_message_text(
            "𝙘𝙤𝙞𝙣𝙨𝙢𝙖𝙧𝙠𝙚𝙩 𝙗𝙤𝙩 ☘️\nبۆ پەرەپێدانی بۆتی تێلیگرام و فرۆشتنی پاکێج.",
            reply_markup=back_home(),
        )
    if data == "m:code":
        context.user_data["awaiting_code"] = True
        return await q.edit_message_text(
            "🔑 کۆدی پاکێج بنوسە:\n(کۆدی بانگێشت یان کۆدی ماستەر)",
            reply_markup=back_home(),
        )
    if data.startswith("pkg:"):
        idx = int(data.split(":")[1])
        p = DB["packages"][idx]
        text = f"📦 {p['name']}\n💰 نرخ: {p['price']}\n\nبۆ کڕین دوگمەی خوارەوە دابگرە."
        return await q.edit_message_text(text, reply_markup=package_view_kb(idx))

    # ─── ئەدمین ───
    if data.startswith("a:") and not is_admin(uid):
        return await q.edit_message_text("❌ ڕێگەت پێنەدراوە.", reply_markup=back_home())

    if data == "a:home":
        return await q.edit_message_text("⚙️ پانێڵی ئەدمین:", reply_markup=admin_kb())
    if data == "a:new":
        return await q.edit_message_text("جۆری پاکێج بۆ کۆدی نوێ هەڵبژێرە:",
                                         reply_markup=pkg_choice_kb("a:newpkg"))
    if data.startswith("a:newpkg:"):
        idx = int(data.split(":")[2])
        pkg = DB["packages"][idx]["name"]
        code = secrets.token_hex(4).upper()
        DB["invite_codes"][code] = {"package": pkg, "used_by": None}
        save_data()
        return await q.edit_message_text(
            f"✅ کۆدی بانگێشت دروستکرا:\n\n<code>{code}</code>\n\n📦 پاکێج: {pkg}",
            parse_mode="HTML", reply_markup=admin_kb(),
        )
    if data == "a:list":
        if not DB["invite_codes"]:
            txt = "هیچ کۆدێک نییە."
        else:
            lines = []
            for c, info in DB["invite_codes"].items():
                used = f"بەکارهات {info['used_by']}" if info["used_by"] else "بەردەستە"
                lines.append(f"<code>{c}</code> — {info['package']} — {used}")
            txt = "📋 کۆدەکان:\n\n" + "\n".join(lines)
        return await q.edit_message_text(txt, parse_mode="HTML", reply_markup=admin_kb())

    if data == "a:addbot":
        context.user_data["addbot"] = {"step": "name"}
        return await q.edit_message_text("✏️ ناوی بۆتەکە بنوسە:", reply_markup=back_home())
    if data.startswith("a:botpkg:"):
        idx = int(data.split(":")[2])
        pkg = DB["packages"][idx]["name"]
        info = context.user_data.get("addbot", {})
        DB["bots"].append({"name": info.get("name",""), "link": info.get("link",""), "package": pkg})
        save_data()
        context.user_data.pop("addbot", None)
        return await q.edit_message_text(f"✅ بۆت زیادکرا بە پاکێجی «{pkg}».", reply_markup=admin_kb())

    if data == "a:delbot":
        if not DB["bots"]:
            return await q.edit_message_text("هیچ بۆتێک نییە.", reply_markup=admin_kb())
        rows = [[InlineKeyboardButton(f"🗑 {b['name']}", callback_data=f"a:rmbot:{i}")]
                for i, b in enumerate(DB["bots"])]
        rows.append([InlineKeyboardButton("⬅️ گەڕانەوە", callback_data="a:home")])
        return await q.edit_message_text("بۆت بۆ سڕینەوە هەڵبژێرە:",
                                         reply_markup=InlineKeyboardMarkup(rows))
    if data.startswith("a:rmbot:"):
        idx = int(data.split(":")[2])
        if 0 <= idx < len(DB["bots"]):
            removed = DB["bots"].pop(idx)
            save_data()
            return await q.edit_message_text(f"🗑 «{removed['name']}» سڕایەوە.", reply_markup=admin_kb())

    if data == "a:pkgs":
        lines = [f"• {p['name']} — {p['price']}" for p in DB["packages"]]
        return await q.edit_message_text("📦 پاکێجەکان:\n" + "\n".join(lines), reply_markup=admin_kb())

    if data == "noop":
        return

# ─────────────── نامەی تێکست ───────────────
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    uid  = update.message.from_user.id

    # کۆد
    if context.user_data.get("awaiting_code"):
        context.user_data["awaiting_code"] = False
        if text == MASTER_CODE:
            if uid not in DB["admins"]:
                DB["admins"].append(uid); save_data()
            return await update.message.reply_text("✅ بەخێربێیت بۆ پانێڵی ئەدمین.",
                                                   reply_markup=admin_kb())
        if text in DB["invite_codes"]:
            info = DB["invite_codes"][text]
            if info["used_by"]:
                return await update.message.reply_text("⚠️ ئەم کۆدە پێشتر بەکارهاتووە.",
                                                       reply_markup=back_home())
            info["used_by"] = uid; save_data()
            return await update.message.reply_text(
                f"✅ کۆد قبوڵکرا!\n📦 پاکێج: {info['package']}",
                reply_markup=main_menu_kb(),
            )
        return await update.message.reply_text("❌ کۆد هەڵەیە.", reply_markup=back_home())

    # زیادکردنی بۆت — هەنگاوەکان
    addbot = context.user_data.get("addbot")
    if addbot and is_admin(uid):
        if addbot["step"] == "name":
            addbot["name"] = text
            addbot["step"] = "link"
            return await update.message.reply_text("🔗 لینکی بۆتەکە بنوسە (مثل: https://t.me/MyBot):")
        if addbot["step"] == "link":
            if not text.startswith("http"):
                return await update.message.reply_text("⚠️ لینکێکی دروست بنوسە.")
            addbot["link"] = text
            addbot["step"] = "pkg"
            return await update.message.reply_text("📦 جۆری پاکێج بۆ ئەم بۆتە هەڵبژێرە:",
                                                   reply_markup=pkg_choice_kb("a:botpkg"))

# ─────────────── دەستپێک ───────────────
async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "دەستپێک"),
        BotCommand("admin", "پانێڵی ئەدمین (پێویستە کۆدت هەبێت)"),
    ])

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.reply_text("⚙️ پانێڵی ئەدمین:", reply_markup=admin_kb())
    else:
        context.user_data["awaiting_code"] = True
        await update.message.reply_text("🔑 کۆدی ماستەر بنوسە:")

def main():
    if BOT_TOKEN.startswith("PUT-"):
        raise SystemExit("⚠️ BOT_TOKEN دانەنراوە. لە ژینگەی سیستەم دایبنێ یان لە سەرەوەی فایلەکە.")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("🚀 Bot is running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
