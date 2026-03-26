import requests
import re
from datetime import datetime, timezone, timedelta

BASE_URL = "https://cablego.com.pe"

PERU_TZ = timezone(timedelta(hours=-5))

def format_time(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        dt = dt.astimezone(PERU_TZ)
        return dt.strftime("%Y%m%d%H%M%S -0500")
    except:
        return ""

def clean_name(name):
    return name.replace("-", " ").replace("_", " ").title()

def get_channels():
    channels = set()

    try:
        r = requests.get(BASE_URL, timeout=10)
        html = r.text

        matches = re.findall(r'channel=([a-zA-Z0-9\-_]+)', html)
        channels.update(matches)

    except Exception as e:
        print("Error obteniendo canales:", e)

    return sorted(list(channels))

def get_epg(channel):
    try:
        url = f"{BASE_URL}/epg?channel={channel}"
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return []

def generate_xml(channels):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<tv generator-info-name="EPG CableGo Peru">\n'

    for ch in channels:
        data = get_epg(ch)

        if not data:
            continue

        display_name = clean_name(ch)

        print(f"✔ Canal: {display_name}")

        xml += f'<channel id="{ch}">\n'
        xml += f'  <display-name>{display_name}</display-name>\n'
        xml += '</channel>\n'

        for prog in data:
            start = format_time(prog.get("start", ""))
            end = format_time(prog.get("end", ""))
            title = prog.get("title", "Sin información")
            desc = prog.get("description", "")

            if not start or not end:
                continue

            xml += f'<programme start="{start}" stop="{end}" channel="{ch}">\n'
            xml += f'  <title>{title}</title>\n'

            if desc:
                xml += f'  <desc>{desc}</desc>\n'

            xml += '</programme>\n'

    xml += '</tv>'

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml)

channels = get_channels()
print(f"Total canales detectados: {len(channels)}")

generate_xml(channels)
