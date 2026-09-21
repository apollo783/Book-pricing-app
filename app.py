import streamlit as st
from PIL import Image
import requests
import urllib.parse
import pytesseract
from pyzbar.pyzbar import decode

# 1. Page Configuration
st.set_page_config(page_title="BookPrice Buddy", layout="centered")

# Custom CSS to make the camera viewport and images expand to FULL mobile width
st.markdown("""
    <style>
        .element-container, .stCameraInput, video {
            width: 100% !important;
            max-width: 100% !important;
        }
        div[data-testid="stCameraInput"] {
            width: 100% !important;
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
        
        # Display image across full mobile width (fixed parameter)
        st.image(img, caption="Captured Image", use_container_width=True)
        
        # 1. Check for Barcode
        barcodes = decode(img)
        if barcodes:
            detected_code = barcodes[0].data.decode('utf-8')
            st.success(f"Barcode Detected: {detected_code}")
            book_title = detected_code
        else:
            # 2. Extract Text via OCR if no barcode
            try:
                ocr_text = pytesseract.image_to_string(img)
                clean_lines = [line.strip() for line in ocr_text.split('\n') if len(line.strip()) > 3]
                if clean_lines:
                    detected_text = " ".join(clean_lines[:2])
                    st.success(f"Detected Title: {detected_text}")
                    book_title = st.text_input("Confirm or Edit Title:", value=detected_text)
                else:
                    st.warning("Could not automatically read title. Enter it manually below:")
                    book_title = st.text_input("Enter Title:")
            except Exception:
                st.warning("OCR processing skipped. Please type the title below:")
                book_title = st.text_input("Enter Title:")

with tab2:
    manual_input = st.text_input("Type Book Title / ISBN manually:")
    if manual_input:
        book_title = manual_input

# 2. Search & Pricing Results
if book_title:
    st.divider()
    st.subheader("📖 Book Information")
    
    query_url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(book_title)}"
    try:
        res = requests.get(query_url, timeout=5).json()
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
    except Exception:
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
