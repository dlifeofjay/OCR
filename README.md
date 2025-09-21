Invoice Extractor Pro
Overview

Invoice Extractor Pro is a Streamlit-based web application designed to extract structured invoice data from scanned or digital documents in PDF or image formats using OCR (Optical Character Recognition). It automates the extraction of key invoice fields such as invoice number, date, billed party, item, amount, and address, and stores the results in an Excel spreadsheet for record-keeping or further processing.

This tool is ideal for accounting teams, finance departments, and small businesses looking to digitize invoice processing and reduce manual data entry.

Features

Supports PDF, JPEG, PNG, and JPG invoice files

Uses OCR to extract text from scanned documents

Automatically parses common invoice fields:

Invoice Number

Date

Billed To

Address

Item

Amount

Allows inline review and editing of extracted fields

Saves all confirmed invoices to a persistent Excel file (invoice.xlsx)

Download the updated Excel file directly from the interface

View the full OCR text for transparency and verification

Technologies Used

Streamlit – for building the web interface

pytesseract – Python wrapper for Tesseract OCR

Pillow (PIL) – for image manipulation and loading

OpenCV (opencv-python) – for image preprocessing

pdf2image – for converting PDF pages into images for OCR

NumPy – for image buffer handling

Pandas – for data processing and Excel output

openpyxl – for writing data to Excel (.xlsx) format

Installation
1. Clone the Repository
git clone https://github.com/dlifeofjay/OCR.git
cd OCR

2. (Optional) Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

3. Install Required Packages
pip install -r requirements.txt

4. Install Tesseract OCR

Make sure Tesseract OCR
 is installed on your system:

Ubuntu:

sudo apt install tesseract-ocr


Windows:
Download from Tesseract OCR GitHub

Add the installation path (e.g., C:\Program Files\Tesseract-OCR) to your system’s environment variables.

Running the App

To launch the application:

streamlit run automation.py


This will open the app in your default browser.

How It Works

Upload an Invoice
Accepts a single invoice in PDF or image format.

OCR and Extraction
The document is preprocessed, and text is extracted using Tesseract OCR.

Field Parsing
The app attempts to parse key invoice fields using regular expressions.

Review and Edit
Each extracted invoice is displayed in an editable form so you can review and correct data.

Save and Download
Confirmed invoices are stored in a persistent Excel file (invoice.xlsx). You can also download the updated file directly from the app.

View OCR Text
For full transparency, you can expand each document to view the raw OCR text extracted.

Example Fields Extracted
Invoice No	Date	Billed To	Address	Item	Amount
INV-1024	2023-08-15	Acme Corp.	123 Main Street	Web Design Fee	150,000.00
Output File

All confirmed invoice data is saved to an Excel file:

invoice.xlsx


This file is automatically updated each time new invoice data is submitted and confirmed.
