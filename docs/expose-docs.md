# Serving the AsyncAPI Docs

## Serve docs from an already created spec

```bash
{!./src/auto_spec/docs.sh!}
```

```
{!./src/auto_spec/docs.output!}
```


## Create subscriber module

```python
{!./src/auto_spec/user_events_http.py!}
```


## Start subscriber to listen events from exposed spec

```bash
{!./src/auto_spec/subscriber-http.sh!}
```


## Publishing updates from exposed spec

```python
{!./src/auto_spec/publish_http.py!}
```

```
{!./src/publish.output!}
```


## Receive Updates

```
{!./src/subscriber-receive-message.output!}
```
