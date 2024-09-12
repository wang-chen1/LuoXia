import streamlit as st

from luoxia.app.config import CONF, ROOT_DIR, LOG
from luoxia.app.models.schema import VideoParams
from luoxia.webui import tool
from luoxia.app.config.log import setup as log_setup

# Add the root directory of the project to the system path to allow importing modules from the project
# if ROOT_DIR not in sys.path:
#     sys.path.append(ROOT_DIR)
#     print("******** sys.path ********")
#     print(sys.path)
#     print("")


# print(f"******** system locale: {system_locale} ********")


# system_locale = utils.get_system_locale()

# llm_provider = CONF.default.llm_provider

# config.save_config()

if __name__ == "__main__":
    LOG.info("start streamlit")
    log_dir = ROOT_DIR.joinpath("log")
    if log_dir.exists() is False:
        log_dir.mkdir()
    log_setup(
        log_dir.joinpath("streamlit.log"),
        debug=CONF.default.log_level,
    )
    tool.base_page_config(st)

    if st.session_state["ui_language"]: CONF.ui.language
    if not CONF.default.hide_config:
        tool.basic_settings(st)
    panel = st.columns(3)
    params = VideoParams(video_subject="")
    uploaded_files = []
    tool.left_panel_settings(st, panel, params)
    tool.middle_panel_settings(st, panel, params)
    tool.right_panel_settings(st, panel, params)
    tool.start_button_setting(st, params, uploaded_files)
    st.write(tool.tr("Get Help"))