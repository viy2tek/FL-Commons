# FL Commons

Το FL Commons είναι ένα ανεξάρτητο API κοινότητας για ενσωματώσεις με το FL Studio. Παρέχει τεκμηριωμένες και επαληθευμένες δυνατότητες μέσω μιας σταθερής δημόσιας σύμβασης. Οι προγραμματιστές ορίζουν τις δικές τους ενσωματώσεις.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · **Ελληνικά**

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Τρέχουσες δυνατότητες

Πειραματική v0.1.0: τοπικό HTTP με έλεγχο ταυτότητας, Python SDK, κατάσταση αναπαραγωγής, Play/Pause και Stop μέσω πρόσθετου του επίσημου SDK. Το προαιρετικό Core παρέχει κατάλογο τεκμηρίων για 87 επιλογείς SDK· οι εγγραφές δεν ενεργοποιούν αυτόματα εντολές. Το MIDI είναι προαιρετικό· το άμεσο API δεν χρειάζεται ξεχωριστό διακομιστή Python.

```text
transport.state
transport.play_pause
transport.stop
```

## Γρήγορη εκκίνηση

**Στόχος συμβατότητας: FL Studio 25/26 και νεότερα σε Windows x64.** Το αποθετήριο διανέμει προς το παρόν πηγαίο κώδικα. Η μεταγλώττιση απαιτεί Python 3.10+, MSVC 2022 Build Tools, Windows SDK και εξωτερικό **fpsdk_20210311b**. Είναι απαιτήσεις μεταγλώττισης για προγραμματιστές. Αποσυμπιέστε το SDK εκτός αποθετηρίου και αλλάξτε τις διαδρομές. Το δημοσιευμένο εγγενές στοιχείο δέχεται ακόμη μόνο το δοκιμασμένο build· προσαρμοστική επιλογή και έτοιμη διανομή δεν υλοποιήθηκαν.

Εγκαταστήστε το πακέτο Python από αυτό το αποθετήριο και μεταγλωττίστε το εγγενές στοιχείο:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Αποθηκεύστε την εργασία σας και κλείστε κανονικά το FL πριν την εγκατάσταση. Ο εγκαταστάτης διατηρεί τις υπάρχουσες εκδόσεις χωρίς αντικατάσταση. Μετά την εκκίνηση προσθέστε το **FL Commons API** σε ελεύθερη υποδοχή Mixer. Ο εκκινητής αποθηκεύει το token με Windows DPAPI. Ένα εγγενές στιγμιότυπο χρησιμοποιεί τη θύρα 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## Python SDK

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Ξεκινήστε με ερωτήματα μόνο για ανάγνωση. Εκτελέστε τις παρακάτω εντολές μόνο για αλλαγή αναπαραγωγής. Το Play/Pause εναλλάσσει κατάσταση και δεν είναι ιδιοδύναμη εκκίνηση. Μετά από λήξη χρόνου εγγραφής ή outcome_unknown, ελέγξτε την κατάσταση πριν αποφασίσετε· μην επαναλαμβάνετε αυτόματα.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Προαιρετικός διακομιστής Core

Το άμεσο SDK συνδέεται στο πρόσθετο στο 127.0.0.1:3211. Για τον κατάλογο και τη σύμβαση OpenAPI του Core, εκκινήστε τον προαιρετικό διακομιστή στη θύρα 3210. Το token πελάτη είναι ξεχωριστό από το εγγενές token DPAPI. Το --demo είναι ρητή προσομοίωση· ο προεπιλεγμένος διακομιστής ξεκινά αποσυνδεδεμένος.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Επαλήθευση και όρια

**Επαληθεύτηκαν:** 52 δοκιμές Python και 21 εγγενείς δοκιμές πέρασαν τοπικά. Το Python CI πέρασε σε Windows και Linux με Python 3.10, 3.12 και 3.14. Οι επανακλήσεις του FL 26.1.7.5653 επιβεβαίωσαν Play → Pause → Play → Stop σε εξουσιοδοτημένη συνεδρία δοκιμής. Το Linux CI δεν επαληθεύει το πρόσθετο FL.

**Δεν έχουν υλοποιηθεί:** επεξεργασία Mixer/καναλιών/έργων, δημόσιες ροές συμβάντων, απεριόριστη ανακάλυψη και αυτόματες ενημερώσεις προσαρμογέων. Η επίδραση στον ήχο και άλλα builds δεν δοκιμάστηκαν. Η τελευταία διόρθωση κλειδώματος ουράς πέρασε ελεγχόμενη δοκιμή αργού πελάτη αλλά δεν επαναφορτώθηκε στο FL· τα hashes μεταγλωττισμένης και ζωντανά δοκιμασμένης DLL καταγράφονται χωριστά. Δεν πιστοποιείται ολόκληρο το SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Τεκμηρίωση

Οι παρακάτω σύνδεσμοι οδηγούν σε αναλυτική τεκμηρίωση, κυρίως στα πορτογαλικά προς το παρόν. Η κύρια γλώσσα του README είναι τα αγγλικά· διορθώσεις μεταφράσεων είναι ευπρόσδεκτες.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility design — not implemented](docs/adaptive-compatibility-design.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Συνεισφορά και άδεια

Συνεισφέρετε τεκμηριωμένες διεπαφές, αναπαραγώγιμα στοιχεία και δοκιμές. Διαχωρίστε τον αρχικό κώδικα, το υλικό SDK και την έρευνα. Ένα εντοπισμένο σύμβολο ή προσομοιωμένο αποτέλεσμα δεν αποδεικνύει έλεγχο του FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Ο αρχικός κώδικας FL Commons διατίθεται με άδεια **MIT**. Αρχεία SDK Image-Line και μεταγλωττισμένες DLL δεν διανέμονται εδώ· οι όροι SDK ισχύουν χωριστά. Το FL Commons δεν συνδέεται με την Image-Line, ούτε εγκρίνεται ή συντηρείται από αυτήν. Το FL Studio είναι εμπορικό σήμα της Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
