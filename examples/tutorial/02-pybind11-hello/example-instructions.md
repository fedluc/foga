# Tutorial 02 Example

The example environment is ready in `/workspace/example`.

Run these commands to exercise the example:

```bash
foga validate
foga install --target system
foga build cpp
./build-cpp/hello_cli
foga build python
foga install --target dev
hello-demo
```

You can also inspect the configured workflows with:

```bash
foga inspect build cpp
```
