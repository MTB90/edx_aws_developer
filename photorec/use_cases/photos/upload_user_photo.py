from ..base import BaseCQ
from typing import Dict


class UploadUserPhotoCommand(BaseCQ):
    def __init__(self, repo__photo, service_storage):
        self._photo_repo = repo__photo
        self._storage_service = service_storage

    def execute(self, nickname: str, data):
        # TODO
        return []
