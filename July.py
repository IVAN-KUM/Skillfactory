import json
from datetime import datetime
from statistics import mean
from collections import Counter, defaultdict

def parse_date_ydm(date_str: str):
    # Формат ГГГГ-ДД-ММ
    return datetime.strptime(date_str, "%Y-%d-%m").date()

def order_totals(order):
    # Сумма заказа и число товарных единиц
    total_cost = 0.0
    total_qty = 0
    for it in order.get("items", []):
        price = float(it.get("price", 0))
        qty = int(it.get("quantity", 1))
        total_cost += price * qty
        total_qty += qty
    return total_cost, total_qty

def analyze_orders(orders):
    order_cost = {}          # сумма заказа
    order_qty = {}           # количество товарных единиц
    date_counts = Counter()  # число заказов
    user_order_count = Counter()   # число заказов
    user_order_sum = defaultdict(float)  # суммарная стоимость заказов

    all_item_prices = []     # для средней цены товара (по всем единицам)
    all_order_costs = []     # для средней стоимости заказа

    for od in orders:
        oid = od.get("order_id")
        uid = od.get("user_id")
        # Разбор даты с форматом YYYY-DD-MM
        d = parse_date_ydm(od.get("date"))

        total_cost, total_qty = order_totals(od)
        order_cost[oid] = total_cost
        order_qty[oid] = total_qty

        date_counts[d] += 1
        user_order_count[uid] += 1
        user_order_sum[uid] += total_cost
        all_order_costs.append(total_cost)

        # Для средней цены товара — собираем цену каждой единицы товара
        for it in od.get("items", []):
            price = float(it.get("price", 0))
            qty = int(it.get("quantity", 1))
            # Добавляем price столько раз, сколько единиц куплено
            all_item_prices.extend([price] * qty)

    # 1. Номер самого дорогого заказа
    most_expensive_order = max(order_cost, key=order_cost.get) if order_cost else None

    # 2. Номер заказа с самым большим количеством товаров (единиц)
    most_items_order = max(order_qty, key=order_qty.get) if order_qty else None

    # 3. День с самым большим количеством заказов
    busiest_day = max(date_counts, key=date_counts.get) if date_counts else None

    # 4. Пользователь с самым большим количеством заказов
    top_user_by_orders = max(user_order_count, key=user_order_count.get) if user_order_count else None

    # 5. Пользователь с самой большой суммарной стоимостью заказов
    top_user_by_revenue = max(user_order_sum, key=user_order_sum.get) if user_order_sum else None

    # 6. Средняя стоимость заказа
    avg_order_cost = mean(all_order_costs) if all_order_costs else 0.0

    # 7. Средняя стоимость товаров (это средняя цена одной товарной единицы, а не заказа)
    avg_item_price = mean(all_item_prices) if all_item_prices else 0.0

    return {
        "1. Номер самого дорогого заказа " : most_expensive_order,
        "2. Номер заказа с самым большим количеством товаров ": most_items_order,
        "3. День с самым большим количеством заказов ": busiest_day.isoformat() if busiest_day else None,
        "4. Пользователь с самым большим количеством заказов": top_user_by_orders,
        "5. Пользователь с самой большой суммарной стоимостью заказов": top_user_by_revenue,
        "6. Средняя стоимость заказа": avg_order_cost,
        "7. Средняя стоимость товаров": avg_item_price
    }
