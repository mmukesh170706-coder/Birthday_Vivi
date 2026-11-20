import html

import streamlit as st
import streamlit.components.v1 as components

import config
from utils.helpers import BASE_DIR, load_css, image_to_data_uri, time_until_birthday

# ---------- Page setup ----------
st.set_page_config(
    page_title=f"Happy Birthday {config.FRIEND_NAME}! 🎂",
    page_icon="🎂",
    layout="centered",
)

# ---------- Global styling ----------
st.markdown(f"<style>{load_css('styles/style.css')}</style>", unsafe_allow_html=True)

# ---------- Session state ----------
st.session_state.setdefault("opened", False)
st.session_state.setdefault("celebrate", False)
st.session_state.setdefault("current_slide", "main")   # "main", "funny_slide", "secret_slide"
st.session_state.setdefault("ask_funny_pwd", False)
st.session_state.setdefault("wish_made", False)
st.session_state.setdefault("ask_secret_pwd", False)
st.session_state.setdefault("secret_substep", 1)       # 1 = Polaroid frame, 2 = Full letter


def scroll_to_top():
    """Smoothly scroll to the top when entering a new slide."""
    components.html(
        "<script>window.parent.document.querySelector('section.main').scrollTo(0, 0);</script>",
        height=0,
    )


# ============================================================
# 1. GATE — the surprise intro
# ============================================================
if not st.session_state.opened:
    st.markdown(
        f"""
<div class="gate fade-in">
  <div class="gate-gift">🎁</div>
  <h1 class="gate-title">Hey {html.escape(config.FRIEND_NAME)}...</h1>
  <p class="gate-sub">Someone special made something just for you 💖</p>
</div>
""",
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1, 1])
    with col:
        if st.button("🎉 Open My Surprise", use_container_width=True):
            st.session_state.opened = True
            st.session_state.celebrate = True
            st.rerun()
    st.stop()

# ---------- Floating hearts (shown across all slides) ----------
hearts_data = [
    (5, 0, 10, "💖"), (18, 3, 13, "💗"), (32, 1, 9, "💕"),
    (47, 5, 12, "💖"), (63, 2, 11, "💘"), (78, 4, 14, "💗"), (92, 0, 10, "💕"),
]
hearts = "".join(
    f'<span class="heart" style="left:{x}%;animation-delay:{d}s;animation-duration:{t}s">{e}</span>'
    for x, d, t, e in hearts_data
)
st.markdown(hearts, unsafe_allow_html=True)

# ---------- Background music (kept at top so it plays across slides) ----------
music_path = BASE_DIR / config.MUSIC_FILE
if music_path.exists():
    st.markdown(
        f'<div class="now-playing">🎵 Now playing: {html.escape(config.SONG_TITLE)}</div>',
        unsafe_allow_html=True,
    )
    st.audio(str(music_path), format="audio/mp3", autoplay=True, loop=True)
else:
    st.info(f"🎵 Add your song at `{config.MUSIC_FILE}` to play background music!")


# ============================================================
# SLIDE A: FUNNY PHOTO SLIDE (New Slide after Password)
# ============================================================
if st.session_state.current_slide == "funny_slide":
    scroll_to_top()
    st.balloons()

    funny = next((p for p in config.PHOTOS if p.get("funny")), None)
    st.markdown(
        '<h2 class="section-title">😂 Unlocked: The Funniest Moment!</h2>',
        unsafe_allow_html=True,
    )

    if funny and (BASE_DIR / config.PHOTO_DIR / funny["file"]).exists():
        funny_src = image_to_data_uri(f"{config.PHOTO_DIR}/{funny['file']}")
        st.markdown(
            f"""
<div class="polaroid-frame">
  <img src="{funny_src}" alt="Funny photo"/>
  <div class="polaroid-title">Sorry Vivitha! 😂💖</div>
  <div class="polaroid-caption">{html.escape(funny["caption"])}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    _, back_col, _ = st.columns([1, 2, 1])
    with back_col:
        if st.button("⬅️ Back to Birthday Page", use_container_width=True):
            st.session_state.current_slide = "main"
            st.rerun()

    st.stop()


# ============================================================
# SLIDE B: SECRET MESSAGE SLIDE (New Slide after Make a Wish + Password)
# ============================================================
if st.session_state.current_slide == "secret_slide":
    scroll_to_top()

    st.markdown(
        f'<h2 class="section-title">💌 Secret Slide for {html.escape(config.FRIEND_NAME)}</h2>',
        unsafe_allow_html=True,
    )

    # Sub-step 1: Show the Fairy-Lights Polaroid Photo first
    if st.session_state.secret_substep == 1:
        final_photo_path = BASE_DIR / config.PHOTO_DIR / config.FINAL_NOTE_PHOTO
        if final_photo_path.exists():
            polaroid_src = image_to_data_uri(f"{config.PHOTO_DIR}/{config.FINAL_NOTE_PHOTO}")
            st.markdown(
                f"""
<div class="polaroid-frame">
  <img src="{polaroid_src}" alt="Fairy lights memory"/>
  <div class="polaroid-title">{html.escape(config.FINAL_NOTE_TITLE)}</div>
  <div class="polaroid-caption">{html.escape(config.FINAL_NOTE_CAPTION)}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        _, mid_btn, _ = st.columns([1, 2, 1])
        with mid_btn:
            if st.button("📜 Unfold & Read My Secret Letter", use_container_width=True):
                st.session_state.secret_substep = 2
                st.rerun()
            if st.button("⬅️ Back to Birthday Page", use_container_width=True):
                st.session_state.current_slide = "main"
                st.rerun()

    # Sub-step 2: Show the Unfolded Heartfelt Tanglish Note
    elif st.session_state.secret_substep == 2:
        st.balloons()

        paragraphs = "".join(
            f'<p style="animation-delay:{idx * 0.25:.2f}s">{html.escape(line)}</p>'
            for idx, line in enumerate(config.FINAL_NOTE)
        )
        st.markdown(
            f"""
<div class="final-note">
  <div class="final-note-badge">💌✨</div>
  <h3>{html.escape(config.FINAL_NOTE_TITLE)}</h3>
  {paragraphs}
  <p class="sign">— Always your friend, {html.escape(config.YOUR_NAME)} 🫶</p>
</div>
""",
            unsafe_allow_html=True,
        )

        voice_path = BASE_DIR / config.VOICE_MESSAGE_FILE
        if voice_path.exists():
            st.markdown(
                '<div class="now-playing" style="margin-top:1.8rem;">🎙️ Listen to my voice note for you:</div>',
                unsafe_allow_html=True,
            )
            st.audio(str(voice_path), format="audio/mp3")

        _, back_col2, _ = st.columns([1, 2, 1])
        with back_col2:
            if st.button("📸 Back to Fairy-Lights Photo", use_container_width=True):
                st.session_state.secret_substep = 1
                st.rerun()
            if st.button("⬅️ Back to Main Birthday Page", use_container_width=True):
                st.session_state.current_slide = "main"
                st.rerun()

    st.stop()


# ============================================================
# SLIDE C: MAIN BIRTHDAY PAGE
# ============================================================
if st.session_state.celebrate:
    st.balloons()
    st.session_state.celebrate = False

# ---------- Hero ----------
st.markdown(
    f"""
<div class="hero fade-in">
  <div class="hero-tag">for my favourite person</div>
  <h1 class="hero-title">Happy Birthday</h1>
  <h2 class="hero-name">{html.escape(config.FRIEND_NAME)} 🎂</h2>
  <p class="hero-sub">{html.escape(config.HERO_SUBTITLE)}</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- Countdown ----------
st.markdown('<h2 class="section-title">⏳ Countdown to Your Day</h2>', unsafe_allow_html=True)

remaining = time_until_birthday(config.BIRTHDAY_MONTH, config.BIRTHDAY_DAY)
if remaining is None:
    countdown_html = '<div class="count-today">🥳 Today is YOUR day! 🥳</div>'
else:
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    countdown_html = (
        '<div class="countdown">'
        f'<div class="count-box"><b>{days}</b><span>Days</span></div>'
        f'<div class="count-box"><b>{hours}</b><span>Hours</span></div>'
        f'<div class="count-box"><b>{minutes}</b><span>Minutes</span></div>'
        "</div>"
    )
st.markdown(countdown_html, unsafe_allow_html=True)

# ---------- Photo gallery ----------
st.markdown('<h2 class="section-title">📸Ithulam yaru nu theriutha?😂</h2>', unsafe_allow_html=True)

cards = []
for i, photo in enumerate(config.PHOTOS):
    if photo.get("funny"):
        continue  # the funny photo has its own slide
    photo_file = BASE_DIR / config.PHOTO_DIR / photo["file"]
    if not photo_file.exists():
        continue
    src = image_to_data_uri(f"{config.PHOTO_DIR}/{photo['file']}")
    caption = html.escape(photo["caption"])
    cards.append(
        f'<div class="card" style="animation-delay:{i * 0.12:.2f}s">'
        f'<img src="{src}" alt="memory {i + 1}"/>'
        f'<div class="caption">{caption}</div>'
        "</div>"
    )
gallery_body = "".join(cards)
st.markdown(f'<div class="gallery">{gallery_body}</div>', unsafe_allow_html=True)

# ============================================================
# 😂 FUNNY PHOTO BUTTON -> ASKS PASSWORD -> OPENS NEXT SLIDE
# ============================================================
funny = next((p for p in config.PHOTOS if p.get("funny")), None)
if funny and (BASE_DIR / config.PHOTO_DIR / funny["file"]).exists():
    st.markdown('<h2 class="section-title">😂 The Funniest Moment</h2>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if not st.session_state.ask_funny_pwd:
            if st.button("👀 Click only if you're ready...", use_container_width=True):
                st.session_state.ask_funny_pwd = True
                st.rerun()
        else:
            st.markdown(
                f"""
<div class="lock-card fade-in">
  <div class="lock-icon">🤪🔒</div>
  <div class="lock-title">Enter Password for Next Slide</div>
  <div class="lock-hint">{html.escape(config.FUNNY_PHOTO_HINT)}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            funny_pwd = st.text_input(
                "Enter Funny Photo Password",
                type="password",
                placeholder="Type password...",
                label_visibility="collapsed",
                key="funny_pwd_box",
            )
            if st.button("🔓 Unlock & Enter Funny Slide and Return to the Page & Continue➡️", use_container_width=True):
                if funny_pwd.strip().lower() == config.FUNNY_PHOTO_PASSWORD.strip().lower():
                    st.session_state.current_slide = "funny_slide"
                    st.rerun()
                else:
                    st.error(f"❌ Wrong password! {config.FUNNY_PHOTO_HINT}")

# ---------- Short Birthday Wish ----------
st.markdown('<h2 class="section-title">💌 A Birthday Wish For You</h2>', unsafe_allow_html=True)
letter_paragraphs = "".join(
    f"<p>{html.escape(line.format(name=config.FRIEND_NAME))}</p>"
    for line in config.LOVE_LETTER
)
st.markdown(
    f'<div class="glass letter">{letter_paragraphs}'
    f'<p class="sign">— {html.escape(config.YOUR_NAME)} 💖</p></div>',
    unsafe_allow_html=True,
)

# ============================================================
# 🌠 MAKE A WISH -> REVEALS "SECRET MSG" BUTTON -> PASSWORD -> NEW SLIDE
# ============================================================
st.markdown('<h2 class="section-title">🌠 Make a Wish</h2>', unsafe_allow_html=True)
_, mid2, _ = st.columns([1, 2, 1])
with mid2:
    if st.button("✨ Make a wish & blow the candles", use_container_width=True):
        st.session_state.wish_made = True
        st.balloons()
        st.snow()

    if st.session_state.wish_made:
        st.success(f"Wish received! I hope it comes true, {config.FRIEND_NAME} 💫")

        # Step 1 after Make a Wish: Show the "Secret Message" button
        if not st.session_state.ask_secret_pwd:
            if st.button("💌 Click to Open Secret Message 🔐", use_container_width=True):
                st.session_state.ask_secret_pwd = True
                st.rerun()

        # Step 2 after clicking Secret Message button: Ask password & open in new slide
        else:
            st.markdown(
                f"""
<div class="secret-vault fade-in" style="margin-top: 1rem;">
  <div class="secret-badge">🔒 For {html.escape(config.FRIEND_NAME)} Only</div>
  <div class="envelope-icon">💌</div>
  <div class="secret-title">One Last Secret Slide</div>
  <p class="secret-sub">Enter the secret password to enter the final slide 🥹💛</p>
  <div class="lock-hint" style="margin-top:0.6rem;">{html.escape(config.SECRET_NOTE_HINT)}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            secret_pwd = st.text_input(
                "Enter Secret Note Password",
                type="password",
                placeholder="Enter password (DDMM)...",
                label_visibility="collapsed",
                key="secret_pwd_box",
            )
            if st.button("🗝️ Unlock & Enter Secret Slide ➡️", use_container_width=True):
                if secret_pwd.strip().lower() == config.SECRET_NOTE_PASSWORD.strip().lower():
                    st.session_state.secret_substep = 1
                    st.session_state.current_slide = "secret_slide"
                    st.rerun()
                else:
                    st.error(f"❌ Wrong password! {config.SECRET_NOTE_HINT}")

# ---------- Footer ----------
st.markdown(
    f'<div class="footer">Made with 💖 by {html.escape(config.YOUR_NAME)} for {html.escape(config.FRIEND_NAME)}</div>',
    unsafe_allow_html=True,
)