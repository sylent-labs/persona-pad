from __future__ import annotations

import logging
import os
from functools import lru_cache

import numpy as np
from numpy.typing import NDArray
from openai import APITimeoutError, OpenAI, OpenAIError, RateLimitError

from app.schemas import Example
from app.services.persona_engine import _load_examples

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """
    Method: _get_client
    Objective: Lazily build the OpenAI client so import-time does not require an API key
    Parameters:
        None
    Return:
        OpenAI: a singleton OpenAI client used for embedding calls
    """
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _normalize_rows(matrix: NDArray[np.float32]) -> NDArray[np.float32]:
    """
    Method: _normalize_rows
    Objective: Normalize each row of a 2D matrix to unit length so cosine similarity
               reduces to a plain dot product
    Parameters:
        matrix (NDArray[np.float32]): shape (n, d) of raw embedding vectors
    Return:
        NDArray[np.float32]: shape (n, d) with each row L2-normalized; rows that are
                             all-zero are left as zeros (their similarity is then 0
                             against any query)
    """
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


@lru_cache(maxsize=32)
def _load_examples_with_embeddings(
    persona_id: str,
) -> tuple[tuple[Example, ...], NDArray[np.float32]]:
    """
    Method: _load_examples_with_embeddings
    Objective: Load a persona's few-shot examples and embed each example's question
               in one batched call, then cache the result for the life of the process
    Parameters:
        persona_id (str): The persona slug
    Return:
        tuple[tuple[Example, ...], NDArray[np.float32]]: examples in original file
            order alongside an (n, d) row-normalized embedding matrix indexed in the
            same order
    """
    examples = _load_examples(persona_id)
    if not examples:
        return examples, np.zeros((0, 0), dtype=np.float32)

    response = _get_client().embeddings.create(
        model=_EMBEDDING_MODEL,
        input=[example.question for example in examples],
    )
    matrix = np.array(
        [item.embedding for item in response.data], dtype=np.float32
    )
    return examples, _normalize_rows(matrix)


def select_examples(
    persona_id: str,
    question: str,
    k: int,
) -> tuple[Example, ...]:
    """
    Method: select_examples
    Objective: Pick the k few-shot examples whose questions are most semantically
               similar to the user's question, ordered with the most relevant LAST so
               it sits closest to the user turn in the prompt (recency bias)
    Parameters:
        persona_id (str): The persona slug
        question (str): The user's incoming question
        k (int): Maximum number of examples to return
    Return:
        tuple[Example, ...]: up to k examples sorted by ascending similarity. Falls
            back to the first k examples in file order if either the example-pool
            embedding or the query embedding fails.
    """
    examples = _load_examples(persona_id)
    if not examples or k <= 0:
        return ()

    try:
        cached_examples, matrix = _load_examples_with_embeddings(persona_id)
    except (RateLimitError, APITimeoutError, OpenAIError):
        logger.warning(
            "embedding example pool failed, falling back to first-k",
            extra={"persona_id": persona_id, "k": k},
        )
        return examples[:k]

    try:
        query_response = _get_client().embeddings.create(
            model=_EMBEDDING_MODEL,
            input=[question],
        )
    except (RateLimitError, APITimeoutError, OpenAIError):
        logger.warning(
            "embedding query failed, falling back to first-k",
            extra={"persona_id": persona_id, "k": k},
        )
        return cached_examples[:k]

    query_vector = np.array(query_response.data[0].embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query_vector)
    if query_norm > 0:
        query_vector = query_vector / query_norm

    similarities = matrix @ query_vector
    take = min(k, similarities.shape[0])

    # argpartition gives us the top-k indices in arbitrary order, then we sort
    # those k by similarity ascending so the most relevant example is last.
    if take >= similarities.shape[0]:
        candidate_idx = np.arange(similarities.shape[0])
    else:
        candidate_idx = np.argpartition(-similarities, take - 1)[:take]
    ordered_idx = candidate_idx[np.argsort(similarities[candidate_idx])]

    return tuple(cached_examples[int(i)] for i in ordered_idx)
