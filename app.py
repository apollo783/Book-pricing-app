import streamlit as st
from PIL import Image
import requests
import urllib.parse
import pytesseract
from pyzbar.pyzbar import decode

st.set_page_config(page_title="BookPrice Buddy", layout="centered")

# CSS to override Streamlit defaults and make camera preview & images full-screen width
st.markdown("""
    <style>
        div[data-testid="stCameraInput"] {
            width: 100% !important;
            max-width: 100% !important;
        }
        div[data-testid="stCameraInput"] > div {
            width: 100% !important;
        }
        div[data-testid="stCameraInput"] video {
            width: 100% !important;
            height: auto !important;
            border-radius: 12px;
        }
        div[data-testid="stImage"] img {
            width: 100% !important;
            height: auto !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📚 BookPrice Buddy")
st.caption("Quick second-hand book pricing for shop staff")

tab1, tab2 = st.tabs(["📷 Scan Cover / Barcode", "⌨️ Manual Search"])

book_title = ""

with tab1:
    st.subheader("Take a Photo")
    camera_photo = st.camera_input("Capture front cover or barcode")
    
    if camera_photo:
        img = Image.open(camera_photo)
        
        # Display image across full container width
        st.image(img, caption="Captured Image", use_container_width=True)
        
        # 1. Barcode check
        barcodes = decode(img)
        if barcodes:
            detected_code = barcodes[0].data.decode('utf-8')
            st.success(f"Barcode Detected: {detected_code}")
            book_title = detected_code
        else:
            # 2. OCR text extraction
            try:
                ocr_text = pytesseract.image_to_string(img)
                clean_lines = [line.strip() for line in ocr_text.split('\n') if len(line.strip()) > 3]
                if clean_lines:
                    detected_text = " ".join(clean_lines[:2])
                    st.success(f"Detected Text: {detected_text}")
                    book_title = st.text_input("Confirm or Edit Book Title:", value=detected_text)
                else:
                    st.warning("Could not automatically read text. Type title below:")
                    book_title = st.text_input("Enter Title:")
            except Exception:
                st.warning("OCR unavailable. Type title below:")
                book_title = st.text_input("Enter Title:")

with tab2:
    manual_input = st.text_input("Type Book Title / ISBN manually:")
    if manual_input:
        book_title = manual_input

# Marketplace Direct Deep-Linking Section
if book_title:
    st.divider()
    st.subheader("📖 Book Details")
    
    # Query OpenLibrary to grab exact title and author for precise marketplace links
    query_url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(book_title)}"
    exact_title = book_title
    author = ""
    
    try:
        res = requests.get(query_url, timeout=5).json()
        if res.get("docs"):
            first_doc = res["docs"][0]
            exact_title = first_doc.get("title", book_title)
            authors = first_doc.get("author_name", [])
            if authors:
                author = authors[0]
            st.write(f"**Title:** {exact_title}")
            if author:
                st.write(f"**Author:** {author}")
    except Exception:
        st.write(f"**Search Query:** {book_title}")

    st.divider()
    st.subheader("🔍 Open Directly to Book Page")

    # Build quoted search query to land directly on exact book matches
    if author:
        exact_query = f'"{exact_title}" "{author}"'
    else:
        exact_query = f'"{exact_title}"'
        
    encoded_query = urllib.parse.quote(exact_query)

    col1, col2 = st.columns(2)
    with col1:
        st.link_button(
            "AbeBooks (Direct Match)", 
            f"https://www.abebooks.co.uk/servlet/SearchResults?sts=t&tn={urllib.parse.quote(exact_title)}&an={urllib.parse.quote(author)}"
        )
        st.link_button(
            "World of Books", 
            f"https://www.wob.com/en-gb/category/all?search={encoded_query}"
        )
    with col2:
        st.link_button(
            "eBay UK (Exact Book)", 
            f"https://www.ebay.co.uk/sch/267/i.html?_nkw={encoded_query}"
        )
        st.link_button(
            "ThriftBooks", 
            f"https://www.thriftbooks.com/browse/?b.s={encoded_query}"
        )

    st.divider()
    st.subheader("🏷️ Shop Pricing Calculator")
    
    online_price = st.number_input("Found Online Price (£):", min_value=0.0, value=5.0, step=0.50)
    condition = st.select_slider(
        "Condition (1 = Poor, 5 = Like New):",
        options=[1, 2, 3, 4, 5],
        value=3
    )
    
    multipliers = {1: 0.30, 2: 0.30, 3: 0.40, 4: 0.50, 5: 0.50}
    calculated = online_price * multipliers[condition]
    final_price = round(calculated * 2) / 2
    
    st.metric(label="Recommended Sticker Price", value=f"£{final_price:.2f}")
