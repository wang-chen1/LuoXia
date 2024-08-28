import uvicorn
from loguru import logger

from luoxia.app.config import CONF

if __name__ == "__main__":
    logger.info(
        "start server, docs: http://127.0.0.1:" + str(CONF.listen_port) + "/docs"
    )
    uvicorn.run(
        app="app.asgi:app",
        host=CONF.listen_host,
        port=CONF.listen_port,
        reload=CONF.reload_debug,
        log_level="warning",
    )
