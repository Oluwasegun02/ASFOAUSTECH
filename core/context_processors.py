from .db import repository


def site_context(request):
    return {
        "site_name": "ASF OAUSTECH",
        "branch_name": "Tabernacle of Faith",
        "current_user": request.user if request.user.is_authenticated else None,
        "current_admin": request.user if request.user.is_staff else None,
        "mongo_status": repository.status(),
    }
