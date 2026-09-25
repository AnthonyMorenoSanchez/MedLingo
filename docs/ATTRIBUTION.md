# Data and code attribution

Code: MIT, see LICENSE. Authored curated YAML: Creative Commons Attribution 4.0 International, attribution to MedLingo contributors. Preserve this notice when reusing the authored teaching material.

## Wikidata

Wikidata contributors. Structured data is CC0 1.0. Snapshot requests were made on 2026-09-13 through https://query.wikidata.org/sparql. Original entity URIs are stored in `terms.source_id`; original bindings are in `backend/ingest/fixtures/wikidata_*.json`. The `_sample` file contains 800 actual disease-query rows, not invented examples. Class definitions are recorded in PROVENANCE.json.

Source: https://www.wikidata.org/wiki/Wikidata:Licensing

## MedlinePlus

Information from MedlinePlus.gov, U.S. National Library of Medicine, National Institutes of Health. Health-topic XML release 2026-09-12, refreshed by `make ingest` when available. Only explicitly mapped bilingual topic titles and topic metadata are ingested. This application does not imply NLM or NIH endorsement. Copyrighted articles linked from the XML are not imported as teaching passages.

Sources: https://medlineplus.gov/xml.html and https://medlineplus.gov/copyright.html

## Wiktionary

Wiktionary contributors. The bundled raw Action API responses preserve page IDs and revision IDs for 300 lookup titles. Attribution can be resolved by the stored title at `https://en.wiktionary.org/wiki/<title>` and revision at `https://en.wiktionary.org/w/index.php?oldid=<revid>`. The parsed gender enrichment dictionary has 186 entries. The original entry text is available under CC BY-SA 4.0 and GFDL according to the current Wiktionary copyright page. This distribution uses CC BY-SA 4.0 for Wiktionary-derived material, including the raw snapshot and parsed enrichment; it is not relicensed under MIT. License: https://creativecommons.org/licenses/by-sa/4.0/. Changes: raw API responses were parsed to extract Spanish noun gender and incorporated into the term bank. The supplied specification's CC BY-SA 3.0 label is outdated.

Sources: https://en.wiktionary.org/wiki/Wiktionary:Copyrights and https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use

## DeCS

DeCS, Descritores em Ciências da Saúde / Descriptores en Ciencias de la Salud. BIREME / PAHO / WHO (Latin American and Caribbean Center on Health Sciences Information, Pan American Health Organization, World Health Organization).

No DeCS descriptors were retrieved or ingested in this build. The API returned HTTP 403, and the unavailable snapshot explicitly records that result. A DeCS version is therefore not claimed. Before adding an official export, confirm the current BIREME terms, required attribution wording, and redistribution permission for the supplied version.

Source: https://decs.bvsalud.org/en/

## Provenance and quality

The bank report identifies actual ingested sources and counts. No unavailable source data is replaced by invented source snapshots. The synthetic records used to test parsers are confined to the tests directory. Bulk imported labels have not received a complete independent clinical terminology review. Use the in-app report button for corrections, and apply changes through term_overrides.yaml.
