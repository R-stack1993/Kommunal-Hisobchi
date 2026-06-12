# main.py
import asyncio
import os
import io
from datetime import datetime
import openpyxl 

from dotenv import load_dotenv
load_dotenv()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, 
    InlineKeyboardButton, FSInputFile, BufferedInputFile, ReplyKeyboardRemove
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import calculate_tiered_cost, get_days_in_month
from database import (
    init_models, add_user, get_readings_context, save_new_reading, get_all_users, 
    delete_last_reading, count_users, get_all_users_detailed, set_user_ban_status, check_if_banned, 
    get_monthly_usage_data, get_user_houses, add_house, delete_house, get_house_by_id,
    delete_all_readings_for_house, get_user_language, set_user_language
)
from locales import get_text

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))


# --- DYNAMIC KEYBOARDS ---
def get_main_kb(lang: str = 'uz') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('btn_elektr', lang)), KeyboardButton(text=get_text('btn_gaz', lang))],
            [KeyboardButton(text=get_text('btn_my_houses', lang)), KeyboardButton(text=get_text('btn_my_stats', lang))],
            [KeyboardButton(text=get_text('btn_clear_history', lang))],
            [KeyboardButton(text=get_text('btn_share', lang)), KeyboardButton(text=get_text('btn_add_group', lang))]
        ],
        resize_keyboard=True
    )

def get_admin_kb(lang: str = 'uz') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('btn_statistics', lang)), KeyboardButton(text=get_text('btn_broadcast', lang))],
            [KeyboardButton(text=get_text('btn_export_db', lang))],
            [KeyboardButton(text=get_text('btn_ban', lang)), KeyboardButton(text=get_text('btn_unban', lang))],
            [KeyboardButton(text=get_text('btn_back_main', lang))]
        ],
        resize_keyboard=True
    )

def get_lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Russkiy", callback_data="set_lang_ru")]
    ])


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if event.from_user:
            is_banned = await check_if_banned(event.from_user.id)
            if is_banned and event.from_user.id != ADMIN_ID:
                lang = await get_user_language(event.from_user.id)
                if isinstance(event, types.Message):
                    await event.answer(get_text('banned_message', lang))
                elif isinstance(event, types.CallbackQuery):
                    await event.answer(get_text('banned_alert', lang), show_alert=True)
                return 
        return await handler(event, data)

class HouseForm(StatesGroup):
    waiting_for_name = State()

class UtilityForm(StatesGroup):
    waiting_for_current = State()

class AdminForm(StatesGroup):
    waiting_for_broadcast = State()

class AdminBanForm(StatesGroup):
    waiting_for_ban = State()
    waiting_for_unban = State()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.message.middleware(BanCheckMiddleware())
dp.callback_query.middleware(BanCheckMiddleware())

async def send_monthly_reminders():
    users = await get_all_users()
    for user_id in users:
        is_banned = await check_if_banned(user_id)
        if is_banned:
            continue
        try:
            lang = await get_user_language(user_id)
            await bot.send_message(
                chat_id=user_id,
                text=get_text('monthly_reminder', lang),
                reply_markup=get_main_kb(lang), parse_mode="Markdown"
            )
        except Exception:
            pass 

@dp.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_messages(message: types.Message):
    if message.text and (message.text.startswith('/hisob') or message.text.startswith('/start')):
        lang = await get_user_language(message.from_user.id)
        bot_info = await bot.get_me()
        ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=get_text('group_btn_private', lang), url=f"https://t.me/{bot_info.username}")]])
        await message.reply(get_text('group_redirect', lang), reply_markup=ikb)

# --- LANGUAGE SELECTION (/lang command) ---
@dp.message(F.chat.type == "private", Command("lang"))
async def cmd_lang(message: types.Message):
    await message.answer(get_text('lang_select', 'uz'), reply_markup=get_lang_kb())

@dp.callback_query(F.data.in_(["set_lang_uz", "set_lang_ru"]))
async def process_lang_selection(callback: types.CallbackQuery):
    lang = 'uz' if callback.data == "set_lang_uz" else 'ru'
    await add_user(callback.from_user.id, callback.from_user.full_name)
    await set_user_language(callback.from_user.id, lang)
    await callback.message.edit_text(get_text('lang_changed', lang))
    await callback.message.answer(get_text('start_welcome', lang), reply_markup=get_main_kb(lang))

# --- UYLARNI BOSHQARISH (HOUSE MANAGEMENT) ---
@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_my_houses', 'uz'), get_text('btn_my_houses', 'ru')
]))
async def my_houses_menu(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    houses = await get_user_houses(message.from_user.id)
    
    if not houses:
        text = get_text('no_houses', lang)
    else:
        text = get_text('houses_list_header', lang)
        for i, h in enumerate(houses, 1):
            text += f"{i}. **{h.name}**\n"
            
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([InlineKeyboardButton(text=get_text('house_delete_btn', lang, name=h.name), callback_data=f"delhouse_{h.id}")])
        
    if len(houses) < 5:
        ikb.inline_keyboard.append([InlineKeyboardButton(text=get_text('house_add_btn', lang), callback_data="add_house")])
        
    await message.answer(text, reply_markup=ikb, parse_mode="Markdown")

@dp.callback_query(F.data == "add_house")
async def start_add_house(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(callback.from_user.id)
    houses = await get_user_houses(callback.from_user.id)
    if len(houses) >= 5:
        await callback.answer(get_text('house_limit_alert', lang), show_alert=True)
        return
        
    suggested_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text('house_name_main', lang)), KeyboardButton(text=get_text('house_name_yard', lang))],
            [KeyboardButton(text=get_text('house_name_apartment', lang)), KeyboardButton(text=get_text('house_name_dacha', lang))],
            [KeyboardButton(text=get_text('house_cancel_btn', lang))]
        ], resize_keyboard=True
    )
    await callback.message.delete()
    await callback.message.answer(get_text('house_name_prompt', lang), reply_markup=suggested_kb)
    await state.set_state(HouseForm.waiting_for_name)

@dp.message(F.chat.type == "private", HouseForm.waiting_for_name)
async def process_house_name(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    cancel_texts = [get_text('house_cancel_btn', 'uz'), get_text('house_cancel_btn', 'ru')]
    if message.text in cancel_texts:
        await message.answer(get_text('house_cancelled', lang), reply_markup=get_main_kb(lang))
        await state.clear()
        return
        
    name = message.text[:30]  # Limit length
    success = await add_house(message.from_user.id, name)
    if success:
        await message.answer(get_text('house_added', lang, name=name), reply_markup=get_main_kb(lang), parse_mode="Markdown")
    else:
        await message.answer(get_text('house_add_error', lang), reply_markup=get_main_kb(lang))
    await state.clear()

@dp.callback_query(F.data.startswith("delhouse_"))
async def prompt_del_house(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    house_id = int(callback.data.split("_")[1])
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('house_delete_yes', lang), callback_data=f"confdelhouse_{house_id}")],
        [InlineKeyboardButton(text=get_text('house_delete_no', lang), callback_data="cancel_action")]
    ])
    await callback.message.edit_text(get_text('house_delete_confirm', lang), reply_markup=ikb)

@dp.callback_query(F.data.startswith("confdelhouse_"))
async def confirm_del_house(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    house_id = int(callback.data.split("_")[1])
    success = await delete_house(house_id, callback.from_user.id)
    if success:
        await callback.message.edit_text(get_text('house_deleted', lang))
    else:
        await callback.answer(get_text('house_delete_error', lang), show_alert=True)

@dp.callback_query(F.data == "cancel_action")
async def cancel_inline_action(callback: types.CallbackQuery):
    await callback.message.delete()

# --- HISOB-KITOB LOGIKASI (UYLAR KESIMIDA) ---
@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_elektr', 'uz'), get_text('btn_elektr', 'ru'),
    get_text('btn_gaz', 'uz'), get_text('btn_gaz', 'ru')
]))
async def select_utility(message: types.Message, state: FSMContext):
    await add_user(message.from_user.id, message.from_user.full_name)
    lang = await get_user_language(message.from_user.id)
    
    elektr_texts = [get_text('btn_elektr', 'uz'), get_text('btn_elektr', 'ru')]
    utility_type = "elektr" if message.text in elektr_texts else "gaz"
    
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer(get_text('no_houses_for_utility', lang))
        return
        
    if len(houses) == 1:
        await state.update_data(utility_type=utility_type, house_id=houses[0].id)
        await prompt_reading(message, houses[0].id, utility_type, houses[0].name, lang)
    else:
        ikb = InlineKeyboardMarkup(inline_keyboard=[])
        for h in houses:
            ikb.inline_keyboard.append([InlineKeyboardButton(text=h.name, callback_data=f"selhouse_{utility_type}_{h.id}")])
        await message.answer(get_text('select_house_for_utility', lang, utility=utility_type.capitalize()), reply_markup=ikb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("selhouse_"))
async def inline_select_house(callback: types.CallbackQuery, state: FSMContext):
    lang = await get_user_language(callback.from_user.id)
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    house = await get_house_by_id(house_id)
    
    await state.update_data(utility_type=utility_type, house_id=house_id)
    await callback.message.delete()
    await prompt_reading(callback.message, house_id, utility_type, house.name, lang)

async def prompt_reading(message: types.Message, house_id: int, utility_type: str, house_name: str, lang: str = 'uz'):
    last_record, _, _ = await get_readings_context(message.chat.id, house_id, utility_type)
    icon = "💡" if utility_type == "elektr" else "🔥"
    
    if last_record is not None:
        await bot.send_message(
            chat_id=message.chat.id,
            text=get_text('reading_prompt_existing', lang, house_name=house_name, last_value=f"{last_record.reading_value:,.0f}", icon=icon),
            parse_mode="Markdown"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=get_text('reading_prompt_new', lang, house_name=house_name, icon=icon),
            parse_mode="Markdown"
        )
    state = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await state.set_state(UtilityForm.waiting_for_current)

@dp.message(F.chat.type == "private", UtilityForm.waiting_for_current)
async def process_current_reading(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer(get_text('reading_invalid_number', lang))
        return
        
    data = await state.get_data()
    utility_type = data['utility_type']
    house_id = data['house_id']
    current_reading = float(message.text)
    
    house = await get_house_by_id(house_id)
    last_record, curr_month_start, prev_month_start = await get_readings_context(message.from_user.id, house_id, utility_type)
    
    if last_record and current_reading < last_record.reading_value:
        await message.answer(get_text('reading_too_small', lang))
        return

    now = datetime.now()
    if not last_record:
        await save_new_reading(message.from_user.id, house_id, utility_type, current_reading)
        await message.answer(get_text('reading_initial_saved', lang))
        await state.clear()
        return

    is_new_month = last_record.created_at.month != now.month
    await save_new_reading(message.from_user.id, house_id, utility_type, current_reading)

    icon = "💡" if utility_type == "elektr" else "🔥"

    # Undo button
    undo_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('undo_btn', lang), callback_data=f"undo_{utility_type}_{house_id}")]
    ])

    if is_new_month:
        prev_year = last_record.created_at.year
        prev_month = last_record.created_at.month
        days_in_prev = get_days_in_month(prev_year, prev_month)
        
        usage = current_reading - prev_month_start
        cost, season_info = calculate_tiered_cost(usage, utility_type)
        daily_avg = usage / days_in_prev if days_in_prev else 0
        season_text = f" ({season_info})" if season_info else ""
        
        response_text = get_text('report_new_month', lang,
            prev_month=prev_month,
            house_name=house.name,
            icon=icon,
            utility=utility_type.capitalize(),
            season_text=season_text,
            usage=f"{usage:,.0f}",
            cost=f"{cost:,.0f}",
            daily_avg=f"{daily_avg:.1f}",
            curr_month=now.month
        )
        await message.answer(response_text, reply_markup=undo_ikb, parse_mode="Markdown")
    else:
        if curr_month_start is None:
            curr_month_start = current_reading 
            
        total_usage = current_reading - curr_month_start
        total_cost, season_info = calculate_tiered_cost(total_usage, utility_type)
        segment_usage = current_reading - last_record.reading_value
        
        previous_usage = last_record.reading_value - curr_month_start
        previous_cost, _ = calculate_tiered_cost(previous_usage, utility_type)
        segment_cost = total_cost - previous_cost
        
        season_text = f"\n📅 {season_info}" if season_info else ""
        
        response_text = get_text('report_same_month', lang,
            house_name=house.name,
            icon=icon,
            utility=utility_type.capitalize(),
            season_text=season_text,
            total_usage=f"{total_usage:,.0f}",
            total_cost=f"{total_cost:,.0f}"
        )

        if segment_usage > 0 and segment_usage != total_usage:
            response_text += get_text('report_segment', lang,
                segment_usage=f"{segment_usage:,.0f}",
                segment_cost=f"{segment_cost:,.0f}"
            )
        await message.answer(response_text, reply_markup=undo_ikb, parse_mode="Markdown")
        
    await state.clear()

@dp.callback_query(F.data.startswith("undo_"))
async def process_undo_reading(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    success = await delete_last_reading(callback.from_user.id, house_id, utility_type)
    if success:
        await callback.answer(get_text('undo_success', lang), show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer(get_text('undo_not_found', lang), show_alert=True)

# --- TARIXNI TOZALASH ---
@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_clear_history', 'uz'), get_text('btn_clear_history', 'ru')
]))
async def clear_history_menu(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer(get_text('clear_no_houses', lang))
        return
        
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=get_text('clear_elektr_btn', lang, name=h.name), callback_data=f"clrhist_elektr_{h.id}")
        ])
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=get_text('clear_gaz_btn', lang, name=h.name), callback_data=f"clrhist_gaz_{h.id}")
        ])
    await message.answer(get_text('clear_prompt', lang), reply_markup=ikb)

@dp.callback_query(F.data.startswith("clrhist_"))
async def confirm_clear_history(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('clear_yes', lang), callback_data=f"do_clrhist_{utility_type}_{house_id}")],
        [InlineKeyboardButton(text=get_text('clear_no', lang), callback_data="cancel_action")]
    ])
    await callback.message.edit_text(get_text('clear_confirm', lang), reply_markup=ikb)

@dp.callback_query(F.data.startswith("do_clrhist_"))
async def do_clear_history(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    _, utility_type, house_id_str = callback.data.split("_")
    count = await delete_all_readings_for_house(callback.from_user.id, int(house_id_str), utility_type)
    await callback.message.edit_text(get_text('clear_done', lang, count=count))

# --- VIZUAL GRAFIK (STATISTIKA) ---
def create_chart_image(usage_data: list, utility_type: str, house_name: str, lang: str = 'uz') -> io.BytesIO:
    labels = [x[0] for x in usage_data]
    values = [x[1] for x in usage_data]

    plt.figure(figsize=(9, 5), facecolor='#f4f4f9')
    ax = plt.axes()
    ax.set_facecolor('#ffffff')
    
    color = '#ff9999' if utility_type == 'gaz' else '#66b3ff'
    edge_color = '#cc0000' if utility_type == 'gaz' else '#0055ff'

    bars = plt.bar(labels, values, color=color, edgecolor=edge_color, width=0.6, linewidth=1.5, zorder=3)
    
    plt.title(get_text('chart_title', lang, house_name=house_name, utility=utility_type.capitalize()), fontsize=14, fontweight='bold', pad=15)
    plt.ylabel(get_text('chart_ylabel', lang), fontsize=11, labelpad=10)
    plt.grid(axis='y', linestyle='--', alpha=0.6, zorder=0)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max(values)*0.03 if max(values) > 0 else 0), 
                 f"{yval:,.0f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_my_stats', 'uz'), get_text('btn_my_stats', 'ru')
]))
async def stats_menu_handler(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer(get_text('stats_no_houses', lang))
        return
        
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=get_text('stats_elektr_btn', lang, name=h.name), callback_data=f"chart_elektr_{h.id}"),
            InlineKeyboardButton(text=get_text('stats_gaz_btn', lang, name=h.name), callback_data=f"chart_gaz_{h.id}")
        ])
    await message.answer(get_text('stats_prompt', lang), reply_markup=ikb)

@dp.callback_query(F.data.startswith("chart_"))
async def process_chart_generation(callback: types.CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    await callback.answer(get_text('stats_loading', lang))
    
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    house = await get_house_by_id(house_id)
    
    usage_data = await get_monthly_usage_data(callback.from_user.id, house_id, utility_type)
    
    if not usage_data:
        await callback.message.answer(get_text('stats_not_enough', lang))
        return
        
    image_buffer = create_chart_image(usage_data, utility_type, house.name, lang)
    photo = BufferedInputFile(image_buffer.read(), filename=f"{utility_type}_stats.png")
    
    caption = get_text('stats_caption', lang, house_name=house.name, utility=utility_type.capitalize())
    await callback.message.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")

# --- ADMIN QISMLARI ---
@dp.message(F.chat.type == "private", Command("admin"), F.from_user.id == ADMIN_ID)
async def cmd_admin(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('admin_welcome', lang), reply_markup=get_admin_kb(lang))

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_back_main', 'uz'), get_text('btn_back_main', 'ru')
]), F.from_user.id == ADMIN_ID)
async def back_to_main_admin(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('admin_back_main', lang), reply_markup=get_main_kb(lang))

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_statistics', 'uz'), get_text('btn_statistics', 'ru')
]), F.from_user.id == ADMIN_ID)
async def show_statistics(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    total_users = await count_users()
    await message.answer(get_text('admin_stats', lang, count=total_users), parse_mode="Markdown")

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_export_db', 'uz'), get_text('btn_export_db', 'ru')
]), F.from_user.id == ADMIN_ID)
async def export_db(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('admin_export_loading', lang))
    users = await get_all_users_detailed()
    filename = f"baza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = get_text('admin_export_headers', lang)
    ws.append(headers)
    for u in users:
        reg_date = u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else get_text('admin_export_unknown', lang)
        ban_status = get_text('admin_export_yes', lang) if u.is_banned else get_text('admin_export_no', lang)
        ws.append([u.id, u.telegram_id, str(u.full_name), reg_date, ban_status])
    wb.save(filename)
    await message.answer_document(FSInputFile(filename))
    os.remove(filename)

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_broadcast', 'uz'), get_text('btn_broadcast', 'ru')
]), F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('admin_broadcast_prompt', lang), reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminForm.waiting_for_broadcast)

@dp.message(F.chat.type == "private", Command("cancel"), F.from_user.id == ADMIN_ID)
async def cancel_action_admin(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.clear()
    await message.answer(get_text('admin_cancelled', lang), reply_markup=get_admin_kb(lang))

@dp.message(F.chat.type == "private", AdminForm.waiting_for_broadcast, F.from_user.id == ADMIN_ID)
async def send_broadcast(message: types.Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    users = await get_all_users_detailed()
    sent, fail = 0, 0
    await message.answer(get_text('admin_broadcast_sending', lang))
    for u in users:
        if not u.is_banned:
            try:
                await message.copy_to(chat_id=u.telegram_id)
                sent += 1
                await asyncio.sleep(0.05)
            except:
                fail += 1
    await message.answer(get_text('admin_broadcast_done', lang, sent=sent, fail=fail), reply_markup=get_admin_kb(lang))
    await state.clear()

@dp.message(F.chat.type == "private", Command("start"))
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.full_name)
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('lang_select', lang), reply_markup=get_lang_kb())

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_add_group', 'uz'), get_text('btn_add_group', 'ru')
]))
async def add_bot_to_group(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    bot_info = await bot.get_me()
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=get_text('add_group_btn', lang), url=f"https://t.me/{bot_info.username}?startgroup=true")]])
    await message.answer(get_text('add_group_prompt', lang), reply_markup=ikb)

@dp.message(F.chat.type == "private", F.text.in_([
    get_text('btn_share', 'uz'), get_text('btn_share', 'ru')
]))
async def share_bot(message: types.Message):
    lang = await get_user_language(message.from_user.id)
    bot_info = await bot.get_me()
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_info.username}&text=Zo'r bot!"
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=get_text('share_btn', lang), url=share_url)]])
    await message.answer(get_text('share_prompt', lang), reply_markup=ikb)

async def main():
    await init_models()
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_monthly_reminders, trigger='cron', day=1, hour=9, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
