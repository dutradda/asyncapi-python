# Serving the AsyncAPI Docs

### Serve docs from an already created spec

```bash
{!./src/auto_spec/module/docs.sh!}
```

```
{!./src/docs-server.output!}
```

### Create subscriber module

```python
{!./src/expose_docs/user_events_http.py!}
```

### Start subscriber to listen events from exposed spec

```bash
{!./src/expose_docs/subscriber-http.sh!}
```

### Publishing updates from exposed spec

```python
{!./src/expose_docs/publish_http.py!}
```

```
{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
