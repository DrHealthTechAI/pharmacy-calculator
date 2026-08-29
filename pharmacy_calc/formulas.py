"""Pure clinical calculation functions.

Every function here takes numbers and returns numbers. No input(), no print().
That keeps the maths testable and lets the terminal app and the web app share
one single source of truth -- a formula fixed here is fixed everywhere.

Each formula cites its source. Verify against your institutional protocol
before clinical use.
"""

import math

LB_PER_KG = 2.20462
CM_PER_INCH = 2.54


# --------------------------------------------------------------------------
# Total body water / free water deficit
# --------------------------------------------------------------------------

# Watson/Chumlea TBW fractions by age group and sex.
TBW_FACTORS = {
    ("child", "m"): 0.60,
    ("child", "f"): 0.60,
    ("adult", "m"): 0.60,
    ("adult", "f"): 0.50,
    ("elderly", "m"): 0.50,
    ("elderly", "f"): 0.45,
}


def tbw_factor(age_group, sex):
    """Return the total body water fraction, e.g. 0.6 for an adult male."""
    key = (age_group.strip().lower(), sex.strip().lower()[:1])
    if key not in TBW_FACTORS:
        raise ValueError(
            "age_group must be child/adult/elderly and sex must be m/f, "
            f"got {age_group!r}/{sex!r}"
        )
    return TBW_FACTORS[key]


def total_body_water(weight_kg, age_group, sex):
    """Total body water in litres."""
    return tbw_factor(age_group, sex) * weight_kg


def free_water_deficit(weight_kg, serum_sodium, age_group, sex, target_sodium=140.0):
    """Free water deficit in litres for a hypernatraemic patient.

    deficit = TBW x (measured Na / target Na - 1)

    A positive result is a water deficit (hypernatraemia). A negative result
    means measured sodium is below target, so the formula does not apply.
    """
    tbw = total_body_water(weight_kg, age_group, sex)
    return tbw * ((serum_sodium / target_sodium) - 1)


# --------------------------------------------------------------------------
# Body mass index
# --------------------------------------------------------------------------

def bmi(weight_kg, height_cm):
    """Body mass index in kg/m^2."""
    if height_cm <= 0:
        raise ValueError("height must be greater than zero")
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def bmi_class(value):
    """WHO body mass index category."""
    if value < 18.5:
        return "Underweight"
    if value < 25:
        return "Normal weight"
    if value < 30:
        return "Overweight"
    if value < 35:
        return "Obesity class I"
    if value < 40:
        return "Obesity class II"
    return "Obesity class III (morbid obesity)"


def feet_inches_to_cm(feet, inches=0):
    """Convert height in feet and inches to centimetres."""
    return ((feet * 12) + inches) * CM_PER_INCH


# --------------------------------------------------------------------------
# Body surface area
# --------------------------------------------------------------------------

def bsa_mosteller(height_cm, weight_kg):
    """Body surface area in m^2 (Mosteller 1987)."""
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("height and weight must be greater than zero")
    return math.sqrt((height_cm * weight_kg) / 3600)


def dose_from_bsa(dose_per_m2, bsa_m2):
    """Total dose in mg from a mg/m^2 order."""
    return dose_per_m2 * bsa_m2


# --------------------------------------------------------------------------
# Vial reconstitution / mg per mL
# --------------------------------------------------------------------------

def vial_concentration(vial_mg, vial_ml):
    """Concentration of a vial in mg/mL."""
    if vial_ml <= 0:
        raise ValueError("vial volume must be greater than zero")
    return vial_mg / vial_ml


def volume_for_dose(ordered_mg, vial_mg, vial_ml):
    """Volume in mL that delivers the ordered dose."""
    return ordered_mg / vial_concentration(vial_mg, vial_ml)


def vials_needed(ordered_mg, vial_mg, vial_ml):
    """Whole vials required to cover the ordered dose."""
    return math.ceil(volume_for_dose(ordered_mg, vial_mg, vial_ml) / vial_ml)


# --------------------------------------------------------------------------
# IV infusion
# --------------------------------------------------------------------------

def infusion_time_hours(total_volume_ml, rate_ml_per_hr):
    """How long a bag will run, in hours."""
    if rate_ml_per_hr <= 0:
        raise ValueError("infusion rate must be greater than zero")
    return total_volume_ml / rate_ml_per_hr


def infusion_rate_ml_per_hr(total_volume_ml, time_hours):
    """Pump rate in mL/hr."""
    if time_hours <= 0:
        raise ValueError("time must be greater than zero")
    return total_volume_ml / time_hours


def drip_rate_gtt_per_min(total_volume_ml, drop_factor, time_hours):
    """Manual drip rate in drops per minute.

    gtt/min = (volume mL x drop factor gtt/mL) / (time in MINUTES)

    The conversion from hours to minutes is what makes this a per-minute
    rate. Omitting it overstates the answer 60-fold.
    """
    if time_hours <= 0:
        raise ValueError("time must be greater than zero")
    return (total_volume_ml * drop_factor) / (time_hours * 60)


# --------------------------------------------------------------------------
# Renal function
# --------------------------------------------------------------------------

def creatinine_clearance(age, weight_kg, serum_creatinine, sex):
    """Creatinine clearance in mL/min (Cockcroft-Gault 1976).

    CrCl = ((140 - age) x weight kg) / (72 x SCr mg/dL), x 0.85 for females.
    """
    if serum_creatinine <= 0:
        raise ValueError("serum creatinine must be greater than zero")
    sex = sex.strip().lower()[:1]
    if sex not in ("m", "f"):
        raise ValueError(f"sex must be m or f, got {sex!r}")
    crcl = ((140 - age) * weight_kg) / (72 * serum_creatinine)
    if sex == "f":
        crcl *= 0.85
    return crcl


def renal_function_stage(crcl):
    """Descriptive stage for a creatinine clearance.

    Ordered highest to lowest so every band is reachable.
    """
    if crcl >= 90:
        return "Normal renal function"
    if crcl >= 60:
        return "Mildly decreased"
    if crcl >= 30:
        return "Moderate impairment"
    if crcl >= 15:
        return "Severe impairment"
    return "Kidney failure"


# --------------------------------------------------------------------------
# Paediatric dosing
# --------------------------------------------------------------------------

def clarks_rule(weight_kg, adult_dose_mg):
    """Paediatric dose by Clark's rule (weight based)."""
    weight_lb = weight_kg * LB_PER_KG
    return (weight_lb / 150) * adult_dose_mg


def youngs_rule(age_years, adult_dose_mg):
    """Paediatric dose by Young's rule (age based, 1-12 years)."""
    if age_years <= 0:
        raise ValueError("age must be greater than zero")
    return (age_years / (age_years + 12)) * adult_dose_mg


def mg_per_kg_dose(weight_kg, mg_per_kg, doses_per_day=1):
    """Weight based dose. Returns (dose per administration, total per day)."""
    total_daily = weight_kg * mg_per_kg
    if doses_per_day < 1:
        raise ValueError("doses per day must be at least 1")
    return total_daily / doses_per_day, total_daily
