"""每週重建 ptt_gossip 後，bot 手上的舊 collection 失效要能自動換新的。"""


class _Stale:
    def query(self, **kw):
        raise Exception("Error getting collection: Collection [abc] does not exist.")


class _Fresh:
    def query(self, **kw):
        return {"documents": [["top", "r1", "r2"]]}


class _Chroma:
    def __init__(self):
        self.calls = 0

    def get_or_create_collection(self, name, embedding_function=None):
        self.calls += 1
        assert name == "ptt_gossip"
        return _Fresh()


def _brain(collection):
    from line_bot.bot import SassyBrain
    brain = object.__new__(SassyBrain)
    brain.chroma = _Chroma()
    brain.emb_fn = None
    brain.collection = collection
    return brain


def test_stale_collection_is_refetched_and_retried():
    brain = _brain(_Stale())
    assert brain.get_relevant_snippets("q") == ("top", ["r1", "r2"])
    assert isinstance(brain.collection, _Fresh)


def test_other_errors_do_not_refetch():
    class _Broken:
        def query(self, **kw):
            raise RuntimeError("boom")
    brain = _brain(_Broken())
    assert brain.get_relevant_snippets("q") == (None, [])
    assert brain.chroma.calls == 0
