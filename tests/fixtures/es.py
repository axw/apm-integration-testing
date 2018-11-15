import time

import elasticsearch
import pytest
import timeout_decorator

from tests.fixtures import default


@pytest.fixture(scope="session")
def es():
    class Elasticsearch(object):
        def __init__(self, url):
            self.es = elasticsearch.Elasticsearch([url])
            self.index = "apm-*"

        def clean(self):
            self.es.indices.delete(self.index)
            self.es.indices.refresh()

        def term_q(self, terms, exclude_terms=None):
            def make_terms(terms):
                t = []
                for idx in range(len(terms)):
                    for k in terms[idx]:
                        t.append({"term": {k: {"value": terms[idx][k]}}})
                return t
            bool_q = {"must": make_terms(terms)}
            if exclude_terms:
                bool_q["must_not"] = make_terms(exclude_terms)
            return {"query": {"bool": bool_q}}

        @timeout_decorator.timeout(10)
        def fetch(self, q):
            ct = 0
            s = {}
            while ct == 0:
                time.sleep(3)
                s = self.es.search(index=self.index, body=q)
                ct = s['hits']['total']
            return s

    return Elasticsearch(default.from_env("ES_URL"))
