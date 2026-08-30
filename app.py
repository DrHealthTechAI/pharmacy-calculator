"""Web interface for the hospital pharmacy calculator.

Run locally:   streamlit run app.py
Deploy free:   share.streamlit.io  (point it at this repo)

This imports the same formulas module the terminal app uses, so the web and
terminal versions can never disagree about a clinical result.
"""

import streamlit as st

from pharmacy_calc import formulas as f

st.set_page_config(
    page_title="Pharmacy Calculator",
    page_icon="💊",
    layout="centered",
)

CALCULATORS = [
    "Creatinine clearance",
    "IV infusion",
    "Paediatric dose",
    "Vial dose (mg/mL)",
    "Body surface area",
    "Body mass index",
    "Free water deficit",
]

st.title("Hospital Pharmacy Calculator")
st.caption(
    "Clinical calculations for pharmacists, interns and pharmacy students. "
    "Works on a phone."
)

choice = st.sidebar.radio("Calculator", CALCULATORS)
st.sidebar.markdown("---")
st.sidebar.caption(
    "**For educational and reference use only.** Always verify every result "
    "against your institutional protocol before clinical use."
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Also available: "
    "[ABG Calculator](https://abg-calculator.streamlit.app) "
    "— blood gas interpretation, anion gap and compensation."
)


# --------------------------------------------------------------------------

if choice == "Creatinine clearance":
    st.subheader("Creatinine Clearance")
    st.caption("Cockcroft-Gault equation")

    col1, col2 = st.columns(2)
    age = col1.number_input("Age (years)", 1.0, 120.0, 60.0, step=1.0)
    weight = col2.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5)
    scr = col1.number_input("Serum creatinine (mg/dL)", 0.1, 20.0, 1.2, step=0.1)
    sex = col2.selectbox("Sex", ["Male", "Female"])

    crcl = f.creatinine_clearance(age, weight, scr, sex[0])
    stage = f.renal_function_stage(crcl)

    st.metric("Creatinine clearance", f"{crcl:.1f} mL/min", stage, delta_color="off")
    if crcl < 60:
        st.warning("Renal dose adjustment may be required.")
    st.latex(r"CrCl = \frac{(140 - age) \times weight}{72 \times SCr}"
             r"\;\times\; 0.85 \text{ if female}")


elif choice == "IV infusion":
    st.subheader("IV Infusion")
    mode = st.radio(
        "Calculate",
        ["Infusion time", "Pump rate (mL/hr)", "Manual drip rate (gtt/min)"],
        horizontal=False,
    )
    col1, col2 = st.columns(2)

    if mode == "Infusion time":
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0, step=50.0)
        rate = col2.number_input("Rate (mL/hr)", 1.0, 1000.0, 125.0, step=5.0)
        hours = f.infusion_time_hours(volume, rate)
        st.metric("Infusion time",
                  f"{hours:.2f} hours",
                  f"{int(hours)} h {(hours % 1) * 60:.0f} min", delta_color="off")

    elif mode == "Pump rate (mL/hr)":
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0, step=50.0)
        hours = col2.number_input("Over how many hours", 0.25, 48.0, 8.0, step=0.25)
        st.metric("Pump rate", f"{f.infusion_rate_ml_per_hr(volume, hours):.1f} mL/hr")

    else:
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0, step=50.0)
        hours = col2.number_input("Over how many hours", 0.25, 48.0, 8.0, step=0.25)
        drop_factor = st.selectbox(
            "Drop factor (gtt/mL)",
            [10, 15, 20, 60],
            index=1,
            help="60 gtt/mL is a microdrip (paediatric) set.",
        )
        rate = f.drip_rate_gtt_per_min(volume, drop_factor, hours)
        st.metric("Drip rate", f"{rate:.0f} gtt/min",
                  f"count {round(rate / 4)} drops in 15 seconds", delta_color="off")
        st.latex(r"gtt/min = \frac{volume \times drop\ factor}{time\ in\ minutes}")


elif choice == "Paediatric dose":
    st.subheader("Paediatric Dose")
    rule = st.radio("Method", ["mg/kg", "Clark's rule", "Young's rule"])
    col1, col2 = st.columns(2)

    if rule == "mg/kg":
        weight = col1.number_input("Child weight (kg)", 0.5, 100.0, 20.0, step=0.5)
        per_kg = col2.number_input("Dose (mg/kg/day)", 0.1, 500.0, 30.0, step=1.0)
        divided = st.slider("Divided doses per day", 1, 6, 3)
        per_dose, daily = f.mg_per_kg_dose(weight, per_kg, divided)
        col1.metric("Total daily dose", f"{daily:.0f} mg")
        col2.metric("Per dose", f"{per_dose:.1f} mg",
                    f"every {24 / divided:.0f} hours", delta_color="off")

    elif rule == "Clark's rule":
        weight = col1.number_input("Child weight (kg)", 0.5, 100.0, 20.0, step=0.5)
        adult = col2.number_input("Adult dose (mg)", 1.0, 5000.0, 500.0, step=50.0)
        st.metric("Child dose", f"{f.clarks_rule(weight, adult):.1f} mg",
                  f"{weight * f.LB_PER_KG:.1f} lb / 150 lb", delta_color="off")

    else:
        age = col1.number_input("Child age (years)", 1.0, 12.0, 6.0, step=1.0)
        adult = col2.number_input("Adult dose (mg)", 1.0, 5000.0, 500.0, step=50.0)
        st.metric("Child dose", f"{f.youngs_rule(age, adult):.1f} mg")
        st.caption("Young's rule applies to children aged 1-12 years.")


elif choice == "Vial dose (mg/mL)":
    st.subheader("Vial Dose")
    col1, col2, col3 = st.columns(3)
    ordered = col1.number_input("Dose ordered (mg)", 0.1, 10000.0, 750.0, step=50.0)
    vial_mg = col2.number_input("Vial strength (mg)", 0.1, 10000.0, 500.0, step=50.0)
    vial_ml = col3.number_input("Vial volume (mL)", 0.1, 500.0, 10.0, step=1.0)

    conc = f.vial_concentration(vial_mg, vial_ml)
    volume = f.volume_for_dose(ordered, vial_mg, vial_ml)
    vials = f.vials_needed(ordered, vial_mg, vial_ml)

    col1.metric("Concentration", f"{conc:.1f} mg/mL")
    col2.metric("Withdraw", f"{volume:.2f} mL")
    col3.metric("Vials needed", f"{vials}")
    st.info(f"Withdraw **{volume:.2f} mL** to give **{ordered:.0f} mg**. "
            f"Open **{vials}** vial(s).")


elif choice == "Body surface area":
    st.subheader("Body Surface Area")
    st.caption("Mosteller formula")
    col1, col2 = st.columns(2)
    height = col1.number_input("Height (cm)", 30.0, 250.0, 170.0, step=1.0)
    weight = col2.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5)

    bsa = f.bsa_mosteller(height, weight)
    st.metric("Body surface area", f"{bsa:.2f} m²")
    st.latex(r"BSA = \sqrt{\frac{height_{cm} \times weight_{kg}}{3600}}")

    if st.checkbox("Calculate a dose from this BSA"):
        per_m2 = st.number_input("Dose ordered (mg/m²)", 0.1, 5000.0, 500.0, step=10.0)
        st.metric("Total dose", f"{f.dose_from_bsa(per_m2, bsa):.1f} mg",
                  f"{per_m2:.0f} mg/m² × {bsa:.2f} m²", delta_color="off")


elif choice == "Body mass index":
    st.subheader("Body Mass Index")
    col1, col2 = st.columns(2)
    weight = col1.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5)
    unit = col2.radio("Height in", ["cm", "feet + inches"], horizontal=True)

    if unit == "cm":
        height_cm = col2.number_input("Height (cm)", 30.0, 250.0, 170.0, step=1.0)
    else:
        feet = col2.number_input("Feet", 1, 8, 5)
        inches = col2.number_input("Inches", 0.0, 11.5, 8.0, step=0.5)
        height_cm = f.feet_inches_to_cm(feet, inches)
        col2.caption(f"= {height_cm:.1f} cm")

    value = f.bmi(weight, height_cm)
    st.metric("BMI", f"{value:.1f} kg/m²", f.bmi_class(value), delta_color="off")


elif choice == "Free water deficit":
    st.subheader("Free Water Deficit")
    st.caption("For the hypernatraemic patient")
    col1, col2 = st.columns(2)
    weight = col1.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5)
    sodium = col2.number_input("Serum sodium (mEq/L)", 100.0, 200.0, 160.0, step=1.0)
    sex = col1.selectbox("Sex", ["Male", "Female"])
    group = col2.selectbox("Age group", ["Adult", "Elderly", "Child"])

    tbw = f.total_body_water(weight, group.lower(), sex[0])
    deficit = f.free_water_deficit(weight, sodium, group.lower(), sex[0])

    col1.metric("Total body water", f"{tbw:.1f} L")
    col2.metric("Water deficit", f"{deficit:.2f} L")

    if deficit > 0:
        st.warning("Correct slowly. Serum sodium should not fall faster than "
                   "10-12 mEq/L in 24 hours.")
    else:
        st.info("Serum sodium is at or below target, so this formula does "
                "not apply.")


st.markdown("---")
st.caption(
    "For educational and reference use only. Not a substitute for clinical "
    "judgement or your institutional protocol."
)
