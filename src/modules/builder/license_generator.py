# -*- coding: utf-8 -*-
"""
DevCenter - License Generator
Sammelt und generiert Third-Party Lizenzen
Basierend auf ThirdPartyLicenses
"""

import os
import subprocess
import sys
import json
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageLicense:
    """Lizenzinformationen eines Packages"""
    name: str
    version: str
    license: str = "Unknown"
    license_text: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None

    def __post_init__(self):
        if not self.license:
            self.license = "Unknown"


class LicenseGenerator:
    """
    Sammelt Lizenzinformationen aller installierten Packages
    und generiert eine Third-Party-Lizenzdatei
    """

    def __init__(self):
        self._pip_licenses_available = False
        try:
            import pip_licenses  # noqa: F401
            self._pip_licenses_available = True
        except ImportError:
            pass

    def is_available(self) -> bool:
        """Prüft ob pip-licenses installiert ist"""
        return self._pip_licenses_available

    def get_licenses(self,
                     requirements_file: str = None,
                     include_dev: bool = False) -> List[PackageLicense]:
        """
        Sammelt alle Lizenzinformationen

        Args:
            requirements_file: Optionale requirements.txt
            include_dev: Auch Dev-Dependencies einbeziehen

        Returns:
            Liste von PackageLicense
        """
        licenses = []

        # Vorab-Parsing von requirements.txt falls angegeben
        req_names = None
        if requirements_file and os.path.exists(requirements_file):
            req_names = set()
            import re
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith(('#', '-')):
                            continue
                        clean = line.split(';')[0].strip()
                        pkg_match = re.split(r'[=><~@!\s\[]', clean)[0].strip()
                        if pkg_match:
                            req_names.add(pkg_match.lower().replace('_', '-'))
            except Exception:
                req_names = None

        try:
            # pip-licenses verwenden wenn verfügbar
            if self._pip_licenses_available:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip_licenses',
                     '--format=json', '--with-license-file', '--with-urls'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                if result.returncode == 0 and result.stdout:
                    data = json.loads(result.stdout)
                    for pkg in data:
                        pkg_name = pkg.get('Name', '')
                        if req_names is not None and pkg_name.lower().replace('_', '-') not in req_names:
                            continue
                        lic_val = pkg.get('License')
                        licenses.append(PackageLicense(
                            name=pkg_name,
                            version=pkg.get('Version', ''),
                            license=lic_val if lic_val else 'Unknown',
                            license_text=pkg.get('LicenseText', None),
                            url=pkg.get('URL', None),
                            author=pkg.get('Author', None)
                        ))
            else:
                # Fallback: pip list + batch pip show
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                if result.returncode == 0 and result.stdout:
                    packages = json.loads(result.stdout)
                    filtered_packages = []
                    for pkg in packages:
                        name = pkg.get('name', '')
                        if req_names is not None and name.lower().replace('_', '-') not in req_names:
                            continue
                        filtered_packages.append(pkg)

                    batch_size = 40
                    names = [p.get('name', '') for p in filtered_packages if p.get('name')]
                    details_by_name = {}

                    for i in range(0, len(names), batch_size):
                        chunk = names[i:i + batch_size]
                        try:
                            detail = subprocess.run(
                                [sys.executable, '-m', 'pip', 'show'] + chunk,
                                capture_output=True,
                                text=True,
                                encoding='utf-8',
                                errors='replace'
                            )
                            if detail.returncode == 0 and detail.stdout:
                                current_pkg = {}
                                for line in detail.stdout.splitlines():
                                    if line.startswith('---'):
                                        if current_pkg.get('name'):
                                            details_by_name[current_pkg['name'].lower().replace('_', '-')] = current_pkg
                                        current_pkg = {}
                                    elif line.startswith('Name:'):
                                        current_pkg['name'] = line.split(':', 1)[1].strip()
                                    elif line.startswith('License:'):
                                        current_pkg['license'] = line.split(':', 1)[1].strip()
                                    elif line.startswith('Author:'):
                                        current_pkg['author'] = line.split(':', 1)[1].strip()
                                    elif line.startswith('Home-page:'):
                                        current_pkg['url'] = line.split(':', 1)[1].strip()
                                if current_pkg.get('name'):
                                    details_by_name[current_pkg['name'].lower().replace('_', '-')] = current_pkg
                        except Exception:
                            pass

                    for pkg in filtered_packages:
                        raw_name = pkg.get('name', '')
                        norm_key = raw_name.lower().replace('_', '-')
                        info = details_by_name.get(norm_key, {})
                        licenses.append(PackageLicense(
                            name=raw_name,
                            version=pkg.get('version', ''),
                            license=info.get('license') or 'Unknown',
                            author=info.get('author'),
                            url=info.get('url')
                        ))

        except Exception as e:
            print(f"Fehler beim Sammeln der Lizenzen: {e}")

        # Finale Filterung falls req_names angegeben
        if req_names is not None:
            licenses = [
                lic for lic in licenses
                if lic.name.lower().replace('_', '-') in req_names
            ]

        return licenses

    def generate_notice_file(self,
                             output_path: str,
                             app_name: str = "Application",
                             app_version: str = "1.0.1") -> bool:
        """
        Generiert eine THIRD-PARTY-NOTICES Datei

        Args:
            output_path: Ausgabepfad
            app_name: Name der Anwendung
            app_version: Version der Anwendung

        Returns:
            True bei Erfolg
        """
        licenses = self.get_licenses()

        if not licenses:
            return False

        try:
            parent_dir = Path(output_path).parent
            if str(parent_dir) and str(parent_dir) != '.':
                parent_dir.mkdir(parents=True, exist_ok=True)

            lines = [
                "THIRD-PARTY SOFTWARE NOTICES AND INFORMATION",
                "",
                f"This software ({app_name} {app_version}) incorporates components from",
                "the projects listed below.",
                "",
                "=" * 70,
                ""
            ]

            for lic in sorted(licenses, key=lambda x: x.name.lower()):
                lines.append(f"{lic.name} {lic.version}")
                lines.append(f"License: {lic.license}")
                if lic.url:
                    lines.append(f"URL: {lic.url}")
                if lic.author:
                    lines.append(f"Author: {lic.author}")
                lines.append("")

                if lic.license_text:
                    lines.append("-" * 40)
                    lines.append(lic.license_text[:2000])  # Begrenzen
                    if len(lic.license_text) > 2000:
                        lines.append("... [truncated]")
                    lines.append("-" * 40)

                lines.append("")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            return True

        except Exception as e:
            print(f"Fehler beim Generieren der Notice-Datei: {e}")
            return False

    def generate_json(self, output_path: str) -> bool:
        """Exportiert Lizenzen als JSON"""
        licenses = self.get_licenses()

        try:
            parent_dir = Path(output_path).parent
            if str(parent_dir) and str(parent_dir) != '.':
                parent_dir.mkdir(parents=True, exist_ok=True)

            data = []
            for lic in licenses:
                data.append({
                    'name': lic.name,
                    'version': lic.version,
                    'license': lic.license,
                    'url': lic.url,
                    'author': lic.author
                })

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Fehler: {e}")
            return False

    def check_license_compatibility(self,
                                    allowed_licenses: List[str] = None) -> List[str]:
        """
        Prüft auf inkompatible Lizenzen

        Args:
            allowed_licenses: Liste erlaubter Lizenzen

        Returns:
            Liste problematischer Packages
        """
        if allowed_licenses is None:
            allowed_licenses = [
                'MIT', 'MIT License',
                'BSD', 'BSD License', 'BSD-2-Clause', 'BSD-3-Clause',
                'Apache', 'Apache 2.0', 'Apache Software License',
                'Apache License 2.0', 'Apache-2.0',
                'ISC', 'ISC License',
                'PSF', 'Python Software Foundation License',
                'LGPL', 'LGPLv2', 'LGPLv3', 'LGPL-2.1', 'LGPL-3.0',
                'MPL', 'MPL 2.0', 'MPL-2.0',
                'Public Domain', 'Unlicense', 'CC0',
                'WTFPL'
            ]

        licenses = self.get_licenses()
        problematic = []

        for lic in licenses:
            license_ok = False
            lic_str = lic.license if lic.license else 'Unknown'
            for allowed in allowed_licenses:
                if allowed.lower() in lic_str.lower():
                    license_ok = True
                    break

            if not license_ok and lic_str != 'Unknown':
                problematic.append(f"{lic.name}: {lic_str}")

        return problematic


if __name__ == "__main__":
    gen = LicenseGenerator()
    print(f"pip-licenses verfügbar: {gen.is_available()}")

    licenses = gen.get_licenses()
    print(f"\n{len(licenses)} Packages gefunden:")
    for lic in licenses[:10]:
        print(f"  {lic.name} ({lic.version}): {lic.license}")

    if len(licenses) > 10:
        print(f"  ... und {len(licenses) - 10} weitere")
