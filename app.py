import streamlit as st
import easyocr
import numpy as np
import cv2
from PIL import Image
import json

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI OCR App",
    page_icon="🤖",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
}
.sub-text {
    text-align: center;
    color: gray;
    margin-bottom: 20px;
}
[data-testid="stFileUploader"] {
    border: 2px dashed #4CAF50;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<p class="main-title">🤖 Smart OCR App</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Upload → Detect → Extract → Download</p>', unsafe_allow_html=True)

st.divider()

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Settings")

language = st.sidebar.selectbox(
    "🌍 Select Language",
    ["English", "English + Hindi"]
)

lang_map = {
    "English": ['en'],
    "English + Hindi": ['en', 'hi']
}

show_boxes = st.sidebar.checkbox("📦 Show Bounding Boxes", value=True)

# ------------------ DRAG & DROP ------------------
st.markdown("### 📤 Upload Your Image")

uploaded_file = st.file_uploader(
    "Drag & drop or click to upload",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed"
)

st.caption("Supported formats: JPG, PNG")

# ------------------ FUNCTION TO FIX JSON ERROR ------------------
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    return obj

# ------------------ PROCESS ------------------
if uploaded_file:

    col1, col2 = st.columns(2)

    # Original Image
    with col1:
        image = Image.open(uploaded_file)
        st.subheader("🖼 Original Image")
        st.image(image, width="stretch")

    img = np.array(image)

    # OCR Processing
    with st.spinner("🔍 Processing OCR..."):
        reader = easyocr.Reader(lang_map[language])
        results = reader.readtext(img)

    extracted_text = ""
    img_copy = img.copy()

    # Process Results
    for (bbox, text, prob) in results:
        extracted_text += text + " "

        if show_boxes:
            (top_left, top_right, bottom_right, bottom_left) = bbox

            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            cv2.rectangle(img_copy, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(
                img_copy,
                text,
                top_left,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

    # Detected Image
    with col2:
        st.subheader("📍 Detected Text")
        st.image(img_copy, width="stretch")

    st.divider()

    # Extracted Text
    st.subheader("📌 Extracted Text")
    st.text_area("Result", extracted_text, height=200)

    # ------------------ CLEAN JSON FORMAT ------------------
    formatted_results = [
        {
            "text": r[1],
            "confidence": float(r[2])
        }
        for r in results
    ]

    # Downloads
    col3, col4 = st.columns(2)

    with col3:
        st.download_button(
            "📥 Download TXT",
            data=extracted_text,
            file_name="output.txt"
        )

    with col4:
        st.download_button(
            "📥 Download JSON",
            data=json.dumps(formatted_results, indent=2, default=convert_numpy),
            file_name="output.json"
        )

else:
    st.info("👆 Drag & drop an image to start OCR")