# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont
import io
import random
import time

# ---------- Page Config ----------
st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Styling ----------
st.markdown("""
<style>
/* Black background & card styling */
.stApp {
    background-color: #111;  /* Photobooth black */
    color: #f5e7dc;  /* Cream text */
    font-family: 'Helvetica', 'Arial', sans-serif;
}

/* Central card */
.photobooth-card {
    background-color: #111;
    border: 4px solid #a71d2a; /* red border */
    border-radius: 16px;
    padding: 36px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
}

/* Headings */
.photobooth-card h1, .photobooth-card h2 {
    color: #f5e7dc;
    margin-bottom: 12px;
}

/* Subtitles / muted text */
.photobooth-card .muted {
    color: #e0c7b0;
    font-size: 1rem;
    line-height: 1.5;
}

/* Buttons */
div.stButton > button,
div.stDownloadButton > button {
    background-color: #a71d2a !important;  /* deep red */
    color: #f5e7dc !important;  /* cream text */
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    font-size: 16px !important;
    transition: 0.3s !important;
}
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background-color: #c8323b !important; /* lighter red */
}

/* Small helper text */
.photobooth-card small {
    color: #e0c7b0;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "stage" not in st.session_state:
    st.session_state.stage = "landing"
if "photos" not in st.session_state:
    st.session_state.photos = []
if "last_camera_image" not in st.session_state:
    st.session_state.last_camera_image = None

# ---------- Helper Functions ----------
def pil_from_streamlit_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file).convert("RGB")

def make_polaroid(photo: Image.Image,
                  photo_size=(600,600),
                  frame_color=(139,94,60),  # Brown frame
                  bottom_extra=120,
                  border_px=6,
                  caption_text=""):
    photo = ImageOps.fit(photo, photo_size, Image.LANCZOS)
    frame_w = photo_size[0] + border_px*2
    frame_h = photo_size[1] + border_px*2 + bottom_extra
    frame = Image.new("RGB", (frame_w, frame_h), frame_color)
    frame.paste(photo, (border_px, border_px))
    draw = ImageDraw.Draw(frame)
    draw.rectangle([0,0,frame_w-1, frame_h-1], outline=(80,80,80), width=2)
    if caption_text:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=28)
        except Exception:
            font = ImageFont.load_default()
        w, h = draw.textsize(caption_text, font=font)
        text_x = (frame_w - w) // 2
        text_y = photo_size[1] + border_px + (bottom_extra - h) // 2
        draw.text((text_x, text_y), caption_text, fill=(255,255,255), font=font)
    return frame

def make_strip(polaroids, gap=18, background=(17,17,17)):
    widths = [im.width for im in polaroids]
    assert len(set(widths)) == 1, "All polaroids must be same width"
    w = widths[0]
    total_h = sum(im.height for im in polaroids) + gap*(len(polaroids)-1)
    strip = Image.new("RGB", (w, total_h), background)
    y = 0
    for im in polaroids:
        angle = random.uniform(-4,4)
        rotated = im.rotate(angle, expand=True, fillcolor=background)
        x = (w - rotated.width)//2
        strip.paste(rotated, (x, y), rotated.convert("RGBA"))
        y += rotated.height + gap
    return strip

def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    gray = ImageOps.grayscale(img)
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    return rgb

def curtain_animation():
    placeholder = st.empty()
    # Curtain HTML/CSS
    curtain_html = """
    <div style="position: fixed; top:0; left:0; width:100%; height:100%; z-index:9999; display:flex;">
        <div id="left" style="background-color:#a71d2a; width:50%; height:100%; transition: all 0.8s;"></div>
        <div id="right" style="background-color:#a71d2a; width:50%; height:100%; transition: all 0.8s;"></div>
    </div>
    <script>
        setTimeout(() => {
            document.getElementById('left').style.width = '0%';
            document.getElementById('right').style.width = '0%';
        }, 50);
    </script>
    """
    placeholder.markdown(curtain_html, unsafe_allow_html=True)
    time.sleep(0.9)
    placeholder.empty()

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h1>📸 Enter the Photobooth</h1>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Six months of laughs, photos, and tiny moments — make a polaroid strip for Aditya.</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Enter Photobooth", key="enter"):
            curtain_animation()
            st.session_state.photos = []
            st.session_state.stage = "capture"
            st.rerun()
    with col2:
        st.markdown("<small class='muted'>Want help with layout or fonts? I can add captions, sound, or an auto-timer.</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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
                st.image(Image.new("RGB",(500,500),(17,17,17)), width=140, caption=f"#{i+1}")

    # Countdown button
    if st.button("📸 Start Countdown", key="countdown_btn"):
        st.info("Countdown animation would go here (implement if needed).")

    # Camera input
    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Add / Retake / Create buttons
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
                st.warning("Removed last photo. Take a new one.")
            else:
                st.warning("No photos yet.")
            st.session_state.last_camera_image = None
            st.rerun()
    with col3:
        if st.button("Create Polaroid Strip", key="create_strip"):
            if len(st.session_state.photos) < 4:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")
            else:
                st.session_state.stage = "done"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- UI: Done ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Polaroid Strip</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Here is your black & white strip, just printed! Download it, or keep taking more photos.</p>", unsafe_allow_html=True)
    
    try:
        polaroids = []
        for p in st.session_state.photos:
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            pol = make_polaroid(bw, photo_size=(640,640), bottom_extra=140, border_px=10, caption_text="", frame_color=(0,0,0))  # Black frame
            polaroids.append(pol)

        strip = make_strip(polaroids, gap=24, background=(0,0,0))  # black background

        # ---------- Printer Animation ----------
        placeholder = st.empty()
        canvas_height = strip.height + 80
        canvas_width = strip.width + 80
        full_canvas = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))
        frame_thickness = 40

        # Animate strip sliding down like a printer
        for i in range(0, strip.height + 1, 20):
            frame = full_canvas.copy()
            frame.paste(strip.crop((0, 0, strip.width, i)), (frame_thickness, frame_thickness))
            placeholder.image(frame, use_column_width=False)
            time.sleep(0.05)

        # Ensure final frame is fully displayed
        full_frame = full_canvas.copy()
        full_frame.paste(strip, (frame_thickness, frame_thickness))
        placeholder.image(full_frame, use_column_width=False, caption="Polaroid strip preview")

        # ---------- Download ----------
        buf = io.BytesIO()
        full_frame.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="Download Polaroid Strip (PNG)",
            data=byte_im,
            file_name="polaroid_strip.png",
            mime="image/png"
        )

        # ---------- Buttons ----------
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Retake All"):
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()
        with col2:
            if st.button("Add a New Strip (Keep these)"):
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
