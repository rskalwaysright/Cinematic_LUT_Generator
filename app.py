import streamlit as st
import os
import numpy as np
from PIL import Image
from color_analysis import extract_palette, visualize_palette
from lut_generator import generate_cube_lut

# -----------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------
st.set_page_config(
    page_title="🎬 Cinematic LUT Generator & Preview",
    page_icon="🎨",
    layout="wide"
)

st.title("🎬 Cinematic LUT Generator & Application Preview")
st.markdown("""
Upload a **cinematic frame** to generate a LUT and palette,  
then upload another **test image** to preview how that LUT changes its colors.
""")

# -----------------------------------------------------------
# Ensure folders exist
# -----------------------------------------------------------
os.makedirs("samples", exist_ok=True)
os.makedirs("output", exist_ok=True)

# -----------------------------------------------------------
# Sidebar Controls
# -----------------------------------------------------------
st.sidebar.header("🎛 Color Adjustment Controls")

tint_strength = st.sidebar.slider("Tint Intensity", 0.0, 2.0, 0.75, 0.05)
gamma_curve = st.sidebar.slider("Gamma Curve (Contrast)", 0.5, 1.5, 0.9, 0.05)
lut_size = st.sidebar.selectbox("LUT 3D Grid Size", [17, 33, 65], index=0)
preview_intensity = st.sidebar.slider("Preview Intensity", 0.0, 1.0, 1.0, 0.05)

st.sidebar.info("💡 Adjust these before generating your LUT.")

# -----------------------------------------------------------
# SECTION 1: Generate LUT from cinematic reference
# -----------------------------------------------------------
st.header("🎞 Step 1 – Upload Cinematic Reference Frame")

uploaded_ref = st.file_uploader("📁 Upload cinematic reference (JPG/PNG)", type=["jpg", "jpeg", "png"], key="ref")

lut_generated = False
colors = None
shift = None

if uploaded_ref:
    ref_path = os.path.join("samples", uploaded_ref.name)
    with open(ref_path, "wb") as f:
        f.write(uploaded_ref.read())

    ref_img = Image.open(ref_path).convert("RGB")
    st.image(ref_img, caption="🎞 Reference Image", use_container_width=True)

    st.info("Analyzing reference colors and generating LUT...")

    colors = extract_palette(ref_path, n_colors=8)
    palette_path = os.path.join("output", f"{os.path.splitext(uploaded_ref.name)[0]}_palette.png")
    lut_path = os.path.join("output", f"{os.path.splitext(uploaded_ref.name)[0]}_cinematic.cube")
    visualize_palette(colors, save_path=palette_path)

    dominant = colors[0] / 255.0
    shift = (dominant - np.array([0.5, 0.5, 0.5])) * tint_strength

    # Write LUT
    with open(lut_path, 'w') as f:
        f.write('# Cinematic LUT Generator\n')
        f.write(f'# Tint Strength={tint_strength}, Gamma={gamma_curve}\n')
        f.write(f'LUT_3D_SIZE {lut_size}\n')
        for b in range(lut_size):
            for g in range(lut_size):
                for r in range(lut_size):
                    rf, gf, bf = r/(lut_size-1), g/(lut_size-1), b/(lut_size-1)
                    out = np.array([rf, gf, bf])
                    out = np.power(out, gamma_curve)
                    out = out + shift
                    out = np.clip(out, 0.0, 1.0)
                    f.write(f"{out[0]:.6f} {out[1]:.6f} {out[2]:.6f}\n")

    st.success("✅ LUT generated successfully.")
    st.image(palette_path, caption="Extracted Palette", use_container_width=False, width=400)
    lut_generated = True

# -----------------------------------------------------------
# SECTION 2: Apply that LUT to another image (simulation)
# -----------------------------------------------------------
st.header("🧩 Step 2 – Test LUT on Another Image")

uploaded_test = st.file_uploader("📁 Upload test image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="test")

def apply_lut_simulation(image_array, gamma, shift, intensity):
    img = np.asarray(image_array) / 255.0
    img = np.power(img, gamma)
    img = img + shift * intensity
    img = np.clip(img, 0, 1)
    return (img * 255).astype(np.uint8)

if uploaded_test:
    if not lut_generated or shift is None:
        st.warning("⚠️ Please generate a LUT first by uploading a cinematic reference image above.")
    else:
        test_path = os.path.join("samples", uploaded_test.name)
        with open(test_path, "wb") as f:
            f.write(uploaded_test.read())

        test_img = Image.open(test_path).convert("RGB")
        test_array = np.array(test_img)
        after_img = apply_lut_simulation(test_array, gamma_curve, shift, preview_intensity)

        col1, col2 = st.columns(2)
        with col1:
            st.image(test_array, caption="Before (Original)", use_container_width=True)
        with col2:
            st.image(after_img, caption="After (LUT Simulation)", use_container_width=True)

        st.success("✅ LUT successfully applied for preview.")
