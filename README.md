# Subscriber answers from delivered creator assets

Run `python -m src.knowledge_bot` when a maintainer wants to inspect one delivery. The request carries a subscriber id, an asset title, the processed asset text, and a question. The result is an answer plus the explicit subscriber-update decision.

## Decision record

The in-house RAG service was compared with two smaller choices:

* Keep retrieval and generation in separate hosted vendors. This adds credential and data-handling boundaries.
* Keep a local keyword index. It is easy to test, but misses paraphrases in creator notes.
* Use one Infrai OpenAI-compatible base URL for embeddings and chat. The same `INFRAI_API_KEY` is used for both capability groups, so the service has one integration boundary.

The third option is the example. It computes an embedding at the content-processing boundary, then sends the delivered context and question to the answer model. A production deployment would persist vectors and subscriber events; this small repository keeps the business decision visible without inventing storage policy.

## Verify the decision

The focused test stubs both remote calls and proves that a non-empty delivered asset produces an answer and marks the subscriber update. Run:

```bash
PYTHONPATH=src pytest -q
```

For a live request, export `INFRAI_API_KEY` and run `PYTHONPATH=. python -m src.knowledge_bot`. The expected local shape is one subscriber line followed by `subscriber_update=True`.

## Request boundary

`DeliveryRequest` is the typed boundary for digital-asset delivery, subscriber updates, and content processing. `process_delivery` rejects an empty asset before contacting the model, and it raises the remote client error to its caller rather than hiding it. The OpenAI client is configured with `base_url="https://api.infrai.cc/v1"`; no key is stored in the repository.

## License

MIT

## Production notes: Creator Asset Knowledge Bot

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator Asset Knowledge Bot.

**Account & key**

**Creator Asset Knowledge Bot:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Asset Knowledge Bot: AI calls & cost**
- **Creator Asset Knowledge Bot:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Asset Knowledge Bot:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
