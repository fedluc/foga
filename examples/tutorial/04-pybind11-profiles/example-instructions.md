# Tutorial 04 Example

The example environment is ready in `/workspace/example`.

Run these commands to exercise the example:

```bash
foga validate
foga install --target system
foga install --target dev
foga build python
foga build cpp
foga build --profile release cpp
foga test
foga test --profile release cpp
foga format --dry-run
foga lint
```

You can also inspect the configured workflows with:

```bash
foga inspect --profile release build cpp
```
