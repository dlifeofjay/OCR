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

# --- OCR Preprocessing ---
def preprocess_image(image_bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

def extract_text(img):
    return pytesseract.image_to_string(img, config="--psm 6")

# --- Field Parser ---
def parse_fields(text):
    def get(pattern, group=1):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(group).strip() if match else ""
    return {
        "Invoice No": get(r"Invoice No[:\s]*([A-Z0-9-]+)"),
        "Date": get(r"Date[:\s]*([\d/\-]+)"),
        "Billed To": get(r"Billed To[:\s]*(.+)"),
        "Address": get(r"Address[:\s]*(.+)"),
        "Item": get(r"Item[:\s]*(.+)"),
        "Amount": get(r"(Total|Amount)[^\d]*([\d,]+\.?\d*)", group=2)
    }

# --- File Upload ---
uploaded_file = st.file_uploader("📎 Upload Invoice (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

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
            full_texts.append((f"Page {i+1}", text))
            extracted_rows.append(parse_fields(text))
    else:
        img = preprocess_image(file_bytes)
        text = extract_text(img)
        full_texts.append(("Image", text))
        extracted_rows.append(parse_fields(text))

    # --- Editable Forms for Each Page/Image ---
    st.subheader("🔍 Review & Edit Invoice Data")
    confirmed_rows = []
    for i, row in enumerate(extracted_rows):
        label = f"Page {i+1}" if uploaded_file.type == "application/pdf" else "Invoice Image"
        with st.form(f"form_{i}"):
            st.markdown(f"**📝 {label}**")
            edited = {}
            for key, value in row.items():
                edited[key] = st.text_input(f"{key}", value=value, key=f"{key}_{i}")
            if st.form_submit_button("✅ Confirm This Invoice"):
                confirmed_rows.append(edited)
                st.success(f"{label} confirmed!")

    # --- Save & Download ---
    if confirmed_rows:
        new_df = pd.DataFrame(confirmed_rows)
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=new_df.columns)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save to Excel
        excel_buf = io.BytesIO()
        combined_df.to_excel(excel_buf, index=False, engine="openpyxl")
        excel_buf.seek(0)
        with open(EXCEL_FILE, "wb") as f:
            f.write(excel_buf.getvalue())

        st.success("✅ Data saved to invoice.xlsx")

        # Download Button
        st.download_button(
            label="⬇️ Download invoice.xlsx",
            data=excel_buf,
            file_name="invoice.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --- Full OCR Text ---
    st.subheader("📜 Full OCR Text")
    for label, text in full_texts:
        with st.expander(f"📄 {label} Text"):
            st.text(text)
