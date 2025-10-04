from utils import call_openai, fetch_hunter_email


def test_call_openai_no_key():
    # Ensure we get an error-like response when OPENAI_API_KEY is missing
    res = call_openai("Hello")
    assert isinstance(res, dict)


def test_fetch_hunter_no_key():
    res = fetch_hunter_email("example.com")
    assert res is None or isinstance(res, dict)
