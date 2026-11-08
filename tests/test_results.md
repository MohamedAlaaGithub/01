# Test results

| # | Case | Expected | Actual | Result |
|---|------|----------|--------|--------|
| V1 | Room 50 m2, 1.0 + 2.0 + 0.5 kW, 8 h | [28.0, 0.56] | [28.0, 0.56] | PASS |
| V2 | Server room, 8.0+5.0+0.2 kW, 24 h (limit value) | 316.8 | 316.8 | PASS |
| V3 | Reduce AC by 20 % (AC 10, light 1, equip 1, 10 h) | [120.0, 100.0, 20.0] | [120.0, 100.0, 20.0] | PASS |
| I1 | Area = 0 | Room area must be greater than zero | Room area must be greater than zero | PASS |
| I2 | Lighting power = -1 | Power values must not be negative | Power values must not be negative | PASS |
| I3 | Operating hours = 25 | Operating hours must be between 0 and 24 | Operating hours must be between 0 and 24 | PASS |

6 of 6 tests passed.
