# app.py
import streamlit as st

st.title("Photobooth Test 🖤")
st.write("If you see this, your app runs perfectly!")

from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import random

st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Session state ----------
if "stage" not in st.session_state:
    st.session_state.stage = "landing"  # landing, capture, done
if "photos" not in st.session_state:
    st.session_state.photos = []  # list of PIL Images
if "last_camera_image" not in st.session_state:
    st.session_state.last_camera_image = None

# ---------- Global button CSS ----------
st.markdown("""
<style>
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

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div class="photobooth-card center">', unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom:6px;'>📸 Enter the Photobooth</h1>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Six months of laughs, photos, and tiny moments — make a polaroid strip for Aditya.</p>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Enter Photobooth", key="enter", help="Click to start the photobooth"):
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
    st.write("")

    # Show thumbnails of already taken photos
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB", (500,500), (240,240,240)), width=140, caption=f"#{i+1}")

    st.write("")

    # Countdown overlay placeholder
    countdown_placeholder = st.empty()

    def start_countdown():
        import time
        overlay_style = """
        <div style='position: fixed; top:0; left:0; width:100%; height:100%;
                    background-color: rgba(0,0,0,0.6); z-index: 900;
                    display:flex; justify-content:center; align-items:center;
                    flex-direction: column;'>
            <h1 style='color:white; font-size:140px; margin:0;'>{}</h1>
        </div>
        """
        for count in ["3", "2", "1", "📸"]:
            countdown_placeholder.markdown(overlay_style.format(count), unsafe_allow_html=True)
            time.sleep(0.8)
        countdown_placeholder.empty()
        st.info("Countdown finished! Click the camera button to take a photo.")

    # Start Countdown button
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    if st.button("📸 Start Countdown", key="countdown_btn"):
        start_countdown()
    st.markdown("</div>", unsafe_allow_html=True)

    # Camera input
    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Add / Retake / Create Strip buttons
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
            st.warning("Retake: use the camera above to take a new photo.")
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
        for idx, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            caption = ""
            pol = make_polaroid(bw, photo_size=(640,640), bottom_extra=140, border_px=10, caption_text=caption)
            polaroids.append(pol)

        strip = make_strip(polaroids, gap=24, background=(250,250,250))

        # Add classic black photobooth frame
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

        st.write("")
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





