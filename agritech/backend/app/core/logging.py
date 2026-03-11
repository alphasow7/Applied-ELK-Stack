import logging
import json
from datetime import datetime
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "agritech-backend",
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("agritech")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    try:
        import logstash
        ls_handler = logstash.TCPLogstashHandler(
            settings.logstash_host, settings.logstash_port, version=1
        )
        logger.addHandler(ls_handler)
    except Exception:
        pass  # Logstash not available in dev mode

    return logger


logger = setup_logging()
