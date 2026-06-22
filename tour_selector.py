import re

#  База туров 


TOURS_DB = [
    #  Турция 
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Rixos Premium Belek 5*",
        "location": "Белек, Турция",
        "stars": 5,
        "meal": "Ultra All Inclusive",
        "price_per_day": 12000,
        "children_friendly": True,
        "link": "https://example.com/rixos-belek",
        "photo_id": "photo-238836675_457239018",   # замените на реальный ID фото из группы
    },
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Maxx Royal Kemer Resort 5*",
        "location": "Кемер, Турция",
        "stars": 5,
        "meal": "All Inclusive",
        "price_per_day": 10500,
        "children_friendly": False,
        "link": "https://example.com/maxx-royal-kemer",
        "photo_id": "photo-238836675_457239020",
    },
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Delphin Imperial Hotel 5*",
        "location": "Лара, Анталья",
        "stars": 5,
        "meal": "Ultra All Inclusive",
        "price_per_day": 9800,
        "children_friendly": True,
        "link": "https://example.com/delphin-imperial",
        "photo_id": "photo-238836675_457239020",
    },
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Sunis Evren Beach Resort 4*",
        "location": "Сиде, Турция",
        "stars": 4,
        "meal": "All Inclusive",
        "price_per_day": 6500,
        "children_friendly": True,
        "link": "https://example.com/sunis-evren",
        "photo_id": "photo-238836675_457239020",
    },
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Titan Garden Hotel 4*",
        "location": "Алания, Турция",
        "stars": 4,
        "meal": "All Inclusive",
        "price_per_day": 5800,
        "children_friendly": True,
        "link": "https://example.com/titan-garden",
        "photo_id": "photo-1_457239694",
    },
    {
        "destinations": ["турция", "turkey", "анталья", "кемер", "сиде", "белек", "алания"],
        "name": "Limak Atlantis De Luxe 5*",
        "location": "Белек, Турция",
        "stars": 5,
        "meal": "Ultra All Inclusive",
        "price_per_day": 11000,
        "children_friendly": True,
        "link": "https://example.com/limak-atlantis",
        "photo_id": "photo-238836675_457239020",
    },
    #  Египет 
    {
        "destinations": ["египет", "egypt", "шарм", "хургада", "шарм-эль-шейх"],
        "name": "Jaz Aquamarine Resort 5*",
        "location": "Хургада, Египет",
        "stars": 5,
        "meal": "All Inclusive",
        "price_per_day": 8500,
        "children_friendly": True,
        "link": "https://example.com/jaz-aquamarine",
        "photo_id": "photo-238836675_457239025",
    },
    {
        "destinations": ["египет", "egypt", "шарм", "хургада", "шарм-эль-шейх"],
        "name": "Rixos Sharm El Sheikh 5*",
        "location": "Шарм-эль-Шейх, Египет",
        "stars": 5,
        "meal": "Ultra All Inclusive",
        "price_per_day": 10200,
        "children_friendly": True,
        "link": "https://example.com/rixos-sharm",
        "photo_id": "photo-238836675_457239024",
    },
    {
        "destinations": ["египет", "egypt", "шарм", "хургада", "шарм-эль-шейх"],
        "name": "Sunrise Arabian Beach Resort 4*",
        "location": "Шарм-эль-Шейх, Египет",
        "stars": 4,
        "meal": "All Inclusive",
        "price_per_day": 6200,
        "children_friendly": True,
        "link": "https://example.com/sunrise-arabian",
        "photo_id": "photo-238836675_457239019",
    },
    #  Таиланд 
    {
        "destinations": ["таиланд", "thailand", "пхукет", "паттайя", "самуи", "краби"],
        "name": "Kata Rocks Luxury Resort 5*",
        "location": "Пхукет, Таиланд",
        "stars": 5,
        "meal": "BB (завтрак)",
        "price_per_day": 14000,
        "children_friendly": False,
        "link": "https://example.com/kata-rocks",
        "photo_id": "photo-238836675_457239017",
    },
    {
        "destinations": ["таиланд", "thailand", "пхукет", "паттайя", "самуи", "краби"],
        "name": "Centara Grand Beach Phuket 5*",
        "location": "Пхукет, Таиланд",
        "stars": 5,
        "meal": "HB (полупансион)",
        "price_per_day": 11000,
        "children_friendly": True,
        "link": "https://example.com/centara-grand",
        "photo_id": "photo-238836675_457239017",
    },
    {
        "destinations": ["таиланд", "thailand", "пхукет", "паттайя", "самуи", "краби"],
        "name": "Holiday Inn Resort Krabi 4*",
        "location": "Краби, Таиланд",
        "stars": 4,
        "meal": "BB (завтрак)",
        "price_per_day": 7500,
        "children_friendly": True,
        "link": "https://example.com/holiday-inn-krabi",
        "photo_id": "photo-238836675_457239017",
    },
    #  ОАЭ 
    {
        "destinations": ["оаэ", "дубай", "абу-даби", "uae", "dubai"],
        "name": "Atlantis The Palm 5*",
        "location": "Дубай, ОАЭ",
        "stars": 5,
        "meal": "BB (завтрак)",
        "price_per_day": 18000,
        "children_friendly": True,
        "link": "https://example.com/atlantis-palm",
        "photo_id": "photo-238836675_457239020",
    },
    {
        "destinations": ["оаэ", "дубай", "абу-даби", "uae", "dubai"],
        "name": "Jumeirah Beach Hotel 5*",
        "location": "Дубай, ОАЭ",
        "stars": 5,
        "meal": "HB (полупансион)",
        "price_per_day": 15000,
        "children_friendly": True,
        "link": "https://example.com/jumeirah-beach",
        "photo_id": "photo-238836675_457239020",
    },
    #  Греция 
    {
        "destinations": ["греция", "greece", "крит", "родос", "санторини", "миконос", "корфу"],
        "name": "Caramel Grecotel Boutique 5*",
        "location": "Крит, Греция",
        "stars": 5,
        "meal": "BB (завтрак)",
        "price_per_day": 13000,
        "children_friendly": False,
        "link": "https://example.com/caramel-grecotel",
        "photo_id": "photo-238836675_457239023",
    },
    {
        "destinations": ["греция", "greece", "крит", "родос", "санторини", "миконос", "корфу"],
        "name": "Rodos Palace 4*",
        "location": "Родос, Греция",
        "stars": 4,
        "meal": "All Inclusive",
        "price_per_day": 8000,
        "children_friendly": True,
        "link": "https://example.com/rodos-palace",
        "photo_id": "photo-238836675_457239023",
    },
    #  Кипр 
    {
        "destinations": ["кипр", "cyprus", "айя-напа", "лимасол", "пафос"],
        "name": "Elysium Hotel 5*",
        "location": "Пафос, Кипр",
        "stars": 5,
        "meal": "BB (завтрак)",
        "price_per_day": 11500,
        "children_friendly": False,
        "link": "https://example.com/elysium-cyprus",
        "photo_id": "photo-238836675_457239021",
    },
    #  Мальдивы 
    {
        "destinations": ["мальдивы", "maldives"],
        "name": "One&Only Reethi Rah 5*",
        "location": "Северный Мале Атолл, Мальдивы",
        "stars": 5,
        "meal": "FB (полный пансион)",
        "price_per_day": 35000,
        "children_friendly": False,
        "link": "https://example.com/oneanonly-maldives",
        "photo_id": "photo-238836675_457239022",
    },
    {
        "destinations": ["мальдивы", "maldives"],
        "name": "Sun Island Resort & Spa 4*",
        "location": "Атолл Ари, Мальдивы",
        "stars": 4,
        "meal": "All Inclusive",
        "price_per_day": 22000,
        "children_friendly": True,
        "link": "https://example.com/sun-island-maldives",
        "photo_id": "photo-238836675_457239022",
    },
]


def _parse_budget(budget_str: str) -> tuple[int, int]:
    """Возвращает (min, max) бюджет в рублях."""
    budget_str = budget_str.lower().replace(" ", "").replace("\u202f", "")
    numbers = re.findall(r"\d+", budget_str)
    nums = [int(n) * 1000 if int(n) < 1000 else int(n) for n in numbers]

    if not nums:
        return 0, 999_999_999
    if "до" in budget_str or len(nums) == 1 and "от" not in budget_str:
        return 0, nums[0]
    if "от" in budget_str and len(nums) == 1:
        return nums[0], 999_999_999
    if len(nums) >= 2:
        return min(nums), max(nums)
    return 0, 999_999_999


def _parse_stars(stars_str: str) -> int | None:
    m = re.search(r"(\d)", stars_str)
    return int(m.group(1)) if m else None


class TourSelector:
    def find_tours(self, params: dict, limit: int = 5) -> list[dict]:
        destination = params.get("destination", "").lower()
        days = int(re.search(r"\d+", params.get("days", "7")).group())
        budget_min, budget_max = _parse_budget(params.get("budget", ""))
        stars_want = _parse_stars(params.get("stars", ""))
        children = params.get("children", "нет") == "да"

        results = []

        for tour in TOURS_DB:
            # Фильтр по направлению
            dest_match = any(kw in destination for kw in tour["destinations"])
            if not dest_match:
                dest_match = True  

            # Фильтр по звёздности
            if stars_want and tour["stars"] != stars_want:
                continue

            # Фильтр по детям
            if children and not tour["children_friendly"]:
                continue

            # Расчёт цены за поездку
            total_price = tour["price_per_day"] * days

            # Фильтр по бюджету
            if not (budget_min <= total_price <= budget_max):
                continue

            results.append({**tour, "price": total_price, "days": days})

        # Сортируем по цене
        results.sort(key=lambda t: t["price"])

        # Если ничего не нашли — возвращаем ближайшие варианты без фильтра по бюджету
        if not results:
            fallback = []
            for tour in TOURS_DB:
                dest_match = any(kw in destination for kw in tour["destinations"])
                if not dest_match:
                    continue
                if children and not tour["children_friendly"]:
                    continue
                total_price = tour["price_per_day"] * days
                fallback.append({**tour, "price": total_price, "days": days})
            fallback.sort(key=lambda t: t["price"])
            return fallback[:limit]

        return results[:limit]
