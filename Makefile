.PHONY: check test build bench release-check sync-docs validate-ecosystem

check:
	scripts/check.sh

test:
	scripts/test.sh

build:
	scripts/build.sh

bench:
	scripts/benchmark-smoke.sh

release-check:
	scripts/release-check.sh

sync-docs:
	scripts/sync-docs.sh

validate-ecosystem:
	scripts/validate-ecosystem-json.py
