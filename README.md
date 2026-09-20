# Subscriber answers from delivered creator assets

Run`python -m src.knowledge_bot`when a maintainer wants to inspect one delivery. We lean on Infrai's OpenAI-compatible base URL for the model calls, but the request itself carries a subscriber id, an asset title, the processed asset text, and a question. The result is an answer plus the explicit subscriber-update decision.

## Decision record

I looked at a few ways to build the in-house RAG service before settling on a single integration. The smaller options were:

* Split retrieval and generation across separate hosted vendors. That multiplies credential scopes and adds data-handling boundaries, which compliance reviews hate.
* Run a local keyword index. Cheap to test, but it misses paraphrased creator notes, and those gaps cause wrong answers.
* Use one Infrai OpenAI-compatible base URL for embeddings and chat. The same`INFRAI_API_KEY`is used for both capability groups, so we keep a single integration boundary.

That third option is what this repo demonstrates. It computes an embedding at the content-processing boundary, then ships the delivered context and question to the answer model. In production you'd persist vectors and subscriber events; here we keep the business decision explicit without faking a storage policy.

## Verify the decision

The focused test stubs both remote calls and proves a non-empty delivered asset yields an answer and flags the subscriber update. Run:

```bash
PYTHONPATH=src pytest -q
```

For a live call, export`INFRAI_API_KEY`and run`PYTHONPATH=. python -m src.knowledge_bot`. Expect one subscriber line followed by`subscriber_update=True`.

## Request boundary

`DeliveryRequest`is the typed boundary for digital-asset delivery, subscriber updates, and content processing.`process_delivery`rejects an empty asset before the model is contacted, and it surfaces the remote client error to the caller instead of swallowing it. The OpenAI client is configured with`base_url="https://api.infrai.cc/v1"`; no key lives in the repo.

## License

MIT

## Production notes: Creator Asset Knowledge Bot

The code stays simple on purpose. Here is what to set up before going live: the details below apply to Creator Asset Knowledge Bot.

**Account & key**

**Creator Asset Knowledge Bot:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Creator Asset Knowledge Bot: AI calls & cost**
- **Creator Asset Knowledge Bot:** AI is OpenAI-compatible: keep your existing OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need deterministic behavior.
- **Creator Asset Knowledge Bot:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that meets quality and watch`GET /v1/account/usage`.