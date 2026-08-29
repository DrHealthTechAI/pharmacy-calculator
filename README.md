# Hospital Pharmacy Calculator

Seven clinical calculations pharmacists and pharmacy students actually need at
the counter or on the ward, in a terminal app and a mobile-friendly web app.

> **For educational and reference use only.** Every result must be verified
> against your institutional protocol before clinical use. This tool does not
> replace clinical judgement.

## Calculators

| Calculator | Formula | Reference |
|---|---|---|
| Creatinine clearance | `((140 − age) × weight) / (72 × SCr)`, × 0.85 for females | Cockcroft & Gault, 1976 |
| IV infusion time | `volume ÷ rate` | — |
| IV pump rate | `volume ÷ time` | — |
| Manual drip rate | `(volume × drop factor) ÷ time in minutes` | — |
| Vial dose / mg per mL | `ordered mg ÷ (vial mg ÷ vial mL)` | — |
| Body surface area | `√((height cm × weight kg) ÷ 3600)` | Mosteller, 1987 |
| BSA dosing | `mg/m² × BSA` | — |
| Body mass index | `weight kg ÷ (height m)²` | WHO categories |
| Free water deficit | `TBW × ((measured Na ÷ 140) − 1)` | — |
| Paediatric — Clark's rule | `(weight lb ÷ 150) × adult dose` | — |
| Paediatric — Young's rule | `(age ÷ (age + 12)) × adult dose` | — |
| Paediatric — mg/kg | `weight × mg/kg ÷ doses per day` | — |

## Quick start

Terminal version — needs Python 3.9 or newer, nothing else:

```bash
git clone https://github.com/YOUR-USERNAME/pharmacy-calculator.git
```

```bash
cd pharmacy-calculator
```

```bash
python -m pharmacy_calc.cli
```

Web version:

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Then open `http://localhost:8501`.

## How it is put together

```
pharmacy_calc/formulas.py   pure maths, no input/output — the single source of truth
pharmacy_calc/cli.py        terminal menu
app.py                      Streamlit web app
tests/test_formulas.py      known-value tests for every formula
```

Both interfaces import the same `formulas.py`. A formula corrected in one place
is corrected everywhere, and the tests cover both.

## Tests

```bash
python -m pytest tests/ -q
```

44 tests check each formula against hand-worked values — for example a 60-year
old 70 kg male with a serum creatinine of 1.2 mg/dL must give a creatinine
clearance of 64.81 mL/min, and 1000 mL at 15 gtt/mL over 8 hours must give
31.25 gtt/min.

## Contributing

Corrections to any formula are very welcome, especially from practising
pharmacists. Please open an issue with the reference you are working from.

## Licence

MIT — see [LICENSE](LICENSE).
