import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import time
import os

st.set_page_config(page_title="Photobooth", layout="wide")

# ---------------------- SHARED STYLING ----------------------
PAGE_STYLE = """
<style>
/* Global page background */
.stApp {
    background-color: #f7f2e8 !important;
}

/* Center column container on landing page */
.landing-wrapper {
    position: relative;
    width: 100%;
    height: 92vh;
    background-color: #f7f2e8;
    border: 0px solid transparent;
    overflow: hidden;
}

/* Romantic text styling */
.love-script {
    position: absolute;
    font-family: 'Pinyon Script', cursive;
    font-size: 44px;
    color: #b30000;
    z-index: 4;
}

/* Scattered images */
.polaroid-img {
    position: absolute;
    width: 180px;
    z-index: 3;
}

/* Big button area */
.enter-container {
    position: absolute;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 320px;
    height: 320px;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
}

/* Actual button styling */
.big-enter-btn button {
    font-size: 28px !important;
    padding: 22px 38px !important;
    border-radius: 12px !important;
    background-color: #8b0000 !important;
    color: white !important;
    border: 3px solid #300000 !important;
}

/* Camera / booth page */
.booth-container {
    text-align: center;
}
</style>
"""

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

# ---------------------- STATE ----------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "photos" not in st.session_state:
    st.session_state.photos = []

# ---------------------- STRIP GENERATOR ----------------------
def create_strip(images):
    """Create a traditional photobooth strip with white borders and text space on bottom."""
    strip_width = 800
    frame_height = 1100
    bottom_text_space = 250
    spacing = 30

    total_height = len(images) * frame_height + (spacing * (len(images) - 1)) + bottom_text_space
    strip = Image.new("RGB", (strip_width, total_height), "white")

    draw = ImageDraw.Draw(strip)
    font = ImageFont.load_default()

    y = 0
    for img in images:
        img = img.resize((strip_width, frame_height - 20))
        strip.paste(img, (0, y))
        y += frame_height + spacing

    message = "Happy 6 Months My Love ❤️"
    bbox = draw.textbbox((0, 0), message, font=font)
    tw = bbox[2] - bbox[0]

    draw.text(
        ((strip_width - tw) // 2, total_height - bottom_text_space + 80),
        message,
        fill="black",
        font=font
    )

    return strip

# ---------------------- LANDING PAGE ----------------------
if st.session_state.page == "landing":

    st.markdown("<div class='landing-wrapper'>", unsafe_allow_html=True)

    # Romantic text placements
    st.markdown("""<div class="love-script" style="top:40px; left:60px;">I can’t wait to kiss you in a photobooth one day</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="love-script" style="top:120px; right:80px;">I love you so much, Aditya</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="love-script" style="bottom:140px; left:120px;">Best boyfriend</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="love-script" style="bottom:80px; right:160px;">Happy 6 months, my love</div>""", unsafe_allow_html=True)

    # Scattered PNGs (from your repo root)
    for i, pos in enumerate([
        ("20px", "20px", -6),
        ("40px", "20px", 8),
        ("40px", "40px", -10),
        ("50px", "40px", 6),
        ("150px", "-15px", 4),
        ("170px", "-10px", -4)
    ]):
        top, side, rot = pos
        if i < 3:
            align = f"top:{top}; left:{side};"
        else:
            align = f"top:{top}; right:{side};"
        st.markdown(
            f"<img src='{i+1}.png' class='polaroid-img' style='{align} transform:rotate({rot}deg);' />",
            unsafe_allow_html=True
        )

    # Big Enter Button
    st.markdown("<div class='enter-container'>", unsafe_allow_html=True)
    if st.container().button("Enter Photobooth", key="enter", help="Step inside ❤️", type="primary"):
        st.session_state.page = "booth"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

# ---------------------- PHOTOBOOTH PAGE ----------------------
elif st.session_state.page == "booth":

    st.markdown("<h1 style='text-align:center; color:#8b0000;'>📸 Photobooth</h1>", unsafe_allow_html=True)

    camera_photo = st.camera_input("Take a picture!")

    if camera_photo:
        st.session_state.photos.append(Image.open(camera_photo))

    # Show photo count
    if st.session_state.photos:
        st.markdown(f"<p style='text-align:center; color:#8b0000;'>Photos taken: {len(st.session_state.photos)}</p>", unsafe_allow_html=True)

    # Instructions
    st.markdown(
        "<p style='text-align:center; color:#8b0000;'>Take up to 4 photos for your strip. Click 'Create My Strip' when ready.</p>",
        unsafe_allow_html=True
    )

    if len(st.session_state.photos) >= 4:
        if st.button("Create My Strip ❤️"):
            # Take last 4 photos
            photos_to_strip = st.session_state.photos[-4:]

            # Messages for last photo
            messages = [
                "Happy 6 months!",
                "I love you so much, Aditya ❤️",
                "Best boyfriend",
                "Can't wait to kiss you in a photobooth one day 😘"
            ]
            last_message = random.choice(messages)

            # Create strip
            strip_images = []
            for i, p in enumerate(photos_to_strip):
                bw = bw_transform(p, contrast=1.15, sharpness=1.05)

                # Extra bottom for last photo for message
                extra_bottom = 80 if i == len(photos_to_strip)-1 else 0
                new_img = Image.new("RGB", (bw.width, bw.height + extra_bottom), (0,0,0))
                new_img.paste(bw, (0,0))

                # Draw the message on the last photo
                if extra_bottom > 0:
                    draw = ImageDraw.Draw(new_img)
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", 28)
                    except:
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0,0), last_message, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    draw.text(
                        ((new_img.width - w)//2, bw.height + (extra_bottom - h)//2),
                        last_message,
                        fill=(245,235,220),
                        font=font
                    )
                strip_images.append(new_img)

            # Combine into final vertical strip
            total_h = sum(im.height for im in strip_images)
            strip_w = max(im.width for im in strip_images)
            final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
            y = 0
            for im in strip_images:
                final_strip.paste(im, (0, y))
                y += im.height

            # Save and display
            buf = io.BytesIO()
            final_strip.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.image(final_strip, caption="Your Photobooth Strip", use_container_width=True)
            st.download_button("Download Strip", byte_im, file_name="photobooth_strip.png")

    if st.button("Back to Start"):
        st.session_state.page = "landing"
        st.rerun()
