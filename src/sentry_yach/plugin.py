# coding: utf-8
from __future__ import absolute_import

import json
import time
import hmac
import hashlib
import base64
import requests

from six import text_type

from six.moves.urllib.parse import (
    urlparse,
    parse_qsl,
    urlencode,
    urlunparse,
)

from sentry.plugins.bases.notify import NotificationPlugin

from . import VERSION
from .forms import YachOptionsForm


def build_http_url(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


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

    slug = "Yach"
    title = "Yach"
    required_field = "url"
    conf_key = slug
    conf_title = title
    project_conf_form = YachOptionsForm

    def is_configured(self, project):
        return bool(self.get_option("url", project))

    def notify_users(self, group, event, *args, **kwargs):
        self.post_process(group, event, *args, **kwargs)

    def post_process(self, group, event, *args, **kwargs):
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        url = self.get_option("url", group.project)
        secret_key = self.get_option("secret_key", group.project)

        if secret_key:
            timestamp = int(time.time() * 1000)
            secret_enc = secret_key.encode("utf-8")
            string_to_sign = "{}\n{}".format(timestamp, secret_key).encode("utf-8")
            hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
            sign = base64.b64encode(hmac_code)
            send_url = build_http_url(url, {"timestamp": timestamp, "sign": sign})
        else:
            send_url = url

        title = text_type("New message from {}").format(event.project.slug)

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text_type("#### {title} \n > {message} [detail]({url})").format(
                    title=title,
                    message=text_type(event.message or event.title),
                    url=text_type("{}events/{}/").format(group.get_absolute_url(), event.event_id),
                )
            }
        }

        requests.post(
            url=send_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
