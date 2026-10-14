# FL Commons

FL Commons est une API communautaire indépendante pour les intégrations avec FL Studio. Elle expose des capacités documentées et vérifiées au moyen d’un contrat public stable. Les développeurs définissent leurs propres intégrations.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · **Français** · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Capacités actuelles

v0.1.0 expérimentale : HTTP local authentifié, SDK Python, état de lecture, Play/Pause et Stop via un plugin du SDK officiel. Le Core facultatif fournit un catalogue de preuves pour 87 sélecteurs du SDK ; ses entrées ne rendent pas automatiquement les commandes disponibles. MIDI est facultatif ; l’API directe ne nécessite pas de serveur Python séparé.

```text
transport.state
transport.play_pause
transport.stop
```

## Démarrage rapide

**Compatibilité visée : FL Studio 25/26 et versions ultérieures, sur Windows x64.** Le dépôt distribue actuellement le code source. Sa compilation exige Python 3.10+, MSVC 2022 Build Tools, Windows SDK et **fpsdk_20210311b** fourni séparément. Ce sont des prérequis de compilation pour développeurs. Extrayez le SDK hors du dépôt et remplacez les chemins.

Installez le paquet Python depuis ce dépôt, puis compilez le composant natif :

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Enregistrez votre travail et fermez FL normalement avant l’installation. L’installateur préserve les versions existantes sans les écraser. Après le lancement, ajoutez **FL Commons API** dans un emplacement libre du Mixer. Le lanceur stocke le jeton avec Windows DPAPI. Une instance native utilise le port 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## SDK Python

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Commencez par les requêtes en lecture seule. Exécutez les commandes suivantes uniquement pour modifier la lecture. Play/Pause bascule l’état ; ce n’est pas un démarrage idempotent. Après un délai dépassé en écriture ou `outcome_unknown`, consultez l’état avant de décider ; ne réessayez jamais automatiquement.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Serveur Core facultatif

Le SDK direct se connecte au plugin sur `127.0.0.1:3211`. Pour accéder aussi au catalogue et au contrat OpenAPI du Core, lancez le serveur facultatif sur le port 3210. Son jeton client est distinct du jeton DPAPI natif. `--demo` est une simulation explicite ; le serveur par défaut démarre déconnecté.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validation et limites

**Vérifié :** 77 tests Python et 27 tests natifs ont réussi localement. Le CI Python a réussi sous Windows et Linux avec Python 3.10, 3.12 et 3.14. Play → Pause → Play → Stop a été confirmé par les callbacks de FL dans une session de test autorisée sur le build 26.1.7.5653. Le CI Linux ne valide pas le plugin FL.

L’édition du Mixer/des canaux/des projets et les événements publics ne sont pas implémentés. La sélection adaptative utilise des profils d’interfaces implémentées ; les mises à jour vérifiées offrent staging et rollback. Les autres contrats nécessitent des profils vérifiés ; ni découverte illimitée ni compatibilité avec tous les builds ne sont affirmées. La nouvelle DLL a passé les tests contrôlés mais n’a pas été rechargée dans FL. Consultez le guide de compatibilité.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Documentation

Les liens ci-dessous approfondissent la documentation, actuellement surtout en portugais. Le README principal est en anglais ; les corrections de traduction sont bienvenues.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Contributions et licence

Contribuez avec des interfaces documentées, des preuves reproductibles et des tests. Séparez code original, matériel du SDK et recherche. Un symbole détecté ou un résultat simulé ne prouve pas le contrôle de FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Le code original de FL Commons est sous licence **MIT**. Les fichiers du SDK Image-Line et les DLL compilées ne sont pas distribués ici ; les conditions du SDK s’appliquent séparément. FL Commons n’est ni affilié à Image-Line, ni approuvé ou maintenu par cette société. FL Studio est une marque d’Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
