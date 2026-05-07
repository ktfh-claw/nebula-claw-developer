# OpenNebula VM Autostart via systemd

This guide configures a single OpenNebula VM to automatically resume after host reboot. Note that the I didnt manage to make the OpenNebula-native way work: ["A Complete Example: Autostart Hooks for KVM"](https://docs.opennebula.io/7.2/product/integration_references/system_interfaces/hook_driver/).

---

# 1. Create the autostart script

At the below path with content of `openclaw-vm-autostart.sh`.

Make it executable:

```bash
sudo chmod +x /usr/local/sbin/openclaw-vm-autostart.sh
```

---

# 2. Create the systemd service

At path `/etc/systemd/system/openclaw-vm-autostart.service` with content of `openclaw-vm-autostart.service`.

---

# 3. Enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-vm-autostart.service
```

---

# 4. Test manually

Run:

```bash
sudo systemctl start openclaw-vm-autostart.service
```

View logs:

```bash
sudo journalctl -u openclaw-vm-autostart.service -n 100 --no-pager
```

---

# 5. Reboot test

Ensure VM is running:

```bash
onevm list
```

Reboot host:

```bash
sudo reboot
```

After host returns:

```bash
onevm list
```

VM should automatically transition back to running state after a while.

Check service logs:

```bash
sudo journalctl -u openclaw-vm-autostart.service --no-pager
```
