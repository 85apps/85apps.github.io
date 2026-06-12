# Генератор лендинга LiDTrainer

Одобренный дизайн вынесен в шаблон; все языковые страницы собираются автоматически.

## Структура

```
builder/
├── template.html        # дизайн с плейсхолдерами {{key}} — единственный источник разметки
├── build.py             # генератор: python3 build.py
└── data/
    ├── languages.json   # языки + константы (SITE_URL, BASE_PATH, ссылки на сторы)
    └── strings/
        ├── ru.json      # 67 локализованных строк на язык
        ├── en.json
        └── ...
site/lidtrainer/         # РЕЗУЛЬТАТ генерации — это деплоится на GitHub Pages
├── {lang}/index.html    # 11 языков
├── sitemap.xml
├── index.html           # корневой редирект по языку браузера (не генерируется)
└── assets/              # общий CSS, скриншоты, og.png
```

## Правки дизайна

Никогда не редактировать `site/lidtrainer/{lang}/index.html` руками — правки
затрутся при следующей генерации. Вместо этого:
- разметка/структура → `template.html`
- тексты → `data/strings/{lang}.json`
- затем `python3 build.py`

## Добавление языка (масштабирование до 100)

1. Запись в `languages.json`: `{"code": "...", "dir": "ltr|rtl", "name": "...", "ogLocale": "...", "fastlane": "..."}`
2. Перевод 67 строк → `data/strings/{code}.json` (образец — `en.json`)
3. Скриншоты `site/lidtrainer/assets/img/{code}/1.jpg` и `2.jpg`
   из `fastlane/metadata/android/{fastlane}/images/phoneScreenshots/`
4. `python3 build.py` — страница, футеры и sitemap обновятся на всех языках сразу

## SEO-слой (в шаблоне, попадает на все страницы автоматически)

- hreflang на все языки + `x-default` (en), абсолютные URL
- canonical
- Open Graph + Twitter Card (og:image = `assets/img/og.png`, 1200×630)
- JSON-LD `SoftwareApplication`
- `sitemap.xml` генерируется вместе со страницами

`robots.txt` со строкой `Sitemap: https://48apps.com/lidtrainer/sitemap.xml`
должен лежать в корне домена (зонтичный репозиторий `48apps.github.io`).

## Решено заказчиком (12.06.2026)

- **Цвет бренда**: остаётся бордовый `#6D3B3B`.
- **App Store**: https://apps.apple.com/app/id6762415996 (вписано в `languages.json`, кнопки активны).
