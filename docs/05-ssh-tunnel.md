# 5 · SSH maintenance tunnel

The NUC is usually behind a venue NAT/firewall, so it dials **out**: an
autossh **reverse tunnel** to a machine you control (VPS or home server with
a public address), kept alive by systemd
([`config/systemd/c2c-tunnel.service`](../config/systemd/c2c-tunnel.service)).

```
you ──ssh -p 2222 localhost──▶ relay host ◀──reverse tunnel── NUC
```

## One-time setup

### On the NUC

```sh
# dedicated key, no passphrase (unattended)
sudo -u c2c ssh-keygen -t ed25519 -f /home/c2c/.ssh/id_tunnel -N '' -C c2c-tunnel
sudo -u c2c cat /home/c2c/.ssh/id_tunnel.pub   # copy this
```

Set the relay host/user/port in `/etc/c2c/c2c.env`
(`TUNNEL_HOST`, `TUNNEL_USER`, `TUNNEL_REMOTE_PORT` — see
[`config/c2c.env.example`](../config/c2c.env.example)), then:

```sh
sudo systemctl enable --now c2c-tunnel
```

### On the relay host

Add the NUC's public key to the tunnel user's `authorized_keys`, restricted
to port forwarding only:

```
restrict,port-forwarding ssh-ed25519 AAAA… c2c-tunnel
```

In the relay's `sshd_config`, keep `GatewayPorts no` (default) so the
forwarded port is only reachable from the relay itself.

## Using it

From anywhere, hop via the relay:

```sh
ssh -J relayuser@relay.example.org -p 2222 admin@localhost
# or two steps: ssh relay.example.org, then ssh -p 2222 admin@localhost
```

## Hardening on the NUC

`bootstrap.sh` deploys [`config/ssh/10-c2c.conf`](../config/ssh/10-c2c.conf):
key-only auth, no root login. Put your personal public key in
`admin`'s `authorized_keys` before disabling password auth — the config is
only applied by `bootstrap.sh` after it finds at least one authorized key.

## If the tunnel dies

autossh reconnects automatically (`Restart=always`, keep-alives every 30 s).
If the relay host itself is down, the service retries forever — nothing to
do on the NUC. Test the whole chain before the exhibition opens by pulling
the NUC's network cable for a minute and confirming the tunnel comes back.
