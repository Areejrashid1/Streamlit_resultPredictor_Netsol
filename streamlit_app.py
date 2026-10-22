import os

import joblib
import numpy as np
import streamlit as st

# Path to the model, relative to this file (works locally and on Streamlit Cloud)
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")


@st.cache_resource
def load_model():
    """Load the trained model once and reuse it."""
    return joblib.load(MODEL_PATH)


st.set_page_config(
    page_title="Student Predictor",
    page_icon="🎓",
    layout="centered"
)
st.title("🎓 Student Pass / Fail Predictor")
st.markdown("Enter the student's details below to predict their result.")
st.markdown("---")


col1, col2 = st.columns(2)

with col1:
    study_hours = st.slider(
        label="Study Hours Per Day",
        min_value=0.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        help="How many hours the student studies each day"
    )

with col2:
    prev_score = st.slider(
        label="Previous Exam Score",
        min_value=0.0,
        max_value=100.0,
        value=60.0,
        step=1.0,
        help="Score from the most recent exam (out of 100)"
    )

st.markdown("---")


if st.button("🔮 Predict Result", use_container_width=True):
    try:
        # Load the model directly (no FastAPI needed)
        model = load_model()

        # Build the input the model expects: [[study_hours, prev_score]]
        input_data = np.array([[study_hours, prev_score]])

        prediction = int(model.predict(input_data)[0])
        probabilities = model.predict_proba(input_data)[0]
        confidence = round(float(probabilities[prediction]), 3)

        result = {
            "prediction": prediction,
            "result_label": "Pass" if prediction == 1 else "Fail",
            "confidence": confidence,
        }

        # Display the result prominently
        if result["prediction"] == 1:
            st.success(f"✅ Prediction: **{result['result_label']}**")
        else:
            st.error(f"❌ Prediction: **{result['result_label']}**")

        # Show confidence
        st.metric(
            label="Model Confidence",
            value=f"{result['confidence'] * 100:.1f}%"
        )

        # Show the data that went into the model
        with st.expander("See what went into the model"):
            st.json({
                "study_hours": study_hours,
                "prev_score": prev_score
            })

            st.json(result)

    except FileNotFoundError:
        st.error("model.pkl not found. Make sure it is in the same folder as this file.")
    except Exception as e:
        st.error(f"Something went wrong while predicting: {e}")

# This updates live as the user moves the sliders — no button click needed
st.markdown("---")
st.subheader("Current Input Summary")
m1, m2 = st.columns(2)
m1.metric("Study Hours", f"{study_hours} hrs/day")
m2.metric("Previous Score", f"{prev_score}/100")