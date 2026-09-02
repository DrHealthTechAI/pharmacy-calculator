"""Web interface for the hospital pharmacy calculator.

Run locally:   streamlit run app.py
Deploy free:   share.streamlit.io  (point it at this repo)

This imports the same formulas module the terminal app uses, so the web and
terminal versions can never disagree about a clinical result.
"""

import importlib

import streamlit as st

from pharmacy_calc import formulas as _formulas

# Streamlit re-runs this script on every interaction and re-reads it after a
# deploy, but it never re-imports modules -- Python keeps the first copy in
# sys.modules for the life of the process. So when formulas.py gains a new
# function, the running app can still be holding the old module and fails with
# AttributeError until someone restarts it by hand. Reloading here reads the
# current file from disk instead. The module is pure functions and constants
# with no state, so reloading it is cheap and safe.
f = importlib.reload(_formulas)

st.set_page_config(
    page_title="Pharmacy Calculator",
    page_icon="💊",
    layout="centered",
)

# --------------------------------------------------------------------------
# Plain-language definitions, shown as the little (i) next to each input and
# each result. Kept in one place so a term reads identically everywhere.
# --------------------------------------------------------------------------

HELP = {
    # --- values the user enters -------------------------------------------
    "age": (
        "Patient age in years. Creatinine clearance falls with age even when "
        "serum creatinine looks normal, which is why the equation subtracts "
        "age from 140."
    ),
    "weight_crcl": (
        "Body weight in kg. **Which weight to use matters.** Cockcroft-Gault "
        "with *actual* body weight overestimates clearance in obesity, because "
        "fat contributes little to creatinine production. Many institutions "
        "use ideal body weight, or adjusted body weight when actual exceeds "
        "ideal by more than about 30%. This calculator uses whatever weight "
        "you enter — follow your own protocol."
    ),
    "scr": (
        "Serum creatinine, a breakdown product of muscle metabolism cleared by "
        "the kidneys. Typical range 0.6–1.2 mg/dL. It must be **stable** for "
        "this equation to be valid — in acute kidney injury, while creatinine "
        "is still rising or falling, the result is unreliable."
    ),
    "sex_crcl": (
        "Females are multiplied by 0.85 to account for lower average muscle "
        "mass, which produces less creatinine for the same kidney function."
    ),
    "volume": (
        "Total volume of fluid in the bag or syringe, in millilitres."
    ),
    "rate": (
        "How fast the fluid runs, in millilitres per hour — the number set on "
        "an infusion pump."
    ),
    "hours": (
        "How long the infusion should take, in hours."
    ),
    "drop_factor": (
        "How many drops make up 1 mL for that giving set — printed on the "
        "packet. A **macrodrip** set is 10, 15 or 20 gtt/mL and is used for "
        "routine adult fluids. A **microdrip** set is 60 gtt/mL and is used "
        "for paediatrics and for drugs needing fine control."
    ),
    "child_weight": (
        "The child's weight in kg. Weight-based dosing is the standard "
        "approach in paediatrics — always prefer it over the age-based "
        "historical rules where a mg/kg dose is published."
    ),
    "adult_dose": (
        "The usual adult dose of the drug, in mg. The historical rules scale "
        "this down to a child."
    ),
    "mg_per_kg": (
        "The published dose in mg per kg of body weight per day, from your "
        "formulary or the product literature."
    ),
    "divided": (
        "How many times a day the total is given. Three divided doses means "
        "one every 8 hours."
    ),
    "ordered_mg": (
        "The dose prescribed for the patient, in mg."
    ),
    "vial_mg": (
        "How many mg of drug the vial contains, from the label."
    ),
    "vial_ml": (
        "The volume in the vial after reconstitution, in mL. Read the "
        "reconstitution instructions — adding diluent to a powder changes the "
        "final volume."
    ),
    "height_cm": (
        "Standing height in centimetres."
    ),
    "weight_kg": (
        "Body weight in kilograms."
    ),
    "dose_per_m2": (
        "The published dose in mg per square metre of body surface area. "
        "Common for cytotoxics and some paediatric drugs, where BSA tracks "
        "metabolic rate better than weight alone."
    ),
    "sodium": (
        "Measured serum sodium in mEq/L. Normal 135–145. This calculation "
        "applies to **hypernatraemia**, where sodium is above target."
    ),
    "sex_tbw": (
        "Sex and age set the total body water fraction: 0.6 of body weight for "
        "adult males, 0.5 for adult females, and lower again in the elderly as "
        "lean mass falls."
    ),
    "age_group": (
        "Total body water falls with age. Child and adult male 0.6, adult "
        "female and elderly male 0.5, elderly female 0.45."
    ),

    # --- values the calculator returns ------------------------------------
    "out_crcl": (
        "Estimated creatinine clearance in mL/min — an estimate of kidney "
        "function used for **drug dose adjustment**. Most drug labels specify "
        "Cockcroft-Gault, which is why it is used here rather than eGFR."
    ),
    "out_renal_stage": (
        "A plain description of where this clearance falls. It describes the "
        "**calculated value**, and is not a formal chronic kidney disease "
        "stage — CKD staging is defined on eGFR, not on Cockcroft-Gault."
    ),
    "out_infusion_time": (
        "How long the bag will take to empty at the rate given."
    ),
    "out_pump_rate": (
        "The rate to set on the infusion pump, in mL per hour."
    ),
    "out_drip_rate": (
        "Drops per minute for a **manual** giving set with a roller clamp, "
        "where there is no pump. Count the drops in the chamber against a "
        "watch to set it."
    ),
    "out_daily_dose": (
        "The total amount of drug for the whole day, before dividing it into "
        "individual doses."
    ),
    "out_per_dose": (
        "The amount to give at each administration — the daily total divided "
        "by the number of doses."
    ),
    "out_child_dose": (
        "The scaled paediatric dose. These historical rules are useful for "
        "teaching and exams, but where a mg/kg or BSA-based dose is published, "
        "use that instead."
    ),
    "out_concentration": (
        "How many mg of drug are in each mL after reconstitution. This is the "
        "number that converts a dose in mg into a volume to draw up."
    ),
    "out_withdraw": (
        "The volume in mL to draw into the syringe to deliver the ordered dose."
    ),
    "out_vials": (
        "How many whole vials to open. Always rounded **up** — you cannot draw "
        "more than a vial holds."
    ),
    "out_bsa": (
        "Body surface area in m². Used for dosing where metabolic rate matters "
        "more than weight alone, such as cytotoxics. An average adult is "
        "around 1.7 m²."
    ),
    "out_bsa_dose": (
        "The total dose for this patient: the published mg/m² multiplied by "
        "their body surface area."
    ),
    "out_bmi": (
        "Weight divided by height squared. **Category thresholds differ by "
        "population** — this uses the WHO international cutoffs (overweight "
        "≥25, obese ≥30). South Asian criteria use lower thresholds "
        "(overweight ≥23, obese ≥27.5) because cardiometabolic risk rises at a "
        "lower BMI."
    ),
    "out_sodium_status": (
        "Hypernatraemia is a serum sodium above 145 mEq/L. Sources disagree on "
        "where 'moderate' and 'severe' begin — figures between 151 and 160 are "
        "all quoted — so only the well-agreed boundaries are shown. Severe "
        "symptoms typically appear above 160."
    ),
    "onset": (
        "**This changes the safe correction rate.** Acute hypernatraemia, "
        "developed within 24 hours, may be corrected faster because the brain "
        "has not yet generated protective osmolytes. Chronic, or of unknown "
        "duration, must be corrected slowly. **If in doubt, treat as chronic.**"
    ),
    "out_tbw": (
        "Estimated total body water in litres — the volume the sodium is "
        "dissolved in, and the basis for the deficit calculation."
    ),
    "out_deficit": (
        "How many litres of **electrolyte-free water** are needed to bring "
        "sodium back to 140. It is a starting estimate, not a prescription: it "
        "ignores ongoing losses and maintenance requirements."
    ),
}

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
    "Works on a phone. Tap any ⓘ for an explanation of that term."
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
st.sidebar.markdown("---")
st.sidebar.caption(
    "Also available: "
    "[Insulin Dose Calculator](https://insulin-calculator.streamlit.app) "
    "— TDD, basal/bolus, ICR, ISF and correction doses."
)


def explain(title, body):
    """Collapsed explanation shown under a result."""
    with st.expander(f"What this means — {title}"):
        st.markdown(body)


# --------------------------------------------------------------------------

if choice == "Creatinine clearance":
    st.subheader("Creatinine Clearance")
    st.caption("Cockcroft-Gault equation")

    col1, col2 = st.columns(2)
    age = col1.number_input("Age (years)", 1.0, 120.0, 60.0, step=1.0,
                            help=HELP["age"])
    weight = col2.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5,
                               help=HELP["weight_crcl"])
    scr = col1.number_input("Serum creatinine (mg/dL)", 0.1, 20.0, 1.2,
                            step=0.1, help=HELP["scr"])
    sex = col2.selectbox("Sex", ["Male", "Female"], help=HELP["sex_crcl"])

    crcl = f.creatinine_clearance(age, weight, scr, sex[0])
    stage = f.renal_function_stage(crcl)

    st.metric("Creatinine clearance", f"{crcl:.1f} mL/min", stage,
              delta_color="off", help=HELP["out_crcl"])
    if crcl < 60:
        st.warning("Renal dose adjustment may be required.")
    st.latex(r"CrCl = \frac{(140 - age) \times weight}{72 \times SCr}"
             r"\;\times\; 0.85 \text{ if female}")

    st.markdown("**Classification bands**")
    st.markdown(
        "| Interpretation | CrCl (mL/min) |\n|---|---|\n" + "\n".join(
            f"| {name}{' ←' if name == stage else ''} | {band} |"
            for name, band in f.CRCL_BANDS
        )
    )
    st.caption(
        "← marks this patient's band. These describe the calculated clearance "
        "and are not formal CKD stages — CKD staging is defined on eGFR, not "
        "on Cockcroft-Gault."
    )

    explain("creatinine clearance", """
Creatinine is produced steadily by muscle and cleared almost entirely by the
kidneys, so the amount left in the blood reflects how well they are filtering.

**Why this equation rather than eGFR.** Most drug labels and renal dosing tables
were written against Cockcroft-Gault, so using it keeps you consistent with the
source you are dosing from. eGFR (CKD-EPI) is what nephrology uses to stage
chronic kidney disease — a different question.

**Three things that make the result unreliable:**

- **Which weight you use.** With *actual* body weight the equation overestimates
  clearance in obesity, since fat produces little creatinine. Many institutions
  use ideal body weight, or adjusted body weight when actual exceeds ideal by
  more than about 30%. Follow your own protocol — this calculator uses the
  number you type in.
- **Unstable renal function.** The equation assumes creatinine is in steady
  state. During acute kidney injury, while it is still climbing, true clearance
  is already far worse than the calculated figure suggests.
- **Very low muscle mass.** In the frail elderly, amputees, or patients with
  muscle-wasting disease, creatinine is low because there is little muscle — not
  because the kidneys are working well. The result flatters them.

Below 60 mL/min, check every renally cleared drug on the chart. Below 30, expect
substantial adjustments and some outright contraindications.
    """)


elif choice == "IV infusion":
    st.subheader("IV Infusion")
    mode = st.radio(
        "Calculate",
        ["Infusion time", "Pump rate (mL/hr)", "Manual drip rate (gtt/min)"],
        horizontal=False,
    )
    col1, col2 = st.columns(2)

    if mode == "Infusion time":
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0,
                                   step=50.0, help=HELP["volume"])
        rate = col2.number_input("Rate (mL/hr)", 1.0, 1000.0, 125.0, step=5.0,
                                 help=HELP["rate"])
        hours = f.infusion_time_hours(volume, rate)
        st.metric("Infusion time",
                  f"{hours:.2f} hours",
                  f"{int(hours)} h {(hours % 1) * 60:.0f} min",
                  delta_color="off", help=HELP["out_infusion_time"])

    elif mode == "Pump rate (mL/hr)":
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0,
                                   step=50.0, help=HELP["volume"])
        hours = col2.number_input("Over how many hours", 0.25, 48.0, 8.0,
                                  step=0.25, help=HELP["hours"])
        st.metric("Pump rate",
                  f"{f.infusion_rate_ml_per_hr(volume, hours):.1f} mL/hr",
                  help=HELP["out_pump_rate"])

    else:
        volume = col1.number_input("Total volume (mL)", 1.0, 5000.0, 1000.0,
                                   step=50.0, help=HELP["volume"])
        hours = col2.number_input("Over how many hours", 0.25, 48.0, 8.0,
                                  step=0.25, help=HELP["hours"])
        drop_factor = st.selectbox(
            "Drop factor (gtt/mL)",
            [10, 15, 20, 60],
            index=1,
            help=HELP["drop_factor"],
        )
        rate = f.drip_rate_gtt_per_min(volume, drop_factor, hours)
        st.metric("Drip rate", f"{rate:.0f} gtt/min",
                  f"count {round(rate / 4)} drops in 15 seconds",
                  delta_color="off", help=HELP["out_drip_rate"])
        st.latex(r"gtt/min = \frac{volume \times drop\ factor}{time\ in\ minutes}")

    explain("IV infusion calculations", """
Three related questions, depending on what you already know:

- **Infusion time** — you have a bag and a rate, and want to know when it
  finishes.
- **Pump rate** — you have a bag and a time, and need the number to set on the
  pump. This is the everyday one.
- **Manual drip rate** — there is no pump, so the fluid runs by gravity through
  a roller clamp and you count drops.

**The drop factor is the part people get wrong.** It is printed on the giving
set packet and it is not universal. Macrodrip sets deliver 10, 15 or 20 drops
per mL; microdrip sets deliver 60 and are used in paediatrics and for drugs
needing fine control. Using the wrong figure changes the delivered rate by up to
six-fold.

The other classic error is forgetting that drip rate is **per minute** while the
prescription is in hours. The conversion is built into this calculator.

In practice, counting drops for a full minute is awkward, so the result also
tells you how many to count in 15 seconds.
    """)


elif choice == "Paediatric dose":
    st.subheader("Paediatric Dose")
    rule = st.radio("Method", ["mg/kg", "Clark's rule", "Young's rule"])
    col1, col2 = st.columns(2)

    if rule == "mg/kg":
        weight = col1.number_input("Child weight (kg)", 0.5, 100.0, 20.0,
                                   step=0.5, help=HELP["child_weight"])
        per_kg = col2.number_input("Dose (mg/kg/day)", 0.1, 500.0, 30.0,
                                   step=1.0, help=HELP["mg_per_kg"])
        divided = st.slider("Divided doses per day", 1, 6, 3,
                            help=HELP["divided"])
        per_dose, daily = f.mg_per_kg_dose(weight, per_kg, divided)
        col1.metric("Total daily dose", f"{daily:.0f} mg",
                    help=HELP["out_daily_dose"])
        col2.metric("Per dose", f"{per_dose:.1f} mg",
                    f"every {24 / divided:.0f} hours", delta_color="off",
                    help=HELP["out_per_dose"])

    elif rule == "Clark's rule":
        st.info("Historical rule — prefer mg/kg dosing where a paediatric dose "
                "is published.")
        weight = col1.number_input("Child weight (kg)", 0.5, 100.0, 20.0,
                                   step=0.5, help=HELP["child_weight"])
        adult = col2.number_input("Adult dose (mg)", 1.0, 5000.0, 500.0,
                                  step=50.0, help=HELP["adult_dose"])
        st.metric("Child dose", f"{f.clarks_rule(weight, adult):.1f} mg",
                  f"{weight * f.LB_PER_KG:.1f} lb / 150 lb", delta_color="off",
                  help=HELP["out_child_dose"])

    else:
        st.info("Historical rule — prefer mg/kg dosing where a paediatric dose "
                "is published.")
        age = col1.number_input("Child age (years)", 1.0, 12.0, 6.0, step=1.0,
                                help="Young's rule applies to ages 1–12.")
        adult = col2.number_input("Adult dose (mg)", 1.0, 5000.0, 500.0,
                                  step=50.0, help=HELP["adult_dose"])
        st.metric("Child dose", f"{f.youngs_rule(age, adult):.1f} mg",
                  help=HELP["out_child_dose"])
        st.caption("Young's rule applies to children aged 1-12 years.")

    explain("paediatric dosing", """
**mg/kg is the standard approach** and the one to use whenever a paediatric dose
is published. You take the dose per kilogram from the formulary, multiply by the
child's weight, and divide it across the day.

**Clark's and Young's rules are historical.** They scale an *adult* dose down
using weight or age, and they were designed for an era before paediatric dosing
was studied properly. They are still taught and still appear in exams, which is
why they are here — but they assume a child is simply a small adult, which is
not how drug handling works. Neonates and infants in particular differ in
absorption, distribution, hepatic metabolism and renal clearance in ways no
simple ratio captures.

If you have a published mg/kg dose, use it. Reach for these rules only when
nothing better exists, and treat the result as a rough ceiling rather than a
recommendation.

Two safety habits regardless of method: check the calculated dose against the
**maximum adult dose** — a large adolescent can compute to more than an adult
would receive — and check it against the **maximum daily dose** for that drug.
    """)


elif choice == "Vial dose (mg/mL)":
    st.subheader("Vial Dose")
    col1, col2, col3 = st.columns(3)
    ordered = col1.number_input("Dose ordered (mg)", 0.1, 10000.0, 750.0,
                                step=50.0, help=HELP["ordered_mg"])
    vial_mg = col2.number_input("Vial strength (mg)", 0.1, 10000.0, 500.0,
                                step=50.0, help=HELP["vial_mg"])
    vial_ml = col3.number_input("Vial volume (mL)", 0.1, 500.0, 10.0, step=1.0,
                                help=HELP["vial_ml"])

    conc = f.vial_concentration(vial_mg, vial_ml)
    volume = f.volume_for_dose(ordered, vial_mg, vial_ml)
    vials = f.vials_needed(ordered, vial_mg, vial_ml)

    col1.metric("Concentration", f"{conc:.1f} mg/mL",
                help=HELP["out_concentration"])
    col2.metric("Withdraw", f"{volume:.2f} mL", help=HELP["out_withdraw"])
    col3.metric("Vials needed", f"{vials}", help=HELP["out_vials"])
    st.info(f"Withdraw **{volume:.2f} mL** to give **{ordered:.0f} mg**. "
            f"Open **{vials}** vial(s).")

    explain("working from the vial", """
The vial gives you a **concentration** — mg per mL — and everything follows from
it:

1. Concentration = vial strength ÷ vial volume
2. Volume to draw up = dose ordered ÷ concentration
3. Vials to open = volume needed ÷ vial volume, **always rounded up**

The rounding is not arbitrary. If you need 15 mL from 10 mL vials, you open two
— there is no way to get 1.5 vials.

**The reconstitution trap.** For a powder vial, the final volume is not the
volume of diluent you added. The powder itself occupies space, so adding 10 mL
of water to a vial may give 10.5 mL of solution. The reconstitution instructions
state the resulting concentration or final volume — use that figure here, not
the diluent volume. Getting this wrong shifts every dose drawn from that vial.
    """)


elif choice == "Body surface area":
    st.subheader("Body Surface Area")
    st.caption("Mosteller formula")
    col1, col2 = st.columns(2)
    height = col1.number_input("Height (cm)", 30.0, 250.0, 170.0, step=1.0,
                               help=HELP["height_cm"])
    weight = col2.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5,
                               help=HELP["weight_kg"])

    bsa = f.bsa_mosteller(height, weight)
    st.metric("Body surface area", f"{bsa:.2f} m²", help=HELP["out_bsa"])
    st.latex(r"BSA = \sqrt{\frac{height_{cm} \times weight_{kg}}{3600}}")

    if st.checkbox("Calculate a dose from this BSA"):
        per_m2 = st.number_input("Dose ordered (mg/m²)", 0.1, 5000.0, 500.0,
                                 step=10.0, help=HELP["dose_per_m2"])
        st.metric("Total dose", f"{f.dose_from_bsa(per_m2, bsa):.1f} mg",
                  f"{per_m2:.0f} mg/m² × {bsa:.2f} m²", delta_color="off",
                  help=HELP["out_bsa_dose"])

    explain("body surface area", """
BSA tracks metabolic rate, cardiac output and renal blood flow better than body
weight alone, which is why it is the basis for **cytotoxic dosing** and for a
number of paediatric drugs.

The **Mosteller formula** used here is the one most commonly applied in
practice, chosen because it is simple enough to check by hand. Du Bois and
Haycock are alternatives and give slightly different values — a few percent
apart. That difference matters for a narrow-therapeutic-index cytotoxic, so use
whichever formula your protocol specifies rather than mixing them between
cycles.

An average adult is about 1.7 m². A rough sanity check: if a result comes out
far from that for an adult-sized patient, re-check the height units — entering
height in metres instead of centimetres is the usual cause.

Note that BSA dosing is itself debated for obese patients, where some protocols
cap the BSA used for calculation. Follow local guidance.
    """)


elif choice == "Body mass index":
    st.subheader("Body Mass Index")
    col1, col2 = st.columns(2)
    weight = col1.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5,
                               help=HELP["weight_kg"])
    unit = col2.radio("Height in", ["cm", "feet + inches"], horizontal=True)

    if unit == "cm":
        height_cm = col2.number_input("Height (cm)", 30.0, 250.0, 170.0,
                                      step=1.0, help=HELP["height_cm"])
    else:
        feet = col2.number_input("Feet", 1, 8, 5)
        inches = col2.number_input("Inches", 0.0, 11.5, 8.0, step=0.5)
        height_cm = f.feet_inches_to_cm(feet, inches)
        col2.caption(f"= {height_cm:.1f} cm")

    value = f.bmi(weight, height_cm)
    who_class = f.bmi_class(value)
    ap_class = f.bmi_class_asia_pacific(value)

    st.metric("BMI", f"{value:.1f} kg/m²", who_class,
              delta_color="off", help=HELP["out_bmi"])

    col1, col2 = st.columns(2)
    col1.markdown(f"**WHO international**  \n{who_class}")
    col2.markdown(f"**WHO Asia-Pacific**  \n{ap_class}")

    if who_class != ap_class:
        st.warning(
            f"The two classifications disagree: **{who_class}** by the WHO "
            f"international cut-offs, **{ap_class}** by the Asia-Pacific "
            "cut-offs. Asian populations carry higher cardiometabolic risk at "
            "the same BMI. Use whichever your service has adopted."
        )

    st.markdown("**Classification bands**")

    def band_table(bands, current):
        return (
            "| Category | BMI (kg/m²) |\n|---|---|\n"
            + "\n".join(
                f"| {name}{' ←' if name == current else ''} | {band} |"
                for name, band in bands
            )
        )

    col1, col2 = st.columns(2)
    col1.markdown("**WHO international**")
    col1.markdown(band_table(f.BMI_BANDS_WHO, who_class))
    col2.markdown("**WHO Asia-Pacific**")
    col2.markdown(band_table(f.BMI_BANDS_ASIA_PACIFIC, ap_class))

    st.caption(
        "← marks this patient's band on each scale. The two are shown "
        "separately because their structure differs: the Asia-Pacific "
        "classification has two obesity classes rather than three, and its "
        "boundaries do not line up with the international ones."
    )

    explain("body mass index", """
BMI is weight divided by height squared — a quick screen for whether body weight
is appropriate for height. It is a population measure applied to an individual,
so it comes with real limits.

**Why the obesity class matters, not just "obese".** Management is
class-dependent, so collapsing everything above 30 into one label loses the
information that drives the decision:

| Class | WHO international | What typically changes |
|---|---|---|
| Overweight | 25.0 – 29.9 | Lifestyle intervention; treat comorbidities |
| Obesity class I | 30.0 – 34.9 | Lifestyle plus pharmacotherapy considered; surgery considered where metabolic disease is present |
| Obesity class II | 35.0 – 39.9 | Metabolic and bariatric surgery recommended regardless of comorbidity |
| Obesity class III | ≥ 40.0 | Surgery recommended; higher perioperative risk |

The 2022 ASMBS/IFSO guidelines recommend metabolic and bariatric surgery at
**BMI ≥ 35 regardless of the presence or severity of obesity-related
conditions**, and say it should be considered at **BMI 30–34.9 with metabolic
disease** — with metabolic surgery endorsed from BMI 30 in type 2 diabetes.
These replaced the 1991 NIH criteria. Thresholds still vary between health
systems, so check what your service applies.

**The categories are not universal.** This calculator classifies using the WHO
international cut-offs, and shows the WHO Asia-Pacific classification (WPRO,
2000) alongside. The Asia-Pacific scale sets lower boundaries and has a
different structure — two obesity classes, not three — because Asian
populations carry a higher proportion of body fat and greater cardiometabolic
risk at any given BMI.

A patient at BMI 24 is **normal weight** internationally and **overweight** by
the Asia-Pacific classification. The same 2022 surgical guidelines adjust for
this, suggesting Asian patients be considered for surgery from **BMI 27.5**
rather than 35.

**What BMI cannot tell you.** It does not distinguish muscle from fat, so a
muscular person can classify as overweight while being perfectly healthy. It
does not account for fat distribution, and central obesity carries far more risk
than the same BMI distributed peripherally. It is also unreliable in pregnancy,
in the very elderly, and in patients with significant oedema or ascites, where
weight includes fluid rather than tissue.

For drug dosing, BMI is rarely the right input — ideal or adjusted body weight
usually is.
    """)


elif choice == "Free water deficit":
    st.subheader("Free Water Deficit")
    st.caption("For the hypernatraemic patient")
    col1, col2 = st.columns(2)
    weight = col1.number_input("Weight (kg)", 1.0, 300.0, 70.0, step=0.5,
                               help=HELP["weight_kg"])
    sodium = col2.number_input("Serum sodium (mEq/L)", 100.0, 200.0, 160.0,
                               step=1.0, help=HELP["sodium"])
    sex = col1.selectbox("Sex", ["Male", "Female"], help=HELP["sex_tbw"])
    group = col2.selectbox("Age group", ["Adult", "Elderly", "Child"],
                           help=HELP["age_group"])

    tbw = f.total_body_water(weight, group.lower(), sex[0])
    deficit = f.free_water_deficit(weight, sodium, group.lower(), sex[0])

    col1.metric("Total body water", f"{tbw:.1f} L", help=HELP["out_tbw"])
    col2.metric("Water deficit", f"{deficit:.2f} L", help=HELP["out_deficit"])

    status = f.sodium_status(sodium)
    if deficit > 0:
        st.metric("Serum sodium", f"{sodium:.0f} mEq/L", status,
                  delta_color="off", help=HELP["out_sodium_status"])

        onset_label = st.radio(
            "How long has the hypernatraemia been present?",
            ["Chronic or unknown duration", "Acute (developed within 24 hours)"],
            help=HELP["onset"],
        )
        onset = "acute" if onset_label.startswith("Acute") else "chronic"
        max_fall = f.max_sodium_fall_per_day(onset)
        target_24h = sodium - max_fall

        if onset == "chronic":
            st.warning(
                f"**Correct slowly.** Sodium should fall no faster than "
                f"**{max_fall:.0f} mEq/L in 24 hours** — aim for no lower than "
                f"about **{target_24h:.0f} mEq/L** by this time tomorrow, "
                "correcting fully over roughly 48 hours. The brain has "
                "generated protective osmolytes; lowering sodium faster than it "
                "can unload them causes cerebral oedema and seizures."
            )
        else:
            st.warning(
                f"**Acute hypernatraemia** may be corrected faster — up to "
                f"about **1–2 mEq/L per hour**, roughly {max_fall:.0f} mEq/L "
                "over 24 hours — because protective osmolytes have not yet "
                "formed. Only apply this if you are confident it developed "
                "within the last 24 hours. **If the duration is uncertain, "
                "treat it as chronic.**"
            )

        if sodium >= f.SODIUM_SEVERE_SYMPTOMS:
            st.error(
                f"Sodium {sodium:.0f} mEq/L — severe symptoms typically occur "
                "above 160. Escalate rather than managing this from a "
                "calculator."
            )
    else:
        st.info(f"{status}. Serum sodium is at or below the target used here, "
                "so the free water deficit formula does not apply.")

    explain("free water deficit", """
In hypernatraemia the problem is usually not too much sodium but **too little
water**. This estimates how many litres of electrolyte-free water are needed to
dilute the sodium back to 140 mEq/L.

The calculation runs in two steps: estimate total body water from weight and the
appropriate fraction, then work out how much extra water would bring the sodium
to target.

**The rate matters more than the volume.** Brain cells adapt to a high sodium by
generating osmolytes. Lower the sodium faster than they can unload those and
water rushes into the cells, causing cerebral oedema and seizures.

**How fast depends on how long it has been present:**

| Onset | Safe correction |
|---|---|
| **Acute** — developed within 24 hours | Up to about 1–2 mEq/L per hour, correcting over roughly 24 hours |
| **Chronic**, or of unknown duration | No more than 10–12 mEq/L in 24 hours, correcting over about 48 hours |

The distinction exists because protective osmolytes take days to accumulate. A
patient whose sodium rose in the last few hours has not yet formed them and
tolerates faster correction; one who has been hypernatraemic for a week has, and
does not. **When the duration is uncertain, treat it as chronic** — the cost of
correcting an acute case too slowly is far lower than the cost of correcting a
chronic one too fast.

**On severity.** Hypernatraemia is a sodium above 145 mEq/L. Where "moderate"
and "severe" begin is genuinely disputed — different sources place the severe
threshold anywhere from 152 to 160 — so this calculator reports only the agreed
definition and flags 160, above which severe symptoms typically appear.

**What this figure does not include:**

- **Ongoing losses** — urine, gastrointestinal, insensible. A patient in
  diabetes insipidus can lose several litres a day while you are replacing the
  deficit, so replacement must exceed the deficit alone.
- **Maintenance requirements** for the same period.
- **The choice of fluid.** The deficit is in *free water*. If you give 5%
  dextrose, the volume matches; if you give 0.45% saline, only about half of
  each litre counts as free water.

Treat the result as a starting estimate that guides a plan, then follow the
sodium with repeat measurements every few hours and adjust.
    """)


st.markdown("---")
st.caption(
    "For educational and reference use only. Not a substitute for clinical "
    "judgement or your institutional protocol."
)
