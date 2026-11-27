# Aria2: authenticated engine listener correction

The existing `aria2-rpc` Kubernetes Service resolves to VM103's published engine
port, but `rpc-listen-all=false` restricted aria2c to its container loopback.
The gateway's separate RPC adapter could therefore work while native internal
RPC clients failed. This is a listener fault, not a DNS record fault.

`aria2-listener-config.py` changes only `rpc-listen-all`, refuses a missing or empty
RPC secret, and runs before Compose starts, after the dedicated firewall guards.
Deploy the helper to `/etc/homelab-aria2/aria2-listener-config.py` together with the
updated unit. Do not run it against an active writer. No RPC secret is published.

Verified after a systemd restart:
- authenticated read-only `aria2.getVersion` through the original cluster DNS;
- the same native endpoint rejects a request without its RPC token;
- AriaNg HTML through its original cluster DNS;
- read-only version request through the gateway's VM adapter;
- HTTPS gateway preserves its pinned certificate and Basic challenge;
- all three VM listeners retain cluster-only firewall rules and are unreachable
  from the non-cluster management host.

A successful password-based Basic login was **not** exercised: the migration has
only the existing password hash. No password was reset and no identity added.
Private acceptance details and preserved configuration are outside Git.

Test helper safeguards with `python3 -m unittest discover -s tests`.
`it-tools-cluster-firewall.py` extends only the existing dedicated ITTools chain
to the known Kubernetes node and pod ranges. Its oneshot unit preserves those
rules across service restarts; it refuses an absent or unexpected original guard
rather than guessing or flushing shared rules. The terminal drop is retained.
The helper was exercised twice successfully before stopping the original pod.
The existing production runner previously exercised return-of-current-data
rollback. The separate draft rollback CLI is not acceptance-tested or published.

## Redundant origins

Original ITTools, FlareSolverr, SearXNG/Valkey and Dependency-Track frontend can
be scaled to zero only through their owning GitOps sources, after verifying VM
backends. Preserve original Service DNS by explicit VM EndpointSlices rather
than leaving a selector pointing at zero pods. Dependency-Track API/database and
all PVCs remain untouched. Reversal requires restoring the owning manifest from
the preceding Git revision and verifying reconciliation; never revert a stateful
writer without returning its current data first.
