# invenio-pidstore-extra

Erweiterung für InvenioRDM zur Verwaltung von **URNs (Uniform Resource Names)** über den REST-API-Dienst der Deutschen Nationalbibliothek (DNB).

InvenioRDM unterstützt von Haus aus DOIs via Datacite. Dieses Modul ergänzt die Unterstützung für URNs als Persistent Identifiers (PIDs), wie sie an deutschen Institutionen im Zusammenspiel mit der DNB benötigt werden.

---

## Was das Modul tut

1. **URN-Generierung**: Aus einem konfigurierbaren Präfix (dem von der DNB zugewiesenen Namespace, z. B. `urn:nbn:de:hbz:6`) und der internen Record-ID wird automatisch eine URN gebildet.

2. **Registrierung bei der DNB**: Per HTTP-Request (Basic Auth) wird die URN zusammen mit der öffentlichen Resolving-URL des Records bei der DNB registriert. Restricted Records werden übersprungen, da die DNB keine nicht-öffentlichen Ressourcen akzeptiert.

3. **Versionsverwaltung / Nachfolger-Ketten**: Wird eine neue Version eines Records veröffentlicht, setzt das Modul bei der DNB automatisch einen Successor-Verweis von der alten auf die neue URN. Aufrufende der alten URN werden so transparent weitergeleitet. Beim Löschen oder Wiederherstellen von Versionen werden diese Verweise entsprechend angepasst.

4. **URL-Synchronisierung**: Ändert sich die Resolving-URL eines Records (z. B. nach einem Domain-Wechsel), kann das Modul die hinterlegte URL bei der DNB per PATCH aktualisieren.

5. **Lokale Entwicklung / Sandbox**: Eine mitgelieferte Minimal-Flask-App simuliert die DNB-API lokal, sodass keine echten DNB-Zugangsdaten zum Entwickeln und Testen nötig sind.

---

## Konfiguration

Alle Variablen werden in der `invenio.cfg` der Instanz gesetzt:

| Variable | Typ | Beschreibung |
|---|---|---|
| `PIDSTORE_EXTRA_DNB_ENABLED` | `bool` | Provider aktivieren (`True`) oder deaktivieren |
| `PIDSTORE_EXTRA_TEST_MODE` | `bool` | `True` → Sandbox-URL verwenden; `False` → echte DNB-API |
| `PIDSTORE_EXTRA_DNB_USERNAME` | `str` | Benutzername (von der DNB vergeben) |
| `PIDSTORE_EXTRA_DNB_PASSWORD` | `str` | Passwort |
| `PIDSTORE_EXTRA_DNB_ID_PREFIX` | `str` | URN-Namespace-Präfix, z. B. `urn:nbn:de:hbz:6` |
| `PIDSTORE_EXTRA_DNB_SANDBOX_URI` | `str` | Alternative Basis-URL für die lokale Sandbox (Standard: `http://127.0.0.1:8000/`) |
| `PIDSTORE_EXTRA_FORMAT` | `str` | Template für die URN-Bildung, z. B. `{prefix}-{id}` |

Fehlen `USERNAME`, `PASSWORD` oder `ID_PREFIX`, wirft das Modul beim Start einen `RuntimeError`.

---

## Integration in InvenioRDM

Die Einbindung erfolgt in drei Schritten in der `invenio.cfg`:

### 1. Provider registrieren

Den DNB-URN-Provider an die Liste der RDM-Provider anhängen:

```python
RDM_PERSISTENT_IDENTIFIER_PROVIDERS = DEFAULT_PERSISTENT_IDENTIFIER_PROVIDERS + [
    providers.DnbUrnProvider(
        "urn",
        client=providers.DNBUrnClient(...),
        label=_("URN"),
    ),
]
```

### 2. PID-Schema konfigurieren

URN als (optional oder verpflichtenden) PID-Typ hinzufügen:

```python
RDM_PERSISTENT_IDENTIFIERS = {
    **DEFAULT_PERSISTENT_IDENTIFIERS,
    "urn": {
        "providers": ["urn"],
        "required": True,
        "label": _("URN"),
        "is_enabled": providers.DnbUrnProvider.is_enabled,
    },
}
```

### 3. Service-Komponente einbinden

Damit Successor-Verweise bei Versionierungsaktionen automatisch gesetzt werden:

```python
RDM_RECORDS_SERVICE_COMPONENTS = DefaultRecordsComponents + [URNRelationsComponent]
```

---

## Lokale Entwicklung mit der Sandbox

```bash
# Sandbox starten
flask --app invenio_pidstore_extra.dnb-sandbox run --port=8000

# invenio.cfg
PIDSTORE_EXTRA_TEST_MODE = True
PIDSTORE_EXTRA_DNB_SANDBOX_URI = "http://127.0.0.1:8000/"
```

Die Sandbox simuliert alle relevanten DNB-Endpunkte (Registrierung, URL-Abfrage, Successor-Verwaltung) ohne echte Datenbank.

---

## Selektive URN-Vergabe: `should_skip()`

Standardmäßig registriert `DnbUrnProvider` für jeden öffentlichen Datensatz eine URN bei der DNB. Über die Klassenmethode `should_skip(record)` lässt sich das für beliebige Bedingungen abschalten.

### Funktionsweise

`should_skip()` wird am Anfang von `register()` aufgerufen. Gibt sie `True` zurück, wird die DNB-Registrierung übersprungen — die URN bleibt lokal im Status `RESERVED`, existiert bei der DNB aber nicht. Alle anderen Schritte (lokale PID-Anlage, Versionsverwaltung) laufen normal weiter.

### Eigene Subklasse anlegen

```python
from invenio_pidstore_extra.providers.dnb import DnbUrnProvider

class MyDnbUrnProvider(DnbUrnProvider):
    @classmethod
    def should_skip(cls, record) -> bool:
        # True  → keine DNB-Registrierung
        # False → normale URN-Vergabe
        return ...
```

In der `invenio.cfg` dann `MyDnbUrnProvider` statt `DnbUrnProvider` verwenden (siehe Abschnitt „Integration in InvenioRDM").

### Beispiele

**Custom Field (Boolean)**
```python
@classmethod
def should_skip(cls, record) -> bool:
    return record.get("custom_fields", {}).get("mynamespace:flag", False)
```

**Ressourcentyp**
```python
@classmethod
def should_skip(cls, record) -> bool:
    rt = record.get("metadata", {}).get("resource_type", {}).get("id", "")
    return rt.startswith("image")  # keine URNs für Bilder
```

**Zugriffsstatus**
```python
@classmethod
def should_skip(cls, record) -> bool:
    return record.get("access", {}).get("record") == "restricted"
    # Hinweis: DnbUrnProvider prüft das bereits intern;
    # dieses Beispiel zeigt nur das Muster.
```

**Community-Zugehörigkeit**
```python
@classmethod
def should_skip(cls, record) -> bool:
    communities = record.get("parent", {}).get("communities", {}).get("ids", [])
    return "some-community-slug" in communities
```

**Mehrere Bedingungen kombinieren**
```python
@classmethod
def should_skip(cls, record) -> bool:
    meta = record.get("metadata", {})
    cf = record.get("custom_fields", {})
    is_external = cf.get("myns:external_publication", False)
    is_preprint = meta.get("resource_type", {}).get("id", "") == "publication-preprint"
    return is_external or is_preprint
```

### Hinweise

- Das `record`-Objekt kann je nach Aufrufkontext ein `dict` oder ein `ChainObject` (bei Drafts) sein. `record.get(...)` funktioniert in beiden Fällen.
- `should_skip()` wird nur bei der **Registrierung** geprüft, nicht bei der lokalen PID-Anlage. Benötigt man letzteres ebenfalls, muss zusätzlich `create()` überschrieben werden.
- Die Methode ist bewusst als `classmethod` ausgeführt, damit sie ohne Instanz z. B. in Tests direkt aufgerufen werden kann.

---

## Besonderheiten und Einschränkungen

- **Restricted Records** erhalten keine URN — die DNB setzt Öffentlichkeit voraus.
- **URNs können nicht gelöscht werden** (DNB-seitige Einschränkung). Das Modul entfernt sie nur lokal; stattdessen wird Successor-Logik zur Weiterleitung genutzt.
- **Änderungen sind nur vor der Registrierung möglich.** Sobald eine URN bei der DNB registriert ist, kann nur noch die Resolving-URL per Update geändert werden.
- Das Modul ist als **Flask-Extension** implementiert und wird automatisch über den Entry Point `invenio_base.apps` geladen.
