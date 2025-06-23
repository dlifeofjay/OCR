import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re
import pytesseract
import cv2
from pdf2image import convert_from_bytes
from PIL import Image

st.set_page_config(page_title="Invoice Extractor Pro", page_icon="📄")
st.title("📄 Invoice Extractor Pro")

EXCEL_FILE = "invoice.xlsx"

# OCR + Preprocessing
def preprocess_image(image_bytes):
    image_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

def extract_text(img):
    return pytesseract.image_to_string(img, config="--psm 6")

def parse_fields(text):
    def get(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else np.nan

    return {
        "Invoice No": get(r"Invoice No[:\s]*([A-Z0-9-]+)"),
        "Date": get(r"Date[:\s]*([\d/\-]+)"),
        "Billed To": get(r"Billed To[:\s]*(.+)"),
        "Address": get(r"Address[:\s]*(.+)"),
        "Item": get(r"Item[:\s]*(.+)"),
        "Amount": get(r"Amount[:\s]*([\d,.]+)")
    }

uploaded_file = st.file_uploader("📎 Upload an invoice (PDF or Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    extracted_rows = []
    full_text_log = []

    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(file_bytes)
        for i, page in enumerate(pages):
            buf = io.BytesIO()
            page.save(buf, format="PNG")
            img = preprocess_image(buf.getvalue())
            text = extract_text(img)
            parsed = parse_fields(text)
            extracted_rows.append(parsed)
            full_text_log.append((f"Page {i+1}", text))
    else:
        img = preprocess_image(file_bytes)
        text = extract_text(img)
        parsed = parse_fields(text)
        extracted_rows.append(parsed)
        full_text_log.append(("Image", text))

    st.subheader("🔍 Extracted Invoice Fields")
    for i, row in enumerate(extracted_rows):
        label = f"Page {i+1}" if uploaded_file.type == "application/pdf" else "Invoice Image"
        st.markdown(f"**🧾 {label}**")
        for key, val in row.items():
            st.write(f"**{key}:** {val}")

    if st.button("✅ Yes, Save to Excel"):
        new_df = pd.DataFrame(extracted_rows)
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=new_df.columns)

        combined = pd.concat([existing_df, new_df], ignore_index=True)
        combined.to_excel(EXCEL_FILE, index=False)
        st.success("📥 Invoice data saved to Excel.")

        with open(EXCEL_FILE, "rb") as f:
            st.download_button(
                label="⬇️ Download invoice.xlsx",
                data=f,
                file_name="invoice.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.subheader("📜 Full OCR Extracted Text")
    for label, text in full_text_log:
        with st.expander(f"📄 {label} Text"):
            st.text(text)
