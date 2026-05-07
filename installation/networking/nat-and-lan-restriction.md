# Ubuntu iptables Setup Summary

This summarizes how to set up NAT on the bridge, created by `one-deploy` for the virtual network (`10.1.1.0/24`) and some restrictions to prevent the OpenClaw VM to talk to the local network (`192.168.1.0/24`)

## 1. Enable IPv4 forwarding

```bash
sudo sysctl -w net.ipv4.ip_forward=1

# Optional: make persistent
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ipforward.conf
sudo sysctl --system
```

---

## 2. NAT traffic from `10.1.1.0/24` to the local LAN

> Replace `enp3s0` with your actual LAN interface if needed.

```bash
sudo iptables -t nat -A POSTROUTING \
  -s 10.1.1.0/24 \
  -d 192.168.1.0/24 \
  -o enp3s0 \
  -j MASQUERADE
```

---

## 3. Allow established/return traffic

```bash
sudo iptables -A FORWARD \
  -m conntrack \
  --ctstate RELATED,ESTABLISHED \
  -j ACCEPT
```

---

## 4. Block general access from `10.1.1.0/24` into `192.168.1.0/24`

```bash
sudo iptables -A FORWARD \
  -s 10.1.1.0/24 \
  -d 192.168.1.0/24 \
  -j REJECT \
  --reject-with icmp-port-unreachable
```

This creates a default deny policy between the VPN/subnet and the local LAN.

---

## 5. Allow access specifically to this Ubuntu host on port `8080`

The goal of this is to run the restricted OpenNebula API on the `.16` host and make it reachable for OpenClaw VM.

> Important: this must be an INPUT rule, not FORWARD.

```bash
sudo iptables -I INPUT 2 \
  -p tcp \
  -s 10.1.1.0/24 \
  -d 192.168.1.16 \
  --dport 8080 \
  -j ACCEPT
```

This allows:
- Source network: `10.1.1.0/24`
- Destination host: `192.168.1.16`
- TCP port: `8080`

while keeping the broader LAN blocked.

---

## 6. Persist rules across reboot

```bash
sudo apt install -y iptables-persistent

sudo iptables-save | sudo tee /etc/iptables/rules.v4 >/dev/null

sudo systemctl enable netfilter-persistent
sudo systemctl restart netfilter-persistent
```

---

# Verification

## View active rules

```bash
sudo iptables -L -n -v --line-numbers
```

## Verify NAT

1. check VMs can talk to each other on the VNET.
1. check OpenClaw VM can't reach LAN
1. check public internet access

## Verify service is listening on port 8080

```bash
sudo ss -ltnp | grep :8080
```

## Verify persistent rule exists

```bash
sudo grep -n "192.168.1.16.*8080" /etc/iptables/rules.v4
```