"""
Test de sécurité du sandbox pour file_tools.py
Vérifie que les chemins dangereux sont bloqués
"""
from src.tools.file_tools import read_file, write_file, SecurityError


def test_security():
    """Test security restrictions."""
    print("="*70)
    print("  TEST DE SÉCURITÉ - SANDBOX FILE_TOOLS")
    print("="*70)
    
    # Liste de chemins dangereux à tester
    dangerous_paths = [
        # Tentative de sortir du sandbox
        "../../../etc/passwd",
        "../../requirements.txt",
        "../main.py",
        
        # Chemins absolus Windows
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        "C:\\Users\\HP\\Desktop\\secret.txt",
        
        # Chemins absolus Linux
        "/etc/passwd",
        "/home/user/.ssh/id_rsa",
        
        # Chemins relatifs dangereux
        "..\\..\\..\\Windows\\System32\\cmd.exe",
        "..\\..\\.env",
    ]
    
    blocked_count = 0
    
    print(f"\n🔒 TEST DE {len(dangerous_paths)} CHEMINS DANGEREUX:\n")
    
    for i, path in enumerate(dangerous_paths, 1):
        try:
            # Tenter de lire un fichier dangereux
            content = read_file(path)
            
            # Si on arrive ici, la sécurité a échoué !
            print(f"  {i}. ❌ DANGER: '{path}' a été autorisé !")
            
        except SecurityError as e:
            # La sécurité fonctionne !
            print(f"  {i}. ✅ BLOQUÉ: '{path}'")
            blocked_count += 1
            
        except FileNotFoundError:
            # Le fichier n'existe pas (mais le path était sûr)
            print(f"  {i}. ⚠️  AUTORISÉ mais fichier inexistant: '{path}'")
            
        except Exception as e:
            # Autre erreur
            print(f"  {i}. ⚠️  Erreur inattendue: {type(e).__name__}: {e}")
    
    # Résultat final
    print(f"\n" + "="*70)
    print(f"  RÉSULTAT FINAL")
    print("="*70)
    print(f"\n  Chemins testés:  {len(dangerous_paths)}")
    print(f"  Chemins bloqués: {blocked_count}")
    print(f"  Taux de blocage: {blocked_count/len(dangerous_paths)*100:.1f}%")
    
    if blocked_count == len(dangerous_paths):
        print(f"\n  ✅ SÉCURITÉ PARFAITE - Tous les chemins dangereux sont bloqués!")
    elif blocked_count > len(dangerous_paths) * 0.8:
        print(f"\n  ⚠️  SÉCURITÉ PARTIELLE - Quelques chemins passent encore")
    else:
        print(f"\n  ❌ SÉCURITÉ INSUFFISANTE - Trop de chemins dangereux autorisés!")
    
    # Test de chemins VALIDES (doivent passer)
    print(f"\n" + "="*70)
    print(f"  TEST DE CHEMINS VALIDES (doivent être autorisés)")
    print("="*70 + "\n")
    
    valid_paths = [
        "sandbox/test_dataset/bad_code.py",
        "sandbox/dataset_inconnu/test.py",
        "./sandbox/test_dataset/ok_code.py",
    ]
    
    valid_count = 0
    
    for i, path in enumerate(valid_paths, 1):
        try:
            # Ces paths doivent être autorisés (même si le fichier n'existe pas)
            from src.tools.file_tools import is_safe_path
            is_safe_path(path)
            print(f"  {i}. ✅ AUTORISÉ: '{path}'")
            valid_count += 1
            
        except SecurityError:
            print(f"  {i}. ❌ BLOQUÉ (erreur): '{path}'")
            
        except Exception as e:
            print(f"  {i}. ⚠️  Erreur: {e}")
    
    print(f"\n  Chemins valides autorisés: {valid_count}/{len(valid_paths)}")
    
    print(f"\n" + "="*70)
    print(f"  FIN DES TESTS DE SÉCURITÉ")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_security()
