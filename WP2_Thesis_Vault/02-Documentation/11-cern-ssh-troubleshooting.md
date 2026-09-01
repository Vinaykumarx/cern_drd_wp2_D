# CERN SSH Connection Troubleshooting

**Date:** 2026-06-16 15:11

**Category:** `CERN-DRD8-WP4`

---

### 🧑 **User** _2026-06-16 15:11_

go through this and let. me know how to check whether no issue with von connect to connect to my cern remote ssh

---

### 🤖 **Assistant** _2026-06-16 15:11_

Based on the CERN eduVPN support page you have open, the fastest way to determine whether your SSH issue is caused by VPN connectivity or by the remote server itself is to perform a few checks in order. citeturn0search0

### 1. Verify eduVPN is actually passing traffic

Open the eduVPN client and check **Show Connection Info**.

You should see:

- Uploaded counter increasing
- Downloaded counter increasing
- Certificate validity countdown still active

If the **Downloaded counter remains at 0**, CERN notes that a firewall may be blocking traffic from the CERN VPN server. This would explain SSH failures. citeturn0search0

---

### 2. Check WireGuard handshake (Linux)

Run:

```bash
sudo wg show eduVPN
```

Look for:

```text
latest handshake: 20 seconds ago
transfer: 10 MiB received, 5 MiB sent
```

Good signs:

- Recent handshake (seconds or a few minutes ago)
- Non-zero received and sent traffic

Bad signs:

```text
latest handshake: never
```

or

```text
transfer: 0 B received
```

That indicates the VPN tunnel itself is not working correctly. citeturn0search0turn0search3

---

### 3. Verify CERN routes are present

Run:

```bash
sudo wg showconf eduVPN
```

Then:

```bash
ip rule show
```

and

```bash
ip route get 128.142.0.0
```

Expected result:

```text
128.142.0.0 dev eduVPN
```

If traffic to CERN is not going through the `eduVPN` interface, SSH will never reach CERN resources. citeturn0search0

---

### 4. Test basic CERN connectivity

Before SSH, check whether CERN is reachable through VPN.

Try:

```bash
ping 128.142.0.0
```

or

```bash
ping <your-server-ip>
```

Then:

```bash
traceroute <your-server-ip>
```

If ping and traceroute fail, the problem is VPN/routing.

If they succeed, VPN is likely fine and the issue is elsewhere. citeturn0search2

---

### 5. Test SSH with verbose logging

This is the most useful test.

```bash
ssh -vvv username@server
```

Look for:

```text
Connecting to ...
Connection established.
```

If you get that far, VPN is working.

Common outcomes:

**Connection timeout**

```text
Connection timed out
```

Usually network, VPN, routing, or firewall.

**Connection refused**

```text
Connection refused
```

Server reachable but SSH service not running.

**Authentication failure**

```text
Permission denied
```

VPN is fine; credentials are wrong.

CERN support specifically recommends collecting `ssh -v` output for troubleshooting. citeturn0search2

---

### 6. Determine whether the server itself is down

Since you mentioned that **you lost remote SSH access suddenly and had to physically go to the office**, ask Nicola to test from his side.

If:

- You cannot SSH
- Nicola cannot SSH
- Both of you are connected to CERN VPN

then the problem is very likely:

- Server offline
- SSH daemon crashed
- Network issue on the server
- Firewall change
- Host unreachable

rather than a problem with your home connection. CERN troubleshooting guidance recommends checking whether other clients can reach the same server to distinguish client-side versus server-side issues. citeturn0search2

---

### My recommended quick checklist

Run these in order:

```bash
sudo wg show eduVPN
```

```bash
ip route get <server-ip>
```

```bash
ping <server-ip>
```

```bash
ssh -vvv user@server-ip
```

Then message Nicola:

> Can you please try connecting to the server from your side as well? I want to verify whether the issue is specific to my connection or if the server itself is unreachable.

If you paste the outputs of:

```bash
sudo wg show eduVPN
ip route get <server-ip>
ssh -vvv user@server-ip
```

I can usually pinpoint within a few minutes whether the problem is:
- VPN,
- routing,
- firewall,
- SSH service,
- or the server itself.

---
