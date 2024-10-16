import streamlit as st

from luoxia.app.config import CONF, ROOT_DIR, LOG
from luoxia.app.models.schema import VideoParams
from luoxia.streamlit_web import tool
from luoxia.app.config.log import setup as log_setup


if __name__ == "__main__":
    LOG.info("start streamlit")
    log_dir = ROOT_DIR.joinpath("log")
    if log_dir.exists() is False:
        log_dir.mkdir()
    log_setup(
        log_dir.joinpath("streamlit.log"),
        debug=CONF.default.log_level,
    )
    LOG.info("log init success")
    tool.base_page_config(st)
    LOG.info("base page config success")
    if st.session_state["ui_language"]: CONF.ui.language
    if not CONF.default.hide_config:
        tool.basic_settings(st)
    panel = st.columns(3)
    left_panel, middle_panel, right_panel = panel
    params = VideoParams(video_subject="")
    uploaded_files = []
    # st.write(tool.tr("Get Help"))
    
    with left_panel:
        tool.left_panel_settings(st, params)
    with middle_panel:
        tool.middle_panel_settings(st, params)
    with right_panel:
        tool.right_panel_settings(st, params)

    start_button = st.button(tool.tr("Generate Video"), use_container_width=True, type="primary")
    if start_button:
        tool.start_button_setting(st, params, uploaded_files)
    