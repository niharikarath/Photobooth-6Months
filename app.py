import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import random

st.set_page_config(page_title="Niharika Photobooth", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

body, .stApp {
    background-color: #f7f2e8 !important;   /* warm cream */
    font-family: 'Helvetica', sans-serif;
}

/* Handwriting text */
.handwriting {
    font-family: 'Pinyon Script', cursive;
    font-size: 42px;
    color: #b30000;    /* photobooth red */
    position: absolute;
    z-index: 5;
}

/* Scattered polaroids */
.polaroid {
    width: 180px;
    position: absolute;
    z-index: 2;
    filter: drop-shadow(3px 3px 4px rgba(0,0,0,0.3));
}

/* Big red button */
.big-button button {
    background-color: #8b0000 !important; 
    color: white !important;
    padding: 18px 32px !important;
    font-size: 22px !important;
    border-radius: 12px !important;
    border: 3px solid #4a0000 !important;
    font-weight: bold !important;
}

.photobooth-box {
    padding: 40px;
    border-radius: 20px;
    border: 6px solid black;
    background-color: #d9cdc0; /* subtle cream interior */
    width: 600px;
    text-align: center;
    margin: auto;
}

</style>
""", unsafe_allow_html=True)

# -------------------- STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

# -------------------- LANDING PAGE --------------------

if st.session_state.page == "landing":

    st.markdown("<div class='photobooth-box'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 style='font-size:55px; font-weight:800; text-transform:uppercase;'>
        Niharika & Aditya Photobooth
    </h1>
    """, unsafe_allow_html=True)

    st.write(" ")

    # Two loving texts in handwriting font
    st.markdown("""
        <div class="handwriting" style="top:120px; left:40px;">
            Happy 6 months of us, Aditya ❤️
        </div>

        <div class="handwriting" style="bottom:120px; right:60px;">
            Can't wait to kiss you in a photobooth one day 😘
        </div>
    """, unsafe_allow_html=True)

    # Scattered polaroids using your uploaded files
    positions = [
        ("1.png", "top:40px; left:20px; transform:rotate(-6deg);"),
        ("2.png", "top:220px; right:40px; transform:rotate(8deg);"),
        ("3.png", "bottom:60px; left:80px; transform:rotate(-12deg);"),
        ("4.png", "bottom:30px; right:50px; transform:rotate(5deg);"),
        ("5.png", "top:150px; left:260px; transform:rotate(10deg);"),
        ("6.png", "bottom:150px; right:200px; transform:rotate(-8deg);")
    ]

    for img, style in positions:
        if os.path.exists(img):
            st.markdown(
                f"<img src='data:image/png;base64,{st.image(img, output_format='PNG').image_to_url()}' "
                f"class='polaroid' style='{style}'/>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")

    # Big enter button
    st.markdown("<div class='big-button'>", unsafe_allow_html=True)
    if st.button("ENTER PHOTOBOOTH"):
        st.session_state.page = "photobooth"
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# -------------------- PHOTOBOOTH PAGE --------------------
if st.session_state.page == "photobooth":

    st.title("📸 Take a Photobooth Picture")
    picture = st.camera_input("Smile!")

    if picture:
        img = Image.open(picture)

        # Create strip
        w, h = img.size
        strip = Image.new("RGB", (w + 40, h*3 + 100), "white")

        draw = ImageDraw.Draw(strip)

        # Paste picture 3 times
        strip.paste(img, (20, 20))
        strip.paste(img, (20, h + 40))
        strip.paste(img, (20, 2*h + 60))

        # Add love text below — using textbbox instead of getsize/gettextsize
        font = ImageFont.load_default()
        msg = "Niharika ❤️ Aditya"

        bbox = draw.textbbox((0, 0), msg, font=font)
        text_w = bbox[2] - bbox[0]

        draw.text(((w + 40 - text_w) // 2, 3*h + 70), msg, fill="black", font=font)

        st.image(strip)

        st.download_button("Download Strip", data=strip.tobytes(), file_name="photobooth_strip.png")

