from apachelogs import LogParser, COMBINED, COMMON
import re


REQUEST_PATTERN = re.compile(r"(\S+)\s+(\S+)\s+(\S+)")

ENTRY_TEMPLATE = {
    "ip": "",
    "remote_ident": "",
    "remote_user": "",
    "time": "",
    "method": "",
    "path": "",
    "version": "",
    "request_line": "",
    "status_code": "",
    "bytes": "",
    "referer": "",
    "user_agent": "",
    "failed": "",
}


def _create_base_entry(parsed):
    """Create shared entry fields."""

    return {
        "ip": str(parsed.remote_host),
        "remote_ident": str(parsed.remote_logname),
        "remote_user": str(parsed.remote_user),
        "time": parsed.request_time,
        "request_line": str(parsed.request_line),
        "status_code": int(parsed.final_status),
        "bytes": int(parsed.bytes_sent),
    }


def _parse_request(request_line):
    """Parse request line into method, path, and version."""

    request = REQUEST_PATTERN.match(request_line)

    if not request:
        return {
            "method": "N/A",
            "path": "N/A",
            "version": "N/A",
            "failed": True,
        }

    return {
        "method": str(request[1]),
        "path": str(request[2]),
        "version": str(request[3]),
        "failed": False,
    }


def parse_combined(path: str, parser: LogParser):
    """Parse Apache combined format logs."""

    data = []

    with open(path, "r") as file:

        for line in file:

            parsed = parser.parse(line)

            entry = ENTRY_TEMPLATE.copy()

            entry.update(
                _create_base_entry(parsed)
            )

            entry.update(
                _parse_request(parsed.request_line)
            )

            entry["referer"] = str(
                parsed.headers_in.get("Referer", "N/A")
            )

            entry["user_agent"] = str(
                parsed.headers_in.get("User-Agent", "N/A")
            )

            data.append(entry)

    return data


def parse_common(path: str, parser: LogParser):
    """Parse Apache common format logs."""

    data = []

    with open(path, "r") as file:

        for line in file:

            parsed = parser.parse(line)

            entry = ENTRY_TEMPLATE.copy()

            entry.update(
                _create_base_entry(parsed)
            )

            entry.update(
                _parse_request(parsed.request_line)
            )

            data.append(entry)

    return data


def parse_log(path: str, formatting: str):
    """Parse Apache logs based on formatting type."""

    if formatting == "common":

        parser = LogParser(COMMON)

        return parse_common(path, parser)

    elif formatting == "combined":

        parser = LogParser(COMBINED)

        return parse_combined(path, parser)

    raise ValueError("Invalid log format")