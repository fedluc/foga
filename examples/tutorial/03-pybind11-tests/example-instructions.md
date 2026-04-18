# Tutorial 03 Example

The example environment is ready in `/workspace/example`.

Run these commands to exercise the example:

```bash
foga validate
foga install --target system
foga install --target dev
foga build cpp
./build-cpp/hello_cli
foga build python
foga test
foga format --dry-run
foga lint
```

You can also inspect the configured workflows with:

```bash
foga inspect test
```
