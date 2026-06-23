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
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent          # builder/

CONFIG = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
SITE_URL = CONFIG["site_url"]          # "https://85apps.com"
BASE_PATH = CONFIG["base_path"]        # "/lidtrainer"

# Куда писать страницы: docs/ (отсюда GitHub Pages отдаёт сайт) + подпапка
# приложения из base_path. Так для нового приложения путь подстроится сам.
SITE = ROOT.parent / "docs" / BASE_PATH.strip("/")
PLAY_URL = CONFIG["play_url"]
APPSTORE_URL = CONFIG["appstore_url"]
# Apple App Store campaign attribution (App Analytics → Campaigns) работает
# только если задан provider token (число из App Store Connect → App Analytics).
# Пусто => ссылки App Store остаются чистыми (атрибуция идёт по Web Referrers,
# на уровне домена). Заполнить — и per-language метки активируются сами.
APPLE_PT = CONFIG.get("apple_provider_token", "").strip()
X_DEFAULT = CONFIG["x_default"]


def play_link(code: str, pos: str) -> str:
    """Ссылка Google Play с меткой источника (utm в параметре referrer).

    Метки — это только параметры URL: ни кук, ни скриптов на сайте.
    В Play Console (Acquisition) видно установки/визиты по utm_campaign (язык)
    и по utm_content (какая кнопка: hero/final).
    """
    ref = (
        f"utm_source=85apps&utm_medium=landing"
        f"&utm_campaign=lid_{code}&utm_content={pos}"
    )
    sep = "&" if "?" in PLAY_URL else "?"
    return f"{PLAY_URL}{sep}referrer={urllib.parse.quote(ref, safe='')}"


def appstore_link(code: str, pos: str) -> str:
    """Ссылка App Store. С provider token (pt) — добавляет campaign token (ct)
    для per-language атрибуции в App Analytics. Без pt — чистая ссылка."""
    if not APPLE_PT:
        return APPSTORE_URL
    sep = "&" if "?" in APPSTORE_URL else "?"
    ct = f"lid_{code}_{pos}"[:40]
    return f"{APPSTORE_URL}{sep}pt={urllib.parse.quote(APPLE_PT, safe='')}&ct={urllib.parse.quote(ct, safe='')}"
LANGS = sorted(CONFIG["languages"], key=lambda L: L["name"].casefold())

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


def lang_switch(current: str, strings: dict) -> str:
    cur_name = next((L["name"] for L in LANGS if L["code"] == current), current.upper())
    search_ph = esc_attr(strings.get("lang_search", "Search language"))
    globe = (
        '<svg class="globe" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" '
        'd="M12 2a10 10 0 100 20 10 10 0 000-20zm6.92 6h-2.95a15.7 15.7 0 00-1.38-3.56A8.03 8.03 0 0118.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14a7.96 7.96 0 010-4h3.38a16.6 16.6 0 000 4H4.26zm.82 2h2.95c.34 1.27.81 2.47 1.38 3.56A7.99 7.99 0 015.08 16zm2.95-8H5.08a7.99 7.99 0 014.33-3.56A15.7 15.7 0 008.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82a13.7 13.7 0 01-1.91 3.96zM14.34 14H9.66a14.6 14.6 0 010-4h4.68a14.6 14.6 0 010 4zm.25 5.56c.57-1.09 1.04-2.29 1.38-3.56h2.95a8.03 8.03 0 01-4.33 3.56zM16.36 14a16.6 16.6 0 000-4h3.38a7.96 7.96 0 010 4h-3.38z"></path></svg>'
    )
    chev = (
        '<svg class="chev" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path fill="none" '
        'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6"></path></svg>'
    )
    out = ['<details class="lang-switch">']
    out.append(f'  <summary aria-label="Language / Sprache">{globe}<span>{cur_name}</span>{chev}</summary>')
    out.append('  <div class="lang-menu">')
    out.append('    <div class="lang-search-wrap">')
    out.append(
        f'      <input type="search" class="lang-search-input" placeholder="{search_ph}" '
        f'aria-label="{search_ph}" autocomplete="off" autocapitalize="off" spellcheck="false">'
    )
    out.append("    </div>")
    out.append('    <div class="lang-list">')
    for L in LANGS:
        cur = ' aria-current="page"' if L["code"] == current else ""
        rtl = ' dir="rtl"' if L["dir"] == "rtl" else ""
        out.append(f'      <a href="../{L["code"]}/"{cur} lang="{L["code"]}"{rtl}>{L["name"]}</a>')
    out.append("    </div>")
    out.append('    <p class="lang-empty" hidden>—</p>')
    out.append("  </div>")
    out.append("</details>")
    return "\n".join(out)


def json_ld(lang: str, page_url: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "310: Leben in DE (100+ Lang)",
            "applicationCategory": "EducationalApplication",
            "operatingSystem": "Android, iOS",
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
        "lang_switch": lang_switch(code, strings),
        "play_url_hero": play_link(code, "hero"),
        "play_url_final": play_link(code, "final"),
        "appstore_url_hero": appstore_link(code, "hero"),
        "appstore_url_final": appstore_link(code, "final"),
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


def build_redirect() -> str:
    """Корневой редиректор docs/{base_path}/index.html.

    Список языков генерится из languages.json, чтобы не держать его руками
    в двух местах (массив `supported` + видимый список ссылок).
    """
    supported = json.dumps([L["code"] for L in LANGS], ensure_ascii=False)
    links = "\n".join(
        f'    <li><a href="./{L["code"]}/" lang="{L["code"]}"'
        + (' dir="rtl"' if L["dir"] == "rtl" else "")
        + f'>{esc_text(L["name"])}</a></li>'
        for L in LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Leben in DE — Test Trainer</title>
<meta name="robots" content="noindex">
<script>
(function () {{
  var supported = {supported};
  var langs = navigator.languages || [navigator.language || "en"];
  var target = "{X_DEFAULT}";
  for (var i = 0; i < langs.length; i++) {{
    var code = String(langs[i]).slice(0, 2).toLowerCase();
    if (supported.indexOf(code) !== -1) {{ target = code; break; }}
  }}
  window.location.replace("./" + target + "/");
}})();
</script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #F5F5F5; color: #1B1B1B; display: grid; place-items: center; min-height: 100vh; margin: 0; }}
.box {{ text-align: center; padding: 24px; }}
.box ul {{ list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; max-width: 640px; }}
.box a {{ color: #6D3B3B; }}
</style>
</head>
<body>
<div class="box">
  <p>Leben in DE · Test Trainer</p>
  <ul>
{links}
  </ul>
</div>
</body>
</html>
"""


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
    (SITE / "index.html").write_text(build_redirect(), encoding="utf-8")
    print(f"  {SITE / 'index.html'} (redirect)")
    (SITE / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8")
    print(f"  {SITE / 'sitemap.xml'}")
    print(f"Done: {len(LANGS)} pages + redirect + sitemap.xml")


if __name__ == "__main__":
    main()
