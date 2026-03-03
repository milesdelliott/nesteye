# NestEye

Raspberry Pi Zero W bird box camera. Streams live video via a Flask server and exposes it remotely through a Cloudflare Tunnel — no port forwarding required.

## Hardware

- Raspberry Pi Zero W 1.1
- Arducam 16MP Autofocus (CSI ribbon cable)
- 32GB microSD (Class 10)
- 5V 2A USB power adapter

The camera ribbon connects to the Pi's CSI slot. That's the only wiring needed — WiFi is built in.

---

## Files in This Repo

```
app/
  app.py                     → /home/miles/nesteye/app/app.py
  templates/
    index.html               → /home/miles/nesteye/app/templates/index.html

systemd/
  nesteye.service            → /etc/systemd/system/nesteye.service
  cloudflared.service        → /etc/systemd/system/cloudflared.service

cloudflared/
  config.yml                 → /home/miles/.cloudflared/config.yml  (edit first!)
```

---

## Setup on the Pi

### 1. Flash & Boot

Use Raspberry Pi Imager:
- OS: **Raspberry Pi OS Lite (64-bit)**
- Hostname: `nesteye`
- Enable SSH (password auth)
- Set your WiFi SSID and password

### 2. SSH In & Update

```bash
ssh miles@nesteye.local
sudo apt update && sudo apt upgrade -y
```

Change your password if you haven't:
```bash
passwd
```

### 3. Enable Camera Interface

```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

Verify it works:
```bash
libcamera-hello
```

### 4. Install Dependencies

```bash
sudo apt install -y python3-picamera2 python3-libcamera libcamera-tools \
    python3-flask python3-flask-cors python3-pip htop

pip3 install --break-system-packages flask flask-cors werkzeug
```

### 5. Copy App Files to the Pi

From your Mac (run from this repo root):

```bash
scp -r app miles@nesteye.local:/home/miles/nesteye/
scp systemd/nesteye.service miles@nesteye.local:/tmp/
scp systemd/cloudflared.service miles@nesteye.local:/tmp/
```

On the Pi, move the service files:
```bash
sudo mv /tmp/nesteye.service /etc/systemd/system/
sudo mv /tmp/cloudflared.service /etc/systemd/system/
```

### 6. Enable the Flask Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable nesteye.service
sudo systemctl start nesteye.service
sudo systemctl status nesteye.service
```

Test locally — find the Pi's IP and open `http://<pi-ip>:5000` in a browser.

---

## Cloudflare Tunnel (Remote Access)

Skip this section if local-only access is fine.

### 1. Install cloudflared

```bash
curl -L --output cloudflared.deb \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm.deb
sudo dpkg -i cloudflared.deb
```

### 2. Authenticate

```bash
cloudflared tunnel login
# Follow the printed URL to log in — paste it into a browser on another machine
```

### 3. Create the Tunnel

```bash
cloudflared tunnel create nesteye
# Note the tunnel ID printed — you'll need it in the next step
```

### 4. Configure the Tunnel

Edit `cloudflared/config.yml` in this repo:
- Replace `<TUNNEL_ID>` with your actual tunnel ID
- Replace `nesteye.your-domain.com` with your Cloudflare domain

Then copy it to the Pi:
```bash
scp cloudflared/config.yml miles@nesteye.local:/home/miles/.cloudflared/config.yml
```

### 5. Route DNS

```bash
cloudflared tunnel route dns nesteye nesteye.your-domain.com
```

### 6. Enable the Tunnel Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared.service
sudo systemctl start cloudflared.service
```

Your stream is now available at `https://nesteye.your-domain.com`.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/video_feed` | GET | MJPEG stream |
| `/api/status` | GET | Camera + uptime status |
| `/api/camera/settings` | GET | Current camera config |
| `/api/camera/focus` | POST | Trigger autofocus |
| `/api/capture` | POST | Download a still JPEG |

---

## Quick Commands

```bash
# View Flask logs
sudo journalctl -u nesteye.service -f

# View tunnel logs
sudo journalctl -u cloudflared.service -f

# Restart Flask
sudo systemctl restart nesteye.service

# Check Pi temp
vcgencmd measure_temp

# Find Pi's local IP
hostname -I
```

---

## Reducing Resolution (if CPU is overloaded)

Edit `app/app.py` and change:
```python
main={"size": (1920, 1440), "format": "RGB888"},
```
to:
```python
main={"size": (1280, 960), "format": "RGB888"},
```

Then redeploy and restart the service.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Camera not detected | Check CSI ribbon; run `libcamera-hello` |
| Flask won't start | Check logs: `journalctl -u nesteye.service -f` |
| Tunnel not connecting | Run `cloudflared tunnel info nesteye`; check logs |
| Weak WiFi | Move router closer or add a WiFi repeater near the nest box |
| High CPU usage | Reduce resolution (see above) |
