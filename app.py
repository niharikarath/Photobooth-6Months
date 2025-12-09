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
    width: 150px;
    height: 135px;
    position: absolute;
    box-shadow: 0 4px 8px rgba(0,0,0,0.8);
}

/* Enter button container */
.enter-container {
    margin-top: 50px;
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: #a71d2a !important;
    color: #f5e7dc !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 25px 60px !important;
    font-size: 85px !important;
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
    
   if st.session_state.stage == "landing":

    st.markdown("""
    <style>
    /* Red card in center */
    .photobooth-card {
        background-color: #a71d2a;
        border-radius: 20px;
        padding: 60px 40px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        max-width: 400px;
        margin: 120px auto;
        text-align: center;
        position: relative;
    }

    /* Love text scattered around */
    .love-script {
        font-family: 'Pinyon Script', cursive;
        color: #a71d2a;
        font-size: 2rem;
        display: inline-block;
        position: absolute;
        white-space: nowrap;
    }
    .love1 { top: 50px; left: 50px; transform: rotate(-3deg); }
    .love2 { top: 120px; right: 60px; transform: rotate(3deg); }
    .love3 { bottom: 120px; left: 60px; transform: rotate(-5deg); }
    .love4 { bottom: 50px; right: 80px; transform: rotate(5deg); }

    /* Images scattered around the card */
    .decor-img {
        width: 150px;
        height: auto;
        position: absolute;
    }
    .img1 { top: 20px; left: -20px; transform: rotate(-6deg); }
    .img2 { top: 60px; right: -40px; transform: rotate(6deg); }
    .img3 { bottom: 50px; left: 10px; transform: rotate(-10deg); }
    .img4 { bottom: 60px; right: 20px; transform: rotate(8deg); }

    /* Button inside card */
    div.stButton > button {
        background-color: #f5e7dc !important;
        color: #a71d2a !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 25px 60px !important;
        font-size: 28px !important;
    }
    div.stButton > button:hover {
        background-color: #fff0e8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Love texts
    st.markdown("""
    <div class="love-script love1">I can’t wait to kiss you in a photobooth one day</div>
    <div class="love-script love2">I love you so much, Aditya</div>
    <div class="love-script love3">Best boyfriend</div>
    <div class="love-script love4">Happy 6 months, my love</div>
    """, unsafe_allow_html=True)

    # Images
    st.markdown(f"""
    <img class="decor-img img1" src="{img_to_datauri('1.png')}" />
    <img class="decor-img img2" src="{img_to_datauri('2.png')}" />
    <img class="decor-img img3" src="{img_to_datauri('3.png')}" />
    <img class="decor-img img4" src="{img_to_datauri('4.png')}" />
    """, unsafe_allow_html=True)

    # Red card with button inside
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)

    if st.button("📸 Click to Enter the Photobooth"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Done Page ----------
elif st.session_state.stage == "done":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>✨ Your Photobooth Strip is Ready</h2>", unsafe_allow_html=True)

    try:
        strip_images = []
        for i, p in enumerate(st.session_state.photos):
            bw = bw_transform(p, contrast=1.15, sharpness=1.05)
            extra_bottom = 80 if i == len(st.session_state.photos) - 1 else 0
            img_w, img_h = bw.size
            new_img = Image.new("RGB", (img_w, img_h + extra_bottom), (0,0,0))
            new_img.paste(bw, (0,0))
            strip_images.append(new_img)

        messages = ["Happy 6 months My Love!", "Niharika loves Aditya", "Adi baby <3 Nihoo baby", "Aditya loves Niharika", "Happy 6 Crazy Months Together", "Bandar Baby 🐒 ❤️ Sundar Baby 🐰"]
        last_message = random.choice(messages)

        last_img = strip_images[-1]
        if extra_bottom > 0:
            draw = ImageDraw.Draw(last_img)
            try:
               font = ImageFont.truetype("PinyonScript-Regular.ttf", 100)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0,0), last_message, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(
                ((last_img.width - w)//2, last_img.height - extra_bottom + (extra_bottom - h)//2),
                last_message,
                fill=(245,235,220),
                font=font
            )

        total_h = sum(im.height for im in strip_images)
        strip_w = max(im.width for im in strip_images)
        final_strip = Image.new("RGB", (strip_w, total_h), (0,0,0))
        y = 0
        for im in strip_images:
            final_strip.paste(im, (0, y))
            y += im.height

        buf = io.BytesIO()
        final_strip.save(buf, format="PNG")

        st.image(final_strip, caption="Your Photobooth Strip is ready", use_column_width=True)

        st.download_button(
            label="Download Photobooth Strip (PNG)",
            data=buf.getvalue(),
            file_name="photobooth_strip.png",
            mime="image/png"
        )

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Make Another?"):
                st.session_state.photos = []
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()
        with col2:
            if st.button("Add a New Strip"):
                st.session_state.last_camera_image = None
                st.session_state.stage = "capture"
                st.rerun()

        if st.button("🏠 Back to Home"):
            st.session_state.photos = []
            st.session_state.last_camera_image = None
            st.session_state.stage = "landing"
            st.rerun()

    except Exception as e:
        st.error(f"Error creating the strip: {e}")

    st.markdown("</div>", unsafe_allow_html=True)






