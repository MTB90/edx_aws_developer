from ..base import BaseCQ
from typing import Dict


class GetUserPhotosQuery(BaseCQ):
    def __init__(self, repo__photo, service_storage):
        self._photo_repo = repo__photo
        self._storage_service = service_storage

    def execute(self, request: Dict = None):
        photos = self._photo_repo.list(request)

        for photo in photos:
            photo['thumb_signed_url'] = self.service_storage.get_signed_url(photo['thumb'])
        return photos
