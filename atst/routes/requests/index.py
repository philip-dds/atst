import pendulum
from flask import render_template, g

from . import requests_bp
from atst.domain.requests import Requests


def map_request(user, request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status,
        "app_count": 1,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": user.full_name
    }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    requests = []
    if (
        "review_and_approve_jedi_workspace_request"
        in g.current_user.atat_permissions
    ):
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator_id=g.current_user.id)

    mapped_requests = [map_request(g.current_user, r) for r in requests]

    return render_template("requests.html", requests=mapped_requests)