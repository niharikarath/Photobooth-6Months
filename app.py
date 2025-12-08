# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import base64
import random

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Session State ----------
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing, booth
if "photos" not in st.session_state:
    st.session_state.photos = []

# ---------- Helper Functions ----------
def pil_to_base64(im):
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return base64.b64encode(byte_im).decode()

def create_strip(photos):
    """Combine photos vertically into a strip with random rotation and add a message on the last photo"""
    strip_imgs = []
    for i, p in enumerate(photos):
        # Convert to grayscale with slight contrast
        bw = ImageOps.grayscale(p).convert("RGB")
        bw = ImageEnhance.Contrast(bw).enhance(1.1)
        bw = ImageEnhance.Sharpness(bw).enhance(1.05)

        # Add extra bottom space for message on last photo
        extra_bottom = 80 if i == len(photos)-1 else 0
        new_img = Image.new("RGB", (bw.width, bw.height + extra_bottom), (0,0,0))
        new_img.paste(bw, (0,0))

        # Add message on last photo
        if i == len(photos)-1 and extra_bottom > 0:
            draw = ImageDraw.Draw(new_img)
            messages = ["Happy 6 months!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby"]
            last_message = random.choice(messages)
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

        strip_imgs.append(new_img)

    # Combine vertically
    total_h = sum(im.height for im in strip_imgs)
    w = max(im.width for im in strip_imgs)
    final_strip = Image.new("RGB", (w, total_h), (0,0,0))
    y = 0
    for im in strip_imgs:
        angle = random.uniform(-4,4)
        rotated = im.rotate(angle, expand=True, fillcolor=(0,0,0))
        final_strip.paste(rotated, ((w-rotated.width)//2, y))
        y += rotated.height
    return final_strip

# ---------- UI: Landing ----------
if st.session_state.page == "landing":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap');

    .stApp {background-color:#f3e5d0; font-family: 'Helvetica', sans-serif;}
    .landing-container {
        position: relative; max-width: 900px; margin:auto; height:700px;
    }
    .love-script {
        font-family: 'Pinyon Script', cursive;
        color:#a71d2a; font-size:2rem; position:absolute;
    }
    .polaroid-img {
        width:120px; height:120px; position:absolute; box-shadow:0 4px 8px rgba(0,0,0,0.4);
    }
    .enter-button {
        position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    }
    </style>

    <div class="landing-container">
        <!-- Romantic statements -->
        <div class="love-script" style="top:50px; left:20px;">I can’t wait to kiss you in a photobooth one day</div>
        <div class="love-script" style="top:100px; right:40px;">I love you so much, Aditya</div>
        <div class="love-script" style="bottom:120px; left:30px;">Best boyfriend</div>
        <div class="love-script" style="bottom:60px; right:50px;">Happy 6 months, my love</div>

        <!-- Scattered PNGs -->
        <img src="1.png" class="polaroid-img" style="top:20px; left:20px; transform:rotate(-6deg);" />
        <img src="2.png" class="polaroid-img" style="top:40px; right:20px; transform:rotate(6deg);" />
        <img src="3.png" class="polaroid-img" style="bottom:40px; left:30px; transform:rotate(-10deg);" />
        <img src="4.png" class="polaroid-img" style="bottom:50px; right:40px; transform:rotate(8deg);" />
        <img src="5.png" class="polaroid-img" style="top:150px; left:-15px; transform:rotate(4deg);" />
        <img src="6.png" class="polaroid-img" style="top:170px; right:-10px; transform:rotate(-4deg);" />

        <!-- Enter button placeholder -->
        <div class="enter-button">{}</div>
    </div>
    """.format(st.button("📸 Enter Photobooth", key="enter_landing")), unsafe_allow_html=True)

    if st.session_state.get("enter_landing"):
        st.session_state.page = "booth"
        st.session_state.photos = []
        st.rerun()

# ---------- UI: Photobooth ----------
elif st.session_state.page == "booth":
    st.markdown("<h1 style='text-align:center; color:#8b0000;'>📸 Photobooth</h1>", unsafe_allow_html=True)

    camera_photo = st.camera_input("Take a picture!")

    # Retake last photo
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Retake Last Photo"):
            if st.session_state.photos:
                st.session_state.photos.pop(-1)
    with col2:
        st.write(f"Photos taken: {len(st.session_state.photos)} / 4")

    if camera_photo:
        st.session_state.photos.append(Image.open(camera_photo))

    if len(st.session_state.photos) >= 1:
        if st.button("Create My Strip ❤️"):
            strip = create_strip(st.session_state.photos[-4:])
            buf = io.BytesIO()
            strip.save(buf, format="PNG")
            st.image(strip, caption="Your Photobooth Strip", use_container_width=True)
            st.download_button("Download Strip", buf.getvalue(), file_name="photobooth_strip.png")

    if st.button("Back to Start"):
        st.session_state.page = "landing"
        st.session_state.photos = []
        st.rerun()
