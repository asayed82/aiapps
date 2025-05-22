.PHONY: frontend fe client backend be server

SERVER_DIR := server
CLIENT_DIR := client

frontend fe client: frontend_impl
backend be server: backend_impl

frontend_impl:
	@if [ -d "$(CLIENT_DIR)" ]; then \
		python -m http.server 8000 --directory "$(CLIENT_DIR)"; \
	else \
		echo "Error: $(CLIENT_DIR) directory does not exist!" >&2; \
		exit 1; \
	fi

backend_impl:
	@if [ -d "$(SERVER_DIR)" ]; then \
		python "$(SERVER_DIR)/server.py"; \
	else \
		echo "Error: $(SERVER_DIR) directory does not exist!" >&2; \
		exit 1; \
	fi

context-file:
	find . \( -iname "*.py" -o -iname "*.js" -o -iname "*.html" \) -print0 | xargs -0 -I {} sh -c 'echo "=== {} ==="; cat {}' > code-context.txt