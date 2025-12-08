# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import base64
import random

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="Photobooth — 6 Monthiversary",
    page_icon="📸",
    layout="centered"
)

# ------------------- Session State -------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing, booth
if "photos" not in st.session_state:
    st.session_state.photos = []

# ------------------- Helper Functions -------------------
def img_to_datauri(path):
    """Convert local PNG to base64 data URI for HTML img tag"""
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f"data:image/png;base64,{b64}"

def create_strip(images):
    """Combine up to 4 images into a vertical strip"""
    polaroids = []
    for img in images:
        # make square, add white bottom space for caption
        img = ImageOps.fit(img, (400,400))
        frame_h = 400 + 80
        frame = Image.new("RGB", (400, frame_h), (255,255,255))
        frame.paste(img, (0,0))
        polaroids.append(frame)

    # combine vertically
    total_h = sum(p.height for p in polaroids) + 10*(len(polaroids)-1)
    strip = Image.new("RGB", (400, total_h), (0,0,0))
    y = 0
    for i, p in enumerate(polaroids):
        strip.paste(p, (0,y))
        # add message on last image
        if i == len(polaroids)-1:
            draw = ImageDraw.Draw(strip)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
            message = random.choice([
                "Happy 6 months!",
                "Niharika ❤️ Aditya",
                "I love you so much, Adi!"
            ])
            w,h = draw.textsize(message, font=font)
            draw.text(
                ((400 - w)//2, y + 400 + (80 - h)//2),
                message,
                fill=(0,0,0),
                font=font
            )
        y += p.height + 10
    return strip

# ------------------- CSS Styling -------------------
st.markdown("""
<style>
.stApp {
    background-color: #f3e5d0;
    font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Cream card for landing */
.photobooth-card {
    background-color: #f3e5d0;
    border: 4px solid #a71d2a;
    border-radius: 20px;
    padding: 60px;
    max-width: 800px;
    margin: 80px auto;
    text-align: center;
    position: relative;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* Romantic texts */
.love-script {
    font-family: 'Pinyon Script', cursive;
    color: #a71d2a;
    font-size: 1.6rem;
    margin: 10px 0;
}

/* Polaroid images */
.polaroid-img {
    width: 100px;
    height: 100px;
    position: absolute;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
}

/* Enter button container */
.enter-container {
    height: 150px; /* reserve space for big button */
    margin-top: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Buttons */
div.stButton > button {
    background-color: #a71d2a !important;
    color: #f5e7dc !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 25px 60px !important;
    font-size: 24px !important;
}
div.stButton > button:hover {
    background-color: #c8323b !important;
}
</style>

<!-- Google Font Pinyon Script -->
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ------------------- LANDING PAGE -------------------
if st.session_state.page == "landing":
    st.markdown(f"""
    <div class="photobooth-card">
        <!-- Romantic statements -->
        <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
        <div class="love-script">I love you so much, Aditya</div>
        <div class="love-script">Best boyfriend</div>
        <div class="love-script">Happy 6 months, my love</div>

        <!-- Scattered Images -->
        <img src="{img_to_datauri('1.png')}" class="polaroid-img" style="top:20px; left:20px; transform:rotate(-6deg);" />
        <img src="{img_to_datauri('2.png')}" class="polaroid-img" style="top:40px; right:20px; transform:rotate(6deg);" />
        <img src="{img_to_datauri('3.png')}" class="polaroid-img" style="bottom:40px; left:30px; transform:rotate(-10deg);" />
        <img src="{img_to_datauri('4.png')}" class="polaroid-img" style="bottom:50px; right:40px; transform:rotate(8deg);" />
        <img src="{img_to_datauri('5.png')}" class="polaroid-img" style="top:150px; left:-15px; transform:rotate(4deg);" />
        <img src="{img_to_datauri('6.png')}" class="polaroid-img" style="top:170px; right:-10px; transform:rotate(-4deg);" />

        <!-- Enter button space -->
        <div class="enter-container">
            {st.button("📸 Enter Photobooth")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("Enter Photobooth"):
        st.session_state.page = "booth"
        st.experimental_rerun()

# ------------------- PHOTOBOOTH PAGE -------------------
elif st.session_state.page == "booth":
    st.markdown("<h1 style='text-align:center; color:#8b0000;'>📸 Photobooth</h1>", unsafe_allow_html=True)

    camera_photo = st.camera_input("Take a picture!")
    if camera_photo:
        st.session_state.photos.append(Image.open(camera_photo))

    # Photo counter
    st.write(f"Photos taken: {len(st.session_state.photos)}")

    # Retake last image
    if st.session_state.photos:
        if st.button("Retake Last Image"):
            st.session_state.photos.pop()
            st.experimental_rerun()

    # Create strip if 4 photos
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
        st.experimental_rerun()
