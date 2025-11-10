Cinematic LUT Generator (Python)
=================================
A simple project that extracts a frame from a video or image, computes a dominant color palette, and generates a demo 3D LUT (.cube) file.

How to run:
1. (Optional) place a sample video at samples/sample_video.mp4 or upload via Streamlit.
2. Install dependencies: pip install -r requirements.txt
3. Run the Streamlit app: streamlit run app.py
4. Or run demo: python main.py

Notes:
- This is a demonstration implementation. The LUT generation uses a lightweight heuristic shift based on the dominant color.
- For production/accurate LUTs, consider 3D color mapping techniques and advanced color science libraries.
