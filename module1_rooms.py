import csv


FIELDS = ("room_id", "room_name", "building", "area_m2",
          "lighting_kw", "ac_kw", "equipment_kw", "hours_per_day")


class Room:
    def __init__(self, room_id, room_name, building, area_m2,
                 lighting_kw, ac_kw, equipment_kw, hours_per_day):

        area_m2 = float(area_m2)
        lighting_kw = float(lighting_kw)
        ac_kw = float(ac_kw)
        equipment_kw = float(equipment_kw)
        hours_per_day = float(hours_per_day)

        if str(room_id).strip() == "" or str(room_name).strip() == "":
            raise ValueError("Room ID and room name must not be empty")
        if area_m2 <= 0:
            raise ValueError("Room area must be greater than zero")
        if lighting_kw < 0 or ac_kw < 0 or equipment_kw < 0:
            raise ValueError("Power values must not be negative")
        if hours_per_day < 0 or hours_per_day > 24:
            raise ValueError("Operating hours must be between 0 and 24")

        self.room_id = str(room_id).strip().upper()
        self.room_name = str(room_name).strip()
        self.building = str(building).strip()
        self.area_m2 = area_m2
        self.lighting_kw = lighting_kw
        self.ac_kw = ac_kw
        self.equipment_kw = equipment_kw
        self.hours_per_day = hours_per_day

    def total_power(self):
        return self.lighting_kw + self.ac_kw + self.equipment_kw

    def daily_energy(self):
        return self.total_power() * self.hours_per_day

    def energy_per_m2(self):
        return self.daily_energy() / self.area_m2

    def to_dict(self):
        return {field: getattr(self, field) for field in FIELDS}


def add_room(rooms, room):
    if room.room_id in rooms:
        raise ValueError("Room ID " + room.room_id + " already exists")
    rooms[room.room_id] = room


def list_rooms(rooms):
    if len(rooms) == 0:
        print("No rooms yet.")
        return
    print(f"{'ID':<5}{'Room':<16}{'Building':<16}{'Area':>6}{'kW':>7}{'Hours':>7}{'kWh/day':>9}{'kWh/m2':>8}")
    for room in rooms.values():
        print(f"{room.room_id:<5}{room.room_name:<16}{room.building:<16}"
              f"{room.area_m2:>6.0f}{room.total_power():>7.1f}{room.hours_per_day:>7.0f}"
              f"{room.daily_energy():>9.1f}{room.energy_per_m2():>8.2f}")


def search_rooms(rooms, text):
    text = text.strip().lower()
    found = []
    for room in rooms.values():
        if text in room.room_id.lower() or text in room.room_name.lower() or text in room.building.lower():
            found.append(room)
    return found


def update_room(rooms, room_id, field, new_value):
    if room_id not in rooms:
        raise ValueError("Room " + room_id + " was not found")
    if field not in FIELDS[1:]:
        raise ValueError("You cannot update the field '" + field + "'")
    data = rooms[room_id].to_dict()
    data[field] = new_value
    rooms[room_id] = Room(**data)


def total_consumption(rooms):
    total = 0
    for room in rooms.values():
        total += room.daily_energy()
    return total


def buildings(rooms):
    return {room.building for room in rooms.values()}


def top_rooms(rooms, n=3):
    ordered = sorted(rooms.values(), key=lambda room: room.daily_energy(), reverse=True)
    return ordered[:n]


def save_rooms(rooms, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for room in rooms.values():
            writer.writerow(room.to_dict())


def load_rooms(filename):
    rooms = {}
    with open(filename, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                room = Room(**row)
                rooms[room.room_id] = room
            except ValueError as error:
                print("Skipped a bad row:", error)
    return rooms


def save_energy_report(rooms, filename):
    columns = FIELDS + ("total_power_kw", "daily_kwh", "kwh_per_m2")
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for room in rooms.values():
            row = room.to_dict()
            row["total_power_kw"] = round(room.total_power(), 2)
            row["daily_kwh"] = round(room.daily_energy(), 2)
            row["kwh_per_m2"] = round(room.energy_per_m2(), 3)
            writer.writerow(row)
