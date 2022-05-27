
def validate_response_errors(data):
    if "error" in data:
        raise RuntimeError(data["error"])
    return data