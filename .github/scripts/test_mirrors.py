#!/usr/bin/env python3
"""
Comprehensive TeX Live mirror testing script
Tests mirror structure, content, and compatibility
"""

import urllib.request
import urllib.error
import json
import sys
import re
import os
from datetime import datetime

# Lista dei mirror candidati da testare
MIRRORS_TO_TEST = [
    # Mirror originale (controllo)
    "https://texlive.info/tlnet-archive/2025/05/01/tlnet/",
    
    # Mirror CTAN ufficiali
    "https://mirror.ctan.org/systems/texlive/tlnet/",
    "https://ctan.math.illinois.edu/systems/texlive/tlnet/",
    "https://ctan.mirror.garr.it/ctan/systems/texlive/tlnet/",
    
    # Mirror TUG storici
    "https://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/current/tlnet/",
    "https://mirrors.rit.edu/CTAN/systems/texlive/tlnet/",
    "https://ftp.acc.umu.se/mirror/CTAN/systems/texlive/tlnet/",
    
    # Mirror internazionali
    "https://texlive.info/tlnet-archive/2025/04/01/tlnet/",  # Data alternativa
]

def create_request(url):
    """Crea una richiesta con User-Agent appropriato"""
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'GitHub-Actions-TexLive-Mirror-Test/1.0')
    req.add_header('Accept', '*/*')
    return req

def test_mirror_connectivity(mirror_url, timeout=10):
    """Testa la connettività base del mirror"""
    try:
        with urllib.request.urlopen(create_request(mirror_url), timeout=timeout) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"    Connectivity error: {e}")
        return False

def test_mirror_structure(mirror_url):
    """Testa la struttura completa del mirror"""
    required_files = [
        "install-tl-unx.tar.gz",
        "archive/",
        "tlpkg/",
        "update-info.html",
        "tlnet.html"
    ]
    
    optional_files = [
        "README",
        "LICENSE.CTAN",
        "LICENSE.TL"
    ]
    
    print(f"\n  Testing structure:")
    results = {}
    
    for file in required_files:
        test_url = f"{mirror_url}{file}"
        try:
            with urllib.request.urlopen(create_request(test_url), timeout=15) as response:
                if response.getcode() == 200:
                    results[file] = {"status": "found", "size": response.headers.get('Content-Length', 'unknown')}
                    print(f"    ✓ {file}")
                else:
                    results[file] = {"status": f"HTTP {response.getcode()}"}
                    print(f"    ✗ {file} - HTTP {response.getcode()}")
        except Exception as e:
            results[file] = {"status": f"error: {str(e)}"}
            print(f"    ✗ {file} - {e}")
    
    # Test file opzionali
    for file in optional_files:
        test_url = f"{mirror_url}{file}"
        try:
            with urllib.request.urlopen(create_request(test_url), timeout=10) as response:
                if response.getcode() == 200:
                    results[file] = {"status": "found", "optional": True}
                    print(f"    ✓ {file} (optional)")
        except:
            pass  # I file opzionali non influenzano la validità
    
    return results

def test_package_repository(mirror_url):
    """Testa l'accessibilità del repository pacchetti"""
    print(f"  Testing package repository:")
    
    try:
        # Test del database pacchetti
        tlpdb_url = f"{mirror_url}tlpkg/texlive.tlpdb"
        with urllib.request.urlopen(create_request(tlpdb_url), timeout=20) as response:
            content = response.read(10000).decode('utf-8', errors='ignore')
            
            if "TeX Live" in content and "collection-" in content:
                print("    ✓ Package database accessible")
                
                # Verifica pacchetti essenziali
                essential_packages = ["collection-basic", "latex", "pdftex", "tex"]
                found_packages = []
                for pkg in essential_packages:
                    if pkg in content:
                        found_packages.append(pkg)
                
                print(f"    ✓ Found {len(found_packages)}/{len(essential_packages)} essential packages")
                return {
                    "accessible": True,
                    "packages_found": len(found_packages),
                    "total_essential": len(essential_packages)
                }
            else:
                print("    ✗ Invalid package database")
                return {"accessible": False, "reason": "invalid format"}
                
    except Exception as e:
        print(f"    ✗ Cannot access package repository: {e}")
        return {"accessible": False, "reason": str(e)}

def get_texlive_version(mirror_url):
    """Determina la versione di TeX Live dal mirror"""
    try:
        # Prova dal file tlnet.html
        version_url = f"{mirror_url}tlnet.html"
        with urllib.request.urlopen(create_request(version_url), timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            # Cerca pattern comuni per la versione
            patterns = [
                r'TeX Live\s*(\d{4})',
                r'TEXLIVE_(\d{4})',
                r'TL-(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return f"TeX Live {match.group(1)}"
        
        # Prova alternativa: installer version
        install_url = f"{mirror_url}install-tl"
        with urllib.request.urlopen(create_request(install_url), timeout=10) as response:
            content = response.read(20000).decode('utf-8', errors='ignore')
            version_match = re.search(r'TLVersion.*=.*["\']([^"\']+)["\']', content)
            if version_match:
                return f"TeX Live {version_match.group(1)}"
                
    except Exception as e:
        return f"Unknown (error: {e})"
    
    return "Unknown"

def test_installer_download(mirror_url):
    """Testa il download e l'estrazione dell'installer"""
    print(f"  Testing installer download:")
    
    try:
        import tempfile
        import tarfile
        
        installer_url = f"{mirror_url}install-tl-unx.tar.gz"
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            with urllib.request.urlopen(create_request(installer_url), timeout=30) as response:
                # Scarica i primi 1MB per test
                data = response.read(1024 * 1024)
                tmp_file.write(data)
            
            # Verifica che sia un tar.gz valido
            try:
                with tarfile.open(tmp_file.name, 'r:gz') as tar:
                    members = tar.getnames()
                    if any('install-tl' in member for member in members):
                        print("    ✓ Installer archive is valid")
                        os.unlink(tmp_file.name)
                        return {"valid": True, "files": len(members)}
                    else:
                        print("    ✗ Installer archive missing install-tl")
                        return {"valid": False, "reason": "missing install-tl"}
            except tarfile.ReadError as e:
                print(f"    ✗ Installer archive corrupt: {e}")
                return {"valid": False, "reason": "corrupt archive"}
                
    except Exception as e:
        print(f"    ✗ Installer download failed: {e}")
        return {"valid": False, "reason": str(e)}

def comprehensive_mirror_test(mirror_url):
    """Esegue test completo su un mirror"""
    print(f"\n🔍 Testing: {mirror_url}")
    print("=" * 60)
    
    results = {
        "mirror": mirror_url,
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Connettività
    print("  Testing connectivity...")
    connectivity = test_mirror_connectivity(mirror_url)
    results["tests"]["connectivity"] = connectivity
    if not connectivity:
        print("  ❌ FAILED: Cannot connect to mirror")
        return {**results, "valid": False, "reason": "connectivity failed"}
    
    # Test 2: Versione
    version = get_texlive_version(mirror_url)
    results["version"] = version
    print(f"  Version: {version}")
    
    # Test 3: Struttura
    structure_results = test_mirror_structure(mirror_url)
    results["tests"]["structure"] = structure_results
    
    # Verifica file essenziali
    essential_files = ["install-tl-unx.tar.gz", "archive/", "tlpkg/"]
    missing_essential = [f for f in essential_files if structure_results.get(f, {}).get("status") != "found"]
    
    if missing_essential:
        print(f"  ❌ MISSING: {missing_essential}")
        return {**results, "valid": False, "reason": f"missing files: {missing_essential}"}
    
    # Test 4: Repository pacchetti
    repo_results = test_package_repository(mirror_url)
    results["tests"]["repository"] = repo_results
    if not repo_results["accessible"]:
        return {**results, "valid": False, "reason": "repository inaccessible"}
    
    # Test 5: Installer
    installer_results = test_installer_download(mirror_url)
    results["tests"]["installer"] = installer_results
    if not installer_results["valid"]:
        return {**results, "valid": False, "reason": "installer invalid"}
    
    # Se tutti i test passano
    print(f"  ✅ ALL TESTS PASSED")
    return {**results, "valid": True}

def main():
    """Funzione principale"""
    print("TeX Live Mirror Comprehensive Test Suite")
    print("=" * 50)
    
    all_results = {
        "test_timestamp": datetime.now().isoformat(),
        "mirrors_tested": len(MIRRORS_TO_TEST),
        "results": []
    }
    
    valid_mirrors = []
    
    for mirror_url in MIRRORS_TO_TEST:
        result = comprehensive_mirror_test(mirror_url)
        all_results["results"].append(result)
        
        if result["valid"]:
            valid_mirrors.append(mirror_url)
    
    # Salva risultati dettagliati
    with open('mirror_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Salva lista mirror validi
    with open('valid_mirrors.txt', 'w') as f:
        for mirror in valid_mirrors:
            f.write(mirror + '\n')
    
    # Report finale
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Mirrors tested: {len(MIRRORS_TO_TEST)}")
    print(f"Valid mirrors: {len(valid_mirrors)}")
    print(f"Success rate: {len(valid_mirrors)/len(MIRRORS_TO_TEST)*100:.1f}%")
    
    if valid_mirrors:
        print("\n✅ VALID MIRRORS:")
        for mirror in valid_mirrors:
            print(f"  - {mirror}")
    else:
        print("\n❌ NO VALID MIRRORS FOUND!")
        sys.exit(1)

if __name__ == '__main__':
    main()