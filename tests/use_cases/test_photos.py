import pytest
from unittest.mock import create_autospec, Mock, call

from photorec.repository.photo import RepoPhoto
from photorec.services.storage import ServiceStorageS3
from photorec.validators.nickname import ValidatorNickname, NicknameError
from photorec.use_cases.photos.delete_user_photo import DeleteUserPhotoCommand


@pytest.fixture
def repo_photo():
    return create_autospec(RepoPhoto, instance=True)


@pytest.fixture()
def service_storage():
    return create_autospec(ServiceStorageS3, instance=True)


def test_given_no_nickname_when_delete_photo_then_error_nickname_not_defined(
        repo_photo, service_storage):

    validator = create_autospec(ValidatorNickname)
    validator.validate.side_effect = NicknameError()

    command = DeleteUserPhotoCommand(
        repo__photo=repo_photo,
        service__storage=service_storage,
        validator__nickname=validator
    )
    with pytest.raises(NicknameError):
        command.execute(Mock())


def test_given_nickname_and_uuid_when_delete_not_existing_photo_then_no_changes(
        repo_photo, service_storage):
    repo_photo.get.return_value = None
    
    request = {
        'uuid': 'd48f920c-3994-4ac7-9400-17055854f645',
        'nickname': 'nickname'
    }

    command = DeleteUserPhotoCommand(
        repo__photo=repo_photo,
        service__storage=service_storage,
        validator__nickname=Mock()
    )
    command.execute(request)
    repo_photo.get.assert_called_once()
    repo_photo.delete.assert_not_called()
    service_storage.delete.assert_not_called()


def test_given_nickname_and_uuid_when_delete_existing_photo_then_delete(
        repo_photo, service_storage):
    photo =  {
        'uuid': 'd48f920c-3994-4ac7-9400-17055854f645',
        'nickname': 'nickname',
        'thumb': 'thumb/photo.png',
        'photo': 'photo/photo.png',
        'tag': 'tag',
        'likes': 10
    }
    repo_photo.get.return_value = photo
    
    request = {
        'uuid': 'd48f920c-3994-4ac7-9400-17055854f645',
        'nickname': 'nickname'
    }
    
    command = DeleteUserPhotoCommand(
        repo__photo=repo_photo,
        service__storage=service_storage,
        validator__nickname=Mock()
    )
    command.execute(request)

    repo_photo.get.assert_called_once()
    repo_photo.delete.assert_called_once_with(key=request)
    service_storage.delete.assert_has_calls([
        call(key=photo['thumb']),
        call(key=photo['photo'])
    ])
