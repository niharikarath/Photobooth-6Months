# app.py
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
    background-color: #111;  /* black background */
    color: #f5e7dc;          /* cream/off-white text */
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
    color: #f5e7dc; /* cream/off-white */
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
    color: #f5e7dc !important; /* cream text */
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    font-size: 16px !important;
    transition: 0.3s !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #c8323b !important; /* lighter red on hover */
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

def make_polaroid(photo: Image.Image,
                  photo_size=(600,600),
                  frame_color=(0,0,0),
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

        # Pillow ≥10 compatible
        bbox = draw.textbbox((0,0), caption_text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        text_x = (frame_w - w) // 2
        text_y = photo_size[1] + border_px + (bottom_extra - h) // 2
        draw.text((text_x, text_y), caption_text, fill=(80,80,80), font=font)

    return frame

def make_strip(polaroids, gap=18, background=(0,0,0)):
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

# ---------- UI: Landing ----------
if st.session_state.stage == "landing":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h1>📸 Enter the Photobooth</h1>", unsafe_allow_html=True)
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
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Click the camera icon to open your webcam. Take 4 photos — try different expressions!</p>", unsafe_allow_html=True)

    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB",(500,500),(0,0,0)), width=140, caption=f"#{i+1}")

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
    
# ---------- UI: Done ----------

elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Here is your black & white strip, just printed! Download it, or keep taking more photos.</p>", unsafe_allow_html=True)

    try:
        # Convert all photos to BW and add polaroid-style frame
        resized_photos = []
        for p in st.session_state.photos:
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            pol = make_polaroid(bw, photo_size=(640,640), bottom_extra=60, border_px=10, caption_text="", frame_color=(0,0,0))
            resized_photos.append(pol)

        # Add a random message to the last photo with extra bottom space
        messages = ["Happy 6 months!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby"]
        last_message = random.choice(messages)
        last_photo = resized_photos[-1]
        extra_border = 60  # extra space at bottom for the message
        new_h = last_photo.height + extra_border
        photo_with_border = Image.new("RGB", (last_photo.width, new_h), (0,0,0))  # black background
        photo_with_border.paste(last_photo, (0,0))

        draw = ImageDraw.Draw(photo_with_border)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 28)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0,0), last_message, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((last_photo.width - w)//2, last_photo.height + (extra_border - h)//2),
                  last_message, fill=(245,235,220), font=font)

        resized_photos[-1] = photo_with_border

        # Create the vertical strip
        strip = make_strip(resized_photos, gap=18, background=(0,0,0))

        # Convert strip to Base64 for animation
        buf = io.BytesIO()
        strip.save(buf, format="PNG")
        base64_img = base64.b64encode(buf.getvalue()).decode()

        html_code = f"""
        <div style="position: relative; width: fit-content; margin: auto; overflow: hidden; height: {strip.height + 20}px; background-color: #000;">
            <img src="data:image/png;base64,{base64_img}" 
                 style="
                    display: block; 
                    width: auto; 
                    animation: slideDown 1.2s ease-out forwards;
                    transform: translateY(-{strip.height}px);
                 "/>
        </div>
        <style>
        @keyframes slideDown {{
            0% {{ transform: translateY(-{strip.height}px); }}
            100% {{ transform: translateY(0); }}
        }}
        </style>
        """
        st.markdown(html_code, unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="Download Photobooth Strip (PNG)",
            data=buf.getvalue(),
            file_name="photobooth_strip.png",
            mime="image/png"
        )

        # Retake/Add New Strip buttons
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

        # Back to Home button
        if st.button("🏠 Back to Home"):
            st.session_state.photos = []
            st.session_state.last_camera_image = None
            st.session_state.stage = "landing"
            st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
