from pydantic import BaseModel

from mockmate_ml.providers.fake import FakeLLMProvider


class ExampleOutput(BaseModel):
    value: str


def test_fake_provider_returns_typed_response() -> None:
    provider = FakeLLMProvider(lambda _prompt, schema: schema(value="test"))
    result = provider.generate_structured("make output", ExampleOutput)
    assert result.value == "test"
    assert provider.name == "fake"
    assert len(provider.calls) == 1
