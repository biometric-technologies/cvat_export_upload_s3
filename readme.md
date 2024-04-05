### Run

```bash
python3 export.py
```

```bash
docker build -t cvat_export .
docker run --cap-add=NET_ADMIN -v ./wg0.conf:/etc/wireguard/wg0.conf -v ./.env:/app/conf/.env --sysctl="net.ipv4.conf.all.src_valid_mark=1" -it --rm cvat_export
```