import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_and_clean(rooms_file, readings_file):
    rooms = pd.read_csv(rooms_file)
    readings = pd.read_csv(readings_file)
    log = {"rows_before": len(readings)}

    readings = readings.drop_duplicates()
    log["duplicates_removed"] = log["rows_before"] - len(readings)

    log["missing_values_filled"] = int(readings["actual_kwh"].isna().sum())
    room_average = readings.groupby("room_id")["actual_kwh"].transform("mean")
    readings["actual_kwh"] = readings["actual_kwh"].fillna(room_average)

    readings["date"] = pd.to_datetime(readings["date"])
    readings["month"] = readings["date"].dt.strftime("%Y-%m")

    merged = pd.merge(readings, rooms, on="room_id", how="inner")
    log["rows_dropped_unknown_room"] = len(readings) - len(merged)
    log["rows_after"] = len(merged)
    return merged, log


def cost_tables(merged, price):
    data = merged.copy()
    data["cost"] = data["actual_kwh"] * price

    by_room = data.groupby(["room_id", "room_name"])[["actual_kwh", "cost"]].sum().reset_index()
    by_building = data.groupby("building")[["actual_kwh", "cost"]].sum().reset_index()
    by_month = data.groupby("month")[["actual_kwh", "cost"]].sum().reset_index()
    return by_room.round(2), by_building.round(2), by_month.round(2)


def room_statistics(merged):
    stats = merged.groupby("room_name")["actual_kwh"].agg(["mean", "std"]).reset_index()
    stats["cv_percent"] = stats["std"] / stats["mean"] * 100
    return stats.round(2)


def ac_reduction(rooms_file, percent):
    rooms = pd.read_csv(rooms_file)

    ac = rooms["ac_kw"].to_numpy()
    lighting = rooms["lighting_kw"].to_numpy()
    equipment = rooms["equipment_kw"].to_numpy()
    hours = rooms["hours_per_day"].to_numpy()

    before = (ac + lighting + equipment) * hours
    new_ac = ac * (1 - percent / 100)
    after = (new_ac + lighting + equipment) * hours

    result = pd.DataFrame({
        "room_id": rooms["room_id"],
        "room_name": rooms["room_name"],
        "before_kwh": before,
        "after_kwh": after,
        "saved_kwh": before - after,
    })
    return result.round(2)


def linear_fit(x, y):
    n = len(x)
    a1 = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x ** 2) - np.sum(x) ** 2)
    a0 = np.mean(y) - a1 * np.mean(x)
    st = np.sum((y - np.mean(y)) ** 2)
    sr = np.sum((y - a0 - a1 * x) ** 2)
    return a1, a0, 1 - sr / st


def make_charts(merged, price, folder):
    os.makedirs(folder, exist_ok=True)
    paths = []

    daily = merged.groupby("date")["actual_kwh"].sum()
    plt.figure(figsize=(9, 4))
    plt.plot(daily.index, daily.values, color="blue")
    plt.title("Total Daily Energy Consumption")
    plt.xlabel("Date")
    plt.ylabel("Energy (kWh/day)")
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    paths.append(os.path.join(folder, "1_line_daily_consumption.png"))
    plt.savefig(paths[-1], dpi=120, bbox_inches="tight")
    plt.close()

    by_room = merged.groupby("room_name")["actual_kwh"].sum() * price
    by_room = by_room.sort_values(ascending=False)
    plt.figure(figsize=(9, 4.5))
    plt.bar(by_room.index, by_room.values, color="orange")
    plt.title("Total Energy Cost per Room (price = " + str(price) + " per kWh)")
    plt.xlabel("Room")
    plt.ylabel("Cost (currency units)")
    plt.xticks(rotation=30, ha="right")
    paths.append(os.path.join(folder, "2_bar_cost_per_room.png"))
    plt.savefig(paths[-1], dpi=120, bbox_inches="tight")
    plt.close()

    per_room = merged.groupby("room_id").agg(area=("area_m2", "first"),
                                             average=("actual_kwh", "mean"))
    x = per_room["area"].to_numpy()
    y = per_room["average"].to_numpy()
    a1, a0, r2 = linear_fit(x, y)
    line_x = np.linspace(x.min(), x.max(), 50)
    plt.figure(figsize=(7, 5))
    plt.scatter(x, y, color="green", s=60, label="Rooms")
    plt.plot(line_x, a0 + a1 * line_x, color="red", linestyle="--",
             label="Fitted line (r2 = " + str(round(r2, 3)) + ")")
    plt.title("Room Area vs Average Daily Consumption")
    plt.xlabel("Room area (m2)")
    plt.ylabel("Average consumption (kWh/day)")
    plt.legend()
    plt.grid(True)
    paths.append(os.path.join(folder, "3_scatter_area_vs_consumption.png"))
    plt.savefig(paths[-1], dpi=120, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.hist(merged["actual_kwh"], bins=20, color="purple", edgecolor="black")
    plt.title("Distribution of Daily Room Consumption")
    plt.xlabel("Daily consumption (kWh)")
    plt.ylabel("Number of readings")
    paths.append(os.path.join(folder, "4_histogram_consumption.png"))
    plt.savefig(paths[-1], dpi=120, bbox_inches="tight")
    plt.close()

    return paths


def export_reports(merged, price, scenario, folder):
    os.makedirs(folder, exist_ok=True)
    by_room, by_building, by_month = cost_tables(merged, price)
    reports = {
        "cost_by_room.csv": by_room,
        "cost_by_building.csv": by_building,
        "cost_by_month.csv": by_month,
        "room_statistics.csv": room_statistics(merged),
        "ac_reduction_scenario.csv": scenario,
        "cleaned_readings.csv": merged,
    }
    paths = []
    for name, table in reports.items():
        path = os.path.join(folder, name)
        table.to_csv(path, index=False)
        paths.append(path)
    return paths
