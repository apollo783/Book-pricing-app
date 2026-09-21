import streamlit as st
from PIL import Image
import requests
import urllib.parse
import pytesseract
from pyzbar.pyzbar import decode

# 1. App Title & Setup
st.set_page_config(page_title="BookPrice Buddy", layout="centered")
st.title("📚 BookPrice Buddy")
st.caption("Quick second-hand book pricing for shop staff")

tab1, tab2 = st.tabs(["📷 Scan Cover / Barcode", "⌨️ Manual Search"])

def compress_image(image_file, max_size=(1000, 1000)):
    img = Image.open(image_file)
    img.thumbnail(max_size)
    return img

book_title = ""

with tab1:
    st.subheader("Take a Photo")
    camera_photo = st.camera_input("Capture front cover or barcode")
    
    if camera_photo:
        compressed_img = compress_image(camera_photo)
        # Display image larger on screen
        st.image(compressed_img, caption="Captured Image", use_column_width=True)
        
        # 1. Try Barcode Decoding First
        barcodes = decode(compressed_img)
        if barcodes:
            detected_code = barcodes[0].data.decode('utf-8')
            st.success(f"Barcode Detected: {detected_code}")
            book_title = detected_code
        else:
            # 2. OCR Text Extraction from Cover Photo
            ocr_text = pytesseract.image_to_string(compressed_img)
            clean_lines = [line.strip() for line in ocr_text.split('\n') if len(line.strip()) > 3]
            if clean_lines:
                detected_text = " ".join(clean_lines[:2])  # Take primary title lines
                st.success(f"Detected Title: {detected_text}")
                book_title = st.text_input("Confirm or Edit Detected Title:", value=detected_text)
            else:
                st.warning("Could not read text clearly. Please enter title manually below.")

with tab2:
    manual_input = st.text_input("Enter Book Title / ISBN manually:")
    if manual_input:
        book_title = manual_input

# 2. Metadata Fetching & Market Links
if book_title:
    st.divider()
    st.subheader("📖 Book Information")
    
    query_url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(book_title)}"
    res = requests.get(query_url).json()
    
    if res.get("docs"):
        first_doc = res["docs"][0]
        detected_title = first_doc.get("title", book_title)
        author = first_doc.get("author_name", ["Unknown Author"])[0]
        pub_year = first_doc.get("first_publish_year", "N/A")
        
        st.write(f"**Title:** {detected_title}")
        st.write(f"**Author:** {author}")
        st.write(f"**First Published:** {pub_year}")
        
        encoded_query = urllib.parse.quote(f"{detected_title} {author}")
    else:
        encoded_query = urllib.parse.quote(book_title)

    st.divider()
    st.subheader("🔍 Check Second-Hand Market Prices")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("AbeBooks", f"https://www.abebooks.com/servlet/SearchResults?kn={encoded_query}")
        st.link_button("World of Books (Wob)", f"https://www.wob.com/en-gb/category/all?search={encoded_query}")
    with col2:
        st.link_button("eBay Used Books", f"https://www.ebay.co.uk/sch/i.html?_nkw={encoded_query}&_sacat=267")
        st.link_button("ThriftBooks", f"https://www.thriftbooks.com/browse/?b.s={encoded_query}")

    st.divider()
    st.subheader("🏷️ Shop Pricing Calculator")
    
    online_price = st.number_input("Average Online Price (£):", min_value=0.0, value=5.0, step=0.50)
    condition = st.select_slider(
        "Book Condition (1 = Poor, 5 = Like New):",
        options=[1, 2, 3, 4, 5],
        value=3
    )
    
    multipliers = {1: 0.30, 2: 0.30, 3: 0.40, 4: 0.50, 5: 0.50}
    calculated = online_price * multipliers[condition]
    final_price = round(calculated * 2) / 2
    
    st.metric(label="Recommended Sticker Price", value=f"£{final_price:.2f}")
    st.divider()
    st.subheader("📖 Book Information")
    
    # Query Open Library API for book details & publication year
    query_url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(book_title)}"
    res = requests.get(query_url).json()
    
    if res.get("docs"):
        first_doc = res["docs"][0]
        detected_title = first_doc.get("title", book_title)
        author = first_doc.get("author_name", ["Unknown Author"])[0]
        pub_year = first_doc.get("first_publish_year", "N/A")
        
        st.write(f"**Title:** {detected_title}")
        st.write(f"**Author:** {author}")
        st.write(f"**First Published:** {pub_year}")
        
        encoded_query = urllib.parse.quote(f"{detected_title} {author}")
    else:
        encoded_query = urllib.parse.quote(book_title)

    # 3. Direct Second-Hand Price Search Links
    st.divider()
    st.subheader("🔍 Check Second-Hand Market Prices")
    
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("AbeBooks", f"https://www.abebooks.com/servlet/SearchResults?kn={encoded_query}")
        st.link_button("World of Books (Wob)", f"https://www.wob.com/en-gb/category/all?search={encoded_query}")
    with col2:
        st.link_button("eBay Used Books", f"https://www.ebay.co.uk/sch/i.html?_nkw={encoded_query}&_sacat=267")
        st.link_button("ThriftBooks", f"https://www.thriftbooks.com/browse/?b.s={encoded_query}")

    # 4. Charity Shop Calculator
    st.divider()
    st.subheader("🏷️ Shop Pricing Calculator")
    
    online_price = st.number_input("Average Online Price (£):", min_value=0.0, value=5.0, step=0.50)
    condition = st.select_slider(
        "Book Condition (1 = Poor, 5 = Like New):",
        options=[1, 2, 3, 4, 5],
        value=3
    )
    
    # Discount multiplier rules
    multipliers = {1: 0.30, 2: 0.30, 3: 0.40, 4: 0.50, 5: 0.50}
    calculated = online_price * multipliers[condition]
    
    # Round to nearest £0.50
    final_price = round(calculated * 2) / 2
    
    st.metric(label="Recommended Sticker Price", value=f"£{final_price:.2f}")
