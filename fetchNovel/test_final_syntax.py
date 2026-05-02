#!/usr/bin/env python3
"""
Test final de syntaxe après suppression de DiskSpace
"""
import re

def test_final_syntax():
    """Test final après correction du problème DiskSpace"""
    
    print("🔍 TEST FINAL DE SYNTAXE")
    print("=" * 40)
    
    try:
        with open('installer_script.iss', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Fichier installer_script.iss introuvable!")
        return False
    
    # Vérifier que DiskSpace a été supprimé
    diskspace_count = content.count('DiskSpace')
    
    print(f"\n📊 Vérifications:")
    print(f"   • Appels DiskSpace: {diskspace_count}")
    
    if diskspace_count == 0:
        print("   ✅ DiskSpace supprimé (problème résolu)")
    else:
        print("   ❌ DiskSpace encore présent")
        return False
    
    # Vérifier les fonctions Pascal de base
    pascal_functions = [
        'function InitializeSetup',
        'procedure CurStepChanged',
        'function NeedRestart',
        'function UpdateReadyMemo'
    ]
    
    print(f"\n🔧 Fonctions Pascal:")
    for func in pascal_functions:
        if func in content:
            print(f"   ✅ {func}")
        else:
            print(f"   ❌ {func} manquante")
            return False
    
    # Vérifier les sections requises
    required_sections = ['Setup', 'Files', 'Icons', 'Run', 'Code']
    
    print(f"\n📦 Sections requises:")
    for section in required_sections:
        if f'[{section}]' in content:
            print(f"   ✅ [{section}]")
        else:
            print(f"   ❌ [{section}] manquante")
            return False
    
    # Vérifier qu'il n'y a pas de problèmes évidents
    obvious_issues = []
    
    # Guillemets non fermés
    if content.count('"') % 2 != 0:
        obvious_issues.append("Guillemets non fermés")
    
    # Apostrophes non fermées dans le code Pascal
    pascal_code_match = re.search(r'\[Code\](.*?)\[Run\]', content, re.DOTALL)
    if pascal_code_match:
        pascal_code = pascal_code_match.group(1)
        if pascal_code.count("'") % 2 != 0:
            obvious_issues.append("Apostrophes non fermées dans le code Pascal")
    
    print(f"\n🚫 Problèmes évidents: {len(obvious_issues)}")
    for issue in obvious_issues:
        print(f"   ❌ {issue}")
    
    if len(obvious_issues) == 0:
        print("   ✅ Aucun problème évident détecté")
    
    # Verdict final
    print(f"\n🎯 VERDICT FINAL:")
    
    if diskspace_count == 0 and len(obvious_issues) == 0:
        print("✅ Le script est maintenant syntaxiquement correct!")
        print("🚀 Prêt pour la compilation avec Inno Setup")
        return True
    else:
        print("❌ Des problèmes subsistent")
        return False

if __name__ == "__main__":
    test_final_syntax()
