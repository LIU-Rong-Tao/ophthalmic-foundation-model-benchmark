from __future__ import annotations


def validate_embeddings(embeddings) -> None:
    import torch

    if embeddings.ndim != 2:
        raise ValueError(
            f"Adapter must return [batch, embedding_dim], got {tuple(embeddings.shape)}"
        )
    if not torch.isfinite(embeddings).all():
        raise ValueError("Adapter returned NaN or Inf embeddings")
