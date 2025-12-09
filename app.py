# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import random
import base64

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth", page_icon="💕", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
/* Page background & central card */
.stApp {
    background-color: #f3e5d0;  /* cream background */
    color: #111;                 
    font-family: 'Times New Roman', 'Times', serif;
}

/* Central photobooth card */
.photobooth-card {
    background-color: #f3e5d0; /* cream */
    border: 4px solid #a71d2a; /* deep red frame */
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
    position: relative;
}

/* Romantic text */
.love-script {
    font-family: 'Pinyon Script', cursive;
    color: #a71d2a;
    font-size: 2.0rem;
    margin: 8px 0;
    transform: rotate(-3deg);
    display: inline-block;
}

/* Polaroid images */
.polaroid-img {
    width: 135px;  /* 35% bigger than before */
    height: 135px;
    position: absolute;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
}

/* Enter button container */
.enter-container {
    margin-top: 260px;
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
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
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "stage" not in st.session_state:
    st.session_state.stage = "landing"  # landing, capture, done
if "photos" not in st.session_state:
    st.session_state.photos = []
if "last_camera_image" not in st.session_state:
    st.session_state.last_camera_image = None

# ---------- Helper Functions ----------
def pil_from_streamlit_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file).convert("RGB")

def img_to_datauri(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    gray = ImageOps.grayscale(img)
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    return rgb

# ---------- Landing Page ----------
st.markdown("""
<div class="love-container">
    <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
    <div class="love-script">I love you so much, Aditya</div>
    <div class="love-script">Best boyfriend</div>
    <div class="love-script">Happy 6 months, my love</div>
</div>
""", unsafe_allow_html=True)


    # Scattered PNGs
    st.markdown(f"""
    <img src="{img_to_datauri('1.png')}" class="polaroid-img" style="top:20px; left:20px; transform:rotate(-6deg);" />
    <img src="{img_to_datauri('2.png')}" class="polaroid-img" style="top:40px; right:20px; transform:rotate(6deg);" />
    <img src="{img_to_datauri('3.png')}" class="polaroid-img" style="bottom:40px; left:30px; transform:rotate(-10deg);" />
    <img src="{img_to_datauri('4.png')}" class="polaroid-img" style="bottom:50px; right:40px; transform:rotate(8deg);" />
    <img src="{img_to_datauri('5.png')}" class="polaroid-img" style="top:150px; left:-15px; transform:rotate(4deg);" />
    <img src="{img_to_datauri('6.png')}" class="polaroid-img" style="top:170px; right:-10px; transform:rotate(-4deg);" />
    """, unsafe_allow_html=True)

    st.markdown('<div class="enter-container"></div>', unsafe_allow_html=True)

    if st.button("📸 Enter the Photobooth"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()  # fixed to correct rerun

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Capture Page ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)

    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB",(500,500),(200,200,200)), width=140, caption=f"#{i+1}")

    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add Photo to Strip", key="add_photo"):
            if st.session_state.last_camera_image is None:
                st.warning("Take a photo first using the camera above.")
            elif len(st.session_state.photos) >= 4:
                st.info("You already have 4 photos. Click 'Create Polaroid Strip'.")
            else:
                st.session_state.photos.append(st.session_state.last_camera_image.copy())
                st.session_state.last_camera_image = None
                st.rerun()
    with col2:
        if st.button("Retake Last Photo", key="retake"):
            if st.session_state.photos:
                st.session_state.photos.pop()
                st.warning("Removed last photo from the strip. Take a new one using the camera above.")
            else:
                st.warning("No photos in the strip yet. Take a new photo using the camera above.")
            st.session_state.last_camera_image = None
            st.rerun()
    with col3:
        if st.button("Create Polaroid Strip", key="create_strip"):
            if len(st.session_state.photos) < 4:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")
            else:
                st.session_state.stage = "done"
                st.rerun()

    if st.button("🏠 Back to Home"):
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.session_state.stage = "landing"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Done Page ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>", unsafe_allow_html=True)

    try:
        strip_images = []
        for i, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            extra_bottom = 80 if i == len(st.session_state.photos) - 1 else 0
            img_w, img_h = bw.size
            new_img = Image.new("RGB", (img_w, img_h + extra_bottom), (0,0,0))
            new_img.paste(bw, (0,0))
            strip_images.append(new_img)

        messages = ["Happy 6 months My Love!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby", "Aditya ❤️ Niharika", "Happy 6 Crazy Months Together", "Bandar Baby 🐒 ❤️ Sundar Baby 🐰"]
        last_message = random.choice(messages)
        last_img = strip_images[-1]
        if extra_bottom > 0:
            draw = ImageDraw.Draw(last_img)
            try:
               font = ImageFont.truetype("PinyonScript-Regular.ttf", 40)  # bigger + script font
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0,0), last_message, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(((last_img.width - w)//2, last_img.height - extra_bottom + (extra_bottom - h)//2),
                      last_message, fill=(245,235,220), font=font)

        total_h = sum(im.height for im in strip_images)
        strip_w = max(im.width for im in strip_images)
        final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
        y = 0
        for im in strip_images:
            final_strip.paste(im, (0, y))
            y += im.height

        buf = io.BytesIO()
        final_strip.save(buf, format="PNG")

        st.image(final_strip, caption="Your Photobooth Strip", use_column_width=True)

        st.download_button(
            label="Download Photobooth Strip (PNG)",
            data=buf.getvalue(),
            file_name="photobooth_strip.png",
            mime="image/png"
        )

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Retake All"):
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()
        with col2:
            if st.button("Add a New Strip (Keep these)"):
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()

        if st.button("🏠 Back to Home"):
            st.session_state.photos = []
            st.session_state.last_camera_image = None
            st.session_state.stage = "landing"
            st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
