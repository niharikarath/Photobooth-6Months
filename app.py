# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import random
import base64

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
/* Page background & central card */
.stApp {
    background-color: #f3e5d0;  /* cream background */
    font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Central photobooth card */
.photobooth-card {
    background-color: #f3e5d0;
    border: 4px solid #a71d2a; /* deep red border */
    border-radius: 20px;
    padding: 60px;
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
    position: relative;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: #a71d2a !important;
    color: #f5e7dc !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 20px 50px !important;
    font-size: 22px !important;
    transition: 0.3s !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #c8323b !important;
}

/* Handwriting text */
.love-script {
    font-family: 'Pinyon Script', cursive;
    color: #a71d2a;
    font-size: 1.8rem;
    margin: 10px 0;
}

/* Scattered PNGs */
.polaroid-img {
    width: 90px;
    height: 90px;
    position: absolute;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
}

/* Empty container for button spacing */
.enter-container {
    height: 180px;  /* approx 5cm vertical space */
}
</style>

<!-- Import Pinyon Script -->
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "photos" not in st.session_state:
    st.session_state.photos = []

# ---------- Helper Functions ----------
def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    gray = ImageOps.grayscale(img)
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    return rgb

def create_strip(images):
    """Combine images vertically into a photobooth strip, add message on last image"""
    polaroids = []
    bottom_extra = 80  # space for text on last image
    messages = ["Happy 6 months!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby"]
    for i, img in enumerate(images):
        bw = bw_transform(img, contrast=1.15, sharpness=1.05)
        w, h = bw.size
        extra = bottom_extra if i == len(images)-1 else 0
        new_img = Image.new("RGB", (w, h + extra), (0,0,0))
        new_img.paste(bw, (0,0))
        if i == len(images)-1:
            draw = ImageDraw.Draw(new_img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
            last_message = random.choice(messages)
            bbox = draw.textbbox((0,0), last_message, font=font)
            text_w = bbox[2]-bbox[0]
            text_h = bbox[3]-bbox[1]
            draw.text(((w - text_w)//2, h + (bottom_extra - text_h)//2),
                      last_message, fill=(245,235,220), font=font)
        polaroids.append(new_img)
    # Combine vertically
    total_h = sum(im.height for im in polaroids)
    strip_w = max(im.width for im in polaroids)
    final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
    y = 0
    for im in polaroids:
        final_strip.paste(im, (0, y))
        y += im.height
    return final_strip

# ---------------------- LANDING PAGE ----------------------
if st.session_state.page == "landing":
    st.markdown("""
    <div class="photobooth-card">
        <!-- Romantic statements -->
        <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
        <div class="love-script">I love you so much, Aditya</div>
        <div class="love-script">Best boyfriend</div>
        <div class="love-script">Happy 6 months, my love</div>

        <!-- Scattered Images -->
        <img src="1.png" class="polaroid-img" style="top:20px; left:20px; transform:rotate(-6deg);" />
        <img src="2.png" class="polaroid-img" style="top:40px; right:20px; transform:rotate(6deg);" />
        <img src="3.png" class="polaroid-img" style="bottom:40px; left:30px; transform:rotate(-10deg);" />
        <img src="4.png" class="polaroid-img" style="bottom:50px; right:40px; transform:rotate(8deg);" />
        <img src="5.png" class="polaroid-img" style="top:150px; left:-15px; transform:rotate(4deg);" />
        <img src="6.png" class="polaroid-img" style="top:170px; right:-10px; transform:rotate(-4deg);" />

        <!-- Space for button -->
        <div class="enter-container"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📸 Enter Photobooth", key="enter_landing"):
        st.session_state.page = "booth"
        st.rerun()

# ---------------------- PHOTOBOOTH PAGE ----------------------
elif st.session_state.page == "booth":
    st.markdown("<h1 style='text-align:center; color:#8b0000;'>📸 Photobooth</h1>", unsafe_allow_html=True)

    camera_photo = st.camera_input("Take a picture!")

    if camera_photo:
        st.session_state.photos.append(Image.open(camera_photo))

    if st.session_state.photos:
        # Picture counter
        st.write(f"Photos taken: {len(st.session_state.photos)} / 4")

        # Retake last image button
        if st.button("Retake Last Image"):
            st.session_state.photos.pop()
            st.rerun()

    if len(st.session_state.photos) >= 4:
        if st.button("Create My Strip ❤️"):
            strip = create_strip(st.session_state.photos[-4:])
            buf = io.BytesIO()
            strip.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.image(strip, caption="Your Photobooth Strip", use_column_width=True)
            st.download_button("Download Strip", byte_im, file_name="strip.png")

    if st.button("Back to Start"):
        st.session_state.page = "landing"
        st.rerun()
