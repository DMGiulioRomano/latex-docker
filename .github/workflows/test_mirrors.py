# .github/test_mirrors.py
import urllib.request
import urllib.error
import sys
import re

def test_mirror_structure(mirror_url):
    """Testa la struttura di un mirror"""
    required_files = [
        "install-tl-unx.tar.gz",
        "archive/",
        "tlpkg/",
        "update-info.html"
    ]
    
    print(f"\nTesting mirror: {mirror_url}")
    
    for file in required_files:
        test_url = f"{mirror_url}{file}"
        try:
            req = urllib.request.Request(test_url)
            req.add_header('User-Agent', 'GitHub-Actions-Mirror-Test/1.0')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print(f"✓ {file} - Found")
                else:
                    print(f"✗ {file} - HTTP {response.getcode()}")
                    return False
        except Exception as e:
            print(f"✗ {file} - Error: {e}")
            return False
    
    return True

def test_package_availability(mirror_url):
    """Verifica che alcuni pacchetti comuni siano disponibili"""
    print(f"\nTesting package availability on: {mirror_url}")
    
    try:
        index_url = f"{mirror_url}tlpkg/texlive.tlpdb"
        req = urllib.request.Request(index_url)
        req.add_header('User-Agent', 'GitHub-Actions-Mirror-Test/1.0')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read(5000).decode('utf-8', errors='ignore')
            if "TeX Live" in content:
                print("✓ Repository index accessible")
                # Verifica presenza di alcuni pacchetti
                test_packages = ["collection-basic", "latex", "latex-bin"]
                for pkg in test_packages:
                    if pkg in content:
                        print(f"✓ Package {pkg} found in index")
                    else:
                        print(f"⚠ Package {pkg} not immediately found")
                return True
            else:
                print("✗ Invalid repository index")
                return False
    except Exception as e:
        print(f"✗ Cannot access repository: {e}")
        return False

def get_texlive_version(mirror_url):
    """Ottiene la versione TeX Live dal mirror"""
    try:
        version_url = f"{mirror_url}tlnet.html"
        req = urllib.request.Request(version_url)
        req.add_header('User-Agent', 'GitHub-Actions-Mirror-Test/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            version_match = re.search(r'TeX Live (\d+)', content)
            if version_match:
                return f"TeX Live {version_match.group(1)}"
            
        # Prova alternativa nel file di installazione
        install_url = f"{mirror_url}install-tl"
        req = urllib.request.Request(install_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read(10000).decode('utf-8', errors='ignore')
            version_match = re.search(r'TLVersion.*=.*["\']([^"\']+)["\']', content)
            if version_match:
                return f"TeX Live {version_match.group(1)}"
    except Exception as e:
        return f"Unknown (Error: {e})"
    
    return "Unknown"

def comprehensive_mirror_test(mirror_url):
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE TEST: {mirror_url}")
    print(f"{'='*60}")
    
    version = get_texlive_version(mirror_url)
    print(f"Version: {version}")
    
    structure_ok = test_mirror_structure(mirror_url)
    packages_ok = test_package_availability(mirror_url)
    
    if structure_ok and packages_ok:
        print(f"✅ {mirror_url} - VALID MIRROR")
        return True
    else:
        print(f"❌ {mirror_url} - INVALID MIRROR")
        return False

def main():
    mirrors_to_test = [
        "https://texlive.info/tlnet-archive/2025/05/01/tlnet/",  # Originale
        "https://mirror.ctan.org/systems/texlive/tlnet/",
        "https://ftp.tu-chemnitz.de/pub/tug/historic/systems/texlive/current/tlnet/",
    ]
    
    valid_mirrors = []
    for mirror in mirrors_to_test:
        if comprehensive_mirror_test(mirror):
            valid_mirrors.append(mirror)
    
    print(f"\n{'='*60}")
    print(f"VALID MIRRORS FOUND: {len(valid_mirrors)}")
    for mirror in valid_mirrors:
        print(f"  - {mirror}")
    
    # Esci con errore se non ci sono mirror validi
    if len(valid_mirrors) == 0:
        print("No valid mirrors found!")
        sys.exit(1)
    else:
        # Scrivere i mirror validi in un file per lo step successivo
        with open('valid_mirrors.txt', 'w') as f:
            for mirror in valid_mirrors:
                f.write(mirror + '\n')

if __name__ == '__main__':
    main()
