# Automatic Specification Declaration

## Creating subscribers module

```python
{!./src/auto_spec/user_events.py!}
```

## Start subscriber to listen events

```bash
{!./src/auto_spec/subscriber.sh!}
```

```
{!./src/subscriber.output!}
```


## Publishing Updates

```python
{!./src/auto_spec/publish.py!}
```

```
{!./src/publish.output!}
```


## Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
