"""
Test pour vérifier qu'on ne peut PAS accéder aux fichiers hors sandbox
"""
from src.tools.file_tools import read_file, write_file, SecurityError

print("="*70)
print("  TEST: Tentative d'accès à un fichier HORS SANDBOX")
print("="*70)

# Fichier créé HORS du sandbox (à la racine du projet)
dangerous_file = "outside_sandbox_test.py"

print(f"\n🎯 Fichier cible: {dangerous_file}")
print(f"📍 Localisation: Racine du projet (HORS sandbox/)")
print(f"\n⚠️  Tentative de lecture...\n")

try:
    content = read_file(dangerous_file)
    
    # Si on arrive ici = PROBLÈME DE SÉCURITÉ
    print("❌ ERREUR CRITIQUE: Le fichier a été lu !")
    print(f"   Contenu: {content[:100]}...")
    print("\n🚨 SÉCURITÉ COMPROMISE - Le sandbox ne fonctionne pas!\n")
    
except SecurityError as e:
    # C'est ce qu'on veut !
    print("❌ SUCCÈS: Accès bloqué par la sécurité!")
    print(f"   Message d'erreur: {str(e)[:100]}...")
    print("\n🔒 SÉCURITÉ FONCTIONNELLE - Le sandbox protège bien!\n")
    
except Exception as e:
    print(f"⚠️  Autre erreur: {type(e).__name__}: {e}\n")

# Test 2: Tentative d'écriture
print("="*70)
print("  TEST 2: Tentative d'ÉCRITURE hors sandbox")
print("="*70)

print(f"\n⚠️  Tentative d'écriture dans 'malicious.txt'...\n")

try:
    write_file("malicious.txt", "DANGER: This should not work!")
    
    print("❌ ERREUR: Fichier créé hors sandbox!")
    print("🚨 SÉCURITÉ COMPROMISE!\n")
    
except SecurityError as e:
    print("❌ SUCCÈS: Écriture bloquée!")
    print(f"   Message: {str(e)[:100]}...\n")
    
except Exception as e:
    print(f"⚠️  Autre erreur: {e}\n")

# Test 3: Tentative sur fichiers système
print("="*70)
print("  TEST 3: Tentative d'accès à des fichiers système")
print("="*70)

system_files = [
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "../.env",
    "../../main.py",
    "/etc/passwd"
]

blocked = 0
for i, filepath in enumerate(system_files, 1):
    try:
        read_file(filepath)
        print(f"{i}. ❌ DANGER: '{filepath}' accessible!")
    except SecurityError:
        print(f"{i}. ✅ Bloqué: '{filepath}'")
        blocked += 1
    except Exception as e:
        print(f"{i}. ⚠️  Erreur: {filepath}")

print(f"\n📊 Résultat: {blocked}/{len(system_files)} fichiers système bloqués")

if blocked == len(system_files):
    print("✅ Tous les fichiers système sont protégés!\n")
else:
    print("❌ Certains fichiers système sont accessibles!\n")

print("="*70)
print("  FIN DES TESTS")
print("="*70)
