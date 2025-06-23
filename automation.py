import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import pandas as pd
import os
import io
from pdf2image import convert_from_bytes
from PIL import Image

# 🔧 Preprocess image for OCR
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

# 📥 Parse invoice fields
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

# 💾 Export to Excel
def generate_excel(data, filename='invoice.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# 🖥️ Streamlit UI
st.set_page_config(page_title="Invoice Extractor Pro", page_icon="📑")
st.title("📑 Multi-format Invoice Extractor")

uploaded_file = st.file_uploader("Upload a JPG/PNG image or PDF invoice", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    st.write("🔄 Processing file...")
    extracted_data = []
    full_text = ""

    if uploaded_file.type == "application/pdf":
        images = convert_from_bytes(uploaded_file.read())
        for i, page_img in enumerate(images):
            img_byte_arr = io.BytesIO()
            page_img.save(img_byte_arr, format='PNG')
            processed_img = preprocess_image(img_byte_arr.getvalue())
            ocr_text = extract_text(processed_img)
            fields = parse_fields(ocr_text)
            extracted_data.append(fields)
            full_text += f"\n--- Page {i+1} ---\n{ocr_text}"
    else:
        img_bytes = uploaded_file.read()
        processed_img = preprocess_image(img_bytes)
        ocr_text = extract_text(processed_img)
        fields = parse_fields(ocr_text)
        extracted_data.append(fields)
        full_text = ocr_text

    st.subheader("📋 Extracted Invoice Info")
    for i, invoice in enumerate(extracted_data):
        st.markdown(f"### Invoice {i+1}")
        for label, value in invoice.items():
            st.markdown(f"**{label}:** {value}")

    if st.button("✅ Confirm & Download All"):
        generate_excel(extracted_data, "invoices.xlsx")
        st.success("✅ Invoice file ready!")

        with open("invoices.xlsx", "rb") as file:
            st.download_button("⬇️ Download Excel File", file, file_name="invoices.xlsx")
    else:
        st.info("Press the button to export.")

    with st.expander("📜 View Full OCR Text"):
        st.text(full_text)
