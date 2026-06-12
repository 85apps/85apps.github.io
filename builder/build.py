#!/usr/bin/env python3
"""
Генератор языковых страниц лендинга LiDTrainer.

Использование:
    python3 build.py            # генерирует docs/lidtrainer/{lang}/index.html + sitemap.xml

Источники:
    builder/template.html           — одобренный дизайн с плейсхолдерами {{key}}
    builder/data/languages.json     — список языков + константы (SITE_URL и т.д.)
    builder/data/strings/{lang}.json — локализованные строки (67 ключей на язык)

Добавление нового языка:
    1. Добавить запись в languages.json (code, dir, name, ogLocale, fastlane).
    2. Создать data/strings/{code}.json (перевести 67 ключей; за образец — en.json).
    3. Положить скриншоты assets/img/{code}/1.jpg и 2.jpg
       (из fastlane/metadata/android/{fastlane}/images/phoneScreenshots/).
    4. python3 build.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent          # builder/

CONFIG = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
SITE_URL = CONFIG["site_url"]          # "https://48apps.com"
BASE_PATH = CONFIG["base_path"]        # "/lidtrainer"

# Куда писать страницы: docs/ (отсюда GitHub Pages отдаёт сайт) + подпапка
# приложения из base_path. Так для нового приложения путь подстроится сам.
SITE = ROOT.parent / "docs" / BASE_PATH.strip("/")
PLAY_URL = CONFIG["play_url"]
APPSTORE_URL = CONFIG["appstore_url"]
X_DEFAULT = CONFIG["x_default"]
LANGS = CONFIG["languages"]

TEMPLATE = (ROOT / "template.html").read_text(encoding="utf-8")


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def esc_text(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")


def hreflang_links() -> str:
    lines = [
        f'<link rel="alternate" hreflang="{L["code"]}" href="{SITE_URL}{BASE_PATH}/{L["code"]}/">'
        for L in LANGS
    ]
    lines.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{BASE_PATH}/{X_DEFAULT}/">'
    )
    return "\n".join(lines)


def lang_links(current: str) -> str:
    out = ['<div class="f-langs">']
    for L in LANGS:
        cur = ' aria-current="page"' if L["code"] == current else ""
        rtl = ' dir="rtl"' if L["dir"] == "rtl" else ""
        out.append(
            f'          <a href="../{L["code"]}/"{cur} lang="{L["code"]}"{rtl}>{L["name"]}</a>'
        )
    out.append("        </div>")
    return "\n".join(out)


def json_ld(lang: str, page_url: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "310: Leben in DE (100+ Lang)",
            "applicationCategory": "EducationalApplication",
            "operatingSystem": "Android",
            "inLanguage": lang,
            "url": page_url,
            "installUrl": PLAY_URL,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def build_page(L: dict) -> str:
    code = L["code"]
    strings = json.loads(
        (ROOT / "data" / "strings" / f"{code}.json").read_text(encoding="utf-8")
    )
    page_url = f"{SITE_URL}{BASE_PATH}/{code}/"
    out = TEMPLATE
    variables = {
        "lang": code,
        "dir_attr": ' dir="rtl"' if L["dir"] == "rtl" else "",
        "ltr_attr": ' dir="ltr" style="text-align: start;"' if L["dir"] == "rtl" else "",
        "title": esc_text(strings["title"]),
        "title_attr": esc_attr(strings["title"]),
        "description": esc_attr(strings["description"]),
        "page_url": page_url,
        "og_image": f"{SITE_URL}{BASE_PATH}/assets/img/og.png",
        "og_locale": L["ogLocale"],
        "hreflang_links": hreflang_links(),
        "json_ld": json_ld(code, page_url),
        "lang_links": lang_links(code),
        "play_url": PLAY_URL,
        "appstore_url": APPSTORE_URL,
    }
    for k, v in variables.items():
        out = out.replace("{{" + k + "}}", v)
    for k, v in strings.items():
        if k in ("title", "description"):
            continue
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        import re
        leftover = sorted(set(re.findall(r"\{\{[a-z0-9_]+\}\}", out)))
        raise SystemExit(f"{code}: unresolved placeholders: {leftover}")
    return out


def build_sitemap() -> str:
    alts = "\n".join(
        f'    <xhtml:link rel="alternate" hreflang="{L["code"]}" href="{SITE_URL}{BASE_PATH}/{L["code"]}/"/>'
        for L in LANGS
    )
    alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE_URL}{BASE_PATH}/{X_DEFAULT}/"/>'
    urls = "\n".join(
        f"  <url>\n    <loc>{SITE_URL}{BASE_PATH}/{L['code']}/</loc>\n{alts}\n  </url>"
        for L in LANGS
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "\n</urlset>\n"
    )


def main() -> None:
    for L in LANGS:
        path = SITE / L["code"] / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_page(L), encoding="utf-8")
        print(f"  {path}")
    (SITE / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    print(f"  {SITE / 'sitemap.xml'}")
    print(f"Done: {len(LANGS)} pages + sitemap.xml")


if __name__ == "__main__":
    main()
