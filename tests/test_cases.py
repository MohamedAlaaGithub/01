"""
Tests: 3 valid cases + 3 invalid cases.
Run from the project folder:   python tests/test_cases.py
It prints a table and saves it in tests/test_results.md
"""

import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE)

from module1_rooms import Room
import module2_analysis as m2


def valid_energy():
    room = Room("R99", "Test", "Main", 50, 1.0, 2.0, 0.5, 8)
    return [round(room.daily_energy(), 2), round(room.energy_per_m2(), 2)]


def valid_hours_24():
    room = Room("R98", "Server", "Main", 20, 0.2, 5.0, 8.0, 24)
    return round(room.daily_energy(), 2)


def valid_ac_reduction():
    # Room: AC 10 kW, lighting 1, equipment 1, 10 hours -> reduce AC by 20 %
    path = os.path.join(BASE, "tests", "one_room.csv")
    with open(path, "w") as file:
        file.write("room_id,room_name,building,area_m2,lighting_kw,ac_kw,equipment_kw,hours_per_day\n")
        file.write("T1,Test,Main,50,1,10,1,10\n")
    result = m2.ac_reduction(path, 20)
    os.remove(path)
    return [float(result["before_kwh"][0]), float(result["after_kwh"][0]), float(result["saved_kwh"][0])]


def invalid_area():
    Room("R97", "Bad", "Main", 0, 1, 1, 1, 8)


def invalid_power():
    Room("R96", "Bad", "Main", 20, -1, 1, 1, 8)


def invalid_hours():
    Room("R95", "Bad", "Main", 20, 1, 1, 1, 25)


valid_tests = [
    ("V1", "Room 50 m2, 1.0 + 2.0 + 0.5 kW, 8 h", [28.0, 0.56], valid_energy),
    ("V2", "Server room, 8.0+5.0+0.2 kW, 24 h (limit value)", 316.8, valid_hours_24),
    ("V3", "Reduce AC by 20 % (AC 10, light 1, equip 1, 10 h)", [120.0, 100.0, 20.0], valid_ac_reduction),
]

invalid_tests = [
    ("I1", "Area = 0", "Room area must be greater than zero", invalid_area),
    ("I2", "Lighting power = -1", "Power values must not be negative", invalid_power),
    ("I3", "Operating hours = 25", "Operating hours must be between 0 and 24", invalid_hours),
]

lines = ["| # | Case | Expected | Actual | Result |", "|---|------|----------|--------|--------|"]
passed = 0

for number, case, expected, function in valid_tests:
    actual = function()
    ok = actual == expected
    passed += ok
    lines.append(f"| {number} | {case} | {expected} | {actual} | {'PASS' if ok else 'FAIL'} |")

for number, case, expected, function in invalid_tests:
    try:
        function()
        actual = "no error"
    except ValueError as error:
        actual = str(error)
    ok = actual == expected
    passed += ok
    lines.append(f"| {number} | {case} | {expected} | {actual} | {'PASS' if ok else 'FAIL'} |")

text = "\n".join(lines) + f"\n\n{passed} of 6 tests passed.\n"
print(text)
with open(os.path.join(BASE, "tests", "test_results.md"), "w", encoding="utf-8") as file:
    file.write("# Test results\n\n" + text)
