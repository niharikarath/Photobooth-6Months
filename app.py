# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import random
import base64

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Imports for Fonts ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background-color: #f3e5d0; /* cream background */
    font-family: 'Helvetica', 'Arial', sans-serif;
}
.love-script {
    font-family: 'Pinyon Script', cursive;
    color: #a71d2a;
    font-size: 1.8rem;
    position: absolute;
}
.polaroid-img {
    width: 120px;
    height: 120px;
    position: absolute;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
}
.enter-button-container {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 250px;
    height: 80px;
}
div.stButton > button {
    background-color: #a71d2a !important;
    color: #f5e7dc !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 20px 50px !important;
    font-size: 22px !important;
}
div.stButton > button:hover {
    background-color: #c8323b !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "photos" not in st.session_state:
    st.session_state.photos = []

# ---------- Helper Functions ----------
def create_strip(photos):
    strip_images = []
    for i, img in enumerate(photos):
        # Convert to BW, enhance
        bw = ImageOps.grayscale(img).convert("RGB")
        bw = ImageEnhance.Contrast(bw).enhance(1.15)
        bw = ImageEnhance.Sharpness(bw).enhance(1.05)
        # Add extra space to last image for message
        extra_bottom = 80 if i == len(photos)-1 else 0
        new_img = Image.new("RGB", (bw.width, bw.height + extra_bottom), (0,0,0))
        new_img.paste(bw, (0,0))
        # Add random message to last photo
        if extra_bottom > 0:
            messages = ["Happy 6 months!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby"]
            last_message = random.choice(messages)
            draw = ImageDraw.Draw(new_img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0,0), last_message, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(
                ((new_img.width - w)//2, new_img.height - extra_bottom + (extra_bottom - h)//2),
                last_message,
                fill=(245,235,220),
                font=font
            )
        strip_images.append(new_img)
    
    # Combine vertically
    total_h = sum(im.height for im in strip_images)
    strip_w = max(im.width for im in strip_images)
    final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
    y = 0
    for im in strip_images:
        final_strip.paste(im, (0,y))
        y += im.height
    return final_strip

# ---------- LANDING PAGE ----------
if st.session_state.page == "landing":
    st.markdown("<div style='position:relative; height:600px;'>", unsafe_allow_html=True)
    
    # Romantic statements
    statements = [
        "I can’t wait to kiss you in a photobooth one day",
        "I love you so much, Aditya",
        "Best boyfriend",
        "Happy 6 months, my love"
    ]
    statement_positions = [
        {"top":50,"left":30},
        {"top":120,"left":200},
        {"top":80,"left":400},
        {"top":150,"left":350}
    ]
    for s,p in zip(statements, statement_positions):
        st.markdown(f"<div class='love-script' style='top:{p['top']}px; left:{p['left']}px;'>{s}</div>", unsafe_allow_html=True)

    # Scattered PNGs (make sure 1.png … 6.png are in repo)
    img_positions = [
        {"top":20,"left":20,"rotate":-6},
        {"top":40,"right":20,"rotate":6},
        {"bottom":40,"left":30,"rotate":-10},
        {"bottom":50,"right":40,"rotate":8},
        {"top":150,"left":-15,"rotate":4},
        {"top":170,"right":-10,"rotate":-4}
    ]
    for i,pos in enumerate(img_positions,1):
        style_parts = []
        for k,v in pos.items():
            style_parts.append(f"{k}:{v}px")
        style_parts.append(f"transform:rotate({pos['rotate']}deg)")
        style_str = "; ".join(style_parts)
        st.markdown(f"<img src='{i}.png' class='polaroid-img' style='{style_str};' />", unsafe_allow_html=True)
    
    # Big Enter Photobooth button
    st.markdown("<div class='enter-button-container'></div>", unsafe_allow_html=True)
    if st.button("📸 Enter Photobooth", key="enter_landing"):
        st.session_state.page = "booth"
        st.session_state.photos = []
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PHOTOBOOTH PAGE ----------
elif st.session_state.page == "booth":
    st.markdown("<h1 style='text-align:center; color:#8b0000;'>📸 Photobooth</h1>", unsafe_allow_html=True)

    camera_photo = st.camera_input("Take a picture!")
    if camera_photo:
        st.session_state.photos.append(Image.open(camera_photo))

    # Show preview and counter
    for idx, img in enumerate(st.session_state.photos):
        st.image(img, caption=f"Photo {idx+1}", use_column_width=True)
    
    if st.session_state.photos:
        if st.button("Retake Last Image"):
            st.session_state.photos.pop()
            st.experimental_rerun()

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
