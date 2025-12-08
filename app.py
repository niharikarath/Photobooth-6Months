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
.stApp {
    background-color: #fdf3e7;
    color: #111;
    font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Big Enter Photobooth button */
div.stButton > button {
    background-color: #a71d2a !important;
    color: #fdf3e7 !important;
    border-radius: 16px !important;
    font-size: 36px !important;
    padding: 24px 60px !important;
    font-weight: bold !important;
    margin-top: 150px;
    transition: 0.3s !important;
}
div.stButton > button:hover {
    background-color: #c8323b !important;
}

/* Photobooth card for capture/done stages */
.photobooth-card {
    background-color: #111;
    border: 4px solid #a71d2a;
    border-radius: 16px;
    padding: 36px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
}
.photobooth-card h1, .photobooth-card h2 {
    color: #fdf3e7;
}
.photobooth-card .muted {
    color: #e0c7b0;
}

/* Handwriting texts */
.handwriting-text {
    position: absolute;
    font-family: 'Comic Sans MS', 'Bradley Hand', cursive;
    color: #a71d2a;
    font-weight: bold;
    font-size: 28px;
    z-index: 100;
}

/* Polaroid images */
.polaroid-img {
    position: absolute;
    width: 120px;
    z-index: 50;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "stage" not in st.session_state:
    st.session_state.stage = "landing"  # landing, capture, done
if "photos" not in st.session_state:
    st.session_state.photos = []
if "last_camera_image" not in st.session_state:
    st.session_state.last_camera_image = None

# ---------- Helpers ----------
def pil_from_streamlit_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file).convert("RGB")

def make_strip(photos, gap=10, bg=(0,0,0)):
    w = max([p.width for p in photos])
    total_h = sum(p.height for p in photos) + gap*(len(photos)-1)
    strip = Image.new("RGB", (w, total_h), bg)
    y = 0
    for p in photos:
        strip.paste(p, ((w - p.width)//2, y))
        y += p.height + gap
    return strip

def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    gray = ImageOps.grayscale(img)
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    return rgb

# ---------- Landing Page ----------
if st.session_state.stage == "landing":
    st.markdown('<div style="position:relative; height:700px;">', unsafe_allow_html=True)

    # Handwriting texts scattered randomly
    texts = [
        "Happy 6 months of us, Aditya ❤️",
        "Can't wait to kiss you in a photobooth one day 😘",
        "Forever us 💕",
        "Our tiny memories 😍"
    ]
    for t in texts:
        top = random.randint(20, 500)
        left = random.randint(20, 600)
        angle = random.randint(-10, 10)
        st.markdown(
            f'<div class="handwriting-text" style="top:{top}px; left:{left}px; transform: rotate({angle}deg);">{t}</div>', 
            unsafe_allow_html=True
        )

    # Polaroid images scattered
    image_folder = "./"
    polaroid_files = ["1.png","2.png","3.png","4.png","5.png","6.png"]
    for img_file in polaroid_files:
        try:
            with open(image_folder + img_file, "rb") as f:
                img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode()
            top = random.randint(20, 400)
            left = random.randint(20, 650)
            angle = random.randint(-15, 15)
            st.markdown(
                f'<img src="data:image/png;base64,{img_base64}" class="polaroid-img" '
                f'style="top:{top}px; left:{left}px; transform: rotate({angle}deg);"/>',
                unsafe_allow_html=True
            )
        except:
            pass

    # Big centered button
    if st.button("📸 Enter Photobooth"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Capture ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Click the camera below. Take 4 photos — try different expressions!</p>", unsafe_allow_html=True)

    # Show thumbnails
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140)
            else:
                st.image(Image.new("RGB",(500,500),(0,0,0)), width=140)

    cam_file = st.camera_input("Take a photo 📸", key="camera_input")
    if cam_file:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Add / Retake / Create
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add Photo"):
            if st.session_state.last_camera_image and len(st.session_state.photos) < 4:
                st.session_state.photos.append(st.session_state.last_camera_image.copy())
                st.session_state.last_camera_image = None
                st.rerun()
            else:
                st.warning("Take a photo first or already 4 photos.")
    with col2:
        if st.button("Retake Last"):
            if st.session_state.photos:
                st.session_state.photos.pop()
                st.session_state.last_camera_image = None
                st.warning("Removed last photo.")
                st.rerun()
    with col3:
        if st.button("Create Strip"):
            if len(st.session_state.photos) == 4:
                st.session_state.stage = "done"
                st.rerun()
            else:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")

    if st.button("🏠 Back to Home"):
        st.session_state.stage = "landing"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Done ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>")

    try:
        strip_photos = []
        messages = ["Happy 6 months, Niharika ❤️","Niharika loves Aditya 💕","Adi baby Nihoo baby 😘","Forever us ❤️"]
        for i,p in enumerate(st.session_state.photos):
            bw = bw_transform(p, 1.15, 1.05)
            if i==3:
                extra_h = 80
                new_img = Image.new("RGB",(bw.width,bw.height+extra_h),(0,0,0))
                new_img.paste(bw,(0,0))
                draw = ImageDraw.Draw(new_img)
                font = ImageFont.load_default()
                msg = random.choice(messages)
                w,h = font.getsize(msg)
                draw.text(((bw.width-w)//2, bw.height+20), msg, fill=(255,0,0), font=font)
                strip_photos.append(new_img)
            else:
                strip_photos.append(bw)
        final_strip = make_strip(strip_photos, gap=10, bg=(0,0,0))
        buf = io.BytesIO()
        final_strip.save(buf, format="PNG")
        st.image(final_strip, caption="Photobooth Strip Preview")
        st.download_button("Download Strip", data=buf.getvalue(), file_name="photobooth_strip.png", mime="image/png")

        col1,col2 = st.columns([1,1])
        with col1:
            if st.button("Retake All"):
                st.session_state.stage="capture"
                st.session_state.photos=[]
                st.session_state.last_camera_image=None
                st.rerun()
        with col2:
            if st.button("Add New Strip"):
                st.session_state.stage="capture"
                st.session_state.photos=[]
                st.session_state.last_camera_image=None
                st.rerun()
        if st.button("🏠 Back to Home"):
            st.session_state.stage="landing"
            st.session_state.photos=[]
            st.session_state.last_camera_image=None
            st.rerun()
    except Exception as e:
        st.error(f"Error creating strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
