import streamlit as st

st.set_page_config(page_title="Photobooth", layout="centered")

# SESSION STATE
if "stage" not in st.session_state:
    st.session_state.stage = "landing"


# ---------------- LANDING PAGE ----------------

if st.session_state.stage == "landing":

    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&display=swap" rel="stylesheet">

    <style>
        .stApp {
            background-color: #f3e5d0 !important;
        }

        .photobooth-card {
            background-color: #f3e5d0;
            border: 4px solid #a71d2a;
            border-radius: 20px;
            padding: 50px;
            width: 900px;
            margin: 60px auto;
            text-align: center;
            position: relative;
            box-shadow: 0 8px 25px rgba(0,0,0,0.35);
        }

        .love-script {
            font-family: 'Pinyon Script', cursive;
            color: #a71d2a;
            font-size: 2.4rem;
            margin: 15px 0;
            position: relative;
            z-index: 5;
        }

        .polaroid-img {
            width: 95px;
            height: 95px;
            position: absolute;
            box-shadow: 0 4px 8px rgba(0,0,0,0.35);
            border-radius: 6px;
            z-index: 3;
        }

        .enter-container {
            margin-top: 120px;
            margin-bottom: 40px;
        }

        div.stButton > button {
            background-color: #a71d2a !important;
            color: #fff7ef !important;
            border-radius: 18px !important;
            padding: 22px 65px !important;
            font-size: 28px !important;
            font-weight: 800 !important;
            border: 2px solid #7d101c !important;
            cursor: pointer !important;
        }

        div.stButton > button:hover {
            background-color: #c93a40 !important;
        }

    </style>

    <div class="photobooth-card">

        <div class="love-script">I can’t wait to kiss you in a photobooth one day</div>
        <div class="love-script">I love you so much, Aditya</div>
        <div class="love-script">Best boyfriend</div>
        <div class="love-script">Happy 6 months, my love</div>

        <!-- Scattered Images -->
        <img src="1.png" class="polaroid-img" style="top:20px; left:20px; transform:rotate(-6deg);" />
        <img src="2.png" class="polaroid-img" style="top:40px; right:20px; transform:rotate(6deg);" />
        <img src="3.png" class="polaroid-img" style="bottom:40px; left:30px; transform:rotate(-10deg);" />
        <img src="4.png" class="polaroid-img" style="bottom:50px; right:40px; transform:rotate(8deg);" />
        <img src="5.png" class="polaroid-img" style="top:150px; left:-15px; transform:rotate(4deg);" />
        <img src="6.png" class="polaroid-img" style="top:170px; right:-10px; transform:rotate(-4deg);" />

        <div class="enter-container"></div>
    </div>

    """, unsafe_allow_html=True)

    if st.button("Enter Photobooth"):
        st.session_state.stage = "next"
        st.rerun()


# ---------------- NEXT PAGE (just to verify button works) ----------------
if st.session_state.stage == "next":
    st.title("🎉 Inside the Photobooth!")
    st.write("The button works and the HTML loaded correctly.")
