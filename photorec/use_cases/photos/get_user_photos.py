from ..base import BaseCQ


class GetUserPhotosQuery(BaseCQ):
    def __init__(self, repo__photo, service__storage):
        self._photo_repo = repo__photo
        self._storage_service = service__storage

    def execute(self, nickname: str):
        photos = self._photo_repo.list(query={'nickname': nickname})

        for photo in photos:
            photo['thumb_signed_url'] = self._storage_service.get_signed_url(photo['thumb'])
        return photos
