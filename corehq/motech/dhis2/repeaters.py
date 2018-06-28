from __future__ import absolute_import
from __future__ import unicode_literals

import json

from couchdbkit.ext.django.schema import SchemaProperty
from memoized import memoized

from corehq.form_processor.interfaces.dbaccessors import FormAccessors
from corehq.motech.dhis2.dhis2_config import Dhis2Config
from corehq.motech.dhis2.view import send_dhis2_data
from corehq.motech.repeaters.models import FormRepeater
from corehq.motech.repeaters.repeater_generators import FormRepeaterJsonPayloadGenerator
from corehq.motech.repeaters.signals import create_repeat_records
from couchforms.signals import successful_form_received
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


# it actually triggers on forms,
# but I wanted to get a case type, and this is the easiest way
from corehq.motech.requests import Requests
from corehq.toggles import DHIS2_INTEGRATION, DHIS2_REPEATER_INTEGRATION
from corehq.util import reverse


class Dhis2Repeater(FormRepeater):
    class Meta(object):
        app_label = 'repeaters'

    include_app_id_param = False
    friendly_name = _("Forward to DHIS2")
    payload_generator_classes = (FormRepeaterJsonPayloadGenerator,)

    dhis2_config = SchemaProperty(Dhis2Config)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.get_id == other.get_id
        )

    @memoized
    def payload_doc(self, repeat_record):
        return FormAccessors(repeat_record.domain).get_form(repeat_record.payload_id)

    @property
    def form_class_name(self):
        """
        The class name used to determine which edit form to use
        """
        return self.__class__.__name__

    @classmethod
    def available_for_domain(cls, domain):
        return True
            #DHIS2_REPEATER_INTEGRATION.enabled(domain) and DHIS2_INTEGRATION.enabled(domain)

    @classmethod
    def get_custom_url(cls, domain):
        from corehq.motech.repeaters.views.repeaters import AddOpenmrsRepeaterView
        return reverse(AddOpenmrsRepeaterView.urlname, args=[domain])

    def get_payload(self, repeat_record):
        payload = super(Dhis2Repeater, self).get_payload(repeat_record)
        return json.loads(payload)

    def send_request(self, repeat_record, payload, verify=None):
        for form_config in self.dhis2_config.form_configs:
            if form_config.xmlns == payload['form']['@xmlns']:
                return send_dhis2_data(
                    Requests(self.url, self.username, self.password),
                    self.domain,
                    self.dhis2_config,
                    payload,
                )


def create_dhis_repeat_records(sender, xform, **kwargs):
    create_repeat_records(Dhis2Repeater, xform)


successful_form_received.connect(create_dhis_repeat_records)
