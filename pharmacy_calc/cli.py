"""Terminal interface for the hospital pharmacy calculator.

All arithmetic lives in formulas.py -- this file only handles asking and
showing. Run it with:  python -m pharmacy_calc.cli
"""

from . import formulas as f

DISCLAIMER = (
    "For educational and reference use only. Always verify every result\n"
    "against your institutional protocol before clinical use."
)


# --------------------------------------------------------------------------
# Input helpers -- a typo should never crash the program
# --------------------------------------------------------------------------

def ask_number(prompt, minimum=None, maximum=None, allow_blank=False):
    """Ask until the user gives a number in range. Returns None if blank."""
    while True:
        raw = input(prompt).strip()
        if not raw and allow_blank:
            return None
        try:
            value = float(raw)
        except ValueError:
            print("  Please enter a number, for example 70 or 1.2.")
            continue
        if minimum is not None and value < minimum:
            print(f"  Please enter a value of at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"  Please enter a value no greater than {maximum}.")
            continue
        return value


def ask_choice(prompt, options):
    """Ask until the user picks one of options (a dict of key -> label)."""
    while True:
        raw = input(prompt).strip().lower()
        if raw in options:
            return raw
        print(f"  Please enter one of: {', '.join(options)}")


def ask_yes_no(prompt):
    return ask_choice(prompt, {"y": "yes", "n": "no"}) == "y"


def heading(title):
    print()
    print("=" * 58)
    print(f"  {title}")
    print("=" * 58)


# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------

def screen_paediatric_dose():
    heading("Paediatric Dose")
    print("  1. Clark's rule (by weight)")
    print("  2. Young's rule (by age)")
    print("  3. mg/kg dosing")
    choice = ask_choice("Choose 1-3: ", {"1": "", "2": "", "3": ""})

    if choice == "1":
        weight = ask_number("Child weight (kg): ", minimum=0.1)
        adult_dose = ask_number("Adult dose (mg): ", minimum=0.1)
        dose = f.clarks_rule(weight, adult_dose)
        print(f"\n  Child dose (Clark's rule): {dose:.2f} mg")
        print(f"  Based on {weight * f.LB_PER_KG:.1f} lb / 150 lb adult weight.")
    elif choice == "2":
        age = ask_number("Child age (years): ", minimum=0.1, maximum=18)
        adult_dose = ask_number("Adult dose (mg): ", minimum=0.1)
        dose = f.youngs_rule(age, adult_dose)
        print(f"\n  Child dose (Young's rule): {dose:.2f} mg")
    else:
        weight = ask_number("Child weight (kg): ", minimum=0.1)
        per_kg = ask_number("Dose (mg/kg/day): ", minimum=0.01)
        divided = ask_number("Divided into how many doses per day: ", minimum=1)
        per_dose, daily = f.mg_per_kg_dose(weight, per_kg, divided)
        print(f"\n  Total daily dose: {daily:.2f} mg")
        print(f"  Per dose:         {per_dose:.2f} mg every "
              f"{24 / divided:.0f} hours")


def screen_creatinine_clearance():
    heading("Creatinine Clearance (Cockcroft-Gault)")
    age = ask_number("Age (years): ", minimum=1, maximum=120)
    weight = ask_number("Weight (kg): ", minimum=1)
    scr = ask_number("Serum creatinine (mg/dL): ", minimum=0.01)
    sex = ask_choice("Sex (m/f): ", {"m": "", "f": ""})

    crcl = f.creatinine_clearance(age, weight, scr, sex)
    print(f"\n  Creatinine clearance: {crcl:.2f} mL/min")
    print(f"  Interpretation:       {f.renal_function_stage(crcl)}")
    if crcl < 60:
        print("  Renal dose adjustment may be required.")


def screen_iv_infusion():
    heading("IV Infusion")
    print("  1. Infusion time (hours)")
    print("  2. Infusion rate (mL/hr)")
    print("  3. Manual drip rate (gtt/min)")
    choice = ask_choice("Choose 1-3: ", {"1": "", "2": "", "3": ""})

    if choice == "1":
        volume = ask_number("Total volume (mL): ", minimum=0.1)
        rate = ask_number("Infusion rate (mL/hr): ", minimum=0.1)
        hours = f.infusion_time_hours(volume, rate)
        whole, minutes = int(hours), (hours % 1) * 60
        print(f"\n  Infusion time: {hours:.2f} hours "
              f"({whole} h {minutes:.0f} min)")
    elif choice == "2":
        volume = ask_number("Total volume (mL): ", minimum=0.1)
        hours = ask_number("Total time (hours): ", minimum=0.01)
        print(f"\n  Pump rate: {f.infusion_rate_ml_per_hr(volume, hours):.2f} mL/hr")
    else:
        volume = ask_number("Total volume (mL): ", minimum=0.1)
        drop_factor = ask_number("Drop factor (gtt/mL, usually 10/15/20/60): ",
                                 minimum=1)
        hours = ask_number("Time (hours): ", minimum=0.01)
        rate = f.drip_rate_gtt_per_min(volume, drop_factor, hours)
        print(f"\n  Drip rate: {rate:.1f} gtt/min  (count {round(rate / 4)} "
              f"drops in 15 seconds)")


def screen_vial_dose():
    heading("Vial Dose / mg per mL")
    ordered = ask_number("Dose ordered (mg): ", minimum=0.01)
    vial_mg = ask_number("Strength per vial (mg): ", minimum=0.01)
    vial_ml = ask_number("Volume per vial (mL): ", minimum=0.01)

    conc = f.vial_concentration(vial_mg, vial_ml)
    volume = f.volume_for_dose(ordered, vial_mg, vial_ml)
    vials = f.vials_needed(ordered, vial_mg, vial_ml)
    print(f"\n  Concentration:  {conc:.2f} mg/mL")
    print(f"  Withdraw:       {volume:.2f} mL to give {ordered:.0f} mg")
    print(f"  Vials required: {vials} vial(s) of {vial_ml:.0f} mL")


def screen_bsa():
    heading("Body Surface Area (Mosteller)")
    height = ask_number("Height (cm): ", minimum=10, maximum=280)
    weight = ask_number("Weight (kg): ", minimum=0.5, maximum=500)
    bsa = f.bsa_mosteller(height, weight)
    print(f"\n  Body surface area: {bsa:.2f} m^2")

    if ask_yes_no("\nCalculate a dose from this BSA? (y/n): "):
        per_m2 = ask_number("Dose ordered (mg/m^2): ", minimum=0.01)
        print(f"\n  Total dose: {f.dose_from_bsa(per_m2, bsa):.2f} mg")
        print(f"  ({per_m2:.0f} mg/m^2 x {bsa:.2f} m^2)")


def screen_bmi():
    heading("Body Mass Index")
    weight = ask_number("Weight (kg): ", minimum=0.5, maximum=500)
    unit = ask_choice("Height in (c)m or (f)eet and inches: ",
                      {"c": "", "f": ""})
    if unit == "c":
        height_cm = ask_number("Height (cm): ", minimum=10, maximum=280)
    else:
        feet = ask_number("Height (feet): ", minimum=1, maximum=8)
        inches = ask_number("            (inches): ", minimum=0, maximum=11.9)
        height_cm = f.feet_inches_to_cm(feet, inches)
        print(f"  = {height_cm:.1f} cm")

    value = f.bmi(weight, height_cm)
    print(f"\n  BMI:      {value:.2f} kg/m^2")
    print(f"  Category: {f.bmi_class(value)}")


def screen_free_water_deficit():
    heading("Free Water Deficit")
    weight = ask_number("Weight (kg): ", minimum=1)
    sodium = ask_number("Serum sodium (mEq/L): ", minimum=100, maximum=200)
    sex = ask_choice("Sex (m/f): ", {"m": "", "f": ""})
    age_group = ask_choice("Age group (c)hild / (a)dult / (e)lderly: ",
                           {"c": "", "a": "", "e": ""})
    group = {"c": "child", "a": "adult", "e": "elderly"}[age_group]

    tbw = f.total_body_water(weight, group, sex)
    deficit = f.free_water_deficit(weight, sodium, group, sex)
    print(f"\n  Total body water: {tbw:.2f} L")
    print(f"  Water deficit:    {deficit:.2f} L")
    if deficit > 0:
        print("  Correct slowly: sodium should not fall faster than "
              "10-12 mEq/L in 24 h.")
    else:
        print("  Sodium is at or below target, so this formula does not apply.")


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------

MENU = [
    ("1", "Paediatric dose (Clark's / Young's / mg/kg)", screen_paediatric_dose),
    ("2", "Creatinine clearance (Cockcroft-Gault)", screen_creatinine_clearance),
    ("3", "IV infusion time / rate / drip rate", screen_iv_infusion),
    ("4", "Vial dose and mg per mL", screen_vial_dose),
    ("5", "Body surface area and BSA dosing", screen_bsa),
    ("6", "Body mass index", screen_bmi),
    ("7", "Free water deficit", screen_free_water_deficit),
]


def main():
    print()
    print("=" * 58)
    print("  HOSPITAL PHARMACY CALCULATOR")
    print("=" * 58)
    print(DISCLAIMER)

    options = {key: label for key, label, _ in MENU}
    options["8"] = "Exit"
    screens = {key: fn for key, _, fn in MENU}

    while True:
        print()
        for key, label, _ in MENU:
            print(f"  {key}. {label}")
        print("  8. Exit")

        choice = ask_choice("\nEnter your choice (1-8): ", options)
        if choice == "8":
            break

        try:
            screens[choice]()
        except ValueError as exc:
            print(f"\n  Could not calculate: {exc}")

        if not ask_yes_no("\nAnother calculation? (y/n): "):
            break

    print("\nThank you for using the Hospital Pharmacy Calculator.\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled.\n")
