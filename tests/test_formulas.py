"""Known-value tests for every clinical formula.

Each expected value is worked out by hand from the published formula so that
a future change to the code cannot silently alter a clinical result.
"""

import math

import pytest

from pharmacy_calc import formulas as f


# --------------------------------------------------------------------------
# Creatinine clearance (Cockcroft-Gault)
# --------------------------------------------------------------------------

def test_crcl_male():
    # ((140 - 60) x 70) / (72 x 1.2) = 5600 / 86.4 = 64.81
    assert f.creatinine_clearance(60, 70, 1.2, "m") == pytest.approx(64.81, abs=0.01)


def test_crcl_female_is_85_percent_of_male():
    male = f.creatinine_clearance(60, 70, 1.2, "m")
    female = f.creatinine_clearance(60, 70, 1.2, "f")
    assert female == pytest.approx(male * 0.85, abs=0.01)
    assert female == pytest.approx(55.09, abs=0.01)


def test_crcl_rejects_zero_creatinine():
    with pytest.raises(ValueError):
        f.creatinine_clearance(60, 70, 0, "m")


def test_crcl_rejects_bad_sex():
    with pytest.raises(ValueError):
        f.creatinine_clearance(60, 70, 1.2, "x")


@pytest.mark.parametrize("crcl,expected", [
    (120, "Normal renal function"),
    (90, "Normal renal function"),
    (75, "Mildly decreased"),
    (60, "Mildly decreased"),
    (45, "Moderate impairment"),
    (30, "Moderate impairment"),
    (20, "Severe impairment"),
    (15, "Severe impairment"),
    (10, "Kidney failure"),
])
def test_every_renal_stage_is_reachable(crcl, expected):
    assert f.renal_function_stage(crcl) == expected


# --------------------------------------------------------------------------
# IV infusion
# --------------------------------------------------------------------------

def test_drip_rate_converts_hours_to_minutes():
    # 1000 mL x 15 gtt/mL over 8 h = 15000 / 480 min = 31.25 gtt/min
    assert f.drip_rate_gtt_per_min(1000, 15, 8) == pytest.approx(31.25)


def test_drip_rate_is_clinically_plausible():
    # A macrodrip set should land in the tens, never the thousands.
    assert 5 < f.drip_rate_gtt_per_min(1000, 20, 8) < 100


def test_infusion_time():
    assert f.infusion_time_hours(1000, 125) == pytest.approx(8.0)


def test_infusion_rate():
    assert f.infusion_rate_ml_per_hr(1000, 8) == pytest.approx(125.0)


def test_infusion_rejects_zero_time():
    with pytest.raises(ValueError):
        f.infusion_rate_ml_per_hr(1000, 0)


# --------------------------------------------------------------------------
# Body surface area
# --------------------------------------------------------------------------

def test_bsa_mosteller():
    # sqrt((170 x 70) / 3600) = sqrt(3.3056) = 1.8181
    assert f.bsa_mosteller(170, 70) == pytest.approx(1.8181, abs=0.0001)


def test_bsa_average_adult_is_about_1_7():
    assert 1.6 < f.bsa_mosteller(170, 65) < 1.9


def test_dose_from_bsa():
    # 500 mg/m^2 x 1.8181 m^2
    assert f.dose_from_bsa(500, 1.8181) == pytest.approx(909.05, abs=0.01)


# --------------------------------------------------------------------------
# Body mass index
# --------------------------------------------------------------------------

def test_bmi():
    # 70 / 1.70^2 = 24.22
    assert f.bmi(70, 170) == pytest.approx(24.22, abs=0.01)


@pytest.mark.parametrize("value,expected", [
    (17.0, "Underweight"),
    (18.5, "Normal weight"),
    (24.9, "Normal weight"),
    (25.0, "Overweight"),
    (29.9, "Overweight"),
    (30.0, "Obesity class I"),
    (35.0, "Obesity class II"),
    (41.0, "Obesity class III (morbid obesity)"),
])
def test_bmi_class_boundaries(value, expected):
    assert f.bmi_class(value) == expected


def test_feet_inches_conversion():
    # 5 ft 8 in = 68 in x 2.54 = 172.72 cm
    assert f.feet_inches_to_cm(5, 8) == pytest.approx(172.72, abs=0.01)


def test_bmi_rejects_zero_height():
    with pytest.raises(ValueError):
        f.bmi(70, 0)


# --------------------------------------------------------------------------
# Free water deficit
# --------------------------------------------------------------------------

def test_free_water_deficit():
    # TBW = 0.6 x 70 = 42 L; 42 x (160/140 - 1) = 42 x 0.142857 = 6.0 L
    assert f.free_water_deficit(70, 160, "adult", "m") == pytest.approx(6.0, abs=0.01)


def test_tbw_factors():
    assert f.total_body_water(70, "adult", "m") == pytest.approx(42.0)
    assert f.total_body_water(70, "adult", "f") == pytest.approx(35.0)
    assert f.total_body_water(70, "elderly", "f") == pytest.approx(31.5)


def test_normal_sodium_gives_no_deficit():
    assert f.free_water_deficit(70, 140, "adult", "m") == pytest.approx(0.0)


def test_tbw_rejects_unknown_group():
    with pytest.raises(ValueError):
        f.total_body_water(70, "teenager", "m")


# --------------------------------------------------------------------------
# Vial dosing
# --------------------------------------------------------------------------

def test_vial_concentration():
    assert f.vial_concentration(500, 10) == pytest.approx(50.0)


def test_volume_for_dose():
    # 750 mg at 50 mg/mL = 15 mL
    assert f.volume_for_dose(750, 500, 10) == pytest.approx(15.0)


def test_vials_needed_rounds_up():
    # 15 mL needed from 10 mL vials = 2 vials, never 1.5
    assert f.vials_needed(750, 500, 10) == 2
    assert f.vials_needed(500, 500, 10) == 1
    assert f.vials_needed(2100, 500, 10) == 5


# --------------------------------------------------------------------------
# Paediatric dosing
# --------------------------------------------------------------------------

def test_clarks_rule():
    # 20 kg = 44.09 lb; (44.09 / 150) x 500 = 146.97 mg
    assert f.clarks_rule(20, 500) == pytest.approx(146.97, abs=0.01)


def test_youngs_rule():
    # (6 / 18) x 500 = 166.67 mg
    assert f.youngs_rule(6, 500) == pytest.approx(166.67, abs=0.01)


def test_paediatric_dose_never_exceeds_adult_dose():
    for age in range(1, 13):
        assert f.youngs_rule(age, 500) < 500


def test_mg_per_kg_dose():
    per_dose, daily = f.mg_per_kg_dose(20, 30, 3)
    assert daily == pytest.approx(600.0)
    assert per_dose == pytest.approx(200.0)


def test_mg_per_kg_rejects_zero_doses():
    with pytest.raises(ValueError):
        f.mg_per_kg_dose(20, 30, 0)


# --------------------------------------------------------------------------
# WHO Asia-Pacific BMI classification
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (17.0, "Underweight"),
    (18.5, "Normal weight"),
    (22.9, "Normal weight"),
    (23.0, "Overweight (at risk)"),
    (24.9, "Overweight (at risk)"),
    (25.0, "Obesity class I"),
    (29.9, "Obesity class I"),
    (30.0, "Obesity class II"),
    (45.0, "Obesity class II"),
])
def test_asia_pacific_bmi_bands(value, expected):
    assert f.bmi_class_asia_pacific(value) == expected


def test_asia_pacific_is_stricter_than_international():
    # BMI 24 is normal internationally but overweight in the Asia-Pacific scale.
    assert f.bmi_class(24.0) == "Normal weight"
    assert f.bmi_class_asia_pacific(24.0) == "Overweight (at risk)"


def test_asia_pacific_has_two_obesity_classes_not_three():
    names = {name for name, _ in f.BMI_BANDS_ASIA_PACIFIC}
    assert "Obesity class III (morbid obesity)" not in names
    assert "Obesity class II" in names


def test_band_tables_match_the_classifiers():
    # Every label a classifier can return must appear in its band table.
    who_names = {name for name, _ in f.BMI_BANDS_WHO}
    ap_names = {name for name, _ in f.BMI_BANDS_ASIA_PACIFIC}
    for value in (15, 20, 24, 27, 32, 37, 45):
        assert f.bmi_class(value) in who_names
        assert f.bmi_class_asia_pacific(value) in ap_names


def test_crcl_band_table_matches_the_classifier():
    names = {name for name, _ in f.CRCL_BANDS}
    for value in (120, 75, 45, 20, 5):
        assert f.renal_function_stage(value) in names


# --------------------------------------------------------------------------
# Serum sodium classification and correction rate
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sodium,expected", [
    (130, "Hyponatraemia - this calculator does not apply"),
    (140, "Normal serum sodium"),
    (145, "Normal serum sodium"),
    (150, "Hypernatraemia"),
    (159, "Hypernatraemia"),
    (160, "Hypernatraemia - severe symptoms typically occur above 160"),
    (180, "Hypernatraemia - severe symptoms typically occur above 160"),
])
def test_sodium_status(sodium, expected):
    assert f.sodium_status(sodium) == expected


def test_acute_allows_faster_correction_than_chronic():
    assert (f.max_sodium_fall_per_day("acute")
            > f.max_sodium_fall_per_day("chronic"))


def test_chronic_correction_limit_is_the_conventional_figure():
    assert f.max_sodium_fall_per_day("chronic") == pytest.approx(10.0)


def test_correction_rate_rejects_unknown_onset():
    with pytest.raises(ValueError):
        f.max_sodium_fall_per_day("subacute")


# --------------------------------------------------------------------------
# Dosing weights for Cockcroft-Gault
# --------------------------------------------------------------------------

def test_ideal_body_weight_male():
    # 170 cm = 66.93 in, 6.93 in over 5 ft: 50 + 2.3 x 6.93 = 65.94 kg
    assert f.ideal_body_weight(170, "m") == pytest.approx(65.94, abs=0.01)


def test_ideal_body_weight_female_is_4_5_kg_lower():
    male = f.ideal_body_weight(170, "m")
    female = f.ideal_body_weight(170, "f")
    assert male - female == pytest.approx(4.5)


def test_ideal_body_weight_at_exactly_five_feet():
    # 152.4 cm is 5 ft exactly, so IBW is the base value with nothing added.
    assert f.ideal_body_weight(152.4, "m") == pytest.approx(50.0, abs=0.01)
    assert f.ideal_body_weight(152.4, "f") == pytest.approx(45.5, abs=0.01)


def test_ideal_body_weight_rejects_bad_sex():
    with pytest.raises(ValueError):
        f.ideal_body_weight(170, "x")


def test_adjusted_body_weight():
    # IBW 65.94, actual 120: 65.94 + 0.4 x (120 - 65.94) = 87.56
    ideal = f.ideal_body_weight(170, "m")
    assert f.adjusted_body_weight(120, ideal) == pytest.approx(87.56, abs=0.01)


def test_adjusted_sits_between_ideal_and_actual():
    ideal = f.ideal_body_weight(170, "m")
    adjusted = f.adjusted_body_weight(120, ideal)
    assert ideal < adjusted < 120


def test_adjusted_equals_ideal_when_actual_equals_ideal():
    ideal = f.ideal_body_weight(170, "m")
    assert f.adjusted_body_weight(ideal, ideal) == pytest.approx(ideal)


def test_obese_patient_is_given_adjusted_weight():
    name, weight, reason = f.indicated_dosing_weight(120, 170, "m")
    assert name == "Adjusted"
    assert weight == pytest.approx(87.56, abs=0.01)
    assert "182%" in reason


def test_underweight_patient_is_given_actual_weight():
    name, weight, _ = f.indicated_dosing_weight(50, 170, "m")
    assert name == "Actual"
    assert weight == pytest.approx(50.0)


def test_normal_weight_patient_is_given_ideal_weight():
    name, weight, _ = f.indicated_dosing_weight(70, 170, "m")
    assert name == "Ideal"
    assert weight == pytest.approx(f.ideal_body_weight(170, "m"))


def test_actual_weight_overestimates_clearance_in_obesity():
    # The whole reason this feature exists: the same patient reads as normal
    # on actual weight and impaired on ideal weight.
    on_actual = f.creatinine_clearance(60, 120, 1.0, "m")
    ideal = f.ideal_body_weight(170, "m")
    on_ideal = f.creatinine_clearance(60, ideal, 1.0, "m")

    assert on_actual == pytest.approx(133.3, abs=0.1)
    assert on_ideal == pytest.approx(73.3, abs=0.1)
    assert f.renal_function_stage(on_actual) == "Normal renal function"
    assert f.renal_function_stage(on_ideal) == "Mildly decreased"


def test_the_three_weights_converge_for_a_normal_sized_patient():
    # No obesity, so actual, ideal and adjusted should be close together.
    ideal = f.ideal_body_weight(170, "m")
    adjusted = f.adjusted_body_weight(68, ideal)
    assert abs(68 - ideal) < 5
    assert abs(adjusted - ideal) < 5
