# coding: utf-8

from django import forms


class YachOptionsForm(forms.Form):
    url = forms.CharField(
        max_length=255,
        label="URL",
        help_text='WebHook Url',
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "e.g. https://www.example.com"}),
    )
    secret_key = forms.CharField(
        max_length=255,
        label="Secret Key",
        help_text='Secret Key',
        required=False,
    )
