# Serving the AsyncAPI Docs

### Serve docs from an already created spec

```yaml
{!./src/yaml_spec/api-spec.yaml!}
```

```bash
{!./src/yaml_spec/docs.sh!}
```

```
{!./src/docs-server.output!}
```

### Create subscriber module

```python
{!./src/expose_docs/user_events.py!}
```

### Start subscriber to listen events from exposed spec

```bash
{!./src/expose_docs/subscriber.sh!}
```

### Publishing updates from exposed spec

```python
{!./src/expose_docs/publish.py!}
```

```
{!./src/publish.sh!}

{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```

### Request YAML Specification

```bash
curl -i localhost:5000/asyncapi.yaml
```

```
{!./src/docs-yaml.output!}
```

### Request JSON Specification

```bash
curl -i localhost:5000/asyncapi.json
```

```
{!./src/docs-json.output!}
```
