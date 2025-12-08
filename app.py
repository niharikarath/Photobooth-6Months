import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import random
import time
import base64

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
/* Page background & central card */
.stApp {
    background-color: #fdf3e7;  /* cream background */
    color: #111;
    font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Central photobooth card */
.photobooth-card {
    background-color: #111; /* classic black photobooth */
    border: 4px solid #a71d2a; /* deep red frame accent */
    border-radius: 16px;
    padding: 36px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
}

/* Header text */
.photobooth-card h1, .photobooth-card h2 {
    color: #fdf3e7; /* cream/off-white */
    margin-bottom: 12px;
}

/* Subtitle text */
.photobooth-card .muted {
    color: #e0c7b0; /* softer cream */
    font-size: 1rem;
    line-height: 1.5;
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: #a71d2a !important; /* deep red */
    color: #fdf3e7 !important; /* cream text */
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 16px 32px !important;
    font-size: 20px !important;
    transition: 0.3s !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #c8323b !important; /* lighter red on hover */
}

/* Handwriting texts */
.handwriting-text {
    position: absolute;
    font-family: 'Comic Sans MS', 'Bradley Hand', cursive;
    color: #a71d2a;
    font-size: 26px;
    font-weight: bold;
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

# ---------- Helper Functions ----------
def pil_from_streamlit_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file).convert("RGB")

def make_strip(photos, gap=10, bg=(0,0,0)):
    widths = [p.width for p in photos]
    w = max(widths)
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

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div style="position:relative; height:700px;">', unsafe_allow_html=True)

    # Handwriting texts
    st.markdown("""
    <div class="handwriting-text" style="top:40px; left:50px;">Happy 6 months of us, Aditya ❤️</div>
    <div class="handwriting-text" style="top:120px; right:60px;">Can't wait to kiss you in a photobooth one day 😘</div>
    """, unsafe_allow_html=True)

    # Polaroid images from local PNGs
    image_folder = "./"  # adjust if needed
    polaroid_files = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png"]  # use your uploaded files
    positions = [
        "top:20px; left:30px;", "top:100px; right:50px;", 
        "bottom:30px; left:50px;", "bottom:80px; right:60px;", 
        "top:250px; left:200px;", "top:350px; right:150px;"
    ]
    rotations = [-5, 8, -10, 6, -7, 12]

    for idx, img_file in enumerate(polaroid_files):
        try:
            with open(image_folder + img_file, "rb") as f:
                img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{img_base64}" class="polaroid-img" '
                f'style="{positions[idx]} transform: rotate({rotations[idx]}deg);"/>', 
                unsafe_allow_html=True
            )
        except Exception as e:
            st.warning(f"Could not load {img_file}: {e}")

    # Enter photobooth button
    if st.button("📸 Enter Photobooth"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- UI: Capture ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Click the camera icon to open your webcam. Take 4 photos — try different expressions!</p>", unsafe_allow_html=True)

    # Show thumbnails
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB",(500,500),(0,0,0)), width=140, caption=f"#{i+1}")

    # Camera input
    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Buttons: Add / Retake / Create
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add Photo to Strip", key="add_photo"):
            if st.session_state.last_camera_image:
                if len(st.session_state.photos) < 4:
                    st.session_state.photos.append(st.session_state.last_camera_image.copy())
                    st.session_state.last_camera_image = None
                    st.rerun()
                else:
                    st.info("You already have 4 photos. Click 'Create Polaroid Strip'.")
            else:
                st.warning("Take a photo first using the camera above.")
    with col2:
        if st.button("Retake Last Photo", key="retake"):
            if st.session_state.photos:
                st.session_state.photos.pop()
                st.warning("Removed last photo. Take a new one.")
                st.session_state.last_camera_image = None
                st.rerun()
            else:
                st.warning("No photos yet.")
    with col3:
        if st.button("Create Polaroid Strip", key="create_strip"):
            if len(st.session_state.photos) == 4:
                st.session_state.stage = "done"
                st.rerun()
            else:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")

    # Back to Home button
    if st.button("🏠 Back to Home"):
        st.session_state.stage = "landing"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- UI: Done ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>", unsafe_allow_html=True)

    # Create strip
    try:
        strip_photos = []
        messages = [
            "Happy 6 months, Niharika ❤️",
            "Niharika loves Aditya 💕",
            "Adi baby Nihoo baby 😘",
            "Forever us ❤️"
        ]
        for i, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, 1.15, 1.05)
            # Add extra space for message on last photo
            if i == 3:
                extra_height = 80
                new_img = Image.new("RGB", (bw.width, bw.height + extra_height), (0,0,0))
                new_img.paste(bw, (0,0))
                draw = ImageDraw.Draw(new_img)
                font = ImageFont.load_default()
                msg = random.choice(messages)
                w, h = draw.textsize(msg, font=font)
                draw.text(((bw.width - w)//2, bw.height + 20), msg, fill=(255,0,0), font=font)
                strip_photos.append(new_img)
            else:
                strip_photos.append(bw)
        final_strip = make_strip(strip_photos, gap=10, bg=(0,0,0))

        # Show and download
        buf = io.BytesIO()
        final_strip.save(buf, format="PNG")
        st.image(final_strip, caption="Photobooth Strip Preview")
        st.download_button("Download Strip", data=buf.getvalue(), file_name="photobooth_strip.png", mime="image/png")

        # Buttons
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Retake All"):
                st.session_state.stage = "capture"
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.rerun()
        with col2:
            if st.button("Add New Strip (Keep These)"):
                st.session_state.stage = "capture"
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.rerun()

        # Back to Home
        if st.button("🏠 Back to Home"):
            st.session_state.stage = "landing"
            st.session_state.photos = []
            st.session_state.last_camera_image = None
            st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
