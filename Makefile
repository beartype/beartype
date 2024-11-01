install:
	[ -f ~/.cargo/bin/uv || curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync --all-extras
