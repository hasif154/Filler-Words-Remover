import streamlit as st
import subprocess
import tempfile
import os

import imageio_ffmpeg
import os

os.environ["FFMPEG_BINARY"] = imageio_ffmpeg.get_ffmpeg_exe()


# Page config (MUST be first)
st.set_page_config(page_title="Filler Words Remover", page_icon="🎬")

# UI polish
st.markdown("""
<style>
.stButton>button {
  background-color: #4f46e5;
  color: white;
  border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎬 Filler Words Remover")
st.markdown("Remove *uh, um,* and awkward pauses from your videos automatically.")
st.caption("Works best for talking-head videos, podcasts, interviews.")

st.divider()

# Upload
uploaded_file = st.file_uploader(
    "Upload a video",
    type=["mp4", "mov", "mkv"]
)

preset = st.selectbox(
    "Choose preset",
    ["Podcast (aggressive)", "YouTube (balanced)", "Lecture (light)"]
)

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, uploaded_file.name)
        output_path = os.path.join(tmp, "cleaned.mp4")

        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        if st.button("🚀 Remove Filler Words", use_container_width=True):
            st.info("Processing… this may take a minute.")

            if preset == "Podcast (aggressive)":
                margin = "0.1s"
            elif preset == "YouTube (balanced)":
                margin = "0.25s"
            else:
                margin = "0.4s"

            cmd = [
                "auto-editor",
                input_path,
                "--edit", "speech",
                "--margin", margin,
                "--output", output_path
            ]

            result = subprocess.run(cmd, shell=True)

            if result.returncode != 0:
                st.error("Processing failed. Check FFmpeg / Auto-Editor install.")
            else:
                st.success("Done ✨")
                st.video(output_path)

                with open(output_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download cleaned video",
                        f,
                        file_name="cleaned.mp4",
                        use_container_width=True
                    )
else:
    st.info("👆 Upload a video to get started")

st.divider()
st.caption("Built with Auto-Editor + FFmpeg (same core logic as CapCut & Premiere)")
