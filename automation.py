import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import pandas as pd
import os

# 🔧 Preprocess uploaded image for OCR
def preprocess_image(image_bytes):
    image_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

# 🔍 Extract text using Tesseract
def extract_text(img):
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"OCR failed: {e}"

# 📥 Extract key invoice fields from OCR text
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

# 💾 Save extracted data to Excel
def save_to_excel(data, filename='invoices.xlsx'):
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        try:
            existing = pd.read_excel(filename)
            df = pd.concat([existing, df], ignore_index=True)
        except Exception:
            pass  # Start fresh if file is unreadable
    df.to_excel(filename, index=False)

# 🌐 Streamlit app layout
st.set_page_config(page_title="Invoice Extractor", page_icon="📄")
st.title("📄 Invoice Data Extractor")

uploaded_file = st.file_uploader("Upload an invoice image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Invoice", use_column_width=True)
    st.write("🔄 Processing...")

    img_bytes = uploaded_file.read()
    processed_img = preprocess_image(img_bytes)
    ocr_text = extract_text(processed_img)
    extracted_fields = parse_fields(ocr_text)

    st.subheader("📋 Extracted Fields")
    for label, value in extracted_fields.items():
        st.markdown(f"**{label}:** {value}")

    save_to_excel(extracted_fields)
    st.success("✅ Invoice info added to *invoices.xlsx*")

    st.markdown(
        "📥 **Tip:** Upload more invoices and tap the download button below to get the updated Excel file every time."
    )

    with open("invoices.xlsx", "rb") as file:
        st.download_button("⬇️ Download Excel File", file, file_name="invoices.xlsx")

    with st.expander("📜 Full OCR Output"):
        st.text(ocr_text)
