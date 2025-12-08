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
/* Page background & central card */
.stApp {
  background-color: #f6f6f7;
  color: #111;
  font-family: 'Helvetica', 'Arial', sans-serif;
}
.photobooth-card {
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
  max-width: 760px;
  margin: auto;
}
.big-btn {
  background-color:#111;
  color:white;
  padding:10px 20px;
  border-radius:8px;
  font-weight:600;
}
.muted {
  color: #666;
  font-size:14px;
}
.center {
  text-align:center;
}
div.stButton > button, 
div.stDownloadButton > button {
    display: inline-block !important;
    opacity: 1 !important;
    min-width: 160px !important;
    min-height: 50px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #fff !important;
    background-color: #111 !important;
    border-radius: 8px !important;
    border: none !important;
    transition: 0.3s !important;
    z-index: 9999 !important;
}
div.stButton > button:hover,
div.stDownloadButton > button:hover {
    background-color: #555 !important;
}
div.stDownloadButton {
    text-align: center;
    margin-top: 10px;
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
if "camera_counter" not in st.session_state:
    st.session_state.camera_counter = 0

# ---------- Helper Functions ----------
def pil_from_streamlit_uploaded(uploaded_file):
    if uploaded_file is None:
        return None
    return Image.open(uploaded_file).convert("RGB")

def make_polaroid(photo: Image.Image,
                  photo_size=(600,600),
                  frame_color=(255,255,255),
                  bottom_extra=120,
                  border_px=6,
                  caption_text=""):
    photo = ImageOps.fit(photo, photo_size, Image.LANCZOS)
    frame_w = photo_size[0] + border_px*2
    frame_h = photo_size[1] + border_px*2 + bottom_extra
    frame = Image.new("RGB", (frame_w, frame_h), frame_color)
    frame.paste(photo, (border_px, border_px))
    draw = ImageDraw.Draw(frame)
    draw.rectangle([0,0,frame_w-1, frame_h-1], outline=(200,200,200), width=1)
    if caption_text:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", size=28)
        except Exception:
            font = ImageFont.load_default()
        w, h = draw.textsize(caption_text, font=font)
        text_x = (frame_w - w) // 2
        text_y = photo_size[1] + border_px + (bottom_extra - h) // 2
        draw.text((text_x, text_y), caption_text, fill=(80,80,80), font=font)
    return frame

def make_strip(polaroids, gap=18, background=(245,245,246)):
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

def start_countdown():
    countdown_placeholder = st.empty()
    
    overlay_style = """
    <div style='position: fixed; top:0; left:0; width:100%; height:100%;
                background-color: rgba(0,0,0,0.6); z-index: 900;
                display:flex; justify-content:center; align-items:center;
                flex-direction: column;'>
        <h1 style='color:white; font-size:140px; margin:0; opacity:{}'>{}</h1>
    </div>
    """
    flash_style = """
    <div style='position: fixed; top:0; left:0; width:100%; height:100%;
                background-color: rgba(255,255,255,0.9); z-index: 999;
                display:flex; justify-content:center; align-items:center;'>
    </div>
    """
    
    for count in ["3", "2", "1", "📸"]:
        for opacity in [0.2,0.4,0.6,0.8,1.0]:
            countdown_placeholder.markdown(overlay_style.format(opacity, count), unsafe_allow_html=True)
            time.sleep(0.08)
        time.sleep(0.3)
        if count == "📸":
            countdown_placeholder.markdown(flash_style, unsafe_allow_html=True)
            time.sleep(0.15)
            countdown_placeholder.markdown(overlay_style.format(1, count), unsafe_allow_html=True)
            time.sleep(0.2)
    
    countdown_placeholder.empty()
    st.info("Countdown finished! Click the camera button to take a photo.")

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div class="photobooth-card center">', unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom:6px;'>📸 Enter the Photobooth</h1>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Six months of laughs, photos, and tiny moments — make a polaroid strip for Aditya.</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Enter Photobooth", key="enter"):
            st.session_state.photos = []
            st.session_state.stage = "capture"
            st.rerun()
    with col2:
        st.markdown("<small class='muted'>Want help with layout or fonts? I can add captions, sound, or an auto-timer.</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- UI: Capture ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2 class='center'>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted center'>Click the camera icon to open your webcam. Take 4 photos — try different expressions!</p>", unsafe_allow_html=True)

    # Show thumbnails
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB", (500,500), (240,240,240)), width=140, caption=f"#{i+1}")

    # Countdown button
    if st.button("📸 Start Countdown", key="countdown_btn"):
        start_countdown()

    # Camera input with counter to reset
    cam_file = st.camera_input(
        "Smile! Click the camera button to take a photo.",
        key=f"camera_input_{st.session_state.camera_counter}"
    )
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
            st.session_state.last_camera_image = None
            st.session_state.camera_counter += 1  # reset camera widget
            st.warning("Retake: use the camera control below to take a new photo.")
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
    st.markdown('<div class="photobooth-card center">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Polaroid Strip</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Here is your black & white strip. Download it, or print for a real polaroid feel.</p>", unsafe_allow_html=True)

    try:
        polaroids = []
        for p in st.session_state.photos:
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            pol = make_polaroid(bw, photo_size=(640,640), bottom_extra=140, border_px=10, caption_text="")
            polaroids.append(pol)

        strip = make_strip(polaroids, gap=24, background=(250,250,250))
        frame_thickness = 40
        canvas = Image.new("RGB", (strip.width + frame_thickness*2, strip.height + frame_thickness*2), (0,0,0))
        canvas.paste(strip, (frame_thickness, frame_thickness))
        st.image(canvas, use_column_width=False, caption="Polaroid strip preview")

        buf = io.BytesIO()
        canvas.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Download Polaroid Strip (PNG)",
            data=byte_im,
            file_name="polaroid_strip.png",
            mime="image/png"
        )

    # ---------- Add / Retake / Create buttons ----------
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
        # Remove last photo from the strip if any
        if st.session_state.photos:
            st.session_state.photos.pop()
            st.warning("Removed last photo from the strip. Take a new one using the camera below.")
        else:
            st.warning("No photos in the strip yet. Take a new photo using the camera below.")
        # Reset camera input so user can retake
        st.session_state.last_camera_image = None
        st.session_state.camera_counter += 1
        st.rerun()

with col3:
    if st.button("Create Polaroid Strip", key="create_strip"):
        if len(st.session_state.photos) < 4:
            st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")
        else:
            st.session_state.stage = "done"
            st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
