# locales/ru.py
MESSAGES = {
    # Language selection
    "lang_select": "Tilni tanlang / Выберите язык:",
    "lang_changed": "Язык изменен: Русский 🇷🇺",

    # /start
    "start_welcome": "Здравствуйте! Добро пожаловать. Сначала нажмите кнопку '🏠 Мои дома' и добавьте свое жилье.",

    # Ban messages
    "banned_message": "🚫 Вы заблокированы за нарушение правил.",
    "banned_alert": "🚫 Вы заблокированы!",

    # Main menu buttons
    "btn_elektr": "💡 Электричество",
    "btn_gaz": "🔥 Газ",
    "btn_my_houses": "🏠 Мои дома",
    "btn_my_stats": "📈 Моя статистика",
    "btn_clear_history": "❌ Очистить историю",
    "btn_share": "🔗 Поделиться",
    "btn_add_group": "➕ Добавить в группу",

    # Admin menu buttons
    "btn_statistics": "📊 Статистика",
    "btn_broadcast": "📢 Рассылка",
    "btn_export_db": "📁 Выгрузить базу",
    "btn_ban": "🚫 Заблокировать",
    "btn_unban": "✅ Разблокировать",
    "btn_back_main": "🔙 Главное меню",

    # Group message
    "group_redirect": "Уважаемый пользователь, продолжим в личном сообщении 👇",
    "group_btn_private": "✉️ Перейти в личные сообщения",

    # House management
    "no_houses": "У вас пока нет добавленных домов. Для корректной работы бота сначала добавьте жилье.",
    "houses_list_header": "Список ваших домов:\n\n",
    "house_delete_btn": "🗑 Удалить {name}",
    "house_add_btn": "➕ Добавить новый дом",
    "house_limit_alert": "Вы можете добавить максимум 5 домов!",
    "house_name_prompt": "Выберите название для нового жилья или напишите свое:",
    "house_cancel_btn": "❌ Отмена",
    "house_cancelled": "Действие отменено.",
    "house_added": "✅ **{name}** успешно добавлен!",
    "house_add_error": "Ошибка или достигнут лимит (5).",
    "house_delete_confirm": "Удалить этот дом и всю историю расходов?",
    "house_delete_yes": "⚠️ Да, удалить (Вся история будет удалена)",
    "house_delete_no": "❌ Отмена",
    "house_deleted": "✅ Дом и его история полностью удалены.",
    "house_delete_error": "Ошибка.",

    # Suggested house names
    "house_name_main": "🏠 Основной дом",
    "house_name_yard": "🏡 Двор",
    "house_name_apartment": "🏢 Квартира",
    "house_name_dacha": "🏕 Дача",

    # Utility selection
    "no_houses_for_utility": "У вас нет жилья. Пожалуйста, нажмите '🏠 Мои дома' и добавьте дом.",
    "select_house_for_utility": "Для какого адреса вы хотите ввести показания **{utility}**?",

    # Reading prompts
    "reading_prompt_existing": "🏠 Адрес: **{house_name}**\nПоследнее сохраненное показание: **{last_value}**\n\n{icon} Пожалуйста, введите текущее (сегодняшнее) показание счетчика:",
    "reading_prompt_new": "🏠 Адрес: **{house_name}**\nПредыдущие показания не найдены.\n{icon} Пожалуйста, введите текущее показание счетчика (оно станет базовым для будущих расчетов):",
    "reading_invalid_number": "Пожалуйста, введите только число!",
    "reading_too_small": "Ошибка: Текущее показание не может быть меньше предыдущего. Введите заново.",
    "reading_initial_saved": "✅ Начальное показание успешно сохранено! При следующей проверке вы увидите полный расчет.",

    # Report - new month
    "report_new_month": (
        "📊 **ИТОГОВЫЙ ОТЧЕТ за {prev_month}-й месяц**\n"
        "🏠 Адрес: {house_name}\n"
        "🛠 Тип услуги: {icon} {utility}{season_text}\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "🔄 Общий расход за месяц: {usage} кВт/м³\n"
        "💵 Сумма оплаты за месяц: {cost} сум\n"
        "📈 Среднесуточный расход: {daily_avg} кВт/м³\n\n"
        "✅ *Это показание принято как начальная (базовая) точка для нового ({curr_month}-го) месяца.*"
    ),

    # Report - same month
    "report_same_month": (
        "🧾 **Подробный отчет**\n"
        "🏠 Адрес: {house_name}\n"
        "🛠 Услуга: {icon} {utility}{season_text}\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "🔄 Общий расход: {total_usage} кВт/м³\n"
        "💰 **Итого к оплате: {total_cost} сум**\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
    ),
    "report_segment": (
        "⏱ **Период после последней проверки:**\n"
        "🔄 Расход за период: {segment_usage} кВт/м³\n"
        "💵 **Оплата за период: {segment_cost} сум**"
    ),

    # Undo
    "undo_btn": "↩️ Отменить последнее показание",
    "undo_success": "✅ Последнее ошибочное показание отменено!",
    "undo_not_found": "Показание для удаления не найдено.",

    # Clear history
    "clear_no_houses": "У вас нет домов.",
    "clear_elektr_btn": "💡 {name} - Очистить электричество",
    "clear_gaz_btn": "🔥 {name} - Очистить газ",
    "clear_prompt": "Историю какого адреса вы хотите полностью очистить?",
    "clear_confirm": "Вся история будет удалена. Вы уверены?",
    "clear_yes": "⚠️ Да, я уверен",
    "clear_no": "❌ Отмена",
    "clear_done": "✅ Все ({count}) записей успешно удалены.",

    # Stats / Chart
    "stats_no_houses": "Для графика сначала добавьте дом и введите показания.",
    "stats_prompt": "📈 По какому адресу вы хотите увидеть визуальный отчет?",
    "stats_elektr_btn": "💡 {name} (Электр.)",
    "stats_gaz_btn": "🔥 {name} (Газ)",
    "stats_loading": "График готовится, подождите... ⏳",
    "stats_not_enough": "⚠️ Для построения графика нужна история показаний минимум за 2 месяца.",
    "stats_caption": "📈 **График расхода {utility} для {house_name}!**",
    "chart_title": "[{house_name}] Ежемесячный расход {utility}",
    "chart_ylabel": "Объем расхода (кВт / м³)",

    # Admin
    "admin_welcome": "👨‍💻 Добро пожаловать в панель администратора!",
    "admin_back_main": "Вы вернулись в главное меню.",
    "admin_stats": "👥 Всего зарегистрировано: **{count}**",
    "admin_export_loading": "Подготовка Excel...",
    "admin_export_headers": ["ID", "Telegram ID", "Имя", "Дата регистрации", "Заблокирован?"],
    "admin_export_yes": "Да",
    "admin_export_no": "Нет",
    "admin_export_unknown": "Неизвестно",
    "admin_broadcast_prompt": "Напишите сообщение для всех незаблокированных пользователей: (/cancel)",
    "admin_cancelled": "Отменено.",
    "admin_broadcast_sending": "⏳ Отправка...",
    "admin_broadcast_done": "✅ Завершено! \n🟢 Доставлено: {sent}\n🔴 Ошибки: {fail}",

    # Share / Group
    "share_prompt": "Отправьте друзьям:",
    "share_btn": "↗️ Поделиться",
    "add_group_prompt": "Добавьте бота в группу:",
    "add_group_btn": "➕ Добавить в группу",

    # Monthly reminder
    "monthly_reminder": "🔔 **Начался новый месяц!**\n\nВведите показания для просмотра отчетов.",

    # PDF Report
    "btn_pdf_report": "📄 PDF отчет",
    "pdf_title": "Ежемесячный коммунальный отчет",
    "pdf_utility_elektr": "Электроэнергия",
    "pdf_utility_gaz": "Газ",
    "pdf_col_house": "Название жилья",
    "pdf_col_utility": "Тип услуги",
    "pdf_col_month": "Месяц",
    "pdf_col_start_reading": "Начальное показание",
    "pdf_col_end_reading": "Конечное показание",
    "pdf_col_usage": "Объем потребления",
    "pdf_col_cost": "Сумма оплаты",
    "pdf_col_date": "Дата",
    "pdf_footer": "Этот отчет сгенерирован автоматически.",
    "pdf_select_house": "Для какого адреса вы хотите получить PDF отчет?",
    "pdf_select_utility": "По какому типу услуги нужен отчет?",
    "pdf_no_data": "Данные за этот месяц не найдены. Сначала введите показания.",
    "pdf_generating": "PDF отчет готовится... ⏳",
    "pdf_caption": "📄 **{house_name}** - {utility} - отчет за {month_year}",
    "pdf_house_btn": "🏠 {name}",
    "pdf_elektr_btn": "💡 Электричество",
    "pdf_gaz_btn": "🔥 Газ",
    "pdf_month_current": "📅 Текущий месяц",
    "pdf_month_previous": "📅 Предыдущий месяц",
    "pdf_select_month": "За какой месяц нужен отчет?",
    "pdf_auto_report_caption": "📄 Автоматический PDF отчет за прошлый месяц: **{house_name}** - {utility}",

    # SMS Parsing
    "sms_parsed_success": "📨 SMS успешно проанализировано!\n\n{details}",
    "sms_parse_failed": "❌ Не удалось извлечь данные из SMS. Пожалуйста, введите показания вручную.",
    "sms_select_house": "📨 Из SMS извлечены показания.\n\nДля какого дома сохранить?",
    "sms_select_utility": "Для какого типа услуги сохранить?",
    "sms_saved_confirmation": (
        "✅ Данные из SMS сохранены!\n\n"
        "🏠 Адрес: **{house_name}**\n"
        "🛠 Услуга: {icon} {utility}\n"
        "📊 Показание: **{reading}**\n"
        "💰 Рассчитанная сумма: **{cost} сум**"
    ),
    "sms_reading_label": "Показание: {value}",
    "sms_usage_label": "Расход: {value}",
    "sms_amount_label": "Сумма: {value} сум",
    "sms_no_reading": "⚠️ В SMS не найдено показание счетчика. Обнаружен только расход или сумма. Пожалуйста, введите показание вручную.",
    "sms_elektr_btn": "💡 Электричество",
    "sms_gaz_btn": "🔥 Газ",
}
