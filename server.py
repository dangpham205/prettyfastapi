from typing import Any, Awaitable, Callable, MutableMapping

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

total_connections = 0

async def handle_lifespan_rq(scope: Scope, receive: Receive, send: Send):
    assert scope["type"] == "lifespan"

    while True:
        message = await receive()
        print(f"Got message: {message}")

        # talking to the protocol server uvicorn
        if message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})
            # shutdown
            break

async def handle_http_rq(scope: Scope, receive: Receive, send: Send):
    assert scope["type"] == "http"
    while True:
        print("Receiving messages..")
        message = await receive()
        print(f"Received message: {message}")

        # In http scope, when a rq closed, and the server try receive() message, will get: {type: http.disconnect}
        if message["type"] == "http.disconnect":
            return

        # Once no more messages are received, start sending response
        if not message["more_body"]:
            break

    response_message = {
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain")]
    }
    print("Sending HTTP response start: ", response_message)
    await send(response_message)
    response_message = {
        "type": "http.response.body",
        "body": b"thank you",
        "more_body": False,
    }
    print("Sending HTTP response body: ", response_message)
    await send(response_message)

class ASGIApp():

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        global total_connections
        total_connections += 1
        current_connections = total_connections
        print(f"Beginning connection {current_connections}. Scope: ", scope)
        if scope["type"] == "lifespan":
            await handle_lifespan_rq(scope, receive, send)
        elif scope["type"] == "http" or scope["type"] == "https":
            await handle_http_rq(scope, receive, send)
        print(f"Ending connection {current_connections}")


def main():
    import uvicorn
    application = ASGIApp()
    uvicorn.run(
        app=application,
        port=3000,
        log_level="info",
        use_colors=True,
    )

if __name__ == "__main__":
    main()
