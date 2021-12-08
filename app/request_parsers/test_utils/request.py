from unittest import mock


def make_mock_request(json_data=None, query_params=None, headers=None):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    mock_request.args = query_params
    mock_request.headers = headers or {}
    return mock_request
