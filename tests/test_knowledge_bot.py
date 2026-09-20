from knowledge_bot import DeliveryRequest, process_delivery


class FakeMessage:
    content = "Publish it after the link is tested."


class FakeChoice:
    message = FakeMessage()


class FakeChat:
    class completions:
        @staticmethod
        def create(**kwargs):
            return type("Response", (), {"choices": [FakeChoice()]})()


class FakeEmbeddings:
    @staticmethod
    def create(**kwargs):
        item = type("Embedding", (), {"embedding": [0.1, 0.2]})()
        return type("Response", (), {"data": [item]})()


class FakeClient:
    chat = FakeChat()
    embeddings = FakeEmbeddings()


def test_delivery_answer_notifies_subscriber(monkeypatch):
    monkeypatch.setattr("knowledge_bot._client", lambda: FakeClient())
    result = process_delivery(
        DeliveryRequest("sub-1", "Checklist", "Test the link first.", "When do I publish?")
    )
    assert result.answer == "Publish it after the link is tested."
    assert result.should_notify is True
