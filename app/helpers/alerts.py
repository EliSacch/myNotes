ALERT_ICONS = {
    "info": "fa-circle-info",
    "success": "fa-circle-check",
    "warning": "fa-triangle-exclamation",
    "error": "fa-circle-xmark",
}


def alert_icon(category):
    return ALERT_ICONS.get(category, ALERT_ICONS["info"])
