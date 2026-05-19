# NPR 4660 — Toepassingsrichtlijn NEN 2660-reeks

Gepubliceerde website bij de NPR 4660, met praktijkvoorbeelden van de NEN 2660-reeks. De site toont per figuur de beschrijving, het diagram en (waar beschikbaar) de RDF/Turtle-implementatie.
De figuren zijn onderdeel van de NPR4660 zelf. Deze website toont RDF uitwerkingen (in de W3C standaard: Turtle).

## Projectstructuur

```
npr4660/
├── docs/                            # Website root (GitHub Pages source)
│   ├── index.html                   # Statische site (laadt content dynamisch)
│   └── data/
│       ├── manifest.json            # Automatisch gegenereerde inhoudsopgave
│       └── praktijkvoorbeeld_gebouw/
│           ├── figuur9/
│           │   ├── README.md        # Titel (H1) en beschrijving van de figuur
│           │   ├── npr4660_figuur9.png
│           │   └── npr4660_figuur9_rdf.ttl
│           ├── figuur10/
│           │   └── ...
│           └── ...
├── generate_manifest.py             # Genereert docs/data/manifest.json
├── serve.py                         # Lokale server met live reload voor lokale ontwikkeling/preview.
└── .github/workflows/pages.yml     # GitHub Actions: deploy naar GitHub Pages
```

## Lokaal starten

Start de ontwikkelserver vanuit de projectroot:

```bash
python serve.py
```

De site is daarna beschikbaar op [http://localhost:8000](http://localhost:8000).

De server:
- genereert `manifest.json` automatisch bij opstarten
- bewaakt `docs/data/` op bestandswijzigingen
- herlaadt de browser automatisch zodra content aangepast wordt

## Nieuwe figuur toevoegen

1. Maak een map aan: `docs/data/<voorbeeld>/figuur<N>/`
2. Voeg toe: `README.md`, een `.png` en (optioneel) een `.ttl`
3. De server pikt de wijziging automatisch op en herlaadt de browser

Alleen het manifest bijwerken zonder server:

```bash
python generate_manifest.py
```

## Nieuw praktijkvoorbeeld toevoegen

Voeg een nieuwe map toe naast `praktijkvoorbeeld_gebouw/`:

```
docs/data/
├── praktijkvoorbeeld_gebouw/
└── praktijkvoorbeeld_installatie/   ← nieuwe map
    ├── figuur1/
    │   ├── README.md
    │   └── figuur1.png
    └── ...
```

De site en het navigatiemenu passen zich automatisch aan.

## Inhoud per figuur

Elke figuurmap bevat:

| Bestand | Verplicht | Beschrijving |
|---|---|---|
| `README.md` | Ja | Titel (H1) en beschrijving van de figuur |
| `*.png` | Nee | Diagramafbeelding |
| `*_rdf.ttl` | Nee | RDF/Turtle-implementatie (met syntax highlighting) |

## GitHub Pages

De site wordt automatisch gepubliceerd via GitHub Actions bij elke push naar `main`.

**Eenmalige instelling:**
1. Ga naar **Settings → Pages**
2. Zet Source op **GitHub Actions**

De workflow in [`.github/workflows/pages.yml`](.github/workflows/pages.yml) genereert het manifest en publiceert de `docs/` map.

## Techniek

- Puur statisch: geen framework, geen build-stap in productie
- Content wordt client-side geladen via `fetch()` vanuit `manifest.json`
- Markdown via [marked.js](https://marked.js.org/)
- Syntax highlighting via [highlight.js](https://highlightjs.org/) + [highlightjs-turtle](https://github.com/redmer/highlightjs-turtle) (zelfde stack als CROW ReSpec)
- Huisstijl gebaseerd op NEN.nl (`#0082AC`)
