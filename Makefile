PYTHON ?= python3

.PHONY: check test validate links preview screenshots live-check mcp-metadata mcp-runtime mcp-workaround clean

check: test validate

test:
	$(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) tools/verify_profile.py --check-links --check-mcp

links:
	$(PYTHON) tools/verify_profile.py --check-links

preview:
	$(PYTHON) tools/render_preview.py

screenshots:
	$(PYTHON) tools/capture_screenshots.py

live-check:
	$(PYTHON) tools/verify_live_profile.py

mcp-metadata:
	$(PYTHON) tools/audit_mcp_packages.py --metadata

mcp-runtime:
	$(PYTHON) tools/audit_mcp_packages.py --runtime

mcp-workaround:
	$(PYTHON) tools/audit_mcp_packages.py --workaround

clean:
	rm -rf .artifacts __pycache__ tools/__pycache__ tests/__pycache__
