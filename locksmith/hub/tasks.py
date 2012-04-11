from locksmith.common import apicall
from locksmith.hub.models import UNPUBLISHED, PUBLISHED, NEEDS_UPDATE

from celery.task import task

@task()
def push_key(key):
    endpoints = {UNPUBLISHED: 'create_key/', NEEDS_UPDATE: 'update_key/'}
    dirty = key.pub_statuses.exclude(status=PUBLISHED).filter(
              api__push_enabled=True).select_related()
    for kps in dirty:
        endpoint = urljoin(kps.api.url, endpoints[kps.status])
        apicall(endpoint, kps.api.signing_key, api=kps.api.name,
                key=kps.key.key, email=kps.key.email, status=kps.key.status)
        actions[kps.status] += 1
        kps.status = PUBLISHED
        kps.save()