"""
Filler Words Remover - REAL Word-Level Detection
Uses Whisper AI to detect and remove actual filler words like "uh", "um", "hmm"
Plus removes silent pauses for tight, professional videos.
"""

import streamlit as st
import whisper
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import tempfile
import os
from pathlib import Path
import re

# Get FFmpeg from imageio_ffmpeg
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_PATH
    
    # Add FFmpeg directory to PATH so Whisper and other tools can find it
    ffmpeg_bin = Path(FFMPEG_PATH)
    ffmpeg_dir = ffmpeg_bin.parent
    
    # CRITICAL: Whisper specifically looks for 'ffmpeg' command.
    # imageio-ffmpeg provides something like 'ffmpeg-win64-v4.4.exe'.
    # We need an 'ffmpeg.exe' in that directory.
    target_ffmpeg = ffmpeg_dir / "ffmpeg.exe"
    if not target_ffmpeg.exists():
        try:
            # Try creating a hardlink or symlink first (faster)
            import ctypes
            if hasattr(os, 'link'):
                os.link(str(ffmpeg_bin), str(target_ffmpeg))
            else:
                import shutil
                shutil.copy2(str(ffmpeg_bin), str(target_ffmpeg))
        except Exception:
            # Fallback to copy if link fails
            import shutil
            shutil.copy2(str(ffmpeg_bin), str(target_ffmpeg))
            
    if str(ffmpeg_dir) not in os.environ["PATH"]:
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ["PATH"]
except ImportError:
    FFMPEG_PATH = None

# Custom CSS
st.markdown("""
<style>
button {
  background-color: #4f46e5 !important;
  color: white !important;
}
div[data-testid="stMetricValue"] {
  font-size: 1.5rem;
}
.stProgress > div > div > div > div {
  background-color: #4f46e5;
}
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🎬 Filler Words Remover")
st.markdown("### Remove 'uh', 'um', 'hmm' and awkward pauses from your videos")
st.caption("Works best for talking-head videos, podcasts, interviews.")

st.divider()

# Define filler words patterns
DEFAULT_FILLERS = ["uh", "um", "uhm", "umm", "hmm", "hm", "er", "ah", "eh"]

import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(f"🏃 Running on: **{device.upper()}**")
    
    # Filler word selection
    st.subheader("🗣️ Filler Words to Remove")
    
    col1, col2 = st.columns(2)
    with col1:
        remove_uh = st.checkbox("uh / uhh", value=True)
        remove_um = st.checkbox("um / umm", value=True)
        remove_hmm = st.checkbox("hmm / hm", value=True)
    with col2:
        remove_er = st.checkbox("er / err", value=True)
        remove_ah = st.checkbox("ah / ahh", value=True)
        remove_like = st.checkbox("like", value=False, help="Careful - may remove intentional 'like'")
    
    # Build active filler list
    active_fillers = ["uh", "uhh", "ugh", "um", "umm", "uhm", "hmm", "hm", "mmm", "mm", "er", "err", "erm", "ah", "ahh", "aah"]
    if remove_like: active_fillers.append("like")
    
    # Filter list based on checkboxes (more robust)
    selected_fillers = []
    if remove_uh: selected_fillers.extend(["uh", "uhh", "ugh"])
    if remove_um: selected_fillers.extend(["um", "umm", "uhm"])
    if remove_hmm: selected_fillers.extend(["hmm", "hm", "mmm", "mm"])
    if remove_er: selected_fillers.extend(["er", "err", "erm"])
    if remove_ah: selected_fillers.extend(["ah", "ahh", "aah"])
    if remove_like: selected_fillers.append("like")
    
    st.divider()
    
    # Margin control
    st.subheader("✂️ Cut Settings")
    margin = st.slider(
        "Margin (seconds)",
        min_value=0.0,
        max_value=0.5,
        value=0.1,
        step=0.05,
        help="Buffer around cuts. Increase if video feels too jumpy."
    )
    
    min_silence = st.slider(
        "Min silence to cut (seconds)",
        min_value=0.3,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Pauses shorter than this are kept"
    )
    
    st.divider()
    
    # Model selection
    st.subheader("🧠 AI Model")
    model_size = st.selectbox(
        "Whisper model",
        options=["tiny", "base", "small", "medium"],
        index=1,
        help="Larger = more accurate but slower. 'base' is recommended."
    )
    
    st.caption(f"**Active fillers:** {', '.join(active_fillers) if active_fillers else 'None'}")

# Helper functions
def is_filler_word(word: str, filler_list: list) -> bool:
    """Check if a word matches any filler pattern"""
    word_clean = re.sub(r'[^\w]', '', word.lower().strip())
    return word_clean in filler_list

def merge_segments(segments: list, min_gap: float = 0.05) -> list:
    """Merge overlapping or very close segments"""
    if not segments:
        return []
    
    segments = sorted(segments, key=lambda x: x[0])
    merged = [segments[0]]
    
    for start, end in segments[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + min_gap:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    
    return merged

def find_segments_to_keep(transcription, filler_list: list, margin: float, video_duration: float):
    """Find which segments of video to keep (non-filler words)"""
    segments_to_keep = []
    
    for segment in transcription.get('segments', []):
        words = segment.get('words', [])
        
        if not words:
            # Fallback: if no word-level timestamps, use segment level
            text = segment.get('text', '').strip().lower()
            is_filler = any(filler in text for filler in filler_list)
            if not is_filler and text:
                start = max(0, segment['start'] - margin)
                end = min(video_duration, segment['end'] + margin)
                segments_to_keep.append((start, end))
        else:
            for word_info in words:
                word = word_info.get('word', '')
                if not is_filler_word(word, filler_list):
                    start = max(0, word_info['start'] - margin)
                    end = min(video_duration, word_info['end'] + margin)
                    segments_to_keep.append((start, end))
    
    return merge_segments(segments_to_keep)

# Main content
st.header("📤 Upload Your Video")

uploaded_file = st.file_uploader(
    "Choose a video file",
    type=["mp4", "mov", "avi", "mkv", "webm"],
    help="Supported: MP4, MOV, AVI, MKV, WebM"
)

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.success(f"✅ **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
    
    with st.expander("👁️ Preview Original", expanded=False):
        st.video(uploaded_file)
    
    if st.button("🚀 Remove Filler Words", type="primary", use_container_width=True):
        
        if not active_fillers:
            st.warning("⚠️ No filler words selected. Check the sidebar settings.")
            st.stop()
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded video
            input_path = temp_path / f"input{Path(uploaded_file.name).suffix}"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Progress tracking
            progress = st.progress(0)
            status = st.empty()
            
            # Initialize variables for cleanup
            video = None
            final_video = None
            clips = []
            
            try:
                # Step 1: Load video
                st.info("📹 Loading video...")
                progress.progress(5)
                video = VideoFileClip(str(input_path))
                original_duration = video.duration
                
                # Step 2: Extract audio for Whisper
                st.info("🎵 Extracting audio...")
                progress.progress(10)
                audio_path = temp_path / "audio.wav"
                
                # Ensure we release the audio file handle
                if video.audio:
                    video.audio.write_audiofile(
                        str(audio_path),
                        codec='pcm_s16le',
                        fps=16000,
                        nbytes=2,
                        logger=None
                    )
                else:
                    st.error("❌ No audio track found in video.")
                    st.stop()
                
                # Step 3: Load Whisper model
                st.info(f"🧠 Loading Whisper ({model_size}) on {device.upper()}...")
                progress.progress(20)
                model = whisper.load_model(model_size, device=device)
                
                # Step 4: Transcribe with word timestamps
                st.info("📝 Transcribing speech (this takes a while)...")
                progress.progress(30)
                result = model.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    language="en",
                    initial_prompt="uh, um, hmm, er, ah, okay, so, like"
                )
                
                # Step 5: Find filler words
                st.info("🔍 Detecting filler words...")
                progress.progress(60)
                
                # Count fillers found
                filler_count = 0
                filler_instances = []
                for segment in result.get('segments', []):
                    for word_info in segment.get('words', []):
                        word = word_info.get('word', '')
                        if is_filler_word(word, selected_fillers):
                            filler_count += 1
                            filler_instances.append({
                                'word': word.strip(),
                                'start': word_info['start'],
                                'end': word_info['end']
                            })
                
                # Step 6: Find segments to keep
                st.info("✂️ Planning cuts...")
                progress.progress(70)
                segments_to_keep = find_segments_to_keep(
                    result, 
                    selected_fillers, 
                    margin, 
                    video.duration
                )
                
                if not segments_to_keep:
                    st.error("❌ No valid segments found. Video might be all fillers or transcription failed.")
                    st.stop()
                
                # Step 7: Create clips
                st.info("🎬 Creating clips...")
                progress.progress(80)
                for start, end in segments_to_keep:
                    if end > start + 0.05:  # Min 50ms clip
                        try:
                            # MoviePy 2.x uses subclipped
                            clip = video.subclipped(start, min(end, video.duration))
                            clips.append(clip)
                        except Exception:
                            continue 
                
                if not clips:
                    st.error("❌ Failed to create video clips.")
                    st.stop()
                
                # Step 8: Concatenate
                st.info("🔗 Joining clips...")
                progress.progress(85)
                final_video = concatenate_videoclips(clips, method="compose")
                
                # Step 9: Export
                st.info("💾 Exporting video...")
                progress.progress(90)
                output_path = temp_path / "output.mp4"
                final_video.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
                
                progress.progress(100)
                
                # Calculate stats
                new_duration = final_video.duration
                time_saved = original_duration - new_duration
                
                # Success Logic
                st.success("🎉 **Processing complete!**")
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Original", f"{original_duration:.1f}s")
                with col2:
                    st.metric("New", f"{new_duration:.1f}s")
                with col3:
                    st.metric("Saved", f"{time_saved:.1f}s")
                with col4:
                    st.metric("Fillers Found", f"{filler_count}")
                
                # Show detected fillers
                if filler_instances:
                    with st.expander(f"📋 Detected {filler_count} filler words", expanded=False):
                        for i, f in enumerate(filler_instances[:20]):  # Show first 20
                            st.text(f"{i+1}. '{f['word']}' at {f['start']:.2f}s - {f['end']:.2f}s")
                        if len(filler_instances) > 20:
                            st.text(f"... and {len(filler_instances) - 20} more")
                
                # Show processed video
                st.subheader("📹 Processed Video")
                with open(output_path, "rb") as f:
                    video_bytes = f.read()
                st.video(video_bytes)
                
                # Download button
                output_name = f"cleaned_{Path(uploaded_file.name).stem}.mp4"
                st.download_button(
                    "⬇️ Download Cleaned Video",
                    data=video_bytes,
                    file_name=output_name,
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🔍 Full Error"):
                    st.code(traceback.format_exc())
            finally:
                # CRITICAL FOR WINDOWS: Always close all clips to release file locks
                if video:
                    video.close()
                if final_video:
                    final_video.close()
                for clip in clips:
                    try:
                        clip.close()
                    except:
                        pass
                
                # Explicitly delete objects to encourage garbage collection
                del video
                del final_video
                del clips

else:
    st.info("👆 Upload a video to get started")
    
    st.divider()
    
    st.subheader("🧪 How to Test Properly")
    st.markdown("""
    **Use videos with:**
    - 🗣️ **"uh / um / hmm"** — actual filler sounds
    - ⏸️ **Long pauses** — thinking moments
    - 💬 **Natural speech** — podcasts, interviews, vlogs
    
    **💡 If cuts feel too tight →** increase the margin
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ What This Does")
        st.markdown("""
        - Transcribes with Whisper AI
        - Detects word-level fillers
        - Cuts "uh", "um", "hmm", etc.
        - Preserves good content
        """)
    with col2:
        st.subheader("⚡ Tech Stack")
        st.markdown("""
        - **Whisper** — OpenAI speech-to-text
        - **MoviePy** — Video editing
        - **Streamlit** — Web UI
        """)

# Footer
st.divider()
st.caption("Built with Whisper AI • Word-level filler detection • 100% free")
