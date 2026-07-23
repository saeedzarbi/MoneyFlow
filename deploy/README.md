# استقرار روی mate.ramonasep.ir

## پیش‌نیاز
1. DNS ساب‌دامین `mate.ramonasep.ir` به IP سرور (A record)
2. پورت‌های 80 و 443 باز باشند
3. پروژه روی سرور در مسیر `/root/MoneyFlow`

## استقرار سریع

```bash
cd /root/MoneyFlow
# مطمئن شوید .env وجود دارد
bash deploy/setup.sh /root/MoneyFlow
```

یا فقط سرویس:

```bash
mkdir -p /var/log/mate
cp /root/MoneyFlow/deploy/mate.service /etc/systemd/system/mate.service
systemctl daemon-reload
systemctl enable --now mate
systemctl status mate
```

## دستورات مفید

```bash
systemctl status mate
journalctl -u mate -f
systemctl restart mate
```
