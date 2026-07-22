import json
from datetime import datetime


def normalize_log(container_name: str, raw_line: str) -> dict:
    raw_line_str = raw_line.strip()
    try:
        data = json.loads(raw_line_str)
    except json.JSONDecodeError:
        return {
            "service": container_name,
            "level": "INFO",
            "message": raw_line_str,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw": {
                "original": raw_line_str
            }
        }

    # Extract log message
    message = data.get("message") or data.get("msg") or data.get("log") or ""

    # Normalize log level/severity
    raw_level = data.get("severity") or data.get("levelname") or data.get("level") or "INFO"
    level = "INFO"

    if isinstance(raw_level, int):
        if raw_level <= 20: level = "DEBUG"
        elif raw_level <= 30: level = "INFO"
        elif raw_level <= 40: level = "WARN"
        elif raw_level <= 50: level = "ERROR"
        else: level = "FATAL"
    elif isinstance(raw_level, str):
        lvl_upper = raw_level.upper()
        if "DEBUG" in lvl_upper: level = "DEBUG"
        elif "WARN" in lvl_upper or "WARNING" in lvl_upper: level = "WARN"
        elif "ERROR" in lvl_upper: level = "ERROR"
        elif "FATAL" in lvl_upper or "CRIT" in lvl_upper: level = "FATAL"

    # Normalize timestamp
    raw_time = data.get("timestamp") or data.get("time") or data.get("asctime")
    timestamp = None
    if raw_time:
        try:
            if isinstance(raw_time, (int, float)):
                timestamp = datetime.utcfromtimestamp(raw_time / 1000.0 if raw_time > 1e11 else raw_time).isoformat() + "Z"
            else:
                timestamp = str(raw_time)
        except Exception:
            pass

    # Extract trace and span context
    raw_trace_id = data.get("traceId") or data.get("trace_id") or data.get("logging.googleapis.com/trace")
    raw_span_id = data.get("spanId") or data.get("span_id") or data.get("logging.googleapis.com/spanId")

    trace_id = str(raw_trace_id) if raw_trace_id and not str(raw_trace_id).startswith("${") else None
    span_id = str(raw_span_id) if raw_span_id and not str(raw_span_id).startswith("${") else None

    # Clean path prefix from GCP trace IDs if present
    if trace_id and "/" in trace_id:
        trace_id = trace_id.split("/")[-1]


    return {
        "service": container_name,
        "level": level,
        "message": str(message) if message else raw_line_str,
        "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
        "trace_id": str(trace_id) if trace_id else None,
        "span_id": str(span_id) if span_id else None,
        "raw": data
    }
