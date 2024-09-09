import os
import sys
from uuid import uuid4

import streamlit as st
from loguru import logger

from luoxia import constans
from luoxia.app.config import CONF, ROOT_DIR
from luoxia.app.models.const import FILE_TYPE_IMAGES, FILE_TYPE_VIDEOS
from luoxia.app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode, VideoParams
from luoxia.app.services import llm, task as tm, voice
from luoxia.app.utils import utils
from luoxia.webui import tool

# Add the root directory of the project to the system path to allow importing modules from the project
root_dir = ROOT_DIR
# if ROOT_DIR not in sys.path:
#     sys.path.append(ROOT_DIR)
#     print("******** sys.path ********")
#     print(sys.path)
#     print("")


# print(f"******** system locale: {system_locale} ********")


# system_locale = utils.get_system_locale()

# llm_provider = CONF.default.llm_provider

# panel = st.columns(3)
# left_panel = panel[0]
# middle_panel = panel[1]
# right_panel = panel[2]

# params = VideoParams(video_subject="")
# uploaded_files = []

# with left_panel:
#     with st.container(border=True):
#         st.write(tr("Video Script Settings"))
#         params.video_subject = st.text_input(
#             tr("Video Subject"),
#             value=st.session_state["video_subject"],
#         ).strip()

#         video_languages = [
#             (tr("Auto Detect"), ""),
#         ]
#         for code in constans.SUPPORT_LOCALES:
#             video_languages.append((code, code))

#         selected_index = st.selectbox(
#             tr("Script Language"),
#             index=0,
#             options=range(len(video_languages)),  # 使用索引作为内部选项值
#             format_func=lambda x: video_languages[x][0],  # 显示给用户的是标签
#         )
#         params.video_language = video_languages[selected_index][1]

#         if st.button(tr("Generate Video Script and Keywords"), key="auto_generate_script"):
#             with st.spinner(tr("Generating Video Script and Keywords")):
#                 script = llm.generate_script(
#                     video_subject=params.video_subject,
#                     language=params.video_language,
#                 )
#                 terms = llm.generate_terms(params.video_subject, script)
#                 st.session_state["video_script"] = script
#                 st.session_state["video_terms"] = ", ".join(terms)

#         params.video_script = st.text_area(
#             tr("Video Script"),
#             value=st.session_state["video_script"],
#             height=280,
#         )
#         if st.button(tr("Generate Video Keywords"), key="auto_generate_terms"):
#             if not params.video_script:
#                 st.error(tr("Please Enter the Video Subject"))
#                 st.stop()

#             with st.spinner(tr("Generating Video Keywords")):
#                 terms = llm.generate_terms(params.video_subject, params.video_script)
#                 st.session_state["video_terms"] = ", ".join(terms)

#         params.video_terms = st.text_area(
#             tr("Video Keywords"),
#             value=st.session_state["video_terms"],
#             height=50,
#         )

# with middle_panel:
#     with st.container(border=True):
#         st.write(tr("Video Settings"))
#         video_concat_modes = [
#             (tr("Sequential"), "sequential"),
#             (tr("Random"), "random"),
#         ]
#         video_sources = [
#             (tr("Pexels"), "pexels"),
#             (tr("Pixabay"), "pixabay"),
#             (tr("Local file"), "local"),
#             (tr("TikTok"), "douyin"),
#             (tr("Bilibili"), "bilibili"),
#             (tr("Xiaohongshu"), "xiaohongshu"),
#         ]

#         saved_video_source_name = CONF.video.video_source
#         saved_video_source_index = [v[1] for v in video_sources].index(saved_video_source_name)

#         selected_index = st.selectbox(
#             tr("Video Source"),
#             options=range(len(video_sources)),
#             format_func=lambda x: video_sources[x][0],
#             index=saved_video_source_index,
#         )
#         params.video_source = video_sources[selected_index][1]
#         CONF.video.video_source = params.video_source

#         if params.video_source == "local":
#             _supported_types = FILE_TYPE_VIDEOS + FILE_TYPE_IMAGES
#             uploaded_files = st.file_uploader(
#                 "Upload Local Files",
#                 type=["mp4", "mov", "avi", "flv", "mkv", "jpg", "jpeg", "png"],
#                 accept_multiple_files=True,
#             )

#         selected_index = st.selectbox(
#             tr("Video Concat Mode"),
#             index=1,
#             options=range(len(video_concat_modes)),  # 使用索引作为内部选项值
#             format_func=lambda x: video_concat_modes[x][0],  # 显示给用户的是标签
#         )
#         params.video_concat_mode = VideoConcatMode(video_concat_modes[selected_index][1])

#         video_aspect_ratios = [
#             (tr("Portrait"), VideoAspect.portrait.value),
#             (tr("Landscape"), VideoAspect.landscape.value),
#         ]
#         selected_index = st.selectbox(
#             tr("Video Ratio"),
#             options=range(len(video_aspect_ratios)),  # 使用索引作为内部选项值
#             format_func=lambda x: video_aspect_ratios[x][0],  # 显示给用户的是标签
#         )
#         params.video_aspect = VideoAspect(video_aspect_ratios[selected_index][1])

#         params.video_clip_duration = st.selectbox(
#             tr("Clip Duration"),
#             options=[2, 3, 4, 5, 6, 7, 8, 9, 10],
#             index=1,
#         )
#         params.video_count = st.selectbox(
#             tr("Number of Videos Generated Simultaneously"),
#             options=[1, 2, 3, 4, 5],
#             index=0,
#         )
#     with st.container(border=True):
#         st.write(tr("Audio Settings"))

#         # tts_providers = ['edge', 'azure']
#         # tts_provider = st.selectbox(tr("TTS Provider"), tts_providers)

#         voices = voice.get_all_azure_voices(filter_locals=constans.SUPPORT_LOCALES)
#         friendly_names = {
#             v: v.replace("Female", tr("Female")).replace("Male", tr("Male")).replace("Neural", "")
#             for v in voices
#         }
#         saved_voice_name = CONF.ui.voice_name
#         saved_voice_name_index = 0
#         if saved_voice_name in friendly_names:
#             saved_voice_name_index = list(friendly_names.keys()).index(saved_voice_name)
#         else:
#             for i, v in enumerate(voices):
#                 if (
#                     v.lower().startswith(st.session_state["ui_language"].lower())
#                     and "V2" not in v
#                 ):
#                     saved_voice_name_index = i
#                     break

#         selected_friendly_name = st.selectbox(
#             tr("Speech Synthesis"),
#             options=list(friendly_names.values()),
#             index=saved_voice_name_index,
#         )

#         voice_name = list(friendly_names.keys())[
#             list(friendly_names.values()).index(selected_friendly_name)
#         ]
#         params.voice_name = voice_name
#         CONF.ui.voice_name = voice_name

#         if st.button(tr("Play Voice")):
#             play_content = params.video_subject
#             if not play_content:
#                 play_content = params.video_script
#             if not play_content:
#                 play_content = tr("Voice Example")
#             with st.spinner(tr("Synthesizing Voice")):
#                 temp_dir = utils.storage_dir("temp", create=True)
#                 audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid4())}.mp3")
#                 sub_maker = voice.tts(
#                     text=play_content,
#                     voice_name=voice_name,
#                     voice_rate=params.voice_rate,
#                     voice_file=audio_file,
#                 )
#                 # if the voice file generation failed, try again with a default content.
#                 if not sub_maker:
#                     play_content = "This is a example voice. if you hear this, the voice synthesis failed with the original content."
#                     sub_maker = voice.tts(
#                         text=play_content,
#                         voice_name=voice_name,
#                         voice_rate=params.voice_rate,
#                         voice_file=audio_file,
#                     )

#                 if sub_maker and os.path.exists(audio_file):
#                     st.audio(audio_file, format="audio/mp3")
#                     if os.path.exists(audio_file):
#                         os.remove(audio_file)

#         if voice.is_azure_v2_voice(voice_name):
#             saved_azure_speech_region = config.azure.get("speech_region", "")
#             saved_azure_speech_key = config.azure.get("speech_key", "")
#             azure_speech_region = st.text_input(
#                 tr("Speech Region"),
#                 value=saved_azure_speech_region,
#             )
#             azure_speech_key = st.text_input(
#                 tr("Speech Key"),
#                 value=saved_azure_speech_key,
#                 type="password",
#             )
#             config.azure["speech_region"] = azure_speech_region
#             config.azure["speech_key"] = azure_speech_key

#         params.voice_volume = st.selectbox(
#             tr("Speech Volume"),
#             options=[0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0],
#             index=2,
#         )

#         params.voice_rate = st.selectbox(
#             tr("Speech Rate"),
#             options=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0],
#             index=2,
#         )

#         bgm_options = [
#             (tr("No Background Music"), ""),
#             (tr("Random Background Music"), "random"),
#             (tr("Custom Background Music"), "custom"),
#         ]
#         selected_index = st.selectbox(
#             tr("Background Music"),
#             index=1,
#             options=range(len(bgm_options)),  # 使用索引作为内部选项值
#             format_func=lambda x: bgm_options[x][0],  # 显示给用户的是标签
#         )
#         # 获取选择的背景音乐类型
#         params.bgm_type = bgm_options[selected_index][1]

#         # 根据选择显示或隐藏组件
#         if params.bgm_type == "custom":
#             custom_bgm_file = st.text_input(tr("Custom Background Music File"))
#             if custom_bgm_file and os.path.exists(custom_bgm_file):
#                 params.bgm_file = custom_bgm_file
#                 # st.write(f":red[已选择自定义背景音乐]：**{custom_bgm_file}**")
#         params.bgm_volume = st.selectbox(
#             tr("Background Music Volume"),
#             options=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#             index=2,
#         )

# with right_panel:
#     with st.container(border=True):
#         st.write(tr("Subtitle Settings"))
#         params.subtitle_enabled = st.checkbox(tr("Enable Subtitles"), value=True)
#         font_names = get_all_fonts()
#         saved_font_name = CONF.ui.font_name
#         saved_font_name_index = 0
#         if saved_font_name in font_names:
#             saved_font_name_index = font_names.index(saved_font_name)
#         params.font_name = st.selectbox(tr("Font"), font_names, index=saved_font_name_index)
#         CONF.ui.font_name = params.font_name

#         subtitle_positions = [
#             (tr("Top"), "top"),
#             (tr("Center"), "center"),
#             (tr("Bottom"), "bottom"),
#             (tr("Custom"), "custom"),
#         ]
#         selected_index = st.selectbox(
#             tr("Position"),
#             index=2,
#             options=range(len(subtitle_positions)),
#             format_func=lambda x: subtitle_positions[x][0],
#         )
#         params.subtitle_position = subtitle_positions[selected_index][1]

#         if params.subtitle_position == "custom":
#             custom_position = st.text_input(tr("Custom Position (% from top)"), value="70.0")
#             try:
#                 params.custom_position = float(custom_position)
#                 if params.custom_position < 0 or params.custom_position > 100:
#                     st.error(tr("Please enter a value between 0 and 100"))
#             except ValueError:
#                 st.error(tr("Please enter a valid number"))

#         font_cols = st.columns([0.3, 0.7])
#         with font_cols[0]:
#             saved_text_fore_color = CONF.ui.text_fore_color
#             params.text_fore_color = st.color_picker(tr("Font Color"), saved_text_fore_color)
#             CONF.ui.text_fore_color = params.text_fore_color

#         with font_cols[1]:
#             saved_font_size = CONF.ui.font_size
#             params.font_size = st.slider(tr("Font Size"), 30, 100, saved_font_size)
#             CONF.ui.font_size = params.font_size

#         stroke_cols = st.columns([0.3, 0.7])
#         with stroke_cols[0]:
#             params.stroke_color = st.color_picker(tr("Stroke Color"), "#000000")
#         with stroke_cols[1]:
#             params.stroke_width = st.slider(tr("Stroke Width"), 0.0, 10.0, 1.5)

# start_button = st.button(tr("Generate Video"), use_container_width=True, type="primary")
# if start_button:
#     # config.save_config()
#     task_id = str(uuid4())
#     if not params.video_subject and not params.video_script:
#         st.error(tr("Video Script and Subject Cannot Both Be Empty"))
#         scroll_to_bottom()
#         st.stop()

#     if llm_provider != "g4f" and not CONF.default.api_key:
#         st.error(tr("Please Enter the LLM API Key"))
#         scroll_to_bottom()
#         st.stop()

#     if params.video_source not in ["pexels", "pixabay", "local"]:
#         st.error(tr("Please Select a Valid Video Source"))
#         scroll_to_bottom()
#         st.stop()

#     if params.video_source == "pexels" and not CONF.video.api_keys:
#         st.error(tr("Please Enter the Pexels API Key"))
#         scroll_to_bottom()
#         st.stop()

#     if params.video_source == "pixabay" and not CONF.video.api_keys:
#         st.error(tr("Please Enter the Pixabay API Key"))
#         scroll_to_bottom()
#         st.stop()

#     if uploaded_files:
#         local_videos_dir = utils.storage_dir("local_videos", create=True)
#         for file in uploaded_files:
#             file_path = os.path.join(local_videos_dir, f"{file.file_id}_{file.name}")
#             with open(file_path, "wb") as f:
#                 f.write(file.getbuffer())
#                 m = MaterialInfo()
#                 m.provider = "local"
#                 m.url = file_path
#                 if not params.video_materials:
#                     params.video_materials = []
#                 params.video_materials.append(m)

#     log_container = st.empty()
#     log_records = []

#     def log_received(msg):
#         if CONF.default.hide_log:
#             return
#         with log_container:
#             log_records.append(msg)
#             st.code("\n".join(log_records))

#     logger.add(log_received)

#     st.toast(tr("Generating Video"))
#     logger.info(tr("Start Generating Video"))
#     logger.info(utils.to_json(params))
#     scroll_to_bottom()

#     result = tm.start(task_id=task_id, params=params)
#     if not result or "videos" not in result:
#         st.error(tr("Video Generation Failed"))
#         logger.error(tr("Video Generation Failed"))
#         scroll_to_bottom()
#         st.stop()

#     video_files = result.get("videos", [])
#     st.success(tr("Video Generation Completed"))
#     try:
#         if video_files:
#             player_cols = st.columns(len(video_files) * 2 + 1)
#             for i, url in enumerate(video_files):
#                 player_cols[i * 2 + 1].video(url)
#     except Exception:
#         pass

#     open_task_folder(task_id)
#     logger.info(tr("Video Generation Completed"))
#     scroll_to_bottom()

# config.save_config()

if __name__ == "__main__":
    tool.init_log()
    tool.base_page_config(st)
    if st.session_state["ui_language"]: CONF.ui.language
    print("CONF.default.hide_config", CONF.default.hide_config)
    if not CONF.default.hide_config:
        tool.basic_settings(st)
    st.write(tool.tr("Get Help"))