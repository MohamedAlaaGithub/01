import os
import module1_rooms as m1
import module2_analysis as m2

BASE = os.path.dirname(os.path.abspath(__file__))
ROOMS_FILE = os.path.join(BASE, "data", "rooms.csv")
READINGS_FILE = os.path.join(BASE, "data", "readings.csv")
REPORTS_DIR = os.path.join(BASE, "outputs", "reports")
CHARTS_DIR = os.path.join(BASE, "outputs", "charts")

MENU = """
========== Building Energy Analyzer ==========
 Module 1 - Rooms
  1) Add a room
  2) List rooms
  3) Search rooms
  4) Update a room
  5) Energy summary
 Module 2 - Analysis
  6) Clean and merge the readings
  7) Consumption and cost report
  8) Air-conditioning reduction scenario
  9) Create the 4 charts
 10) Export all reports (CSV)
  0) Exit
=============================================="""


def ask_number(text, minimum, maximum):
    while True:
        answer = input(text)
        try:
            number = float(answer)
        except ValueError:
            print("  Please type a number.")
            continue
        if number < minimum or number > maximum:
            print("  The number must be between", minimum, "and", maximum)
        else:
            return number


def ask_price():
    while True:
        price = ask_number("Price per kWh (more than 0): ", 0, 1000000)
        if price > 0:
            return price
        print("  The price must be greater than zero.")


def add_room_action(rooms):
    room_id = input("Room ID (example R09): ")
    name = input("Room name: ")
    building = input("Building: ")
    area = input("Area (m2): ")
    lighting = input("Lighting power (kW): ")
    ac = input("Air-conditioning power (kW): ")
    equipment = input("Equipment power (kW): ")
    hours = input("Operating hours per day (0-24): ")
    try:
        room = m1.Room(room_id, name, building, area, lighting, ac, equipment, hours)
        m1.add_room(rooms, room)
        m1.save_rooms(rooms, ROOMS_FILE)
        print("  Room added and saved.")
    except ValueError as error:
        print("  Not added:", error)


def search_action(rooms):
    text = input("Search text (ID, name or building): ")
    found = m1.search_rooms(rooms, text)
    if len(found) == 0:
        print("  Nothing found.")
    for room in found:
        print("  ", room.room_id, "|", room.room_name, "|", room.building,
              "|", round(room.daily_energy(), 1), "kWh/day")


def update_action(rooms):
    room_id = input("Room ID to update: ").strip().upper()
    print("Fields:", ", ".join(m1.FIELDS[1:]))
    field = input("Field to change: ").strip()
    new_value = input("New value: ")
    try:
        m1.update_room(rooms, room_id, field, new_value)
        m1.save_rooms(rooms, ROOMS_FILE)
        print("  Room updated and saved.")
    except ValueError as error:
        print("  Not updated:", error)


def summary_action(rooms):
    m1.list_rooms(rooms)
    print("\nTotal daily consumption:", round(m1.total_consumption(rooms), 1), "kWh/day")
    print("Buildings:", sorted(m1.buildings(rooms)))
    print("Top 3 rooms:")
    for room in m1.top_rooms(rooms, 3):
        print("  ", room.room_name, "-", round(room.daily_energy(), 1), "kWh/day")


def clean_action(data):
    data["merged"], log = m2.load_and_clean(ROOMS_FILE, READINGS_FILE)
    print("Cleaning log:")
    for step, count in log.items():
        print("  ", step, "=", count)


def need_merged(data):
    if "merged" not in data:
        clean_action(data)


def need_price(data):
    if "price" not in data:
        data["price"] = ask_price()


def need_scenario(data):
    if "scenario" not in data:
        percent = ask_number("Reduce AC power by (0-100 %): ", 0, 100)
        data["scenario"] = m2.ac_reduction(ROOMS_FILE, percent)
        data["percent"] = percent


def cost_action(data):
    need_merged(data)
    data["price"] = ask_price()
    by_room, by_building, by_month = m2.cost_tables(data["merged"], data["price"])
    print("\n--- Cost per room ---\n", by_room.to_string(index=False))
    print("\n--- Cost per building ---\n", by_building.to_string(index=False))
    print("\n--- Cost per month ---\n", by_month.to_string(index=False))


def scenario_action(data):
    data.pop("scenario", None)
    need_scenario(data)
    table = data["scenario"]
    print(table.to_string(index=False))
    before = table["before_kwh"].sum()
    saved = table["saved_kwh"].sum()
    print("\nTotal before:", round(before, 1), "kWh/day")
    print("Total saved :", round(saved, 1), "kWh/day (", round(saved / before * 100, 1), "%)")


def charts_action(data):
    need_merged(data)
    need_price(data)
    for path in m2.make_charts(data["merged"], data["price"], CHARTS_DIR):
        print("  Saved", path)


def export_action(rooms, data):
    need_merged(data)
    need_price(data)
    need_scenario(data)
    m1.save_energy_report(rooms, os.path.join(REPORTS_DIR, "rooms_energy_report.csv"))
    for path in m2.export_reports(data["merged"], data["price"], data["scenario"], REPORTS_DIR):
        print("  Saved", path)


def main():
    rooms = m1.load_rooms(ROOMS_FILE)
    data = {}
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                add_room_action(rooms)
                data.clear()
            elif choice == "2":
                m1.list_rooms(rooms)
            elif choice == "3":
                search_action(rooms)
            elif choice == "4":
                update_action(rooms)
                data.clear()
            elif choice == "5":
                summary_action(rooms)
            elif choice == "6":
                clean_action(data)
            elif choice == "7":
                cost_action(data)
            elif choice == "8":
                scenario_action(data)
            elif choice == "9":
                charts_action(data)
            elif choice == "10":
                export_action(rooms, data)
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Please choose a number from the menu.")
        except FileNotFoundError as error:
            print("File not found:", error)


if __name__ == "__main__":
    main()
