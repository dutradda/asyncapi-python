## Starting Development

```bash
git clone git@github.com:dutradda/asyncapi-python.git --recursive
cd asyncapi
make setup-python-virtualenv
source venv/bin/activate
make setup-python-project
bake setup-asyncapi
bake dependencies
```

## Running the integration suite:

```bash
bake integration
```

## Other bake tasks:

```bash
bake check-code

bake tests-docs

bake serve-docs

bake add-changelog m="Add my cool feature"
```

You can run `bake` to see all tasks available.
