# Third-Party Licenses & Software Bill of Materials (SBOM)

**Project:** DevCenter (`devcenter-suite`)<br>
**Version:** 1.0.3<br>
**Audit Date:** 2026-09-16<br>
**Ecosystem:** dev-bricks (open-bricks umbrella)<br>
**Primary License:** GNU General Public License v3.0 ([LICENSE](LICENSE))

This document provides a comprehensive inventory of all third-party open-source libraries, transitive dependencies, build tools, and development frameworks used by DevCenter. Every dependency has been audited for license compatibility, vulnerability floors, zero-egress compliance, and unprivileged user-space execution.

---

## 1. Summary of Dependencies

DevCenter relies on **20 third-party packages** across four operational scopes:
- **Direct Runtime Dependencies (8):** PySide6, Pillow, anthropic, keyring, chardet, ftfy, pip-licenses, watchdog
- **Transitive Runtime Dependencies (4):** pywin32-ctypes, jaraco.classes, jaraco.context, jaraco.functools
- **Build & Packaging Tools (4):** PyInstaller, pyinstaller-hooks-contrib, altgraph, packaging
- **Development & Quality Assurance (4):** pytest, pluggy, iniconfig, ruff

All dependencies are distributed under permissive open-source licenses (MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause, HPND-sell-variant) or standard copyleft licenses with explicit linking/bootloader exceptions (LGPL-3.0, LGPL-2.1, GPL-2.0 with Bootloader exception).

---

## 2. Runtime Dependencies (Direct)

| Package | Minimum Version | License | SPDX Identifier | Upstream URL | Purpose / Scope |
|---|---|---|---|---|---|
| **PySide6** | `>=6.5.0` | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | `LGPL-3.0-only` | [PySide6](https://pypi.org/project/PySide6/) | Official Qt6 Python bindings for GUI, widgets, syntax highlighter, and event loop. |
| **Pillow** | `>=12.3.0` | HPND-sell-variant | `HPND-sell-variant` | [Pillow](https://pypi.org/project/Pillow/) | Image processing, icon conversion, and multi-resolution Windows ICO generation. Hardened against GHSA-4x4j-2g7c-83w6 and GHSA-45hq-cxwh-f6vc. |
| **anthropic** | `>=0.18.0` | MIT | `MIT` | [anthropic](https://pypi.org/project/anthropic/) | Optional local AI development assistant. Strict zero-egress opt-in boundary. |
| **keyring** | `>=25.0.0` | MIT | `MIT` | [keyring](https://pypi.org/project/keyring/) | Secure encrypted storage of optional API keys via native Windows Credential Manager. |
| **chardet** | `>=5.0.0` | LGPL-2.1-or-later | `LGPL-2.1-or-later` | [chardet](https://pypi.org/project/chardet/) | Universal charset and encoding detection for robust source file loading. |
| **ftfy** | `>=6.1.0` | Apache-2.0 | `Apache-2.0` | [ftfy](https://pypi.org/project/ftfy/) | Mojibake repair, encoding glitch resolution, and UTF-8 text normalization. |
| **pip-licenses** | `>=4.0.0` | MIT | `MIT` | [pip-licenses](https://pypi.org/project/pip-licenses/) | Automated license extraction and package metadata inspection in Builder module. |
| **watchdog** | `>=3.0.0` | Apache-2.0 | `Apache-2.0` | [watchdog](https://pypi.org/project/watchdog/) | Local file-system event monitoring for automated project tree updates. |

---

## 3. Transitive Runtime Dependencies

| Package | License | SPDX Identifier | Upstream URL | Parent Dependency | Purpose |
|---|---|---|---|---|---|
| **pywin32-ctypes** | BSD-3-Clause | `BSD-3-Clause` | [pywin32-ctypes](https://pypi.org/project/pywin32-ctypes/) | `keyring` | Pure ctypes access to Windows Credential Manager without external C compilers. |
| **jaraco.classes** | MIT | `MIT` | [jaraco.classes](https://pypi.org/project/jaraco.classes/) | `keyring` | Class and metaclass utilities for keyring credential backends. |
| **jaraco.context** | MIT | `MIT` | [jaraco.context](https://pypi.org/project/jaraco.context/) | `keyring` | Context manager utilities for safe credential isolation. |
| **jaraco.functools** | MIT | `MIT` | [jaraco.functools](https://pypi.org/project/jaraco.functools/) | `keyring` | Functional tools, memoization, and decorators for keyring backends. |

---

## 4. Build & Packaging Dependencies

| Package | Minimum Version | License | SPDX Identifier | Upstream URL | Purpose |
|---|---|---|---|---|---|
| **PyInstaller** | `>=5.0.0` | GPL-2.0-or-later WITH Bootloader-exception | `GPL-2.0-or-later WITH Bootloader-exception` | [PyInstaller](https://www.pyinstaller.org/) | Desktop executable bundling. Packaged output does not relicense user code due to the Bootloader Exception. |
| **pyinstaller-hooks-contrib** | `>=2023.0` | Apache-2.0 | `Apache-2.0` | [hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) | Official community packaging hooks for PySide6, Pillow, and standard packages. |
| **altgraph** | `>=0.17` | MIT | `MIT` | [altgraph](https://pypi.org/project/altgraph/) | Static AST dependency graph analysis during executable compilation. |
| **packaging** | `>=23.0` | Apache-2.0 OR BSD-2-Clause | `Apache-2.0 OR BSD-2-Clause` | [packaging](https://pypi.org/project/packaging/) | PEP 440/508 version parsing and specification verification. |

---

## 5. Development & Testing Dependencies

| Package | Minimum Version | License | SPDX Identifier | Upstream URL | Purpose |
|---|---|---|---|---|---|
| **pytest** | `>=9.1.1` | MIT | `MIT` | [pytest](https://pytest.org/) | Test runner and assertion framework. Hardened against CVE-2025-7117 / GHSA-6w46-j5rx-g56g. |
| **pluggy** | `>=1.5.0` | MIT | `MIT` | [pluggy](https://pypi.org/project/pluggy/) | Plugin and hook management engine for pytest test discovery. |
| **iniconfig** | `>=2.0.0` | MIT | `MIT` | [iniconfig](https://pypi.org/project/iniconfig/) | Fast INI parser for reading pyproject.toml test configurations. |
| **ruff** | `>=0.9.0` | MIT OR Apache-2.0 | `MIT OR Apache-2.0` | [ruff](https://github.com/astral-sh/ruff) | High-performance static analysis, linter, and code formatter. |

---

## 6. License Compatibility & Architecture Assurances

### 6.1 GPL-3.0 and LGPL-3.0 Dynamic Linking
DevCenter is licensed under the **GNU General Public License v3.0 (GPLv3)**. It utilizes **PySide6** under the **LGPLv3** through dynamic linking (`import PySide6`). In accordance with LGPLv3 section 4, users are free to replace or upgrade Qt/PySide6 dynamic libraries in their Python environment without invalidating the application's runtime.

### 6.2 PyInstaller Bootloader Special Exception
The executable builder utilizes PyInstaller, which is licensed under GPL-2.0-or-later with the **PyInstaller Bootloader Special Exception**. This exception guarantees that standalone executables generated by DevCenter:
1. Do not automatically inherit the GPL license unless the developer chooses to do so.
2. Allow developers to distribute their packaged applications under any license of their choice.

### 6.3 Local-First & Zero-Egress Invariant
All direct and transitive libraries operate **100% offline by default**:
- No telemetry, usage tracking, pingbacks, or background phone-home calls are performed.
- Network activity is strictly isolated to explicit user actions:
  - User-initiated HTTP API calls to Anthropic (only when the optional Claude assistant is activated).
  - Explicit package installation commands initiated in the user's shell.

### 6.4 Non-Elevation (RunAsInvoker) Security
DevCenter and all bundled tools run strictly in unprivileged user space (`RunAsInvoker`). No administrative privileges, driver installations, or UAC elevations are required for code editing, static analysis, or executable compilation.

---

## 7. Machine-Readable License Mapping

```json
{
  "project": "devcenter-suite",
  "version": "1.0.3",
  "audit_date": "2026-09-16",
  "spdx_matrix": {
    "PySide6": "LGPL-3.0-only",
    "Pillow": "HPND-sell-variant",
    "anthropic": "MIT",
    "keyring": "MIT",
    "chardet": "LGPL-2.1-or-later",
    "ftfy": "Apache-2.0",
    "pip-licenses": "MIT",
    "watchdog": "Apache-2.0",
    "pywin32-ctypes": "BSD-3-Clause",
    "jaraco.classes": "MIT",
    "jaraco.context": "MIT",
    "jaraco.functools": "MIT",
    "PyInstaller": "GPL-2.0-or-later WITH Bootloader-exception",
    "pyinstaller-hooks-contrib": "Apache-2.0",
    "altgraph": "MIT",
    "packaging": "Apache-2.0 OR BSD-2-Clause",
    "pytest": "MIT",
    "pluggy": "MIT",
    "iniconfig": "MIT",
    "ruff": "MIT OR Apache-2.0"
  },
  "compliance": {
    "zero_egress_default": true,
    "unprivileged_execution": true,
    "os_keyring_isolation": true,
    "vulnerability_floors_enforced": true
  }
}
```
