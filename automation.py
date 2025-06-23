import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import pytesseract
import cv2
from pdf2image import convert_from_bytes
from PIL import Image

st.set_page_config(page_title="Invoice Extractor Pro", page_icon="📄")

st.title("📄 Invoice Data Extractor")
st.write("Upload an invoice to extract key fields and download as CSV")

DATA_FILE = "invoice_data.csv"

# OCR + Preprocessing
def preprocess_image(image_bytes):
    image_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

def extract_text(img):
    return pytesseract.image_to_string(img, config='--psm 6')

def parse_fields(text):
    def get(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else np.nan

    return {
        'Invoice No': get(r'Invoice No[:\s]*([A-Z0-9-]+)'),
        'Date': get(r'Date[:\s]*([\d/\-]+)'),
        'Billed To': get(r'Billed To[:\s]*(.+)'),
        'Address': get(r'Address[:\s]*(.+)'),
        'Item': get(r'Item[:\s]*(.+)'),
        'Amount': get(r'Amount[:\s]*([\d,.]+)'),
        'Timestamp': datetime.now()
    }

# Load existing or create empty DataFrame
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Invoice No', 'Date', 'Billed To', 'Address', 'Item', 'Amount', 'Timestamp'])

uploaded_file = st.file_uploader("📎 Upload invoice (PDF or image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    extracted_data = []

    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(file_bytes)
        for page in pages:
            img_buf = io.BytesIO()
            page.save(img_buf, format="PNG")
            img = preprocess_image(img_buf.getvalue())
            text = extract_text(img)
            extracted_data.append(parse_fields(text))
    else:
        img = preprocess_image(file_bytes)
        text = extract_text(img)
        extracted_data.append(parse_fields(text))

    # Show predictions
    for i, data in enumerate(extracted_data):
        st.markdown(f"### 📋 Invoice {i+1}")
        for key, val in data.items():
            st.write(f"**{key}**: {val}")

        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Invoices processed and saved!")

if st.checkbox("📊 Show extracted data"):
    st.dataframe(df)

if st.button("⬇️ Download All as CSV"):
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    st.download_button("Download CSV", csv_io.getvalue(), file_name="invoice_data.csv", mime="text/csv")
