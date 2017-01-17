from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy

from crispy_forms import layout as crispy
from crispy_forms.layout import Layout, ButtonHolder, Submit

from custom.rch.models import AreaMapping


def get_choices_for(field_name):
    field_values = AreaMapping.objects.values_list(field_name, flat=True).distinct()
    options = set()
    for field_value in field_values:
        options.add((field_value, field_value))
    return tuple(options)


class BeneficiariesFilterForm(forms.Form):
    state = forms.ChoiceField(
        label=ugettext_lazy("State"),
        required=True,
        choices=get_choices_for('stname')
    )

    district = forms.ChoiceField(
        label=ugettext_lazy("District"),
        required=True,
        choices=get_choices_for('dtname')
    )

    awcid = forms.ChoiceField(
        label=ugettext_lazy("AWC-ID"),
        required=True,
        choices=get_choices_for('awcid')
    )

    village_id = forms.ChoiceField(
        label=ugettext_lazy("Village-ID"),
        required=True,
        choices=get_choices_for('villcode')
    )

    village_name = forms.ChoiceField(
        label=ugettext_lazy("Village Name"),
        required=True,
        choices=get_choices_for('Village_name')
    )

    def __init__(self, *args, **kwargs):
        super(BeneficiariesFilterForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.form_name = 'Filter:'
        self.helper.label_class = 'col-sm-2 col-md-1'
        self.helper.field_class = 'col-sm-4 col-md-3'
        self.helper.layout = Layout(
            crispy.Field(
                'state',
            ),
            crispy.Field(
                'district'
            ),
            crispy.Field(
                'awcid'
            ),
            crispy.Field(
                'village_id'
            ),
            crispy.Field(
                'village_name'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
