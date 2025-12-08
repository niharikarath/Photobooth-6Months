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
<!-- Load Pinyon Script font -->
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">

<style>
/* Global App */
.stApp {
    font-family: 'Helvetica', sans-serif;
    overflow-x: hidden;
}

/* Landing page */
.landing-page {
    background-color: #fdf4e3;  /* Cream background */
    height: 100vh;
    position: relative;
    overflow: hidden;
}

/* Handwriting texts */
.landing-text {
    font-family: 'Pinyon Script', cursive;
    font-size: 36px;
    color: #a71d2a;  /* Deep red */
    position: absolute;
}

/* Polaroid images */
.polaroid-img {
    position: absolute;
    width: 140px;
    box-shadow: 4px 4px 12px rgba(0,0,0,0.4);
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: #a71d2a !important;
    color: #fdf4e3 !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    transition: 0.3s !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #c8323b !important;
}

/* Large enter button */
#enter-button button {
    font-size: 28px !important;
    padding: 20px 60px !important;
    display: block;
    margin: 0 auto;
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

def make_strip(images, width=640, gap=10, extra_bottom=50):
    """Create a vertical photobooth strip with optional extra space for text."""
    total_height = sum(im.height for im in images) + gap*(len(images)-1) + extra_bottom
    strip = Image.new("RGB", (width, total_height), (0,0,0))
    y = 0
    for im in images:
        im_resized = ImageOps.fit(im, (width, im.height), Image.LANCZOS)
        strip.paste(im_resized, (0, y))
        y += im.height + gap
    return strip

def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    gray = ImageOps.grayscale(img)
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    return rgb

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div class="landing-page">', unsafe_allow_html=True)

    # Loving texts
    st.markdown('<div class="landing-text" style="top:50px; left:40px; transform: rotate(-4deg);">Happy 6 months of us, Aditya ❤️</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-text" style="top:150px; right:50px; transform: rotate(5deg);">Can\'t wait to kiss you in a photobooth one day 😘</div>', unsafe_allow_html=True)
    st.markdown('<div class="landing-text" style="bottom:60px; left:80px; transform: rotate(-3deg);">Adi baby & Nihoo baby 💕</div>', unsafe_allow_html=True)

    # Polaroid images
    st.markdown('<img src="1.png" class="polaroid-img" style="top:20px; left:200px; transform: rotate(-6deg);"/>', unsafe_allow_html=True)
    st.markdown('<img src="2.png" class="polaroid-img" style="top:100px; right:180px; transform: rotate(8deg);"/>', unsafe_allow_html=True)
    st.markdown('<img src="3.png" class="polaroid-img" style="bottom:50px; left:300px; transform: rotate(-10deg);"/>', unsafe_allow_html=True)
    st.markdown('<img src="4.png" class="polaroid-img" style="bottom:150px; right:250px; transform: rotate(5deg);"/>', unsafe_allow_html=True)

    # Enter button
    if st.button("📸 Enter the Photobooth", key="enter", help="Click to start taking photos"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- UI: Capture ----------
elif st.session_state.stage == "capture":
    st.markdown('<div style="max-width:780px;margin:auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p>Click the camera button to open your webcam and take 4 photos!</p>", unsafe_allow_html=True)

    # Show thumbnails
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140)
            else:
                st.image(Image.new("RGB",(500,500),(0,0,0)), width=140)

    # Camera input
    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add Photo", key="add_photo"):
            if st.session_state.last_camera_image:
                st.session_state.photos.append(st.session_state.last_camera_image.copy())
                st.session_state.last_camera_image = None
                st.rerun()
    with col2:
        if st.button("Retake Last", key="retake"):
            if st.session_state.photos:
                st.session_state.photos.pop()
            st.session_state.last_camera_image = None
            st.rerun()
    with col3:
        if st.button("Create Strip", key="create_strip"):
            if len(st.session_state.photos) == 4:
                st.session_state.stage = "done"
                st.rerun()
            else:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")

    # Back to home
    if st.button("🏠 Back to Home"):
        st.session_state.stage = "landing"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- UI: Done ----------
elif st.session_state.stage == "done":
    st.markdown('<div style="max-width:780px;margin:auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>", unsafe_allow_html=True)

    try:
        # BW transform
        bw_photos = [bw_transform(p, 1.15, 1.05) for p in st.session_state.photos]

        # Add random text at bottom of last image
        messages = [
            "Happy 6 months, Niharika ❤️ Aditya",
            "Adi baby & Nihoo baby 💕",
            "Can't wait to kiss you in a photobooth 😘"
        ]
        message = random.choice(messages)
        last = bw_photos[-1].copy()
        draw = ImageDraw.Draw(last)
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        text_w, text_h = draw.textlength(message, font=font), font.getsize(message)[1] if hasattr(font,'getsize') else 20
        strip_h = last.height + 60
        strip_img = make_strip(bw_photos[:-1] + [ImageOps.expand(last, border=(0,0,0,60), fill=(0,0,0))], extra_bottom=60)

        # Draw text in extra space
        draw = ImageDraw.Draw(strip_img)
        draw.text(((strip_img.width - text_w)//2, strip_img.height - 50), message, fill=(255,0,0), font=font)

        # Convert to base64
        buf = io.BytesIO()
        strip_img.save(buf, format="PNG")
        base64_img = base64.b64encode(buf.getvalue()).decode()

        # Display with slide down animation
        html_code = f"""
        <div style="position: relative; width: fit-content; margin: auto; overflow: hidden; height: {strip_img.height + 20}px; background-color: #000;">
            <img src="data:image/png;base64,{base64_img}" 
                 style="display: block; width: auto; animation: slideDown 1.2s ease-out forwards; transform: translateY(-{strip_img.height}px);"/>
        </div>
        <style>
        @keyframes slideDown {{
            0% {{ transform: translateY(-{strip_img.height}px); }}
            100% {{ transform: translateY(0); }}
        }}
        </style>
        """
        st.markdown(html_code, unsafe_allow_html=True)

        # Download
        st.download_button(
            label="Download Strip (PNG)",
            data=buf.getvalue(),
            file_name="photobooth_strip.png",
            mime="image/png"
        )

        # Retake / new strip / back home buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Retake All"):
                st.session_state.stage = "capture"
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.rerun()
        with col2:
            if st.button("Add a New Strip"):
                st.session_state.stage = "capture"
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.rerun()
        with col3:
            if st.button("🏠 Back to Home"):
                st.session_state.stage = "landing"
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.rerun()

    except Exception as e:
        st.error(f"Error creating strip: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
