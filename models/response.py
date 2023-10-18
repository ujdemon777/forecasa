def Response(data, message,code, error):
    return {
        "data": data,
        "message": message,
        "code": code,
        "error": error
    }

def ErrorResponse(message,code, error):
    return {
        "message": message,
        "code": code,
        "error": error
    }
