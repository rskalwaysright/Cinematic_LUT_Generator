# app.py — Cinematic LUT Generator
import streamlit as st
import os, io, time, tempfile
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
from color_analysis import extract_palette, visualize_palette
from lut_generator import generate_cube_lut

# ---------------- Streamlit Config ----------------
st.set_page_config(
    page_title="Cinematic LUT Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%);
        color: #e6eef8;
        font-family: 'Segoe UI', sans-serif;
    }
    .title {
        font-size: 36px; font-weight: 700; color: #ffd166;
    }
    .muted { color: #a8b3c7; }
    .section {
        background: rgba(255,255,255,0.03);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar Controls ----------------
st.sidebar.header("🎚 Controls & Navigation")
page = st.sidebar.radio("Go to", ["Generate LUT", "Apply LUT", "Presets", "Help"])

st.sidebar.markdown("---")
lut_size = st.sidebar.selectbox("LUT 3D Size", [17, 33, 65], index=0)
tint_strength = st.sidebar.slider("Tint Strength", 0.0, 2.0, 1.0, 0.05)
gamma_curve = st.sidebar.slider("Gamma / Tone Curve", 0.6, 1.6, 1.0, 0.01)
preview_intensity = st.sidebar.slider("Preview Intensity", 0.0, 1.0, 0.7, 0.05)

st.sidebar.markdown("---")
st.sidebar.info("Developed by **Reddy Sujith Kumar (2024BCS0280)**")
st.sidebar.markdown("GitHub: [rskalwaysright/Cinematic_LUT_Generator](https://github.com/rskalwaysright/Cinematic_LUT_Generator)")

WORKDIR = Path(tempfile.gettempdir()) / "cinematic_lut_app"
WORKDIR.mkdir(parents=True, exist_ok=True)

def save_uploaded(file, dest):
    with open(dest, "wb") as f:
        f.write(file.read())
    return dest

def pil_to_bytes(img: Image.Image, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf

# ---------------- Generate LUT ----------------
if page == "Generate LUT":
    st.markdown("<div class='title'>🎨 Generate Cinematic LUT</div>", unsafe_allow_html=True)
    st.markdown("<div class='section'>Upload a cinematic reference frame. The app extracts dominant colors and generates a .cube LUT file with a color palette preview.</div>", unsafe_allow_html=True)

    uploaded_ref = st.file_uploader("Upload Reference Image", type=["jpg", "jpeg", "png"], key="ref")

    if uploaded_ref:
        ref_path = WORKDIR / f"ref_{int(time.time())}_{uploaded_ref.name}"
        save_uploaded(uploaded_ref, ref_path)
        st.image(ref_path, caption="Uploaded Reference Frame", use_container_width=True)

        with st.spinner("Analyzing colors & generating LUT..."):
            try:
                colors = extract_palette(str(ref_path), n_colors=8)
                preview_path = WORKDIR / f"palette_{ref_path.stem}.png"
                lut_path = WORKDIR / f"{ref_path.stem}.cube"

                visualize_palette(colors, save_path=str(preview_path))
                generate_cube_lut(colors, size=lut_size, output_path=str(lut_path))

                st.session_state["lut_colors"] = colors
                st.session_state["lut_path"] = str(lut_path)
                st.session_state["preview_path"] = str(preview_path)

                st.success("✅ LUT generated successfully!")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(str(preview_path), caption="Extracted Palette", use_container_width=True)
                with col2:
                    with open(lut_path, "rb") as f:
                        st.download_button("⬇️ Download .cube LUT", f, file_name=f"{ref_path.stem}.cube", mime="text/plain")
                    with open(preview_path, "rb") as f:
                        st.download_button("🖼 Download Palette Image", f, file_name=f"{preview_path.name}", mime="image/png")

            except Exception as e:
                st.error(f"Error generating LUT: {e}")

# ---------------- Apply LUT ----------------
elif page == "Apply LUT":
    st.markdown("<div class='title'>🧪 Apply LUT to Image</div>", unsafe_allow_html=True)
    st.markdown("<div class='section'>Upload an image to simulate the cinematic LUT effect using your generated color palette.</div>", unsafe_allow_html=True)

    if "lut_colors" not in st.session_state:
        st.warning("Please generate a LUT first under 'Generate LUT'.")
    else:
        uploaded_test = st.file_uploader("Upload Test Image", type=["jpg", "jpeg", "png"], key="test")

        if uploaded_test:
            test_path = WORKDIR / f"test_{int(time.time())}_{uploaded_test.name}"
            save_uploaded(uploaded_test, test_path)
            original = Image.open(test_path).convert("RGB")
            arr = np.asarray(original).astype(np.float32) / 255.0

            colors = st.session_state["lut_colors"]
            dominant = colors[0] / 255.0
            shift = (dominant - np.array([0.5, 0.5, 0.5])) * tint_strength

            arr_gamma = np.power(arr, gamma_curve)
            arr_out = np.clip(arr_gamma + shift * preview_intensity, 0.0, 1.0)
            processed = (arr_out * 255).astype(np.uint8)

            col1, col2 = st.columns(2)
            with col1:
                st.image(original, caption="Before (Original)", use_container_width=True)
            with col2:
                st.image(processed, caption="After (Cinematic LUT Applied)", use_container_width=True)

            out_img = Image.fromarray(processed)
            st.download_button("⬇️ Download Processed Image", pil_to_bytes(out_img), file_name=f"processed_{uploaded_test.name}", mime="image/png")

# ---------------- Preset LUT Styles ----------------
elif page == "Presets":
    st.markdown("<div class='title'>🎞 Preset Looks</div>", unsafe_allow_html=True)
    presets = {
        "Teal & Orange": {"tint": 1.1, "gamma": 0.95, "intensity": 0.75},
        "Vintage Warm": {"tint": 1.25, "gamma": 1.05, "intensity": 0.6},
        "Noir (Cool Desat)": {"tint": 0.7, "gamma": 0.9, "intensity": 0.65},
        "Film Bleach Bypass": {"tint": 1.4, "gamma": 0.92, "intensity": 0.85}
    }

    preset = st.selectbox("Select Preset", ["-- Choose --"] + list(presets.keys()))
    if preset != "-- Choose --":
        p = presets[preset]
        st.success(f"Preset '{preset}' selected!")
        st.markdown(f"""
        - Tint: `{p['tint']}`
        - Gamma: `{p['gamma']}`
        - Intensity: `{p['intensity']}`
        """)
        st.info("Adjust sidebar sliders using these preset values for quick cinematic LUT generation.")

# ---------------- Help Page ----------------
elif page == "Help":
    st.markdown("<div class='title'>❓ Help & Info</div>", unsafe_allow_html=True)
    st.markdown("""
    **Workflow**
    1. Generate LUT → Upload reference image → Download `.cube` and palette
    2. Apply LUT → Upload test image → See cinematic transformation
    3. Presets → Use predefined tone styles

    **Deployment**
    - Optimized for `opencv-python-headless`
    - Ensure `requirements.txt` is pinned
    - Runs on Streamlit Cloud

    **Credits**
    Created by *Reddy Sujith Kumar (2024BCS0280)*  
    GitHub: [rskalwaysright/Cinematic_LUT_Generator](https://github.com/rskalwaysright/Cinematic_LUT_Generator)
    """)

# ---------------- Footer ----------------
st.markdown(
    "<p style='text-align:center; color:#8ea0b8; font-size:12px;'>© 2025 Cinematic LUT Studio — Powered by Streamlit</p>",
    unsafe_allow_html=True
)
