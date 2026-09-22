# 3 · Network

The NUC sits on the installation's private LAN and receives user input over
HTTP on its wired interface.

## Addressing

Static IP via ifupdown (Debian's default) — see
[`config/network/interfaces.d/c2c-lan`](../config/network/interfaces.d/c2c-lan).
Default plan (adapt to the venue):

| Host                | Address           |
|---------------------|-------------------|
| Router / gateway    | `192.168.10.1`    |
| **NUC (`c2c-server`)** | `192.168.10.10` |
| Input clients       | `192.168.10.100+` (DHCP from router) |

Deploy and apply:

```sh
sudo cp config/network/interfaces.d/c2c-lan /etc/network/interfaces.d/
# remove the installer's DHCP stanza for the same interface (usually the
# `allow-hotplug eno1` / `iface eno1 inet dhcp` lines):
sudo nano /etc/network/interfaces
sudo systemctl restart networking
```

DNS with plain ifupdown is *not* set per-interface: put the nameservers in
`/etc/resolv.conf` (the installer writes it once; with a static address it
won't be touched again):

```
nameserver 192.168.10.1
nameserver 9.9.9.9
```

If the venue LAN has no internet uplink, the SSH maintenance tunnel
(`docs/05-ssh-tunnel.md`) needs a second uplink (e.g. LTE router) — decide
this before the opening, not after.

## Firewall

`bootstrap.sh` configures **ufw**:

- allow **22/tcp** (SSH) from the LAN only
- allow **8080/tcp** (input API) from the LAN only
- deny everything else incoming; all outgoing allowed (tunnel, updates)

Check with `sudo ufw status verbose`. If you change the API port, change it
in the ufw rule *and* in `/etc/c2c/c2c.env`.

## Input clients

Clients POST user input to the API:

```
POST http://192.168.10.10:8080/…
```

Give clients the NUC's static IP directly (or add a DNS entry on the router);
don't rely on mDNS — it is flaky across venue switches/APs.
