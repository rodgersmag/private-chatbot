#!/bin/bash
set -euo pipefail

# Start Ollama server in the background, wait until it's reachable,
# then pull the model. Finally wait on the server process so the
# container stays alive and logs from the server are visible.

ADDRESS="0.0.0.0:11434"

echo "Starting ollama serve on ${ADDRESS} (background)"
export OLLAMA_HOST="${ADDRESS}"
ollama serve &
SERV_PID=$!

# Wait for server to be up (timeout 60s)
echo "Waiting for Ollama server to become available..."
RETRIES=60
for i in $(seq 1 ${RETRIES}); do
	if curl -sS -o /dev/null "http://127.0.0.1:11434" >/dev/null 2>&1; then
		echo "Ollama server is up (after ${i}s)"
		break
	fi
	if ! kill -0 ${SERV_PID} >/dev/null 2>&1; then
		echo "Ollama server process exited early. Check logs." >&2
		exit 1
	fi
	sleep 1
done

if ! curl -sS -o /dev/null "http://127.0.0.1:11434" >/dev/null 2>&1; then
	echo "Timed out waiting for Ollama server" >&2
	exit 1
fi

echo "Pulling model qwen3:1.7b (if missing)"
# Attempt to pull; if already present the server will skip
if ! ollama list 2>/dev/null | grep -q "qwen3:1.7b"; then
	echo "Model qwen3:1.7b not found locally. Starting download..."
	# Start the pull and show progress output in the container logs
	ollama pull qwen3:1.7b || true

	# After pull returns, poll until model shows in list (some pulls may complete slowly)
	echo "Waiting for model to become available..."
	for i in $(seq 1 600); do
		if ollama list 2>/dev/null | grep -q "qwen3:1.7b"; then
			echo "Model qwen3:1.7b is now available"
			break
		fi
		sleep 1
		if (( i % 10 == 0 )); then
			echo "...still downloading (waiting ${i}s)"
		fi
	done
else
	echo "Model qwen3:1.7b already present"
fi

echo "Model pull complete (or already present). Tailing server logs..."

# Wait on the server process so the container keeps running and logs remain visible
wait ${SERV_PID}