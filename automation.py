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
        return match.group(1).strip() if match else ""
    return {
        "Invoice No": get(r"Invoice No[:\s]*([A-Z0-9-]+)"),
        "Date": get(r"Date[:\s]*([\d/\-]+)"),
        "Billed To": get(r"Billed To[:\s]*(.+)"),
        "Address": get(r"Address[:\s]*(.+)"),
        "Item": get(r"Item[:\s]*(.+)"),
        "Amount": get(r"Amount[:\s]*([\d,.]+)")
    }

uploaded_file = st.file_uploader("📎 Upload an invoice (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    extracted_rows = []
    full_texts = []

    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(file_bytes)
        for i, page in enumerate(pages):
            buf = io.BytesIO()
            page.save(buf, format="PNG")
            img = preprocess_image(buf.getvalue())
            text = extract_text(img)
            row = parse_fields(text)
            extracted_rows.append(row)
            full_texts.append((f"Page {i+1}", text))
    else:
        img = preprocess_image(file_bytes)
        text = extract_text(img)
        row = parse_fields(text)
        extracted_rows.append(row)
        full_texts.append(("Image", text))

    st.subheader("🧾 Review & Edit Invoice Data")
    final_rows = []
    for i, row in enumerate(extracted_rows):
        label = f"Page {i+1}" if uploaded_file.type == "application/pdf" else "Invoice Image"
        with st.form(f"form_{i}"):
            st.markdown(f"**🔍 {label}**")
            updated = {}
            for key, val in row.items():
                updated[key] = st.text_input(f"{key}", value=val, key=f"{key}_{i}")
            submitted = st.form_submit_button("✅ Confirm This Entry")
            if submitted:
                st.success("Entry confirmed.")
                final_rows.append(updated)

    if final_rows:
        new_df = pd.DataFrame(final_rows)
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=new_df.columns)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_excel(EXCEL_FILE, index=False)
        st.success("📦 Data saved to invoice.xlsx")

        with open(EXCEL_FILE, "rb") as f:
            st.download_button(
                label="⬇️ Download invoice.xlsx",
                data=f,
                file_name="invoice.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.subheader("📜 Full OCR Extracted Text")
    for label, text in full_texts:
        with st.expander(f"📄 {label} Text"):
            st.text(text)
