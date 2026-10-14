# Third-party interfaces and licenses

Original FL Commons code is MIT licensed. No third-party implementation source,
FL binaries, samples, artwork, API stubs or decompiled code is copied into it.

| Component | Role | License / source |
| --- | --- | --- |
| Python | Runtime and standard library, installed separately | [PSF license](https://docs.python.org/3/license.html) |
| Mido | Optional MIDI port interface | [MIT](https://github.com/mido/mido/blob/main/LICENSE) |
| python-rtmidi | Optional Mido backend/native MIDI bindings | [MIT and bundled RtMidi notices](https://github.com/SpotlightKid/python-rtmidi/blob/master/LICENSE.md) |
| setuptools | Build environment only | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) |
| REA / rea-agents | Optional research tooling, not a runtime dependency | [MIT](https://github.com/morluto/rea/blob/main/LICENSE) |
| Ghidra | Optional separate research provider | [Apache 2.0 and component licenses](https://github.com/NationalSecurityAgency/ghidra/blob/master/LICENSE) |
| FL Studio MIDI Scripting | Documented proprietary-host interface | [Official reference](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm), [Image-Line EULA](https://www.image-line.com/image-line-software-eula) |
| FL Plugin SDK fpsdk_20210311b | User-supplied external headers for native contract development | Copyright Image-Line, all rights reserved; not vendored or relicensed as MIT; [assessment](research/sdk-assessment.md) |

The SDK catalog contains extracted interface facts (symbol names, numeric IDs,
source-line references and hashes) and original FL Commons classification. It
does not include SDK headers, implementation code or a license grant over them.

Optional dependencies are installed separately through their official packages,
with their license files. This repository does not redistribute them. Installing
research tooling does not grant rights to analyze third-party targets. No
virtual MIDI driver is selected or redistributed by FL Commons. This source
package contains no logos or implied endorsement from Image-Line.

The experimental native build compiles the externally supplied SDK base class
implementation alongside original FL Commons code. The source archive does
not include that SDK implementation. The locally built DLL includes SDK
material: do not treat the entire binary as MIT or infer permission for public
redistribution from this repository. SDK copyright and terms remain applicable.
