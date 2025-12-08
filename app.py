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
    st.markdown("""
    <!-- Import handwriting font -->
    <link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">

    <style>
    .stApp {
        background-color: #f3e5d0;
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    .photobooth-card {
        background-color: #f3e5d0;
        border: 4px solid #a71d2a;
        border-radius: 20px;
        padding: 60px;
        max-width: 820px;
        margin: 80px auto;
        text-align: center;
        position: relative;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .photobooth-card h1 {
        color: #111;
        font-size: 3rem;
        margin-bottom: 15px;
    }
    .love-script {
        font-family: 'Pinyon Script', cursive;
        color: #a71d2a;
        font-size: 2.2rem;
        margin: 8px 0;
    }
    .polaroid-img {
        width: 85px;
        height: 85px;
        position: absolute;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }

    /* Central button spacing — full 5cm (~190px) radius empty area */
    .enter-container {
        margin-top: 80px;
        margin-bottom: 80px;
        padding: 190px 0;
    }

    div.stButton > button {
        background-color: #a71d2a !important;
        color: #f5e7dc !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        padding: 22px 60px !important;
        font-size: 26px !important;
        transition: 0.3s !important;
        border: 2px solid #7d101c !important;
    }
    div.stButton > button:hover {
        background-color: #c8323b !important;
    }
    </style>

    <div class="photobooth-card">
        <h1>📸 Enter the Photobooth</h1>

        <!-- Romantic statements -->
        <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
        <div class="love-script">I love you so much, Aditya</div>
        <div class="love-script">Best boyfriend</div>
        <div class="love-script">Happy 6 months, my love</div>

        <!-- Scattered PNGs -->
        <img src="https://i.imgur.com/OJkZlYQ.png" class="polaroid-img" style="top:15px; left:20px; transform: rotate(-6deg);" />
        <img src="https://i.imgur.com/4aF0FQy.png" class="polaroid-img" style="top:40px; right:20px; transform: rotate(7deg);" />
        <img src="https://i.imgur.com/Y8VjL2D.png" class="polaroid-img" style="bottom:30px; left:40px; transform: rotate(-9deg);" />
        <img src="https://i.imgur.com/e9elZQZ.png" class="polaroid-img" style="bottom:55px; right:45px; transform: rotate(10deg);" />
        <img src="https://i.imgur.com/7wa0a2b.png" class="polaroid-img" style="top:160px; left:-10px; transform: rotate(4deg);" />
        <img src="https://i.imgur.com/JmYq5iC.png" class="polaroid-img" style="top:180px; right:-10px; transform: rotate(-3deg);" />

        <!-- 5cm radius space reserved for the big button -->
        <div class="enter-container"></div>
    </div>
    """, unsafe_allow_html=True)

    # Button OUTSIDE the markdown, positioned below the empty space
    if st.button("Enter Photobooth", key="enter"):
        st.session_state.photos = []
        st.session_state.stage = "capture"
        st.rerun()

# ---------- UI: Done ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Here is your strip, just printed! Download it, or keep taking more photos.</p>", unsafe_allow_html=True)

    try:
        strip_images = []
        for i, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            # For the last photo, add extra space at bottom for message
            if i == len(st.session_state.photos) - 1:
                extra_bottom = 80
            else:
                extra_bottom = 0
            img_w, img_h = bw.size
            new_img = Image.new("RGB", (img_w, img_h + extra_bottom), (0,0,0))
            new_img.paste(bw, (0,0))
            strip_images.append(new_img)

        # Add a random message on the extra bottom of the last photo
        messages = ["Happy 6 months!", "Niharika loves Aditya", "Adi baby ❤️ Nihoo baby"]
        last_message = random.choice(messages)
        last_img = strip_images[-1]
        if extra_bottom > 0:
            draw = ImageDraw.Draw(last_img)
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0,0), last_message, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(((last_img.width - w)//2, last_img.height - extra_bottom + (extra_bottom - h)//2),
                      last_message, fill=(245,235,220), font=font)

        # Combine all images vertically into a strip
        total_h = sum(im.height for im in strip_images)
        strip_w = max(im.width for im in strip_images)
        final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
        y = 0
        for im in strip_images:
            final_strip.paste(im, (0, y))
            y += im.height

        # Convert to Base64 for slide-down animation
        buf = io.BytesIO()
        final_strip.save(buf, format="PNG")
        base64_img = base64.b64encode(buf.getvalue()).decode()

        html_code = f"""
        <div style="position: relative; width: fit-content; margin: auto; overflow: hidden; height: {final_strip.height}px; background-color: #000;">
            <img src="data:image/png;base64,{base64_img}" 
                 style="
                    display: block; 
                    width: auto; 
                    animation: slideDown 1.2s ease-out forwards;
                    transform: translateY(-{final_strip.height}px);
                 "/>
        </div>
        <style>
        @keyframes slideDown {{
            0% {{ transform: translateY(-{final_strip.height}px); }}
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

        # Buttons
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

        # Back to Home
        if st.button("🏠 Back to Home"):
            st.session_state.photos = []
            st.session_state.last_camera_image = None
            st.session_state.stage = "landing"
            st.rerun()

    except Exception as e:
        st.error(f"Something went wrong while creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

