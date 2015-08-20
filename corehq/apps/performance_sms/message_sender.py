from collections import namedtuple
from corehq.apps.performance_sms.parser import get_parsed_params
from corehq.apps.performance_sms.query_engine import QueryEngine, QueryContext
from corehq.apps.reminders.util import get_preferred_phone_number_for_recipient
from corehq.apps.sms.api import send_sms


MessageResult = namedtuple('MessageResult', ['user', 'message'])


def send_messages_for_config(config, actually_send=True):
    query_engine = QueryEngine(template_vars=config.template_variables)
    params = get_parsed_params(config.template)
    sent_messages = []
    for user in config.group.get_users():
        phone_number = get_preferred_phone_number_for_recipient(user)
        if phone_number:
            query_context = QueryContext(user, config.group, template_vars=config.template_variables)
            message_context = query_engine.get_context(params, query_context)
            message = config.template.format(**message_context)
            if actually_send:
                send_sms(config.domain, user, user.phone_number, message)
            sent_messages.append(MessageResult(user, message))
    return sent_messages
