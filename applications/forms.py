"""
Our form for a job application, with a class to allow us to have Date fields.
"""
from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
from django import forms
from django.forms import ModelForm, HiddenInput
from django.utils.safestring import mark_safe

from . import models


class DateInput(forms.DateInput):
    """
    A class for creating input fields of type date.
    """
    input_type = "date"


class EditApplication(ModelForm):
    """
    The form for creating/editing the details associated with a job application.
    """

    class Meta:
        """
        The model, fields to be excluded and widgets to be used for our form.
        """
        model = models.JobApplication
        fields = [
            "when",
            "company",
            "title",
            "posting",
            "confirm",
            "notes",
            "active",
            "interviews",
            "rejected",
            "saved_posting",
        ]

        widgets = {
            "when": DateInput(),
            "rejected": DateInput(),
            "saved_posting": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize certain aspects of the form.

        Args:
            *args (Any): Any positional parameters such as data, supplied to the parent class.
            **kwargs: And parameters supplied as keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "rendered-form"
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                "when",
                "company",
                "title",
                AppendedText('posting', mark_safe('<i id="scrape-post" class="fa-solid fa-cloud-arrow-down"></i>')),
                "confirm",
                "notes",
                "active",
                "interviews",
                "rejected",

                css_class="field-wrapper",
            ),
            Div(
                Submit("submit", "Submit Application"),

                css_class="button-wrapper"
            ),
        )
