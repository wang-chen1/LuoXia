import os
import platform
import subprocess
from pathlib import Path
from luoxia.app.utils import utils
from luoxia.app.config import CONF, LOG, ROOT_DIR
from luoxia import constans
from luoxia.app.services import llm, task as tm, voice
from luoxia.app.models.schema import MaterialInfo, VideoAspect, VideoConcatMode, ResourceType
from uuid import uuid4
from luoxia.app import __version__


def get_resource(resource: ResourceType):
    folder_path = Path(ROOT_DIR)
    folder_path = folder_path.joinpath("resource", resource.name)
    return list(folder_path.rglob(f'*.{resource.value}'))


def open_task_folder(task_id):
    try:
        sys = platform.system()
        folder_path = Path(ROOT_DIR)
        folder_path = folder_path.joinpath("storage", "tasks", task_id)
        if folder_path.exists():
            if sys == "Windows":
                subprocess.run(['start', f'{folder_path}'])
            if sys == "Darwin":
                subprocess.run(['open', f'{folder_path}'])
    except Exception as e:
        LOG.error(e)


def scroll_to_bottom(st):
    js = """
        <script>
            console.log("scroll_to_bottom");
            function scroll(dummy_var_to_force_repeat_execution){
                var sections = parent.document.querySelectorAll('section.main');
                console.log(sections);
                for(let index = 0; index<sections.length; index++) {
                    sections[index].scrollTop = sections[index].scrollHeight;
                }
            }
            scroll(1);
        </script>
    """
    st.components.v1.html(js, height=0, width=0)


def base_page_config(st):
    st.set_page_config(
        page_title="luoxia",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={},
    )
    hide_streamlit_style = """
    <style>#root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}</style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.title(f"luoxia {__version__}")
    if "video_subject" not in st.session_state:
        st.session_state["video_subject"] = ""
    if "video_script" not in st.session_state:
        st.session_state["video_script"] = ""
    if "video_terms" not in st.session_state:
        st.session_state["video_terms"] = ""
    if "ui_language" not in st.session_state:
        st.session_state["ui_language"] = utils.get_system_locale()
    return st


i18n_dir = ROOT_DIR.joinpath('webui', 'i18')


def tr(key):
    locales = utils.load_locales(i18n_dir)
    loc = locales.get(CONF.ui.language, {})
    return loc.get("Translation", {}).get(key, key)


def basic_settings(st):
    locales = utils.load_locales(i18n_dir)
    with st.expander(tr("Basic Settings"), expanded=False):
        config_panels = st.columns(3)
        left_config_panel = config_panels[0]
        middle_config_panel = config_panels[1]
        right_config_panel = config_panels[2]
        # print(left_config_panel, middle_config_panel, right_config_panel)
        with left_config_panel:
            display_languages = []
            selected_index = 0
            for i, code in enumerate(locales.keys()):
                display_languages.append(f"{code} - {locales[code].get('Language')}")
                if code == st.session_state["ui_language"]:
                    selected_index = i

            selected_language = st.selectbox(
                tr("Language"),
                options=display_languages,
                index=selected_index,
            )
            if selected_language:
                code = selected_language.split(" - ")[0].strip()
                st.session_state["ui_language"] = code

            # checkout hide log
            hide_log = st.checkbox(tr("Hide Log"), value=CONF.default.hide_log)
            CONF.default.hide_log = hide_log

        with middle_config_panel:
            saved_llm_provider = CONF.default.llm_provider
            saved_llm_provider_index = 0
            for i, provider in enumerate(constans.LLM_PROVIDERS):
                if provider.lower() == saved_llm_provider:
                    saved_llm_provider_index = i
                    break

            llm_provider = st.selectbox(
                tr("LLM Provider"),
                options=constans.LLM_PROVIDERS,
                index=saved_llm_provider_index,
            )
            llm_helper = st.container()
            llm_provider = llm_provider.lower()
            CONF.default.llm_provider = llm_provider

            llm_api_key = CONF.default.api_key
            llm_secret_key = CONF.default.secret_key
            llm_base_url = CONF.default.base_url
            llm_model_name = CONF.default.model_name
            llm_account_id = CONF.default.account_id

            tips = ""
            if llm_provider == "ollama":
                if not llm_model_name:
                    llm_model_name = "qwen:7b"
                if not llm_base_url:
                    llm_base_url = "http://localhost:11434/v1"

                with llm_helper:
                    tips = constans.OLLAMA_HELPER

            if llm_provider == "openai":
                if not llm_model_name:
                    llm_model_name = "gpt-3.5-turbo"
                with llm_helper:
                    tips = constans.OPENAI_HELPER

            if llm_provider == "moonshot":
                if not llm_model_name:
                    llm_model_name = "moonshot-v1-8k"
                with llm_helper:
                    tips = constans.MOOSHOT_HELPER
            if llm_provider == "oneapi":
                if not llm_model_name:
                    llm_model_name = "claude-3-5-sonnet-20240620"  # 默认模型，可以根据需要调整
                with llm_helper:
                    tips = constans.ONE_HELPER

            if llm_provider == "qwen":
                if not llm_model_name:
                    llm_model_name = "qwen-max"
                with llm_helper:
                    tips = constans.QWEN_HELPER

            if llm_provider == "g4f":
                if not llm_model_name:
                    llm_model_name = "gpt-3.5-turbo"
                with llm_helper:
                    tips = constans.G4F_HELPER

            if llm_provider == "azure":
                with llm_helper:
                    tips = constans.AZURE_HELPER

            if llm_provider == "gemini":
                if not llm_model_name:
                    llm_model_name = "gemini-1.0-pro"

                with llm_helper:
                    tips = constans.GEMINI_HELPER

            if llm_provider == "deepseek":
                if not llm_model_name:
                    llm_model_name = "deepseek-chat"
                if not llm_base_url:
                    llm_base_url = "https://api.deepseek.com"
                with llm_helper:
                    tips = constans.DEEPSEEK_HELPER

            if llm_provider == "ernie":
                with llm_helper:
                    tips = constans.ERNIE_HELPER

            if tips and CONF.ui.language == "zh":
                st.warning(
                    "中国用户建议使用 **DeepSeek** 或 **Moonshot** 作为大模型提供商\n- 国内可直接访问，不需要VPN \n"
                    "- 注册就送额度，基本够用",
                )
                st.info(tips)

            st_llm_api_key = st.text_input(tr("API Key"), value=llm_api_key, type="password")
            st_llm_base_url = st.text_input(tr("Base Url"), value=llm_base_url)
            st_llm_model_name = ""
            if llm_provider != "ernie":
                st_llm_model_name = st.text_input(
                    tr("Model Name"),
                    value=llm_model_name,
                    key=f"{llm_provider}_model_name_input",
                )
                if st_llm_model_name:
                    CONF.default.model_name = st_llm_model_name
            else:
                st_llm_model_name = None

            if st_llm_api_key:
                CONF.default.api_key = st_llm_api_key
            if st_llm_base_url:
                CONF.default.base_url = st_llm_base_url
            if st_llm_model_name:
                CONF.default.model_name = st_llm_model_name
            if llm_provider == "ernie":
                st_llm_secret_key = st.text_input(
                    tr("Secret Key"),
                    value=llm_secret_key,
                    type="password",
                )
                CONF.default.secret_key = st_llm_secret_key

            if llm_provider == "cloudflare":
                st_llm_account_id = st.text_input(tr("Account ID"), value=llm_account_id)
                if st_llm_account_id:
                    CONF.default.account_id = st_llm_account_id

        with right_config_panel:

            pexels_api_key = CONF.video.api_keys
            pexels_api_key = st.text_input(
                tr("Pexels API Key"),
                value=pexels_api_key,
                type="password",
            )

            pixabay_api_key = CONF.video.api_keys
            pixabay_api_key = st.text_input(
                tr("Pixabay API Key"),
                value=pixabay_api_key,
                type="password",
            )


def left_panel_settings(st, panel, params):
    left_panel = panel[0]
    with left_panel:
        with st.container(border=True):
            st.write(tr("Video Script Settings"))
            params.video_subject = st.text_input(
                tr("Video Subject"),
                value=st.session_state["video_subject"],
            ).strip()

            video_languages = [
                (tr("Auto Detect"), ""),
            ]
            for code in constans.SUPPORT_LOCALES:
                video_languages.append((code, code))

            selected_index = st.selectbox(
                tr("Script Language"),
                index=0,
                options=range(len(video_languages)),  # 使用索引作为内部选项值
                format_func=lambda x: video_languages[x][0],  # 显示给用户的是标签
            )
            params.video_language = video_languages[selected_index][1]

            if st.button(tr("Generate Video Script and Keywords"), key="auto_generate_script"):
                with st.spinner(tr("Generating Video Script and Keywords")):
                    script = llm.generate_script(
                        video_subject=params.video_subject,
                        language=params.video_language,
                    )
                    terms = llm.generate_terms(params.video_subject, script)
                    st.session_state["video_script"] = script
                    st.session_state["video_terms"] = ", ".join(terms)

            params.video_script = st.text_area(
                tr("Video Script"),
                value=st.session_state["video_script"],
                height=280,
            )
            if st.button(tr("Generate Video Keywords"), key="auto_generate_terms"):
                if not params.video_script:
                    st.error(tr("Please Enter the Video Subject"))
                    st.stop()

                with st.spinner(tr("Generating Video Keywords")):
                    terms = llm.generate_terms(params.video_subject, params.video_script)
                    st.session_state["video_terms"] = ", ".join(terms)

            params.video_terms = st.text_area(
                tr("Video Keywords"),
                value=st.session_state["video_terms"],
                height=50,
            )


def middle_panel_settings(st, panel, params):
    middle_panel = panel[1]
    with middle_panel:
        with st.container(border=True):
            st.write(tr("Video Settings"))
            video_concat_modes = [
                (tr("Sequential"), "sequential"),
                (tr("Random"), "random"),
            ]
            video_sources = [
                (tr("Pexels"), "pexels"),
                (tr("Pixabay"), "pixabay"),
                (tr("Local file"), "local"),
                (tr("TikTok"), "douyin"),
                (tr("Bilibili"), "bilibili"),
                (tr("Xiaohongshu"), "xiaohongshu"),
            ]

            saved_video_source_name = CONF.video.video_source
            saved_video_source_index = [v[1] for v in video_sources].index(saved_video_source_name)

            selected_index = st.selectbox(
                tr("Video Source"),
                options=range(len(video_sources)),
                format_func=lambda x: video_sources[x][0],
                index=saved_video_source_index,
            )
            params.video_source = video_sources[selected_index][1]
            CONF.video.video_source = params.video_source

            if params.video_source == "local":
                _supported_types = constans.FILE_TYPE_VIDEOS + constans.FILE_TYPE_IMAGES
                uploaded_files = st.file_uploader(
                    "Upload Local Files",
                    type=["mp4", "mov", "avi", "flv", "mkv", "jpg", "jpeg", "png"],
                    accept_multiple_files=True,
                )

            selected_index = st.selectbox(
                tr("Video Concat Mode"),
                index=1,
                options=range(len(video_concat_modes)),  # 使用索引作为内部选项值
                format_func=lambda x: video_concat_modes[x][0],  # 显示给用户的是标签
            )
            params.video_concat_mode = VideoConcatMode(video_concat_modes[selected_index][1])

            video_aspect_ratios = [
                (tr("Portrait"), VideoAspect.portrait.value),
                (tr("Landscape"), VideoAspect.landscape.value),
            ]
            selected_index = st.selectbox(
                tr("Video Ratio"),
                options=range(len(video_aspect_ratios)),  # 使用索引作为内部选项值
                format_func=lambda x: video_aspect_ratios[x][0],  # 显示给用户的是标签
            )
            params.video_aspect = VideoAspect(video_aspect_ratios[selected_index][1])

            params.video_clip_duration = st.selectbox(
                tr("Clip Duration"),
                options=[2, 3, 4, 5, 6, 7, 8, 9, 10],
                index=1,
            )
            params.video_count = st.selectbox(
                tr("Number of Videos Generated Simultaneously"),
                options=[1, 2, 3, 4, 5],
                index=0,
            )
        with st.container(border=True):
            st.write(tr("Audio Settings"))

            # tts_providers = ['edge', 'azure']
            # tts_provider = st.selectbox(tr("TTS Provider"), tts_providers)

            voices = voice.get_all_azure_voices(filter_locals=constans.SUPPORT_LOCALES)
            friendly_names = {
                v: v.replace("Female", tr("Female")).replace("Male", tr("Male")).replace("Neural", "")
                for v in voices
            }
            saved_voice_name = CONF.ui.voice_name
            saved_voice_name_index = 0
            if saved_voice_name in friendly_names:
                saved_voice_name_index = list(friendly_names.keys()).index(saved_voice_name)
            else:
                for i, v in enumerate(voices):
                    if (
                        v.lower().startswith(st.session_state["ui_language"].lower())
                        and "V2" not in v
                    ):
                        saved_voice_name_index = i
                        break

            selected_friendly_name = st.selectbox(
                tr("Speech Synthesis"),
                options=list(friendly_names.values()),
                index=saved_voice_name_index,
            )

            voice_name = list(friendly_names.keys())[
                list(friendly_names.values()).index(selected_friendly_name)
            ]
            params.voice_name = voice_name
            CONF.ui.voice_name = voice_name

            if st.button(tr("Play Voice")):
                play_content = params.video_subject
                if not play_content:
                    play_content = params.video_script
                if not play_content:
                    play_content = tr("Voice Example")
                with st.spinner(tr("Synthesizing Voice")):
                    temp_dir = utils.get_create_storage_dir("temp", create=True)
                    audio_file = Path(temp_dir).joinpath(constans.VOICE_TEMP_PATH)
                    sub_maker = voice.tts(
                        text=play_content,
                        voice_name=voice_name,
                        voice_rate=params.voice_rate,
                        voice_file=audio_file,
                    )
                    # if the voice file generation failed, try again with a default content.
                    if not sub_maker:
                        play_content = "This is a example voice. if you hear this, the voice synthesis failed with the original content."
                        sub_maker = voice.tts(
                            text=play_content,
                            voice_name=voice_name,
                            voice_rate=params.voice_rate,
                            voice_file=audio_file,
                        )

                    if sub_maker:
                        st.audio(audio_file, format="audio/mp3")
                        
                        audio_file.rmdir()

            if voice.is_azure_v2_voice(voice_name):
                saved_azure_speech_region = CONF.azure.speech_region
                saved_azure_speech_key = CONF.azure.speech_key
                azure_speech_region = st.text_input(
                    tr("Speech Region"),
                    value=saved_azure_speech_region,
                )
                azure_speech_key = st.text_input(
                    tr("Speech Key"),
                    value=saved_azure_speech_key,
                    type="password",
                )
                CONF.azure.speech_region = azure_speech_region
                CONF.azure.speech_key = azure_speech_key

            params.voice_volume = st.selectbox(
                tr("Speech Volume"),
                options=[0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0],
                index=2,
            )

            params.voice_rate = st.selectbox(
                tr("Speech Rate"),
                options=[0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0],
                index=2,
            )

            bgm_options = [
                (tr("No Background Music"), ""),
                (tr("Random Background Music"), "random"),
                (tr("Custom Background Music"), "custom"),
            ]
            selected_index = st.selectbox(
                tr("Background Music"),
                index=1,
                options=range(len(bgm_options)),  # 使用索引作为内部选项值
                format_func=lambda x: bgm_options[x][0],  # 显示给用户的是标签
            )
            # 获取选择的背景音乐类型
            params.bgm_type = bgm_options[selected_index][1]

            # 根据选择显示或隐藏组件
            if params.bgm_type == "custom":
                custom_bgm_file = st.text_input(tr("Custom Background Music File"))
                if custom_bgm_file and os.path.exists(custom_bgm_file):
                    params.bgm_file = custom_bgm_file
                    # st.write(f":red[已选择自定义背景音乐]：**{custom_bgm_file}**")
            params.bgm_volume = st.selectbox(
                tr("Background Music Volume"),
                options=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                index=2,
            )


def right_panel_settings(st, panel, params):
    right_panel = panel[2]
    with right_panel:
        with st.container(border=True):
            st.write(tr("Subtitle Settings"))
            params.subtitle_enabled = st.checkbox(tr("Enable Subtitles"), value=True)
            font_names = get_resource(ResourceType.fonts)
            saved_font_name = CONF.ui.font_name
            saved_font_name_index = 0
            if saved_font_name in font_names:
                saved_font_name_index = font_names.index(saved_font_name)
            params.font_name = st.selectbox(tr("Font"), font_names, index=saved_font_name_index)
            CONF.ui.font_name = params.font_name

            subtitle_positions = [
                (tr("Top"), "top"),
                (tr("Center"), "center"),
                (tr("Bottom"), "bottom"),
                (tr("Custom"), "custom"),
            ]
            selected_index = st.selectbox(
                tr("Position"),
                index=2,
                options=range(len(subtitle_positions)),
                format_func=lambda x: subtitle_positions[x][0],
            )
            params.subtitle_position = subtitle_positions[selected_index][1]

            if params.subtitle_position == "custom":
                custom_position = st.text_input(tr("Custom Position (% from top)"), value="70.0")
                try:
                    params.custom_position = float(custom_position)
                    if params.custom_position < 0 or params.custom_position > 100:
                        st.error(tr("Please enter a value between 0 and 100"))
                except ValueError:
                    st.error(tr("Please enter a valid number"))

            font_cols = st.columns([0.3, 0.7])
            with font_cols[0]:
                saved_text_fore_color = CONF.ui.text_fore_color
                params.text_fore_color = st.color_picker(tr("Font Color"), saved_text_fore_color)
                CONF.ui.text_fore_color = params.text_fore_color

            with font_cols[1]:
                saved_font_size = CONF.ui.font_size
                params.font_size = st.slider(tr("Font Size"), 30, 100, saved_font_size)
                CONF.ui.font_size = params.font_size

            stroke_cols = st.columns([0.3, 0.7])
            with stroke_cols[0]:
                params.stroke_color = st.color_picker(tr("Stroke Color"), "#000000")
            with stroke_cols[1]:
                params.stroke_width = st.slider(tr("Stroke Width"), 0.0, 10.0, 1.5)


def start_button_setting(st, params, uploaded_files: list):
    start_button = st.button(tr("Generate Video"), use_container_width=True, type="primary")
    if start_button:
        # config.save_config()
        task_id = str(uuid4())
        if not params.video_subject and not params.video_script:
            st.error(tr("Video Script and Subject Cannot Both Be Empty"))
            scroll_to_bottom(st)
            st.stop()

        if CONF.default.llm_provider != "g4f" and not CONF.default.api_key:
            st.error(tr("Please Enter the LLM API Key"))
            scroll_to_bottom(st)
            st.stop()

        if params.video_source not in ["pexels", "pixabay", "local"]:
            st.error(tr("Please Select a Valid Video Source"))
            scroll_to_bottom(st)
            st.stop()

        if params.video_source == "pexels" and not CONF.video.api_keys:
            st.error(tr("Please Enter the Pexels API Key"))
            scroll_to_bottom(st)
            st.stop()

        if params.video_source == "pixabay" and not CONF.video.api_keys:
            st.error(tr("Please Enter the Pixabay API Key"))
            scroll_to_bottom(st)
            st.stop()

        if uploaded_files:
            local_videos_dir = utils.get_create_storage_dir("local_videos", create=True)
            for file in uploaded_files:
                file_path = os.path.join(local_videos_dir, f"{file.file_id}_{file.name}")
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                    m = MaterialInfo()
                    m.provider = "local"
                    m.url = file_path
                    if not params.video_materials:
                        params.video_materials = []
                    params.video_materials.append(m)

        log_container = st.empty()
        log_records = []

        def log_received(msg):
            if CONF.default.hide_log:
                return
            with log_container:
                log_records.append(msg)
                st.code("\n".join(log_records))

        LOG.add(log_received)

        st.toast(tr("Generating Video"))
        LOG.info(tr("Start Generating Video"))
        LOG.info(utils.to_json(params))
        scroll_to_bottom(st)

        result = tm.start(task_id=task_id, params=params)
        if not result or "videos" not in result:
            st.error(tr("Video Generation Failed"))
            LOG.error(tr("Video Generation Failed"))
            scroll_to_bottom(st)
            st.stop()

        video_files = result.get("videos", [])
        st.success(tr("Video Generation Completed"))
        try:
            if video_files:
                player_cols = st.columns(len(video_files) * 2 + 1)
                for i, url in enumerate(video_files):
                    player_cols[i * 2 + 1].video(url)
        except Exception:
            pass

        open_task_folder(task_id)
        LOG.info(tr("Video Generation Completed"))
        scroll_to_bottom(st)
