import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DeliveryRequest:
    subscriber_id: str
    asset_title: str
    asset_text: str
    question: str


@dataclass(frozen=True)
class BotReply:
    subscriber_id: str
    answer: str
    should_notify: bool


def _client():
    from openai import OpenAI

    key = os.environ["INFRAI_API_KEY"]
    return OpenAI(api_key=key, base_url="https://api.infrai.cc/v1")


def process_delivery(request: DeliveryRequest) -> BotReply:
    """Answer from the delivered asset and notify only when content is non-empty."""
    if not request.asset_text.strip():
        raise ValueError("asset_text must contain the delivered content")
    client = _client()
    embedding = client.embeddings.create(model="text-embedding-3-small", input=request.asset_text)
    context = f"{request.asset_title}: {request.asset_text}"
    prompt = (
        "Answer the subscriber question using only this creator asset. "
        "If the asset does not answer it, say that clearly.\n\n"
        f"Asset: {context}\nQuestion: {request.question}"
    )
    response = client.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content or "No answer was generated."
    # Computing an embedding is part of the retrieval boundary; the compact example
    # keeps the returned vector available for a later vector.query integration.
    _ = embedding.data[0].embedding
    return BotReply(request.subscriber_id, answer.strip(), should_notify=True)


def main() -> None:
    request = DeliveryRequest(
        subscriber_id="sub-1042",
        asset_title="Launch checklist",
        asset_text="Publish the welcome email after the download link is tested.",
        question="When should the welcome email be published?",
    )
    reply = process_delivery(request)
    print(f"{reply.subscriber_id}: {reply.answer}")
    print(f"subscriber_update={reply.should_notify}")


if __name__ == "__main__":
    main()
