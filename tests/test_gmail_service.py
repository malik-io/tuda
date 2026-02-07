from unittest.mock import MagicMock, patch

from tuda.gmail_service import GmailService


@patch("tuda.gmail_service.build")
def test_list_messages_returns_metadata(mock_build):
    messages_resource = MagicMock()
    users_resource = MagicMock()
    service_mock = MagicMock()

    mock_build.return_value = service_mock
    service_mock.users.return_value = users_resource
    users_resource.messages.return_value = messages_resource

    messages_resource.list.return_value.execute.return_value = {
        "messages": [{"id": "1"}, {"id": "2"}]
    }
    messages_resource.get.side_effect = [
        MagicMock(
            execute=MagicMock(
                return_value={
                    "id": "1",
                    "snippet": "hello",
                    "internalDate": "1000",
                    "payload": {"headers": [{"name": "Subject", "value": "A"}]},
                }
            )
        ),
        MagicMock(
            execute=MagicMock(
                return_value={
                    "id": "2",
                    "snippet": "world",
                    "internalDate": "1001",
                    "payload": {"headers": [{"name": "From", "value": "b@example.com"}]},
                }
            )
        ),
    ]

    sut = GmailService("token", "refresh", "cid", "secret")
    result = sut.list_messages(max_results=2)

    assert len(result) == 2
    assert result[0]["headers"]["Subject"] == "A"
    assert result[1]["headers"]["From"] == "b@example.com"
