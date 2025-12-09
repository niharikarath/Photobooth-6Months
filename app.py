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
    border-radius: 4px;
    padding: 40px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    max-width: 780px;
    margin: 60px auto;
    text-align: center;
    position: relative;
}

/* Container for spreading the romantic text nicely */
.love-container {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    padding: 10px 0;
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
    margin-top: 200px;
}

/* Buttons */
div.stButton > button, div.stDownloadButton > button {
    background-color: #a71d2a !important;
    color: #f5e7dc !important;
    border-radius: 140px !important;
    font-weight: 700 !important;
    padding: 25px 60px !important;
    font-size: 220px !important;
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
        border-radius: 150px;
        padding: 60px 40px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        max-width: 800px;
        margin: 120px auto;
        text-align: center;
        position: center;
        overflow: visible;
    }


    /* Romantic text scattered */
    .love-script {
        font-family: 'Pinyon Script', cursive;
        color: #a71d2a;
        font-size: 3rem;
        display: inline-block;
        position: relative;
        white-space: nowrap;
    }

    /* Positions for each love line */
    .love1 { top: 200px; left: 40px; transform: rotate(-3deg); }
    .love2 { top: 100px; right: 70px; transform: rotate(3deg); }
    .love3 { top: 250px; left: 100px; transform: rotate(-5deg); }
    .love4 { top: 180px; right: 130px; transform: rotate(5deg); }

    /* Scattered landing images */
    .polaroid-img {
        width: 135px;
        height: 135px;
        position: absolute;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }

    </style>
    """, unsafe_allow_html=True)

    # Photobooth Card Begin
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)

    # Romantic Text
    st.markdown("""
<div class="love-container">
    <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
    <div class="love-script">I love you so much, Aditya</div>
    <div class="love-script">Best boyfriend</div>
    <div class="love-script">Happy 6 months, my love</div>
</div>
""", unsafe_allow_html=True)

    # Scattered Images

  st.markdown(f"""
<!-- Top-left image -->
<img src="{img_to_datauri('1.png')}" style="width:160px; top:40px; left:-140px; transform:rotate(-5deg);" />

<!-- Top-right image -->
<img src="{img_to_datauri('2.png')}" style="width:160px; top:20px; right:-140px; transform:rotate(5deg);" />

<!-- Middle-left image -->
<img src="{img_to_datauri('3.png')}" style="width:160px; top:180px; left:-160px; transform:rotate(-3deg);" />

<!-- Middle-right image -->
<img src="{img_to_datauri('4.png')}" style="width:160px; top:180px; right:-160px; transform:rotate(3deg);" />

<!-- Bottom-left image -->
<img src="{img_to_datauri('5.png')}" style="width:160px; bottom:60px; left:-120px; transform:rotate(4deg);" />

<!-- Bottom-right image -->
<img src="{img_to_datauri('6.png')}" style="width:160px; bottom:60px; right:-120px; transform:rotate(-4deg);" />
""", unsafe_allow_html=True)


    # ---- Centered Enter Button ----
    st.markdown("""
    <style>
    .enter-container {
        display: flex;
        justify-content: center;
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="enter-container">', unsafe_allow_html=True)
    if st.button("📸 Click to Enter the Photobooth"):
        st.session_state.stage = "capture"
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Photobooth Card End
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Capture Page ----------
elif st.session_state.stage == "capture":
    st.markdown('<div class="photobooth-card">', unsafe_allow_html=True)
    st.markdown("<h2>Photobooth — Take 4 photos</h2>", unsafe_allow_html=True)

    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            if i < len(st.session_state.photos):
                st.image(st.session_state.photos[i], width=140, caption=f"#{i+1}")
            else:
                st.image(Image.new("RGB",(500,500),(200,200,200)), width=140, caption=f"#{i+1}")

    cam_file = st.camera_input("Smile! Click the camera button to take a photo.", key="camera_input")
    if cam_file is not None:
        st.session_state.last_camera_image = pil_from_streamlit_uploaded(cam_file)

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add Photo to Strip", key="add_photo"):
            if st.session_state.last_camera_image is None:
                st.warning("Take a photo first using the camera above.")
            elif len(st.session_state.photos) >= 4:
                st.info("You already have 4 photos. Click 'Create Your Strip'.")
            else:
                st.session_state.photos.append(st.session_state.last_camera_image.copy())
                st.session_state.last_camera_image = None
                st.rerun()

    with col2:
        if st.button("Retake Last Photo", key="retake"):
            if st.session_state.photos:
                st.session_state.photos.pop()
                st.warning("Removed last photo.")
            else:
                st.warning("No photos yet.")
            st.session_state.last_camera_image = None
            st.rerun()

    with col3:
        if st.button("Create Your Strip", key="create_strip"):
            if len(st.session_state.photos) < 4:
                st.warning(f"Take {4 - len(st.session_state.photos)} more photo(s).")
            else:
                st.session_state.stage = "done"
                st.rerun()

    if st.button("🏠 Return to Home"):
        st.session_state.photos = []
        st.session_state.last_camera_image = None
        st.session_state.stage = "landing"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

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













