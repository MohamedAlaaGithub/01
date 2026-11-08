# Building Energy Analyzer

**Course:** C60 - Assignment 1 (Python project)
**Student:** Mohamed Alaa Hassaneen Mohamed

## Project description

A Python application that calculates and analyzes the energy consumption of a building. It has **two connected modules** that are used from one menu in `main.py`.

| File | What it does |
|------|--------------|
| `module1_rooms.py` | **Module 1.** A `Room` class and functions to add, list, search and update rooms, calculate the daily energy, the total and the consumption per m2, and save the rooms to CSV. |
| `module2_analysis.py` | **Module 2.** pandas: read, clean (duplicates, missing values), merge and group the readings, cost per room / building / month. NumPy: air-conditioning reduction. Matplotlib: 4 charts. Exports reports as CSV and charts as PNG. |
| `main.py` | The menu that connects both modules. |

**Formulas**

```
Daily energy (kWh)           = total power (kW) x operating hours
Consumption per square meter = daily energy (kWh) / room area (m2)
Cost                         = energy (kWh) x price per kWh (typed by the user)
```

**Input rules:** area > 0, power >= 0, operating hours between 0 and 24, price > 0, AC reduction between 0 and 100 %.

## Required libraries

```
pandas   numpy   matplotlib   (notebook - only to open the .ipynb file)
```

```bash
pip install -r requirements.txt
```

## How to run

```bash
python main.py                       # the menu
python tests/test_cases.py           # 3 valid + 3 invalid tests -> tests/test_results.md
jupyter notebook analysis_notebook.ipynb
```

Menu: `1` add room, `2` list, `3` search, `4` update, `5` energy summary, `6` clean and merge readings, `7` cost report (asks for the price per kWh), `8` AC reduction (asks for the percentage), `9` create the 4 charts, `10` export all reports, `0` exit.

## Folders

```
data/rooms.csv       8 rooms in 2 buildings (Admin Block, Academic Block)
data/readings.csv    daily readings, 1 Aug - 30 Sep 2026 (490 rows)
outputs/reports/     CSV reports
outputs/charts/      4 PNG charts (line, bar, scatter, histogram)
tests/               test_cases.py and test_results.md
```

## Data cleaning

* Duplicate rows are removed (2 found).
* Missing kWh values are filled with the average of the same room (3 found).
* Readings are merged with the room data using `room_id`.

## Presentation

Repository link (also on the final slide): https://github.com/MohamedAlaaGithub/01.git
