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
    get_monthly_usage_data, get_user_houses, add_house, delete_house, get_house_by_id, delete_all_readings_for_house
)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if event.from_user:
            is_banned = await check_if_banned(event.from_user.id)
            if is_banned and event.from_user.id != ADMIN_ID:
                if isinstance(event, types.Message):
                    await event.answer("🚫 Siz qoidalarni buzganligingiz sababli botdan foydalanishdan chetlatilgansiz.")
                elif isinstance(event, types.CallbackQuery):
                    await event.answer("🚫 Siz bloklangansiz!", show_alert=True)
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

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Elektr"), KeyboardButton(text="🔥 Gaz")],
        [KeyboardButton(text="🏠 Mening uylarim"), KeyboardButton(text="📈 Mening sarfiyatim")],
        [KeyboardButton(text="❌ Tarixni tozalash")],
        [KeyboardButton(text="🔗 Do'stlarga ulashish"), KeyboardButton(text="➕ Guruhga qo'shish")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="📁 Baza yuklab olish")],
        [KeyboardButton(text="🚫 Bloklash"), KeyboardButton(text="✅ Bandan yechish")],
        [KeyboardButton(text="🔙 Asosiy menyuga")]
    ],
    resize_keyboard=True
)

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
            await bot.send_message(
                chat_id=user_id,
                text="🔔 **Yangi oy boshlandi!**\n\nHisobotlarni ko'rish uchun ko'rsatkichlarni kiriting.",
                reply_markup=main_kb, parse_mode="Markdown"
            )
        except Exception:
            pass 

@dp.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_messages(message: types.Message):
    if message.text and (message.text.startswith('/hisob') or message.text.startswith('/start')):
        bot_info = await bot.get_me()
        ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✉️ Shaxsiy xabarga o'tish", url=f"https://t.me/{bot_info.username}")]])
        await message.reply("Hurmatli foydalanuvchi, jarayonni shaxsiy xabarda amalga oshiramiz 👇", reply_markup=ikb)

# --- UYLARNI BOSHQARISH (HOUSE MANAGEMENT) ---
@dp.message(F.chat.type == "private", F.text == "🏠 Mening uylarim")
async def my_houses_menu(message: types.Message):
    houses = await get_user_houses(message.from_user.id)
    
    if not houses:
        text = "Sizda hali uylar qo'shilmagan. Bot hisob-kitobni to'g'ri olib borishi uchun avval xonadon qo'shing."
    else:
        text = "Sizning uylaringiz ro'yxati:\n\n"
        for i, h in enumerate(houses, 1):
            text += f"{i}. **{h.name}**\n"
            
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([InlineKeyboardButton(text=f"🗑 {h.name} ni o'chirish", callback_data=f"delhouse_{h.id}")])
        
    if len(houses) < 5:
        ikb.inline_keyboard.append([InlineKeyboardButton(text="➕ Yangi uy qo'shish", callback_data="add_house")])
        
    await message.answer(text, reply_markup=ikb, parse_mode="Markdown")

@dp.callback_query(F.data == "add_house")
async def start_add_house(callback: types.CallbackQuery, state: FSMContext):
    houses = await get_user_houses(callback.from_user.id)
    if len(houses) >= 5:
        await callback.answer("Siz eng ko'pi bilan 5 ta uy qo'sha olasiz!", show_alert=True)
        return
        
    suggested_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Asosiy uy"), KeyboardButton(text="🏡 Hovli")],
            [KeyboardButton(text="🏢 Kvartira"), KeyboardButton(text="🏕 Dacha")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ], resize_keyboard=True
    )
    await callback.message.delete()
    await callback.message.answer("Yangi xonadon uchun nom tanlang yoki o'zingiz xohlagan nomni matn qilib yozing:", reply_markup=suggested_kb)
    await state.set_state(HouseForm.waiting_for_name)

@dp.message(F.chat.type == "private", HouseForm.waiting_for_name)
async def process_house_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Jarayon bekor qilindi.", reply_markup=main_kb)
        await state.clear()
        return
        
    name = message.text[:30] # Limit length
    success = await add_house(message.from_user.id, name)
    if success:
        await message.answer(f"✅ **{name}** muvaffaqiyatli qo'shildi!", reply_markup=main_kb, parse_mode="Markdown")
    else:
        await message.answer("Xatolik yoki limit (5 ta) to'ldi.", reply_markup=main_kb)
    await state.clear()

@dp.callback_query(F.data.startswith("delhouse_"))
async def prompt_del_house(callback: types.CallbackQuery):
    house_id = int(callback.data.split("_")[1])
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ Ha, o'chirish (Barcha tarix o'chadi)", callback_data=f"confdelhouse_{house_id}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ])
    await callback.message.edit_text("Ushbu uyni va unga tegishli barcha sarfiyat tarixini o'chirib tashlaysizmi?", reply_markup=ikb)

@dp.callback_query(F.data.startswith("confdelhouse_"))
async def confirm_del_house(callback: types.CallbackQuery):
    house_id = int(callback.data.split("_")[1])
    success = await delete_house(house_id, callback.from_user.id)
    if success:
        await callback.message.edit_text("✅ Uy va uning tarixi to'liq o'chirildi.")
    else:
        await callback.answer("Xatolik.", show_alert=True)

@dp.callback_query(F.data == "cancel_action")
async def cancel_inline_action(callback: types.CallbackQuery):
    await callback.message.delete()

# --- HISOB-KITOB LOGIKASI (UYLAR KESIMIDA) ---
@dp.message(F.chat.type == "private", F.text.in_(["💡 Elektr", "🔥 Gaz"]))
async def select_utility(message: types.Message, state: FSMContext):
    await add_user(message.from_user.id, message.from_user.full_name)
    utility_type = "elektr" if message.text == "💡 Elektr" else "gaz"
    
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer("Sizda xonadonlar yo'q. Iltimos, pastdagi menyudan '🏠 Mening uylarim' tugmasini bosib uy qo'shing.")
        return
        
    if len(houses) == 1:
        await state.update_data(utility_type=utility_type, house_id=houses[0].id)
        await prompt_reading(message, houses[0].id, utility_type, houses[0].name)
    else:
        ikb = InlineKeyboardMarkup(inline_keyboard=[])
        for h in houses:
            ikb.inline_keyboard.append([InlineKeyboardButton(text=h.name, callback_data=f"selhouse_{utility_type}_{h.id}")])
        await message.answer(f"Qaysi manzil uchun **{utility_type.capitalize()}** ko'rsatkichini kiritmoqchisiz?", reply_markup=ikb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("selhouse_"))
async def inline_select_house(callback: types.CallbackQuery, state: FSMContext):
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    house = await get_house_by_id(house_id)
    
    await state.update_data(utility_type=utility_type, house_id=house_id)
    await callback.message.delete()
    await prompt_reading(callback.message, house_id, utility_type, house.name)

async def prompt_reading(message: types.Message, house_id: int, utility_type: str, house_name: str):
    last_record, _, _ = await get_readings_context(message.chat.id, house_id, utility_type)
    icon = "💡" if utility_type == "elektr" else "🔥"
    
    if last_record is not None:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"🏠 Manzil: **{house_name}**\nBazada saqlangan oxirgi ko'rsatkich: **{last_record.reading_value:,.0f}**\n\n{icon} Iltimos, hisoblagichingizdagi joriy (bugungi) ko'rsatkichni kiriting:",
            parse_mode="Markdown"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"🏠 Manzil: **{house_name}**\nSizda eski ko'rsatkichlar topilmadi.\n{icon} Iltimos, joriy hisoblagich ko'rsatkichini kiriting (Bu kelajak hisob-kitoblar uchun tayanch bo'ladi):",
            parse_mode="Markdown"
        )
    state = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await state.set_state(UtilityForm.waiting_for_current)

@dp.message(F.chat.type == "private", UtilityForm.waiting_for_current)
async def process_current_reading(message: types.Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
        
    data = await state.get_data()
    utility_type = data['utility_type']
    house_id = data['house_id']
    current_reading = float(message.text)
    
    house = await get_house_by_id(house_id)
    last_record, curr_month_start, prev_month_start = await get_readings_context(message.from_user.id, house_id, utility_type)
    
    if last_record and current_reading < last_record.reading_value:
        await message.answer("Xatolik: Joriy ko'rsatkich o'tgan safargidan kichik bo'lishi mumkin emas. Qayta kiriting.")
        return

    now = datetime.now()
    if not last_record:
        await save_new_reading(message.from_user.id, house_id, utility_type, current_reading)
        await message.answer("✅ Boshlang'ich ko'rsatkich muvaffaqiyatli saqlandi! Keyingi safar tekshirganingizda to'liq hisob-kitobni ko'rasiz.")
        await state.clear()
        return

    is_new_month = last_record.created_at.month != now.month
    await save_new_reading(message.from_user.id, house_id, utility_type, current_reading)

    icon = "💡" if utility_type == "elektr" else "🔥"

    # Xato kiritgan bo'lsa o'chirish tugmasi (Kvitansiya ostida turadi)
    undo_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Oxirgi ko'rsatkichni bekor qilish", callback_data=f"undo_{utility_type}_{house_id}")]
    ])

    if is_new_month:
        prev_year = last_record.created_at.year
        prev_month = last_record.created_at.month
        days_in_prev = get_days_in_month(prev_year, prev_month)
        
        usage = current_reading - prev_month_start
        cost, season_info = calculate_tiered_cost(usage, utility_type)
        daily_avg = usage / days_in_prev if days_in_prev else 0
        season_text = f" ({season_info})" if season_info else ""
        
        response_text = (
            f"📊 **{prev_month}-oy uchun YAKUNIY HISOBOT**\n"
            f"🏠 Manzil: {house.name}\n"
            f"🛠 Xizmat turi: {icon} {utility_type.capitalize()}{season_text}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🔄 Bir oylik jami sarf: {usage:,.0f} kVt/m³\n"
            f"💵 Oylik to'lov summasi: {cost:,.0f} so'm\n"
            f"📈 Kunlik o'rtacha sarf: {daily_avg:.1f} kVt/m³\n\n"
            f"✅ *Ushbu ko'rsatkich yangi ({now.month}-oy) uchun boshlang'ich (tayanch) nuqta sifatida qabul qilindi.*"
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
        
        response_text = (
            f"🧾 **Batafsil Hisobot**\n"
            f"🏠 Manzil: {house.name}\n"
            f"🛠 Xizmat: {icon} {utility_type.capitalize()}{season_text}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🔄 Jami sarf: {total_usage:,.0f} kVt/m³\n"
            f"💰 **Jami to'lov: {total_cost:,.0f} so'm**\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
        )

        if segment_usage > 0 and segment_usage != total_usage:
            response_text += (
                f"⏱ **Oxirgi tekshiruvdan keyingi oraliq:**\n"
                f"🔄 Oraliq sarf: {segment_usage:,.0f} kVt/m³\n"
                f"💵 **Oraliq uchun to'lov: {segment_cost:,.0f} so'm**"
            )
        await message.answer(response_text, reply_markup=undo_ikb, parse_mode="Markdown")
        
    await state.clear()

@dp.callback_query(F.data.startswith("undo_"))
async def process_undo_reading(callback: types.CallbackQuery):
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    success = await delete_last_reading(callback.from_user.id, house_id, utility_type)
    if success:
        await callback.answer("✅ Oxirgi xato kiritilgan ko'rsatkich bekor qilindi!", show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("O'chirish uchun ko'rsatkich topilmadi.", show_alert=True)

# --- TARIXNI TOZALASH ---
@dp.message(F.chat.type == "private", F.text == "❌ Tarixni tozalash")
async def clear_history_menu(message: types.Message):
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer("Sizda xonadonlar topilmadi.")
        return
        
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=f"💡 {h.name} - Elektrni tozalash", callback_data=f"clrhist_elektr_{h.id}")
        ])
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=f"🔥 {h.name} - Gazni tozalash", callback_data=f"clrhist_gaz_{h.id}")
        ])
    await message.answer("Qaysi manzilning hisoblash tarixini butunlay tozalab tashlamoqchisiz?", reply_markup=ikb)

@dp.callback_query(F.data.startswith("clrhist_"))
async def confirm_clear_history(callback: types.CallbackQuery):
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚠️ Ha, ishonchim komil", callback_data=f"do_clrhist_{utility_type}_{house_id}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ])
    await callback.message.edit_text("Barcha tarix o'chiriladi. Ishonchingiz komilmi?", reply_markup=ikb)

@dp.callback_query(F.data.startswith("do_clrhist_"))
async def do_clear_history(callback: types.CallbackQuery):
    _, utility_type, house_id_str = callback.data.split("_")
    count = await delete_all_readings_for_house(callback.from_user.id, int(house_id_str), utility_type)
    await callback.message.edit_text(f"✅ Barcha ({count} ta) yozuvlar tarix bo'yicha tozalandi.")

# --- VIZUAL GRAFIK (STATISTIKA) ---
def create_chart_image(usage_data: list, utility_type: str, house_name: str) -> io.BytesIO:
    labels = [x[0] for x in usage_data]
    values = [x[1] for x in usage_data]

    plt.figure(figsize=(9, 5), facecolor='#f4f4f9')
    ax = plt.axes()
    ax.set_facecolor('#ffffff')
    
    color = '#ff9999' if utility_type == 'gaz' else '#66b3ff'
    edge_color = '#cc0000' if utility_type == 'gaz' else '#0055ff'

    bars = plt.bar(labels, values, color=color, edgecolor=edge_color, width=0.6, linewidth=1.5, zorder=3)
    
    plt.title(f"[{house_name}] {utility_type.capitalize()} oylik sarfiyati", fontsize=14, fontweight='bold', pad=15)
    plt.ylabel("Sarfiyat miqdori (kVt / m³)", fontsize=11, labelpad=10)
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

@dp.message(F.chat.type == "private", F.text == "📈 Mening sarfiyatim")
async def stats_menu_handler(message: types.Message):
    houses = await get_user_houses(message.from_user.id)
    if not houses:
        await message.answer("Grafikni ko'rish uchun avval uy qo'shing va ko'rsatkich kiriting.")
        return
        
    ikb = InlineKeyboardMarkup(inline_keyboard=[])
    for h in houses:
        ikb.inline_keyboard.append([
            InlineKeyboardButton(text=f"💡 {h.name} (Elektr)", callback_data=f"chart_elektr_{h.id}"),
            InlineKeyboardButton(text=f"🔥 {h.name} (Gaz)", callback_data=f"chart_gaz_{h.id}")
        ])
    await message.answer("📈 Qaysi manzil bo'yicha vizual oylik hisobotni ko'rmoqchisiz?", reply_markup=ikb)

@dp.callback_query(F.data.startswith("chart_"))
async def process_chart_generation(callback: types.CallbackQuery):
    await callback.answer("Grafik tayyorlanmoqda, kuting... ⏳")
    
    _, utility_type, house_id_str = callback.data.split("_")
    house_id = int(house_id_str)
    house = await get_house_by_id(house_id)
    
    usage_data = await get_monthly_usage_data(callback.from_user.id, house_id, utility_type)
    
    if not usage_data:
        await callback.message.answer("⚠️ Grafik shakllantirish uchun kamida 2 oylik ko'rsatkichlar tarixi kerak.")
        return
        
    image_buffer = create_chart_image(usage_data, utility_type, house.name)
    photo = BufferedInputFile(image_buffer.read(), filename=f"{utility_type}_stats.png")
    
    icon = "💡" if utility_type == 'elektr' else "🔥"
    caption = f"📈 **{house.name} uchun {utility_type.capitalize()} sarfiyat grafigi!**"
    await callback.message.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")

# --- ADMIN QISMLARI (ESKIDAN QOLGAN) ---
@dp.message(F.chat.type == "private", Command("admin"), F.from_user.id == ADMIN_ID)
async def cmd_admin(message: types.Message):
    await message.answer("👨‍💻 Admin panelga xush kelibsiz!", reply_markup=admin_kb)

@dp.message(F.chat.type == "private", F.text == "🔙 Asosiy menyuga", F.from_user.id == ADMIN_ID)
async def back_to_main_admin(message: types.Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_kb)

@dp.message(F.chat.type == "private", F.text == "📊 Statistika", F.from_user.id == ADMIN_ID)
async def show_statistics(message: types.Message):
    total_users = await count_users()
    await message.answer(f"👥 Jami ro'yxatdan o'tganlar: **{total_users} ta**", parse_mode="Markdown")

@dp.message(F.chat.type == "private", F.text == "📁 Baza yuklab olish", F.from_user.id == ADMIN_ID)
async def export_db(message: types.Message):
    await message.answer("Excel tayyorlanmoqda...")
    users = await get_all_users_detailed()
    filename = f"baza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Telegram ID", "Ism", "Ro'yxatdan o'tgan sana", "Bloklanganmi?"])
    for u in users:
        reg_date = u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else "Noma'lum"
        ws.append([u.id, u.telegram_id, str(u.full_name), reg_date, "Ha" if u.is_banned else "Yo'q"])
    wb.save(filename)
    await message.answer_document(FSInputFile(filename))
    os.remove(filename)

@dp.message(F.chat.type == "private", F.text == "📢 Xabar yuborish", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer("Barcha bloklanmagan foydalanuvchilarga xabarni yozing: (/cancel)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminForm.waiting_for_broadcast)

@dp.message(F.chat.type == "private", Command("cancel"), F.from_user.id == ADMIN_ID)
async def cancel_action_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=admin_kb)

@dp.message(F.chat.type == "private", AdminForm.waiting_for_broadcast, F.from_user.id == ADMIN_ID)
async def send_broadcast(message: types.Message, state: FSMContext):
    users = await get_all_users_detailed()
    sent, fail = 0, 0
    await message.answer("⏳ Yuborilmoqda...")
    for u in users:
        if not u.is_banned:
            try:
                await message.copy_to(chat_id=u.telegram_id)
                sent += 1
                await asyncio.sleep(0.05)
            except:
                fail += 1
    await message.answer(f"✅ Yakunlandi! \n🟢 Yetib bordi: {sent}\n🔴 Xato: {fail}", reply_markup=admin_kb)
    await state.clear()

@dp.message(F.chat.type == "private", Command("start"))
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Assalomu alaykum! Xush kelibsiz. Eng avval '🏠 Mening uylarim' tugmasini bosib o'z xonadoningizni qo'shing.", reply_markup=main_kb)

@dp.message(F.chat.type == "private", F.text == "➕ Guruhga qo'shish")
async def add_bot_to_group(message: types.Message):
    bot_info = await bot.get_me()
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Guruhga qo'shish", url=f"https://t.me/{bot_info.username}?startgroup=true")]])
    await message.answer("Botni guruhga qo'shing:", reply_markup=ikb)

@dp.message(F.chat.type == "private", F.text == "🔗 Do'stlarga ulashish")
async def share_bot(message: types.Message):
    bot_info = await bot.get_me()
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_info.username}&text=Zo'r bot!"
    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↗️ Ulashish", url=share_url)]])
    await message.answer("Do'stlarga yuboring:", reply_markup=ikb)

async def main():
    await init_models()
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_monthly_reminders, trigger='cron', day=1, hour=9, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())