"""
Script de test complet pour bad_code.py
Execute tous les tests et affiche un rapport detaille
"""
import json
from src.tools.pylint_tool import run_pylint_analysis, get_directory_quality_score
from src.tools.pytest_tool import run_pytest
from src.tools.code_modifier import get_code_metrics, add_docstring, compare_files


def print_separator(title=""):
    """Print a nice separator."""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)


def test_bad_code():
    """Run all tests on bad_code.py."""
    print_separator("RAPPORT COMPLET : bad_code.py vs ok_code.py")
    
    # TEST 1: Analyse Pylint
    print_separator("TEST 1 : ANALYSE PYLINT (Qualite du Code)")
    
    bad_analysis = run_pylint_analysis('sandbox/test_dataset/bad_code.py')
    ok_analysis = run_pylint_analysis('sandbox/test_dataset/ok_code.py')
    
    print(f"\n📊 SCORES PYLINT:")
    print(f"  ❌ bad_code.py:  {bad_analysis['score']:.2f}/10  ({bad_analysis['total_issues']} issues)")
    print(f"  ✅ ok_code.py:   {ok_analysis['score']:.2f}/10  ({ok_analysis['total_issues']} issues)")
    
    improvement = ok_analysis['score'] - bad_analysis['score']
    print(f"\n💡 Amelioration possible: +{improvement:.2f} points")
    
    print(f"\n🔍 TOP 5 PROBLEMES (bad_code.py):")
    for i, issue in enumerate(bad_analysis.get('issues_detail', [])[:5], 1):
        print(f"  {i}. Ligne {issue['line']:2d} [{issue['symbol']}]")
        print(f"     → {issue['message']}")
    
    # TEST 2: Tests unitaires
    print_separator("TEST 2 : TESTS UNITAIRES (Pytest)")
    
    test_result = run_pytest('sandbox/test_dataset')
    
    print(f"\n📝 RESULTATS DES TESTS:")
    print(f"  ✅ Passes:   {test_result['passed']}")
    print(f"  ❌ Echoues:  {test_result['failed']}")
    print(f"  ⏭️  Ignores:  {test_result['skipped']}")
    print(f"  📊 Total:    {test_result['total']}")
    print(f"  🎯 Taux de succes: {test_result['success_rate']:.1f}%")
    
    if test_result['failed'] > 0:
        print(f"\n🔴 ERREURS DETECTEES:")
        print(test_result['error_log'][:400])
    
    # TEST 3: Metriques du code
    print_separator("TEST 3 : METRIQUES ET DOCSTRINGS")
    
    bad_metrics = get_code_metrics('sandbox/test_dataset/bad_code.py')
    ok_metrics = get_code_metrics('sandbox/test_dataset/ok_code.py')
    
    bad_docs = add_docstring('sandbox/test_dataset/bad_code.py')
    ok_docs = add_docstring('sandbox/test_dataset/ok_code.py')
    
    print(f"\n📏 STRUCTURE DU CODE:")
    print(f"  bad_code.py:")
    print(f"    - Lignes:     {bad_metrics['lines_of_code']}")
    print(f"    - Fonctions:  {bad_metrics['function_count']}")
    print(f"    - Classes:    {bad_metrics['class_count']}")
    print(f"    - Complexite: {bad_metrics['complexity']}")
    print(f"    - Docstrings manquantes: {bad_docs['missing_docstrings']}")
    
    print(f"\n  ok_code.py:")
    print(f"    - Lignes:     {ok_metrics['lines_of_code']}")
    print(f"    - Fonctions:  {ok_metrics['function_count']}")
    print(f"    - Classes:    {ok_metrics['class_count']}")
    print(f"    - Complexite: {ok_metrics['complexity']}")
    print(f"    - Docstrings manquantes: {ok_docs['missing_docstrings']}")
    
    # TEST 4: Comparaison
    print_separator("TEST 4 : COMPARAISON DIRECTE")
    
    comparison = compare_files(
        'sandbox/test_dataset/bad_code.py',
        'sandbox/test_dataset/ok_code.py'
    )
    
    print(f"\n🔄 DIFFERENCES:")
    print(f"  Lignes:     {comparison['file1_lines']} → {comparison['file2_lines']}")
    print(f"  Fonctions:  {comparison['file1_functions']} → {comparison['file2_functions']}")
    print(f"  Identiques: {'Oui' if comparison['identical'] else 'Non'}")
    
    # VERDICT FINAL
    print_separator("VERDICT FINAL")
    
    print(f"\n🎯 EVALUATION DE bad_code.py:")
    
    issues = []
    if bad_analysis['score'] < 7.0:
        issues.append(f"Score Pylint trop bas ({bad_analysis['score']:.2f}/10)")
    if bad_docs['missing_docstrings'] > 0:
        issues.append(f"{bad_docs['missing_docstrings']} docstrings manquantes")
    if test_result['success_rate'] < 100:
        issues.append(f"Tests incomplets ({test_result['success_rate']:.1f}%)")
    if bad_analysis['total_issues'] > 5:
        issues.append(f"{bad_analysis['total_issues']} problemes de style")
    
    if issues:
        print(f"\n  ❌ CODE DE MAUVAISE QUALITE")
        print(f"\n  Raisons:")
        for issue in issues:
            print(f"    - {issue}")
        
        print(f"\n  📋 ACTIONS RECOMMANDEES:")
        print(f"    1. Ajouter docstrings module/fonctions/classes")
        print(f"    2. Fixer l'indentation (4 espaces)")
        print(f"    3. Ajouter type hints")
        print(f"    4. Supprimer variables inutilisees")
        print(f"    5. Deplacer print() dans main()")
    else:
        print(f"\n  ✅ CODE DE BONNE QUALITE")
    
    # TEST 5: Logs
    print_separator("TEST 5 : VERIFICATION DES LOGS")
    
    try:
        with open('logs/experiment_data.json') as f:
            logs = json.load(f)
            print(f"\n✅ Logs valides")
            print(f"   Total d'actions enregistrees: {len(logs)}")
            
            if logs:
                last = logs[-1]
                print(f"\n   Derniere action:")
                print(f"     - Agent:  {last.get('agent_name')}")
                print(f"     - Action: {last.get('action')}")
                print(f"     - Status: {last.get('status')}")
                
                # Compter actions
                action_counts = {}
                for entry in logs:
                    action = entry.get('action')
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                print(f"\n   Resume des actions:")
                for action, count in action_counts.items():
                    print(f"     - {action}: {count}")
    except Exception as e:
        print(f"\n❌ Erreur logs: {e}")
    
    print("\n" + "="*70)
    print("  FIN DU RAPPORT")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_bad_code()
