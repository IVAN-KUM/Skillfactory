import pandas as pd

INPUT_CSV = "test.csv"  # имя файла

# даты в формате ГГГГ-ДД-ММ
def parse_ydm(date_str):
    return pd.to_datetime(date_str, format="%Y-%d-%m", errors="coerce")

df = pd.read_csv(INPUT_CSV)

required = ["order_id", "user_id", "order_date", "quantity", "item_price"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"В файле нет колонок: {missing}")

# Приведём типы
df["order_date"] = df["order_date"].map(parse_ydm)
if df["order_date"].isna().all():
    raise ValueError("Не удалось распарсить даты в формате ГГГГ-ДД-ММ. Проверьте пример значения в order_date.")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["item_price"] = pd.to_numeric(df["item_price"], errors="coerce")

# Очистка некорректных строк
df = df.dropna(subset=["order_id", "user_id", "order_date", "quantity", "item_price"])
df = df[df["quantity"] >= 0]

# Если строка = одна позиция заказа: считаем стоимость позиции и затем агрегируем к заказу
df["line_total"] = df["quantity"] * df["item_price"]

# Агрегация по заказу
orders = df.groupby("order_id", as_index=False).agg(
    user_id=("user_id", "first"),
    order_date=("order_date", "first"),
    items_count=("quantity", "sum"),
    order_total=("line_total", "sum"),
    sku_lines=("quantity", "size")  # количество строк/позиций (если нужно)
)

# 1.Номер самого дорогого заказа
most_expensive_order_id = orders.loc[orders["order_total"].idxmax(), "order_id"]

# 2.Номер заказа с самым большим количеством товаров (по сумме quantity)
most_items_order_id = orders.loc[orders["items_count"].idxmax(), "order_id"]

# 3.День с самым большим количеством заказов
orders["order_day"] = orders["order_date"].dt.date
day_counts = orders.groupby("order_day")["order_id"].nunique()
top_day = day_counts.idxmax()
top_day_orders = int(day_counts.max())

# 4.Пользователь с самым большим количеством заказов
user_order_counts = orders.groupby("user_id")["order_id"].nunique()
top_user_by_orders = user_order_counts.idxmax()
top_user_orders = int(user_order_counts.max())

# 5.Пользователь с самой большой суммарной стоимостью заказов
user_revenue = orders.groupby("user_id")["order_total"].sum()
top_user_by_revenue = user_revenue.idxmax()
top_user_revenue = float(user_revenue.max())

# 6.Средняя стоимость заказа
avg_order_value = float(orders["order_total"].mean())

# 7.Средняя стоимость товаров (средняя цена одной единицы товара)
# total всех line_total / total всех quantity
total_revenue = float(df["line_total"].sum())
total_units = float(df["quantity"].sum())
avg_item_price_weighted = total_revenue / total_units if total_units else float("nan")

print("1) Самый дорогой заказ (order_id):", most_expensive_order_id)
print("2) Самый большой по количеству товаров (order_id):", most_items_order_id)
print("3) День с максимальным количеством заказов:", top_day, "| Кол-во заказов:", top_day_orders)
print("4) Пользователь с макс. кол-вом заказов:", top_user_by_orders, "| Кол-во заказов:", top_user_orders)
print("5) Пользователь с макс. суммой заказов:", top_user_by_revenue, "| Сумма:", round(top_user_revenue, 2))
print("6) Средняя стоимость заказа (AOV):", round(avg_order_value, 2))
print("7) Средняя стоимость товаров (ср. цена единицы):", round(avg_item_price_weighted, 4))