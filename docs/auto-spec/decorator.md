# Automatic Specification decorator

### Creating subscribers module

```python
{!./src/auto_spec/decorator/user_events.py!}
```

### Start subscriber to listen events

```bash
{!./src/auto_spec/decorator/subscriber.sh!}
```

```
{!./src/subscriber.output!}
```

### Publishing Updates

```python
{!./src/auto_spec/decorator/publish.py!}
```

```
{!./src/publish.output!}
```

### Receive Updates

```
{!./src/subscriber-receive-message.output!}
```

### Expose Specification

```bash
{!./src/auto_spec/decorator/docs.sh!}
```

```bash
curl -i localhost:5000/asyncapi.yaml
```
