from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .builder import catalog_is_current
from .loader import load_registry


class RegistryValidationError(ValueError):
    pass


TOKEN_PATTERN = re.compile(
    r"(?:hf_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,})"
)


def _duplicates(values):
    return sorted(value for value, count in Counter(values).items() if count > 1)


def validate_records(models, checkpoints):
    errors = []
    warnings = []
    model_duplicates = _duplicates(m.model_id for m in models)
    checkpoint_duplicates = _duplicates(c.checkpoint_id for c in checkpoints)
    if model_duplicates:
        errors.append(f"Duplicate model_id: {', '.join(model_duplicates)}")
    if checkpoint_duplicates:
        errors.append(f"Duplicate checkpoint_id: {', '.join(checkpoint_duplicates)}")
    model_ids = {m.model_id for m in models}
    for checkpoint in checkpoints:
        if checkpoint.model_id not in model_ids:
            errors.append(
                f"Checkpoint {checkpoint.checkpoint_id} references unknown model_id "
                f"{checkpoint.model_id}"
            )
        if checkpoint.weight_url and Path(checkpoint.weight_url).is_absolute():
            errors.append(f"Checkpoint {checkpoint.checkpoint_id} points to an absolute local path")
    urls = [u for m in models for u in (m.paper_url, m.code_url) if u]
    urls.extend(c.weight_url for c in checkpoints if c.weight_url)
    for duplicate in _duplicates(urls):
        warnings.append(f"Duplicate URL: {duplicate}")
    payload = "\n".join(str(item.model_dump()) for item in [*models, *checkpoints])
    if TOKEN_PATTERN.search(payload):
        errors.append("Registry contains a token-like secret")
    if errors:
        raise RegistryValidationError("; ".join(errors))
    return warnings


def validate_registry(
    root: Path = Path("registry"), online: bool = False, check_catalog: bool = True
):
    models, checkpoints = load_registry(root)
    warnings = validate_records(models, checkpoints)
    if online:
        for url in sorted(
            {u for m in models for u in (m.paper_url, m.code_url) if u}
            | {c.weight_url for c in checkpoints if c.weight_url}
        ):
            try:
                with urlopen(
                    Request(url, method="HEAD", headers={"User-Agent": "ophbench/0.1"}), timeout=10
                ) as response:
                    if response.status >= 400:
                        warnings.append(f"URL returned HTTP {response.status}: {url}")
            except HTTPError as exc:
                level = "warning" if exc.code in {302, 401, 403} else "error"
                warnings.append(f"URL {level} HTTP {exc.code}: {url}")
            except (URLError, TimeoutError) as exc:
                warnings.append(f"URL warning {type(exc).__name__}: {url}")
    if (
        check_catalog
        and Path("catalog").exists()
        and not catalog_is_current(root, Path("catalog"), Path("MODEL_ZOO.md"))
    ):
        raise RegistryValidationError("Generated catalog is stale; run 'ophbench catalog build'")
    return models, checkpoints, warnings
