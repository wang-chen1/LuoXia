import sys
import platform
import subprocess
from pathlib import Path
from loguru import logger
from luoxia.app.config import ROOT_DIR
from luoxia.app.utils import utils
from luoxia.app.config import CONF
from luoxia import constans

from luoxia.app import __version__

def get_resource(resource_type: str):
    folder_path = Path(ROOT_DIR)
    folder_path = folder_path.joinpath("resource", resource_type)
    return list(folder_path.rglob('*.ttf'))


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
        logger.error(e)


def scroll_to_bottom():
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


def init_log():
    logger.remove()
    _lvl = "DEBUG"

    def format_record(record):
        # 获取日志记录中的文件全路径
        file_path = record["file"].path
        # 将绝对路径转换为相对于项目根目录的路径
        # relative_path = os.path.relpath(file_path, ROOT_DIR)
        relative_path = Path(file_path).relative_to(ROOT_DIR)
        # 更新记录中的文件路径
        record["file"].path = f"./{relative_path}"
        # 返回修改后的格式字符串
        # 您可以根据需要调整这里的格式
        print(record["message"])
        record["message"] = record["message"].replace(ROOT_DIR, ".")

        _format = (
            "<green>{time:%Y-%m-%d %H:%M:%S}</> | "
            + "<level>{level}</> | "
            + '"{file.path}:{line}":<blue> {function}</> '
            + "- <level>{message}</>"
            + "\n"
        )
        return _format

    logger.add(
        sys.stdout,
        level=_lvl,
        format=format_record,
        colorize=True,
    )


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
        print(left_config_panel, middle_config_panel, right_config_panel)
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
