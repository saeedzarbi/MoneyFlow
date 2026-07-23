# استقرار روی mate.ramonasep.ir

## پیش‌نیاز
1. DNS ساب‌دامین `mate.ramonasep.ir` به IP سرور (A record)
2. پورت‌های 80 و 443 باز باشند
3. سرور Ubuntu/Debian با دسترسی root/sudo

## استقرار سریع

```bash
# روی سرور
sudo mkdir -p /opt/MoneyFlow
# پروژه را به /opt/MoneyFlow کپی یا clone کنید
cd /opt/MoneyFlow
sudo bash deploy/setup.sh /opt/MoneyFlow
```

قبل از اجرا، `.env` را کامل کنید:

```bash
sudo nano /opt/MoneyFlow/.env
```

حداقل این‌ها را ست کنید:
- `SECRET_KEY` — یک رشته تصادفی بلند
- `FLASK_ENV=production`
- `TELEGRAM_BOT_TOKEN` و در صورت نیاز `TELEGRAM_CHAT_IDS`
- `GEMINI_API_KEY` اگر واژه‌های انگلیسی لازم است

ایمیل گواهی SSL:

```bash
sudo CERTBOT_EMAIL=you@example.com bash deploy/setup.sh /opt/MoneyFlow
```

## دستی (بدون setup.sh)

```bash
cd /opt/MoneyFlow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo mkdir -p /var/log/mate
sudo cp deploy/mate.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mate

sudo cp deploy/nginx-mate.ramonasep.ir.conf /etc/nginx/sites-available/mate.ramonasep.ir
# اگر هنوز گواهی ندارید، اول فقط بلاک listen 80 را فعال کنید، بعد:
sudo ln -s /etc/nginx/sites-available/mate.ramonasep.ir /etc/nginx/sites-enabled/
sudo certbot --nginx -d mate.ramonasep.ir
sudo nginx -t && sudo systemctl reload nginx
```

## دستورات مفید

```bash
sudo systemctl status mate
sudo journalctl -u mate -f
sudo systemctl restart mate
sudo certbot renew --dry-run
```

اپ با Gunicorn روی `127.0.0.1:8000` اجرا می‌شود و nginx ترافیک HTTPS دامنه را به آن پروکسی می‌کند.
