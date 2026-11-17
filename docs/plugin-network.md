# JavaScript plugin networking

`host.http(request)` uses a separate HTTP client without the app's account cookies or authentication interceptors. It returns `status`, `headers`, `body`, `bodyEncoding`, `finalUrl` and `setCookies`. Redirects are returned to the plugin instead of followed automatically. A plugin that follows them must validate each destination and manage its own account cookies. `setCookies` preserves every separate Set-Cookie header.

Text bodies remain the default. Binary protobuf requests and responses can opt into base64:

```javascript
const response = await host.http({
  url: endpoint,
  method: 'POST',
  headers: {'Content-Type': 'application/x-protobuf'},
  body: encodedRequest,
  bodyEncoding: 'base64',
  responseType: 'base64',
  maxBytes: 512 * 1024
});
```

The decoded request and response bodies are limited to 2 MiB. `maxBytes` can lower the response limit. HTTP timeouts are between 1 and 30,000 ms. Unsupported body encodings are rejected. Native HttpRequest and HttpResponse constructors retain their original signatures; the additional serialized fields are body properties.

## WebSocket sessions

The plugin manifest must declare `network.websocket` in `capabilities`. Sockets belong to the plugin session and close on disable, replacement, failed startup or app shutdown. A session can open at most four sockets. URLs must use `wss`; `ws` is allowed only for loopback development servers. URL credentials, fragments, invalid headers and WebSocket handshake header overrides are rejected. Transport failures use safe error codes without copying connection URLs or server close reasons.

```javascript
const id = await host.socket.open({url: dealerUrl, headers: {Authorization: authorization}});
await host.socket.send(id, JSON.stringify(command));
const event = await host.socket.receive(id, 10000);
await host.socket.close(id);
```

`open` resolves after the handshake. `receive(id, timeoutMs)` returns the next event, or `null` on timeout. The default timeout is 10 seconds; zero drains the queue without waiting. This form can be awaited during initialization, login and service callbacks. Frames arriving with the handshake remain buffered until consumed.

Events have one of these shapes:

- `{type: 'text', text}`
- `{type: 'closed', code}`
- `{type: 'error', code}`

Text frames and outgoing messages are limited to 512 KiB. The incoming queue holds at most 16 events; exceeding these limits closes the connection with `SOCKET_LIMIT`. Binary WebSocket frames are rejected with `SOCKET_BINARY_UNSUPPORTED`.

For background observation, a plugin may instead register `host.on('socket.message/' + id, callback)`. Events are delivered only to that owning plugin. Buffered events drain after initialization and listener registration. Do not mix an active event listener with `receive` on the same socket. Do not await an event callback from an initialization, login or service callback: those callbacks are serialized, so use `receive` for a response needed by the current callback.
