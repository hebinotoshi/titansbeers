# Titans Beers Line Bot

A Line Bot for Titans Craft Beer Bar & Bottle Shop that displays current beers on tap from Untappd, allows users to save favorites, and more.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│   Line App  │────▶│   Render    │────▶│   Oracle Cloud VM   │
│   (Users)   │◀────│  (Bot API)  │◀────│  (Scraper + SQLite) │
└─────────────┘     └─────────────┘     └─────────────────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────────┐
                                        │      Untappd        │
                                        │   (Beer Menu Data)  │
                                        └─────────────────────┘
```

- **Line App**: Users interact via Line messaging app
- **Render**: Hosts the Line webhook handler (FastAPI)
- **Oracle Cloud VM**: Scrapes Untappd (bypasses IP blocking) + stores saved beers in SQLite
- **Untappd**: Source of beer menu data

## Commands

| Command | Description |
|---------|-------------|
| `beer`, `ビール`, `🍺`, `🍻` | Show current beers on tap |
| `my beers`, `mybeers`, `saved` | Show your saved beers |
| `size`, `サイズ` | Show drink size options |
| `staff` | Show staff carousel |
| `hagehige` | Show Hage & Hige beers |
| `yurie`, `adam` | Show personal cards |

## Project Structure

```
titansbeers/
├── app/
│   ├── main.py           # FastAPI app with webhook endpoint
│   ├── config.py         # Configuration and command triggers
│   ├── scraper.py        # Calls Oracle VM scraper API
│   ├── line_handler.py   # Handles Line messages and postbacks
│   ├── flex_messages.py  # Builds Line Flex Message carousels
│   └── data/
│       ├── size_images.json
│       ├── staff.json
│       └── hagehige.json
├── oracle_scraper.py     # Script running on Oracle VM
├── requirements.txt
├── Procfile
└── .env.example
```

## Setup

### 1. Line Developer Console

1. Go to [developers.line.biz](https://developers.line.biz/console/)
2. Create a Provider and Messaging API channel
3. Get your **Channel Secret** (Basic settings)
4. Get your **Channel Access Token** (Messaging API → Issue)
5. Set Webhook URL to: `https://your-app.onrender.com/webhook`
6. Enable **Use webhook**

### 2. Render Deployment

1. Create a Web Service on [render.com](https://render.com)
2. Connect your GitHub repo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `LINE_CHANNEL_ACCESS_TOKEN`: your token
   - `LINE_CHANNEL_SECRET`: your secret

### 3. Oracle Cloud VM Setup

Oracle VM is needed because Untappd blocks datacenter IPs (like Render's). Oracle's IPs work.

#### Create Instance

1. Go to [Oracle Cloud Console](https://cloud.oracle.com/)
2. **Compute** → **Instances** → **Create Instance**
3. Settings:
   - **Image**: Oracle Linux 8 or Ubuntu
   - **Shape**: VM.Standard.A1.Flex (ARM, free tier)
   - **OCPUs**: 1
   - **Memory**: 6GB (free tier allows up to 24GB)
   - **SSH keys**: Generate and download
4. Add **Ingress Rule** for port 5000:
   - **Networking** → **VCN** → **Security Lists** → **Add Ingress Rule**
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `5000`

#### Install Dependencies

```bash
ssh -i your-key.key opc@YOUR_VM_IP

# Install Python packages
sudo yum install -y python3 python3-pip
pip3 install flask requests beautifulsoup4 gunicorn
```

#### Create Database

```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/home/opc/beers.db')
conn.execute('CREATE TABLE IF NOT EXISTS saved_beers (id INTEGER PRIMARY KEY, user_id TEXT, beer_name TEXT, brewery TEXT, style TEXT, abv TEXT, rating TEXT, saved_at TEXT)')
conn.commit()
print('Database created')
EOF
```

#### Create Scraper Script

Create `/home/opc/scraper.py`:

```python
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = '/home/opc/beers.db'

@app.route('/')
def get_beers():
    url = "https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")
        beer_items = soup.select("li.menu-item")

        beers = []
        for item in beer_items:
            name_link = item.select_one("h5 a.track-click")
            if not name_link:
                continue

            name = re.sub(r'^\d+\.\s*', '', name_link.text.strip())
            href = name_link.get("href", "")

            style_em = item.select_one("h5 em")
            style = style_em.text.strip() if style_em else ""

            brewery_link = item.select_one("h6 a.track-click")
            brewery = brewery_link.text.strip() if brewery_link else ""

            h6 = item.select_one("h6")
            abv = ""
            if h6:
                abv_match = re.search(r'([\d.]+)%\s*ABV', h6.get_text())
                if abv_match:
                    abv = abv_match.group(1) + "%"

            rating_span = item.select_one("span.num")
            rating = rating_span.text.strip().strip("()") if rating_span else ""

            img = item.select_one(".beer-label img")
            label = img.get("src", "") if img else ""

            beers.append({
                "name": name,
                "brewery": brewery,
                "style": style,
                "abv": abv,
                "label": label,
                "rating": rating,
                "check_in": "https://untappd.com" + href if href else ""
            })

        return jsonify(beers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save', methods=['POST'])
def save_beer():
    data = request.json
    user_id = data.get('user_id')
    beer_name = data.get('beer_name')
    brewery = data.get('brewery', '')
    style = data.get('style', '')
    abv = data.get('abv', '')
    rating = data.get('rating', '')

    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO saved_beers (user_id, beer_name, brewery, style, abv, rating, saved_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (user_id, beer_name, brewery, style, abv, rating, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})

@app.route('/mybeers/<user_id>')
def get_my_beers(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute('SELECT * FROM saved_beers WHERE user_id = ? ORDER BY saved_at DESC', (user_id,))
    beers = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(beers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### Create Systemd Service

```bash
sudo nano /etc/systemd/system/scraper.service
```

Content:

```ini
[Unit]
Description=Beer Scraper API
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc
ExecStart=/usr/bin/python3 -m gunicorn -w 1 -b 0.0.0.0:5000 --timeout 120 scraper:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start scraper
sudo systemctl enable scraper
sudo systemctl status scraper
```

#### Open Firewall on VM

```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

#### Setup Health Check & Cron Jobs

Create health check script:

```bash
cat > /home/opc/health_check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://localhost:5000)
if [ "$response" != "200" ]; then
    echo "$(date): Scraper not responding, restarting..."
    sudo systemctl restart scraper
fi
EOF
chmod +x /home/opc/health_check.sh
```

Add cron jobs:

```bash
crontab -e
```

Add these lines:

```
*/5 * * * * /home/opc/health_check.sh >> /home/opc/health_check.log 2>&1
*/10 * * * * curl -s https://titansbeers.onrender.com/ > /dev/null 2>&1
```

#### Add Swap (if low memory)

If using AMD shape with only 512MB RAM:

```bash
sudo dd if=/dev/zero of=/swapfile2 bs=1M count=1024
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
echo '/swapfile2 none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. Update Render Config

Make sure `app/scraper.py` points to your Oracle VM IP:

```python
SCRAPER_API_URL = "http://YOUR_VM_IP:5000"
```

Also in `app/line_handler.py`:

```python
SCRAPER_API_URL = "http://YOUR_VM_IP:5000"
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LINE_CHANNEL_ACCESS_TOKEN` | From Line Developer Console |
| `LINE_CHANNEL_SECRET` | From Line Developer Console |

## API Endpoints

### Render (Line Bot)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/webhook` | POST | Line webhook handler |
| `/test-scrape` | GET | Test scraping (returns beer JSON) |

### Oracle VM (Scraper)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Scrape and return beers from Untappd |
| `/save` | POST | Save a beer for a user |
| `/mybeers/<user_id>` | GET | Get user's saved beers |

## Troubleshooting

### Render goes to sleep
The cron job on Oracle pings Render every 10 minutes to keep it awake.

### Oracle VM not responding
1. Check if you can SSH: `ssh -i key.key opc@IP`
2. If not, reboot from Oracle Console
3. Check service: `sudo systemctl status scraper`
4. Check logs: `sudo journalctl -u scraper -f`
5. Check memory: `free -h`

### Untappd blocking requests
This is why we use Oracle VM - Render's IPs are blocked but Oracle's residential-like IPs work.

### Low memory crashes
- Use ARM shape with 6GB RAM instead of AMD with 512MB
- Or add swap space (see setup instructions)

## Line Credentials

- **Channel ID**: 1657152840
- **Channel Secret**: a3f5bdfb7f239e6ec9ade2ef427f5e21
- **Channel Access Token**: IZMOX281n/l9hxw6kC/hdvQWuTJI730qJl3EPUSjI+pf3RCPyQd4SxH7OSMQmFGNMIk8zfT8DlnJTJHAmvM+i0lCdxsN9L6+C/I9av/+s8CrxCnLd4WOoTztrRqcVJKZZO4hS8wNYdWsJXp9/ttIKQdB04t89/1O/w1cDnyilFU=

## Oracle VM Info

- **Public IP**: 140.238.197.186
- **SSH**: `ssh -i oracle-arm.key opc@140.238.197.186`
- **Scraper URL**: http://140.238.197.186:5000

## URLs

- **Render Bot**: https://titansbeers.onrender.com
- **Line Webhook**: https://titansbeers.onrender.com/webhook
- **Untappd Venue**: https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704
