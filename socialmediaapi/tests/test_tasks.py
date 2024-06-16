import httpx
import pytest

from socialmediaapi.tasks import APIResponseError, send_simple_emain


@pytest.mark.anyio
async def test_send_simple_email(mock_httpx_client):
    await send_simple_emain("test@example.com", "Test subject", "Test body")
    mock_httpx_client.post.assert_called()


@pytest.mark.anyio
async def test_send_simple_email_api_error(mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=400, content="", request=httpx.Request("POST", "//")
    )
    with pytest.raises(APIResponseError):
        await send_simple_emain("test@example.com", "Test subject", "Test body")
