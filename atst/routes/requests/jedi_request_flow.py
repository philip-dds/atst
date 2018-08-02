from collections import defaultdict

from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm
from atst.forms.request import RequestForm
from atst.forms.org import OrgForm
from atst.forms.poc import POCForm
from atst.forms.review import ReviewForm


class JEDIRequestFlow(object):
    def __init__(
        self,
        current_step,
        request=None,
        post_data=None,
        request_id=None,
        current_user=None,
        existing_request=None,
    ):
        self.current_step = current_step
        self.request = request

        self.post_data = post_data
        self.is_post = self.post_data is not None

        self.request_id = request_id
        self.form = self._form()

        self.current_user = current_user
        self.existing_request = existing_request

    def _form(self):
        if self.is_post:
            return self.form_class()(self.post_data)
        elif self.request:
            return self.form_class()(data=self.current_step_data)
        else:
            return self.form_class()()

    def validate(self):
        return self.form.validate()

    def validate_warnings(self):
        existing_request_data = (
            self.existing_request and self.existing_request.body.get(self.form_section)
        ) or None

        valid = self.form.perform_extra_validation(existing_request_data)
        return valid

    @property
    def current_screen(self):
        return self.screens[self.current_step - 1]

    @property
    def form_section(self):
        return self.current_screen["section"]

    def form_class(self):
        return self.current_screen["form"]

    @property
    def current_step_data(self):
        data = {}

        if self.is_post:
            data = self.post_data

        if self.request:
            if self.form_section == "review_submit":
                data = self.request.body
            else:
                data = self.request.body.get(self.form_section, {})

        return defaultdict(lambda: defaultdict(lambda: "Input required"), data)

    @property
    def can_submit(self):
        return self.request and self.request.status != "incomplete"

    @property
    def next_screen(self):
        return self.current_step + 1

    @property
    def screens(self):
        return [
            {
                "title": "Details of Use",
                "section": "details_of_use",
                "form": RequestForm,
                "subitems": [
                    {
                        "title": "Overall request details",
                        "id": "overall-request-details",
                    },
                    {"title": "Cloud Resources", "id": "cloud-resources"},
                    {"title": "Support Staff", "id": "support-staff"},
                ],
                "show": True,
            },
            {
                "title": "Information About You",
                "section": "information_about_you",
                "form": OrgForm,
                "show": True,
            },
            {
                "title": "Primary Point of Contact",
                "section": "primary_poc",
                "form": POCForm,
                "show": True,
            },
            {
                "title": "Review & Submit",
                "section": "review_submit",
                "form": ReviewForm,
                "show": True,
            },
        ]

    def create_or_update_request(self):
        request_data = {self.form_section: self.form.data}
        if self.request_id:
            Requests.update(self.request_id, request_data)
        else:
            request = Requests.create(self.current_user["id"], request_data)
            self.request_id = request.id