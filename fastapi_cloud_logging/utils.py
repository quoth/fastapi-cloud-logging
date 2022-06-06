from datetime import date, datetime


def serialize_json(object):
    if isinstance(object, (datetime, date)):
        return object.isoformat()
    elif hasattr(object, "__dict__"):
        return object.__dict__
    return "object that is failed to serialize"
