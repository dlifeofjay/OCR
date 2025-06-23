import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import pandas as pd
import os

# 🔧 Preprocess image before OCR
def preprocess_image(image_bytes):
    image_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

# 🔍 Extract text using pytesseract
def extract_text(img):
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"OCR failed: {e}"

# 📥 Parse invoice fields from extracted text
def parse_fields(text):
    fields = {}
    inv = re.search(r'Invoice No[:\s]*([A-Z0-9-]+)', text, re.IGNORECASE)
    dt = re.search(r'Date[:\s]*([\d/\-]+)', text)
    billed_to = re.search(r'Billed To[:\s]*(.*)', text)
    address = re.search(r'Address[:\s]*(.*)', text)
    item = re.search(r'Item[:\s]*(.*)', text)
    amount = re.search(r'Amount[:\s]*([\d,.]+)', text)

    fields['Invoice No'] = inv.group(1) if inv else np.nan
    fields['Date'] = dt.group(1) if dt else np.nan
    fields['Billed To'] = billed_to.group(1) if billed_to else np.nan
    fields['Address'] = address.group(1) if address else np.nan
    fields['Item'] = item.group(1) if item else np.nan
    fields['Amount'] = amount.group(1) if amount else np.nan

    return fields

# 💾 Generate a downloadable Excel file for just one invoice
def generate_excel(data, filename='invoice.xlsx'):
    df = pd.DataFrame([data])
    df.to_excel(filename, index=False)

# 🖥️ Streamlit interface
st.set_page_config(page_title="Invoice Extractor", page_icon="📄")
st.title("📄 Invoice Data Extractor")

uploaded_file = st.file_uploader("Upload an invoice image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Invoice", use_column_width=True)
    st.write("🔄 Processing image...")

    img_bytes = uploaded_file.read()
    processed_img = preprocess_image(img_bytes)
    ocr_text = extract_text(processed_img)
    extracted_fields = parse_fields(ocr_text)

    st.subheader("📋 Extracted Invoice Info")
    for label, value in extracted_fields.items():
        st.markdown(f"**{label}:** {value}")

    confirm = st.checkbox("✅ I confirm the extracted details are correct and I want to download this invoice")

    if confirm:
        generate_excel(extracted_fields, "invoice.xlsx")
        st.success("📄 Invoice prepared successfully!")

        with open("invoice.xlsx", "rb") as file:
            st.download_button("⬇️ Download This Invoice", file, file_name="invoice.xlsx")
    else:
        st.info("👀 Please confirm the details above before downloading.")

    with st.expander("📜 View Full OCR Text"):
        st.text(ocr_text)
