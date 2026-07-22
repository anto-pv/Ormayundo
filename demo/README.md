# Demo GIF

`assets/ormayundo-demo.gif` is rendered from [`demo.tape`](demo.tape) with
[VHS](https://github.com/charmbracelet/vhs). `replay.py` is an offline stand-in
(no API key or network) that returns the same output shapes as the real
`remember()` / `recall()`, so the GIF is reproducible anywhere.

## Render it

With VHS installed locally:

```bash
cd demo && vhs demo.tape        # writes ormayundo-demo.gif
```

No VHS? Use the official Docker image (needs only Docker):

```bash
docker run --rm -v "$PWD/demo:/vhs" -w /vhs ghcr.io/charmbracelet/vhs demo.tape
```

Then copy the result over the tracked one:

```bash
cp demo/ormayundo-demo.gif assets/ormayundo-demo.gif
```
