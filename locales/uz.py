# locales/uz.py
MESSAGES = {
    # Language selection
    "lang_select": "Tilni tanlang / Выберите язык:",
    "lang_changed": "Til o'zgartirildi: O'zbekcha 🇺🇿",

    # /start
    "start_welcome": "Assalomu alaykum! Xush kelibsiz. Eng avval '🏠 Mening uylarim' tugmasini bosib o'z xonadoningizni qo'shing.",

    # Ban messages
    "banned_message": "🚫 Siz qoidalarni buzganligingiz sababli botdan foydalanishdan chetlatilgansiz.",
    "banned_alert": "🚫 Siz bloklangansiz!",

    # Main menu buttons
    "btn_elektr": "💡 Elektr",
    "btn_gaz": "🔥 Gaz",
    "btn_my_houses": "🏠 Mening uylarim",
    "btn_my_stats": "📈 Mening sarfiyatim",
    "btn_clear_history": "❌ Tarixni tozalash",
    "btn_share": "🔗 Do'stlarga ulashish",
    "btn_add_group": "➕ Guruhga qo'shish",

    # Admin menu buttons
    "btn_statistics": "📊 Statistika",
    "btn_broadcast": "📢 Xabar yuborish",
    "btn_export_db": "📁 Baza yuklab olish",
    "btn_ban": "🚫 Bloklash",
    "btn_unban": "✅ Bandan yechish",
    "btn_back_main": "🔙 Asosiy menyuga",

    # Group message
    "group_redirect": "Hurmatli foydalanuvchi, jarayonni shaxsiy xabarda amalga oshiramiz 👇",
    "group_btn_private": "✉️ Shaxsiy xabarga o'tish",

    # House management
    "no_houses": "Sizda hali uylar qo'shilmagan. Bot hisob-kitobni to'g'ri olib borishi uchun avval xonadon qo'shing.",
    "houses_list_header": "Sizning uylaringiz ro'yxati:\n\n",
    "house_delete_btn": "🗑 {name} ni o'chirish",
    "house_add_btn": "➕ Yangi uy qo'shish",
    "house_limit_alert": "Siz eng ko'pi bilan 5 ta uy qo'sha olasiz!",
    "house_name_prompt": "Yangi xonadon uchun nom tanlang yoki o'zingiz xohlagan nomni matn qilib yozing:",
    "house_cancel_btn": "❌ Bekor qilish",
    "house_cancelled": "Jarayon bekor qilindi.",
    "house_added": "✅ **{name}** muvaffaqiyatli qo'shildi!",
    "house_add_error": "Xatolik yoki limit (5 ta) to'ldi.",
    "house_delete_confirm": "Ushbu uyni va unga tegishli barcha sarfiyat tarixini o'chirib tashlaysizmi?",
    "house_delete_yes": "⚠️ Ha, o'chirish (Barcha tarix o'chadi)",
    "house_delete_no": "❌ Bekor qilish",
    "house_deleted": "✅ Uy va uning tarixi to'liq o'chirildi.",
    "house_delete_error": "Xatolik.",

    # Suggested house names
    "house_name_main": "🏠 Asosiy uy",
    "house_name_yard": "🏡 Hovli",
    "house_name_apartment": "🏢 Kvartira",
    "house_name_dacha": "🏕 Dacha",

    # Utility selection
    "no_houses_for_utility": "Sizda xonadonlar yo'q. Iltimos, pastdagi menyudan '🏠 Mening uylarim' tugmasini bosib uy qo'shing.",
    "select_house_for_utility": "Qaysi manzil uchun **{utility}** ko'rsatkichini kiritmoqchisiz?",

    # Reading prompts
    "reading_prompt_existing": "🏠 Manzil: **{house_name}**\nBazada saqlangan oxirgi ko'rsatkich: **{last_value}**\n\n{icon} Iltimos, hisoblagichingizdagi joriy (bugungi) ko'rsatkichni kiriting:",
    "reading_prompt_new": "🏠 Manzil: **{house_name}**\nSizda eski ko'rsatkichlar topilmadi.\n{icon} Iltimos, joriy hisoblagich ko'rsatkichini kiriting (Bu kelajak hisob-kitoblar uchun tayanch bo'ladi):",
    "reading_invalid_number": "Iltimos, faqat raqam kiriting!",
    "reading_too_small": "Xatolik: Joriy ko'rsatkich o'tgan safargidan kichik bo'lishi mumkin emas. Qayta kiriting.",
    "reading_initial_saved": "✅ Boshlang'ich ko'rsatkich muvaffaqiyatli saqlandi! Keyingi safar tekshirganingizda to'liq hisob-kitobni ko'rasiz.",

    # Report - new month
    "report_new_month": (
        "📊 **{prev_month}-oy uchun YAKUNIY HISOBOT**\n"
        "🏠 Manzil: {house_name}\n"
        "🛠 Xizmat turi: {icon} {utility}{season_text}\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "🔄 Bir oylik jami sarf: {usage} kVt/m³\n"
        "💵 Oylik to'lov summasi: {cost} so'm\n"
        "📈 Kunlik o'rtacha sarf: {daily_avg} kVt/m³\n\n"
        "✅ *Ushbu ko'rsatkich yangi ({curr_month}-oy) uchun boshlang'ich (tayanch) nuqta sifatida qabul qilindi.*"
    ),

    # Report - same month
    "report_same_month": (
        "🧾 **Batafsil Hisobot**\n"
        "🏠 Manzil: {house_name}\n"
        "🛠 Xizmat: {icon} {utility}{season_text}\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "🔄 Jami sarf: {total_usage} kVt/m³\n"
        "💰 **Jami to'lov: {total_cost} so'm**\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
    ),
    "report_segment": (
        "⏱ **Oxirgi tekshiruvdan keyingi oraliq:**\n"
        "🔄 Oraliq sarf: {segment_usage} kVt/m³\n"
        "💵 **Oraliq uchun to'lov: {segment_cost} so'm**"
    ),

    # Undo
    "undo_btn": "↩️ Oxirgi ko'rsatkichni bekor qilish",
    "undo_success": "✅ Oxirgi xato kiritilgan ko'rsatkich bekor qilindi!",
    "undo_not_found": "O'chirish uchun ko'rsatkich topilmadi.",

    # Clear history
    "clear_no_houses": "Sizda xonadonlar topilmadi.",
    "clear_elektr_btn": "💡 {name} - Elektrni tozalash",
    "clear_gaz_btn": "🔥 {name} - Gazni tozalash",
    "clear_prompt": "Qaysi manzilning hisoblash tarixini butunlay tozalab tashlamoqchisiz?",
    "clear_confirm": "Barcha tarix o'chiriladi. Ishonchingiz komilmi?",
    "clear_yes": "⚠️ Ha, ishonchim komil",
    "clear_no": "❌ Bekor qilish",
    "clear_done": "✅ Barcha ({count} ta) yozuvlar tarix bo'yicha tozalandi.",

    # Stats / Chart
    "stats_no_houses": "Grafikni ko'rish uchun avval uy qo'shing va ko'rsatkich kiriting.",
    "stats_prompt": "📈 Qaysi manzil bo'yicha vizual oylik hisobotni ko'rmoqchisiz?",
    "stats_elektr_btn": "💡 {name} (Elektr)",
    "stats_gaz_btn": "🔥 {name} (Gaz)",
    "stats_loading": "Grafik tayyorlanmoqda, kuting... ⏳",
    "stats_not_enough": "⚠️ Grafik shakllantirish uchun kamida 2 oylik ko'rsatkichlar tarixi kerak.",
    "stats_caption": "📈 **{house_name} uchun {utility} sarfiyat grafigi!**",
    "chart_title": "[{house_name}] {utility} oylik sarfiyati",
    "chart_ylabel": "Sarfiyat miqdori (kVt / m³)",

    # Admin
    "admin_welcome": "👨‍💻 Admin panelga xush kelibsiz!",
    "admin_back_main": "Asosiy menyuga qaytdingiz.",
    "admin_stats": "👥 Jami ro'yxatdan o'tganlar: **{count} ta**",
    "admin_export_loading": "Excel tayyorlanmoqda...",
    "admin_export_headers": ["ID", "Telegram ID", "Ism", "Ro'yxatdan o'tgan sana", "Bloklanganmi?"],
    "admin_export_yes": "Ha",
    "admin_export_no": "Yo'q",
    "admin_export_unknown": "Noma'lum",
    "admin_broadcast_prompt": "Barcha bloklanmagan foydalanuvchilarga xabarni yozing: (/cancel)",
    "admin_cancelled": "Bekor qilindi.",
    "admin_broadcast_sending": "⏳ Yuborilmoqda...",
    "admin_broadcast_done": "✅ Yakunlandi! \n🟢 Yetib bordi: {sent}\n🔴 Xato: {fail}",

    # Share / Group
    "share_prompt": "Do'stlarga yuboring:",
    "share_btn": "↗️ Ulashish",
    "add_group_prompt": "Botni guruhga qo'shing:",
    "add_group_btn": "➕ Guruhga qo'shish",

    # Monthly reminder
    "monthly_reminder": "🔔 **Yangi oy boshlandi!**\n\nHisobotlarni ko'rish uchun ko'rsatkichlarni kiriting.",

    # PDF Report
    "btn_pdf_report": "📄 PDF hisobot",
    "pdf_title": "Oylik Kommunal Hisobot",
    "pdf_utility_elektr": "Elektr energiyasi",
    "pdf_utility_gaz": "Gaz",
    "pdf_col_house": "Manzil nomi",
    "pdf_col_utility": "Xizmat turi",
    "pdf_col_month": "Oy",
    "pdf_col_start_reading": "Boshlang'ich ko'rsatkich",
    "pdf_col_end_reading": "Yakuniy ko'rsatkich",
    "pdf_col_usage": "Sarf miqdori",
    "pdf_col_cost": "To'lov summasi",
    "pdf_col_date": "Sana",
    "pdf_footer": "Ushbu hisobot avtomatik tarzda yaratilgan.",
    "pdf_select_house": "Qaysi manzil uchun PDF hisobot olmoqchisiz?",
    "pdf_select_utility": "Qaysi xizmat turi bo'yicha hisobot kerak?",
    "pdf_no_data": "Ushbu oy uchun ma'lumotlar topilmadi. Avval ko'rsatkichlarni kiriting.",
    "pdf_generating": "PDF hisobot tayyorlanmoqda... ⏳",
    "pdf_caption": "📄 **{house_name}** uchun {utility} - {month_year} oylik hisobot",
    "pdf_house_btn": "🏠 {name}",
    "pdf_elektr_btn": "💡 Elektr",
    "pdf_gaz_btn": "🔥 Gaz",
    "pdf_month_current": "📅 Joriy oy",
    "pdf_month_previous": "📅 O'tgan oy",
    "pdf_select_month": "Qaysi oy uchun hisobot kerak?",
    "pdf_auto_report_caption": "📄 O'tgan oy uchun avtomatik PDF hisobot: **{house_name}** - {utility}",

    # SMS Parsing
    "sms_parsed_success": "📨 SMS muvaffaqiyatli tahlil qilindi!\n\n{details}",
    "sms_parse_failed": "❌ SMS dan ma'lumot ajratib olib bo'lmadi. Iltimos, ko'rsatkichni qo'lda kiriting.",
    "sms_select_house": "📨 SMS dan ko'rsatkich topildi.\n\nQaysi uy uchun saqlash kerak?",
    "sms_select_utility": "Qaysi xizmat turi uchun saqlash kerak?",
    "sms_saved_confirmation": (
        "✅ SMS ma'lumotlari saqlandi!\n\n"
        "🏠 Manzil: **{house_name}**\n"
        "🛠 Xizmat: {icon} {utility}\n"
        "📊 Ko'rsatkich: **{reading}**\n"
        "💰 Hisoblangan summa: **{cost} so'm**"
    ),
    "sms_reading_label": "Ko'rsatkich: {value}",
    "sms_usage_label": "Sarf: {value}",
    "sms_amount_label": "Summa: {value} so'm",
    "sms_no_reading": "⚠️ SMS da ko'rsatkich (reading) topilmadi. Faqat sarf yoki summa aniqlandi. Iltimos, ko'rsatkichni qo'lda kiriting.",
    "sms_elektr_btn": "💡 Elektr",
    "sms_gaz_btn": "🔥 Gaz",
}
