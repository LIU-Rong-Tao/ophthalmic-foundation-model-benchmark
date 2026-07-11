.PHONY: install import-seed validate catalog test check
install:
	pip install -e ".[dev]"
import-seed:
	ophbench registry import-seed --input seed/ophthalmic_models_seed_v0.xlsx
validate:
	ophbench registry validate
catalog:
	ophbench catalog build
test:
	pytest -q
check:
	ruff check .
	ophbench registry validate
	ophbench catalog build --check
	pytest -q
