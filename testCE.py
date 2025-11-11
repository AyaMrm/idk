
import os
import tempfile
import json
from datetime import datetime
from src.commandExecutor import CommandExecutor, run_command

def test_creation_fichiers():
    """Test avec création et manipulation de fichiers"""
    print("📁 TEST CRÉATION FICHIERS")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    # Créer un dossier temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Dossier temporaire: {temp_dir}")
        
        # 1. Création multiple de fichiers
        tests = [
            {
                "name": "Création fichier simple",
                "command": f"echo \"Contenu du fichier 1\" > \"{temp_dir}/fichier1.txt\"",
            },
            {
                "name": "Création fichier avec contenu JSON",
                "command": f"echo \"{json.dumps({'test': 'data', 'timestamp': datetime.now().isoformat()})}\" > \"{temp_dir}/data.json\"",
            },
            {
                "name": "Liste fichiers créés",
                "command":  f"type \"{os.path.join(temp_dir, 'fichier1.txt')}\"" if os.name == 'nt' else f"ls -la \"{temp_dir}\"",
            },
            {
                "name": "Lecture fichier",
                "command":  f"type \"{os.path.join(temp_dir, 'fichier1.txt')}\"" if os.name == 'nt' else f"cat \"{temp_dir}/fichier1.txt\"",
            }
        ]
        
        for test in tests:
            print(f"\n🔧 {test['name']}")
            result = executor.execute_simple(test["command"])
            print(f"   Résultat: {'✅' if result['success'] else '❌'} (Code: {result['return_code']})")

def test_commandes_chainees():
    """Test avec commandes chaînées et pipelines"""
    print("\n⛓️  TEST COMMANDES CHAÎNÉES")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    if os.name == 'nt':  # Windows
        commands = [
            {
                "name": "Pipeline simple",
                "command": "echo \"Hello World\" | findstr \"World\"",
            },
            {
                "name": "Commandes multiples",
                "command": "cd . && echo Current: %CD% && dir | findstr \".py\"",
            },
            {
                "name": "Redirection sortie",
                "command": "echo Test redirection > temp_output.txt && type temp_output.txt && del temp_output.txt",
            }
        ]
    else:  # Linux
        commands = [
            {
                "name": "Pipeline simple", 
                "command": "echo \"Hello World\" | grep \"World\"",
            },
            {
                "name": "Commandes multiples",
                "command": "cd . && echo Current: $PWD && ls -la | grep \".py\"",
            },
            {
                "name": "Redirection sortie",
                "command": "echo Test redirection > temp_output.txt && cat temp_output.txt && rm temp_output.txt",
            }
        ]
    
    for cmd in commands:
        print(f"\n🔗 {cmd['name']}")
        result = executor.execute_simple(cmd["command"])
        print(f"   Résultat: {'✅' if result['success'] else '❌'}")

def test_variables_complexes():
    """Test avec variables d'environnement complexes"""
    print("\n🔧 TEST VARIABLES COMPLEXES")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    env_vars = {
        'APP_NAME': 'MonApplication',
        'APP_VERSION': '1.0.0',
        'DEBUG_MODE': 'true',
        'MAX_THREADS': '10',
        'DATABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'API_KEYS': 'key1,key2,key3'
    }
    
    if os.name == 'nt':  # Windows
        command = (
            "echo Application: %APP_NAME% && "
            "echo Version: %APP_VERSION% && "
            "echo Debug: %DEBUG_MODE% && "
            "echo Threads: %MAX_THREADS% && "
            "echo DB: %DATABASE_URL% && "
            "echo Keys: %API_KEYS%"
        )
    else:  # Linux
        command = (
            "echo \"Application: $APP_NAME\" && "
            "echo \"Version: $APP_VERSION\" && "
            "echo \"Debug: $DEBUG_MODE\" && "
            "echo \"Threads: $MAX_THREADS\" && "
            "echo \"DB: $DATABASE_URL\" && "
            "echo \"Keys: $API_KEYS\""
        )
    
    result = executor.execute_simple(command, env_vars=env_vars)
    print(f"Variables testées: {len(env_vars)}")
    print(f"Résultat: {'✅' if result['success'] else '❌'} (Code: {result['return_code']})")

def test_git_commands():
    """Test avec des commandes Git (si disponible)"""
    print("\n🐙 TEST COMMANDES GIT")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    git_commands = [
        {"name": "Version Git", "command": "git --version"},
        {"name": "Status Git", "command": "git status"},
        {"name": "Config Git", "command": "git config --list | head -5" if os.name != 'nt' else "git config --list"},
    ]
    
    for git_cmd in git_commands:
        print(f"\n🔧 {git_cmd['name']}")
        result = executor.execute_simple(git_cmd["command"])
        if result['success']:
            print(f"   ✅ Git disponible")
        else:
            print(f"   ⚠️  Git non disponible ou erreur")

def test_network_commands():
    """Test avec commandes réseau"""
    print("\n🌐 TEST COMMANDES RÉSEAU")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    if os.name == 'nt':  # Windows
        network_commands = [
            {"name": "Adresse IP", "command": "ipconfig | findstr \"IPv4\""},
            {"name": "Ping local", "command": "ping -n 2 127.0.0.1"},
            {"name": "Ports ouverts", "command": "netstat -an | findstr :80"},
        ]
    else:  # Linux
        network_commands = [
            {"name": "Adresse IP", "command": "ip addr show | grep inet"},
            {"name": "Ping local", "command": "ping -c 2 127.0.0.1"},
            {"name": "Ports ouverts", "command": "netstat -tuln | grep :80"},
        ]
    
    for net_cmd in network_commands:
        print(f"\n🔧 {net_cmd['name']}")
        result = executor.execute_simple(net_cmd["command"], timeout=10)
        print(f"   Résultat: {'✅' if result['success'] else '❌'} (Timeout: {result.get('timeout', False)})")

def test_processus_long():
    """Test avec processus long et gestion timeout"""
    print("\n⏳ TEST PROCESSUS LONG")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    if os.name == 'nt':  # Windows
        long_commands = [
            {
                "name": "Processus court (2s)",
                "command": "timeout 2 && echo Terminé",
                "timeout": 5
            },
            {
                "name": "Processus trop long (timeout)",
                "command": "timeout 10", 
                "timeout": 3
            },
            {
                "name": "Boucle infinie (annulée)",
                "command": "echo Début && ping -t 127.0.0.1 >nul",
                "timeout": 2
            }
        ]
    else:  # Linux
        long_commands = [
            {
                "name": "Processus court (2s)", 
                "command": "sleep 2 && echo Terminé",
                "timeout": 5
            },
            {
                "name": "Processus trop long (timeout)",
                "command": "sleep 10",
                "timeout": 3
            },
            {
                "name": "Boucle infinie (annulée)",
                "command": "echo Début && while true; do sleep 1; done",
                "timeout": 2
            }
        ]
    
    for long_cmd in long_commands:
        print(f"\n⏰ {long_cmd['name']}")
        result = executor.execute_simple(
            long_cmd["command"], 
            timeout=long_cmd["timeout"]
        )
        
        if result['timeout']:
            print(f"   ⏰ Timeout comme prévu")
        else:
            print(f"   ✅ Exécution normale (Code: {result['return_code']})")

def test_performance():
    """Test de performance avec multiples commandes"""
    print("\n⚡ TEST PERFORMANCE")
    print("-" * 40)
    
    import time
    
    executor = CommandExecutor(verbose=False)  # Désactiver logs pour performance
    
    # Préparer 20 commandes simples
    commands = [f"echo Commande {i}" for i in range(1, 21)]
    
    start_time = time.time()
    results = []
    
    for i, cmd in enumerate(commands, 1):
        result = executor.execute_simple(cmd)
        results.append(result)
        if i % 5 == 0:
            print(f"   📊 {i}/20 commandes exécutées...")
    
    total_time = time.time() - start_time
    
    # Analyse résultats
    success_count = sum(1 for r in results if r['success'])
    avg_time = total_time / len(commands)
    
    print(f"\n📈 STATISTIQUES PERFORMANCE:")
    print(f"   Commandes exécutées: {len(commands)}")
    print(f"   ✅ Succès: {success_count}")
    print(f"   ❌ Échecs: {len(commands) - success_count}")
    print(f"   ⏱️  Temps total: {total_time:.2f}s")
    print(f"   ⏱️  Temps moyen par commande: {avg_time:.3f}s")
    print(f"   🚀 Commandes par seconde: {len(commands)/total_time:.1f}")

def test_erreurs_avancees():
    """Test de gestion d'erreurs avancées"""
    print("\n🚨 TEST GESTION ERREURS")
    print("-" * 40)
    
    executor = CommandExecutor(verbose=True)
    
    error_scenarios = [
        {
            "name": "Commande inexistante",
            "command": "commande_qui_n_existe_pas_12345",
            "expected_success": False
        },
        {
            "name": "Permission refusée (simulée)",
            "command": "cd /dossier_inexistant_12345" if os.name == 'nt' else "cd /dossier_inexistant_12345",
            "expected_success": False  
        },
        {
            "name": "Syntaxe invalide",
            "command": "echo 'missing_quote",
            "expected_success": False
        },
        {
            "name": "Fichier inexistant",
            "command": "type fichier_inexistant_12345.txt" if os.name == 'nt' else "cat fichier_inexistant_12345.txt",
            "expected_success": False
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\n🚨 {scenario['name']}")
        result = executor.execute_simple(scenario["command"])
        
        expected = scenario["expected_success"]
        actual = result['success']
        
        if expected == actual:
            print(f"   ✅ Comportement attendu: {'Échec' if not expected else 'Succès'}")
        else:
            print(f"   ❌ Comportement inattendu: {'Échec' if not actual else 'Succès'}")

def main():
    """Fonction principale de test avancé"""
    print("🧪 TEST AVANCÉ - COMMAND EXECUTOR")
    print("=" * 60)
    print(f"📋 Système: {platform.system()}")
    print(f"🐍 Python: {platform.python_version()}")
    print("=" * 60)
    
    # Exécuter tous les tests
    tests = [
        test_creation_fichiers,
        test_commandes_chainees, 
        test_variables_complexes,
        test_git_commands,
        test_network_commands,
        test_processus_long,
        test_performance,
        test_erreurs_avancees
    ]
    
    results = []
    
    for test_func in tests:
        try:
            test_func()
            results.append(("✅", test_func.__name__))
        except Exception as e:
            results.append(("❌", f"{test_func.__name__}: {e}"))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMUM FINAL DES TESTS AVANCÉS")
    print("=" * 60)
    
    for status, test_name in results:
        print(f"{status} {test_name}")
    
    print("=" * 60)
    print("🎯 TESTS AVANCÉS TERMINÉS!")

if __name__ == "__main__":
    import platform
    main()