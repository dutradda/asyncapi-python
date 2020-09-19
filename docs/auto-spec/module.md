# Automatic Specification module

### Creating automatic specification

```python
{!./src/auto_spec/module/specification.py!}
```

### Creating subscribers module

```python
{!./src/auto_spec/module/user_events.py!}
```

### Start subscriber to listen events

```bash
{!./src/auto_spec/module/subscriber.sh!}
```

```
{!./src/subscriber.output!}
```

### Publishing Updates

```python
{!./src/auto_spec/module/publish.py!}
```

```
{!./src/publish.sh!}

{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```

### Expose Specification

```bash
{!./src/auto_spec/module/docs.sh!}
```

```bash
curl -i localhost:5000/asyncapi.yaml
```
