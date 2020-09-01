# coding: utf-8
from __future__ import absolute_import

import time
import hmac
import hashlib
import base64

from six import text_type

from six.moves.urllib.parse import (
    urlencode,
)

from sentry.exceptions import PluginError
from sentry.http import is_valid_url, safe_urlopen
from sentry.utils.safe import safe_execute
from sentry.plugins.bases.notify import NotificationPlugin

from . import VERSION


def validate_url(url, **kwargs):
    if (not url.startswith(("http://", "https://")) or not is_valid_url(url)):
        raise PluginError("The {} is not a valid URL.".format(url))
    return url


class YachPlugin(NotificationPlugin):
    author = "yp"
    author_url = "https://github.com/qingchunyibeifangzongle/sentry-yach"
    version = VERSION
    description = "Post notifications to Yach."
    resource_links = [
        ("Source", "https://github.com/qingchunyibeifangzongle/sentry-yach"),
        ("Bug Tracker", "https://github.com/qingchunyibeifangzongle/sentry-yach/issues"),
        ("README", "https://github.com/qingchunyibeifangzongle/sentry-yach/blob/master/README.md"),
    ]

    slug = "yach"
    title = "Yach"
    conf_key = slug
    conf_title = title

    def is_configured(self, project, **kwargs):
        return bool(self.get_option("url", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "url",
                "label": "WebHook Url",
                "type": "url",
                "placeholder": "e.g. https://www.example.com",
                "validators": [validate_url],
                "required": True,
            },
            {
                "name": "secret_key",
                "label": "Secret Key",
                "type": "string",
                "required": False,
            }
        ]

    def get_yach_url(self, project):
        url = self.get_option("url", project)
        secret_key = self.get_option("secret_key", project)

        if secret_key:
            timestamp = int(time.time() * 1000)
            secret_enc = secret_key.encode("utf-8")
            string_to_sign = "{}\n{}".format(timestamp, secret_key).encode("utf-8")
            hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(hmac_code)
            params = urlencode({"timestamp": timestamp, "sign": sign})
            s = "?" if url.find("?") == -1 else "&"
            url = text_type("{}{}{}").format(url, s, params)

        return url

    def get_group_data(self, group, event, triggering_rules):
        title = text_type("New message from {}").format(event.project.slug)
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text_type("#### {title}\n > {message} [detail]({url})").format(
                    title=title,
                    message=text_type(event.message[:2048] or event.title),
                    url=text_type("{}events/{}/").format(group.get_absolute_url(), event.event_id),
                )
            }
        }

        return data

    def send_yach(self, url, payload):
        return safe_urlopen(
            url=url,
            json=payload,
            timeout=5,
            verify_ssl=False,
        )

    def post_process(self, group, event, fail_silently=False, triggering_rules=None, **kwargs):
        payload = self.get_group_data(group, event, triggering_rules)
        url = self.get_yach_url(group.project)
        safe_execute(self.send_yach, url, payload, _with_transaction=False)

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)
