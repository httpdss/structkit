from unittest.mock import patch, MagicMock
from structkit.filters import get_latest_release, slugify

@patch('structkit.filters.Github')
@patch('structkit.filters.os.getenv')
def test_get_latest_release(mock_getenv, mock_github):
    # Mock the environment variable
    mock_getenv.return_value = 'fake_token'

    # Mock the Github object and its methods
    mock_repo = MagicMock()
    mock_repo.get_latest_release.return_value.tag_name = 'v1.0.0'
    mock_repo.default_branch = 'main'

    mock_github.return_value.get_repo.return_value = mock_repo

    # Test with a valid release
    assert get_latest_release('fake/repo') == 'v1.0.0'

def test_slugify():
    assert slugify('Hello World') == 'hello-world'
    assert slugify('Python 3.8') == 'python-38'
    assert slugify('Special_Characters!@#') == 'specialcharacters'
