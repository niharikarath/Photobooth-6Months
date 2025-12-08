# app.py
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import random

st.set_page_config(page_title="Photobooth — 6 Monthiversary", page_icon="📸", layout="centered")

# ---------- Styling ----------
st.markdown(
    """
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "stage" not in st.session_state:
    st.session_state.stage = "landing"  # landing, capture, done
if "photos" not in st.session_state:
    st.session_state.photos = []  # list of PIL Images
if "last_camera_image" not in st.session_state:
    st.session_state.last_camera_image = None

# ---------- Helper functions ----------
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
    """
    Wrap a square image into a polaroid frame (white border, larger bottom margin).
    Returns a PIL Image.
    """
    # Resize and crop to square keeping aspect
    photo = ImageOps.fit(photo, photo_size, Image.LANCZOS)
    # Create frame
    frame_w = photo_size[0] + border_px*2
    frame_h = photo_size[1] + border_px*2 + bottom_extra
    frame = Image.new("RGB", (frame_w, frame_h), frame_color)
    # Paste photo
    frame.paste(photo, (border_px, border_px))
    # Add thin border line (subtle)
    draw = ImageDraw.Draw(frame)
    draw.rectangle([0,0,frame_w-1, frame_h-1], outline=(200,200,200), width=1)
    # Add caption text if provided
    if caption_text:
        try:
            # Use a fallback font
            font = ImageFont.truetype("DejaVuSans.ttf", size=28)
        except Exception:
            font = ImageFont.load_default()
        w, h = draw.textsize(caption_text, font=font)
        text_x = (frame_w - w) // 2
        text_y = photo_size[1] + border_px + (bottom_extra - h) // 2
        draw.text((text_x, text_y), caption_text, fill=(80,80,80), font=font)
    return frame

def make_strip(polaroids, gap=18, background=(245,245,246)):
    """
    Stack polaroid frames vertically into a single strip with small gaps.
    polaroids: list of PIL images (all same width).
    """
    widths = [im.width for im in polaroids]
    assert len(set(widths)) == 1, "All polaroids must be same width"
    w = widths[0]
    total_h = sum(im.height for im in polaroids) + gap*(len(polaroids)-1)
    strip = Image.new("RGB", (w, total_h), background)
    y = 0
    for im in polaroids:
        # small random tilt for authentic look
        angle = random.uniform(-4, 4)
        rotated = im.rotate(angle, expand=True, fillcolor=background)
        # paste centered
        x = (w - rotated.width) // 2
        strip.paste(rotated, (x, y), rotated.convert("RGBA"))
        y += rotated.height + gap
    return strip

def bw_transform(img: Image.Image, contrast=1.1, sharpness=1.1):
    """Convert to stylish black & white"""
    gray = ImageOps.grayscale(img)
    # convert back to RGB so polaroid is RGB
    rgb = gray.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    # subtle film grain (optional)
    return rgb

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
            st.experimental_rerun()
    with col2:
        st.write("")
        st.write("")
        st.markdown("<small class='muted'>Want help with layout or fonts? I can add captions, sound, or an auto-timer.</small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- UI: Capture ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2 class='center'>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted center'>Click the camera icon to open your webcam. Take 4 photos — try different expressions.</p>", unsafe_allow_html=True)
    st.write("")

    # Show count & thumbnails of already taken photos
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB", (500,500), (240,240,240)), width=140, caption=f"#{i+1}")

    st.write("")
    # Camera input: returns a file-like object when a photo is taken.
    cam_file = st.camera_input("Smile 😄 — click the camera button below to take a picture", key="camera_input")

    if cam_file is not None:
        # convert to PIL and store temporarily (but only add when user clicks "Add to strip")
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    # Buttons to add photo / retake
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add Photo to Strip", key="add_photo"):
            if st.session_state.last_camera_image is None:
                st.warning("Take a picture first using the camera control above.")
            elif len(st.session_state.photos) >= 4:
                st.info("You already have 4 photos. Click 'Create Polaroid Strip'.")
            else:
                st.session_state.photos.append(st.session_state.last_camera_image.copy())
                st.session_state.last_camera_image = None
                st.experimental_rerun()
    with col2:
        if st.button("Retake Last Photo", key="retake"):
            st.session_state.last_camera_image = None
            st.warning("Retake: use the camera control above to take a new photo.")
    with col3:
        if st.button("Create Polaroid Strip", key="create_strip"):
            if len(st.session_state.photos) < 4:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")
            else:
                st.session_state.stage = "done"
                st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- UI: Done (compose the strip) ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card center">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Polaroid Strip</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Here is your black & white strip. Download it, or print for a real polaroid feel.</p>", unsafe_allow_html=True)

    # Process photos into polaroids
    try:
        polaroids = []
        for idx, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            caption = ""  # you can add captions like "Smile #1" or a date
            pol = make_polaroid(bw, photo_size=(640,640), bottom_extra=140, border_px=10, caption_text=caption)
            polaroids.append(pol)

        # Make vertical strip
        strip = make_strip(polaroids, gap=24, background=(250,250,250))

        # Add a subtle shadow / canvas margin
        margin = 24
        canvas = Image.new("RGB", (strip.width + margin*2, strip.height + margin*2), (246,246,247))
        canvas.paste(strip, (margin, margin))

        # Show preview
        st.image(canvas, use_column_width=False, caption="Polaroid strip preview")

        # Save to bytes buffer
        buf = io.BytesIO()
        canvas.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # Download button
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
                st.experimental_rerun()
        with col2:
            if st.button("Add a New Strip (Keep these)"):
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.experimental_rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
