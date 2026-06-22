import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import logging
from config import VK_TOKEN, ADMIN_ID
from tour_selector import TourSelector
from doc_consultant import DocConsultant
from user_state import UserStateManager, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

#  Глобальные объекты 
state_manager = UserStateManager()
tour_selector = TourSelector()
doc_consultant = DocConsultant()

# Список направлений для кнопок
DESTINATIONS = [
    ("🇹🇷", "Турция"),
    ("🇪🇬", "Египет"),
    ("🇹🇭", "Таиланд"),
    ("🇦🇪", "ОАЭ"),
    ("🇬🇷", "Греция"),
    ("🇨🇾", "Кипр"),
    ("🇲🇻", "Мальдивы"),
    ("🇪🇸", "Испания"),
]


#  Получение имени пользователя
def get_first_name(vk, user_id: int) -> str:
    """
    Возвращает имя из кэша в БД.
    Если нет — запрашивает VK API, сохраняет и возвращает.
    """
    cached = state_manager.get_user_name(user_id)
    if cached:
        return cached
    try:
        info = vk.users.get(user_ids=user_id, fields="first_name")
        name = info[0].get("first_name", "")
        if name:
            state_manager.upsert_user(user_id, name)
        return name
    except Exception as e:
        log.warning("Не удалось получить имя пользователя %s: %s", user_id, e)
        return ""


#  Клавиатуры 
def main_menu_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button("🏖 Подобрать тур", color=VkKeyboardColor.POSITIVE)
    kb.add_button("📄 Документы и визы", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("📞 Связаться с менеджером", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()


def back_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def destination_keyboard():
    """Кнопки выбора страны — 2 в ряду, последняя строка: кнопка «Назад»."""
    kb = VkKeyboard(one_time=True)
    for i, (emoji, name) in enumerate(DESTINATIONS):
        kb.add_button(f"{emoji} {name}", color=VkKeyboardColor.PRIMARY)
        # Перенос строки после каждой второй кнопки
        if i % 2 == 1 and i < len(DESTINATIONS) - 1:
            kb.add_line()
    kb.add_line()
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def days_keyboard():
    kb = VkKeyboard(one_time=True)
    for label in ["7 дней", "10 дней", "14 дней", "21 день"]:
        kb.add_button(label, color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def budget_keyboard():
    kb = VkKeyboard(one_time=True)
    for label in ["до 50 000 ₽", "50-100 000 ₽", "100-150 000 ₽", "от 150 000 ₽"]:
        kb.add_button(label, color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def stars_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button("⭐⭐⭐ 3 звезды", color=VkKeyboardColor.SECONDARY)
    kb.add_button("⭐⭐⭐⭐ 4 звезды", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("⭐⭐⭐⭐⭐ 5 звезд", color=VkKeyboardColor.POSITIVE)
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def yes_no_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button("✅ Да", color=VkKeyboardColor.POSITIVE)
    kb.add_button("❌ Нет", color=VkKeyboardColor.NEGATIVE)
    kb.add_line()
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()


def doc_menu_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button("🇹🇷 Виза в Турцию", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🇪🇬 Виза в Египет", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🇹🇭 Виза в Таиланд", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🇪🇺 Шенгенская виза", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🛂 Загранпаспорт", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🏥 Страховка", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("📋 Апостиль и переводы", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


#  Отправка сообщений 
def send(vk, user_id: int, text: str, keyboard=None, attachment: str = None):
    params = {
        "user_id": user_id,
        "message": text,
        "random_id": random.getrandbits(32),
    }
    if keyboard:
        params["keyboard"] = keyboard
    if attachment:
        params["attachment"] = attachment
    vk.messages.send(**params)


#  Обработка главного меню 
def handle_start(vk, user_id: int):
    state_manager.reset(user_id)
    name = get_first_name(vk, user_id)
    greeting = f"👋 Добро пожаловать, {name}!" if name else "👋 Добро пожаловать!"
    send(
        vk, user_id,
        f"{greeting} Я — бот нашего турагентства.\n\n"
        "Я помогу вам:\n"
        "🏖 Подобрать идеальный тур под ваши параметры\n"
        "📄 Ответить на вопросы по документам и визам\n\n"
        "Выберите, что вас интересует:",
        keyboard=main_menu_keyboard()
    )


#  Модуль 1: Подбор тура 
def start_tour_selection(vk, user_id: int):
    state_manager.set(user_id, {"mode": "tour", "step": "destination", "data": {}})
    name = get_first_name(vk, user_id)
    intro = f"🏖 Отлично, {name}! Подберём тур специально для вас." if name else "🏖 Отлично! Подберём тур специально для вас."
    send(
        vk, user_id,
        f"{intro}\n\n"
        "📍 Куда хотите поехать?\n"
        "Выберите направление:",
        keyboard=destination_keyboard()
    )


def handle_tour_step(vk, user_id: int, text: str, state: dict):
    step = state["step"]
    data = state["data"]

    if step == "destination":
        # Убираем emoji из текста кнопки, если есть
        dest = text.strip()
        for emoji, name in DESTINATIONS:
            if name.lower() in dest.lower():
                dest = name
                break
        data["destination"] = dest
        state["step"] = "days"
        state_manager.set(user_id, state)

        send(
            vk, user_id,
            f"✅ Направление: {dest}\n\n"
            "📅 На сколько дней планируете поездку?",
            keyboard=days_keyboard()
        )

    elif step == "days":
        days_text = text.split()[0].strip()
        data["days"] = days_text
        state["step"] = "budget"
        state_manager.set(user_id, state)

        send(
            vk, user_id,
            f"✅ Длительность: {days_text} дней\n\n"
            "💰 Какой бюджет рассматриваете?\n"
            "(сумма на человека, включая перелёт)",
            keyboard=budget_keyboard()
        )

    elif step == "budget":
        data["budget"] = text
        state["step"] = "stars"
        state_manager.set(user_id, state)

        send(
            vk, user_id,
            f"✅ Бюджет: {text}\n\n"
            "⭐ Какую категорию отеля предпочитаете?",
            keyboard=stars_keyboard()
        )

    elif step == "stars":
        if "3" in text:
            stars = "3*"
        elif "4" in text:
            stars = "4*"
        elif "5" in text:
            stars = "5*"
        else:
            stars = text
        data["stars"] = stars
        state["step"] = "children"
        state_manager.set(user_id, state)

        send(
            vk, user_id,
            f"✅ Категория отеля: {stars}\n\n"
            "👨‍👩‍👧 Поедете с детьми?",
            keyboard=yes_no_keyboard()
        )

    elif step == "children":
        data["children"] = "да" if "да" in text.lower() or "✅" in text else "нет"
        state["step"] = "done"
        state_manager.set(user_id, state)

        tours = tour_selector.find_tours(data)

        # Сохраняем поиск в историю
        state_manager.save_search(user_id, data, len(tours))

        name = get_first_name(vk, user_id)
        send_tours(vk, user_id, tours, data, name)
        state_manager.reset(user_id)


def send_tours(vk, user_id: int, tours: list, params: dict, name: str = ""):
    """Каждый тур — отдельное сообщение с фотографией."""
    dest     = params.get("destination", "")
    days     = params.get("days", "")
    budget   = params.get("budget", "")
    stars    = params.get("stars", "")
    children = params.get("children", "нет")

    name_part = f", {name}" if name else ""

    # Вводное сообщение
    send(vk, user_id,
        f"🎉 Отлично{name_part}! По вашим параметрам я подобрал туры:\n\n"
        f"📍 Направление: {dest}\n"
        f"📅 Дней: {days}\n"
        f"💰 Бюджет: {budget}\n"
        f"⭐ Отель: {stars}\n"
        f"👨‍👩‍👧 С детьми: {children}"
    )

    if not tours:
        send(vk, user_id,
            "😔 К сожалению, по вашим параметрам ничего не найдено.\n"
            "Попробуйте изменить бюджет или количество дней.",
            keyboard=main_menu_keyboard()
        )
        return

    for i, t in enumerate(tours, 1):
        text = (
            f"🏨 Вариант {i}: {t['name']}\n"
            f"   📍 {t['location']}\n"
            f"   ⭐ {t['stars']}★ | 🍽 {t['meal']}\n"
            f"   💰 от {t['price']:,} ₽/чел.\n"
            f"   🔗 {t['link']}"
        )
        photo_id = t.get("photo_id")
        send(vk, user_id, text, attachment=photo_id)

    cta = (
        f"💬 Нравится какой-то вариант, {name}? 😊\n"
        if name else
        "💬 Хотите забронировать или узнать подробности?\n"
    )
    send(vk, user_id,
        cta + "Нажмите «Связаться с менеджером» — свяжемся в течение 15 минут!",
        keyboard=main_menu_keyboard()
    )


#  Модуль 2: Консультант по документам 
def start_doc_consultant(vk, user_id: int):
    state_manager.set(user_id, {"mode": "docs"})
    name = get_first_name(vk, user_id)
    intro = f"📄 {name}, раздел «Документы и визы»." if name else "📄 Раздел «Документы и визы»."
    send(
        vk, user_id,
        f"{intro}\n\n"
        "Выберите интересующую тему — отвечу на самые частые вопросы:",
        keyboard=doc_menu_keyboard()
    )


def handle_doc_topic(vk, user_id: int, text: str):
    answer = doc_consultant.get_answer(text)
    send(vk, user_id, answer, keyboard=doc_menu_keyboard())


#  Главный роутер сообщений 
def route_message(vk, user_id: int, text: str):
    text_lower = text.lower().strip()

    if any(w in text_lower for w in ["начать", "старт", "start", "привет", "меню", "главное меню", "🔙"]):
        handle_start(vk, user_id)
        return

    if "менеджер" in text_lower or "связаться" in text_lower:
        name = get_first_name(vk, user_id)
        name_part = f", {name}" if name else ""
        send(
            vk, user_id,
            f"📞 Отличный выбор{name_part}!\n\n"
            "Наш менеджер свяжется с вами в течение 15 минут.\n"
            "Также вы можете позвонить: +7 (XXX) XXX-XX-XX\n"
            "или написать в WhatsApp/Telegram по тому же номеру.\n\n"
            "🕐 Режим работы: Пн–Пт 9:00–20:00, Сб–Вс 10:00–18:00",
            keyboard=main_menu_keyboard()
        )
        return

    state = state_manager.get(user_id)

    if state and state.get("mode") == "tour" and state.get("step") != "done":
        handle_tour_step(vk, user_id, text, state)
        return

    if state and state.get("mode") == "docs":
        handle_doc_topic(vk, user_id, text)
        return

    if "тур" in text_lower or "подобрать" in text_lower or "🏖" in text:
        start_tour_selection(vk, user_id)
        return

    if "документ" in text_lower or "виза" in text_lower or "📄" in text:
        start_doc_consultant(vk, user_id)
        return

    handle_start(vk, user_id)


#  Точка входа 
def main():
    log.info("Запуск VK турагентство бота...")

    # Инициализируем БД 
    init_db()

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    log.info("Бот успешно запущен и слушает события.")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text.strip() if event.text else ""
            log.info("Сообщение от %s: %r", user_id, text)
            try:
                route_message(vk, user_id, text)
            except Exception as e:
                log.error("Ошибка при обработке сообщения от %s: %s", user_id, e, exc_info=True)
                send(vk, user_id, "⚠️ Произошла ошибка. Попробуйте ещё раз или напишите «Меню».")


if __name__ == "__main__":
    main()
