"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

# Carrega variáveis do .env
load_dotenv()

# Configuração: Mapeia LANGSMITH_API_KEY para LANGCHAIN_API_KEY se necessário
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]

INPUT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
HUB_USERNAME = os.getenv("USERNAME_LANGSMITH_HUB", "")
PROMPT_NAME = f"{HUB_USERNAME}/bug_to_user_story_v2" if HUB_USERNAME else "bug_to_user_story_v2"


def push_prompt_to_langsmith() -> bool:
    """Lê o YAML v2, valida e faz push para o LangSmith Hub."""
    print(f"Lendo prompt de: {INPUT_PATH}...")
    
    prompt_data = load_yaml(str(INPUT_PATH))
    if not prompt_data:
        return False
        
    # Valida estrutura obrigatória antes do push
    is_valid, errors = validate_prompt_structure(prompt_data)
    if not is_valid:
        print("Erro na estrutura do prompt:")
        for err in errors:
            print(f"  - {err}")
        return False
        
    print(f"Fazendo push para o Hub como: {PROMPT_NAME}...")
    
    try:
        client = Client()
        
        # Constrói o template do LangChain
        system_prompt = prompt_data.get('system_prompt', '')
        user_template = prompt_data.get('user_prompt_template', '{bug_report}')
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_template)
        ])
        
        # Tenta push público
        try:
            result = client.push_prompt(
                PROMPT_NAME,
                object=prompt_template,
                is_public=True
            )
        except Exception as e:
            if "handle" in str(e).lower():
                print("Nota: Handle publico nao configurado. Tentando push PRIVADO...")
                result = client.push_prompt(
                    PROMPT_NAME,
                    object=prompt_template,
                    is_public=False
                )
            else:
                raise e
                
        print(f"Prompt publicado com sucesso: {result}")
        return True
        
    except Exception as e:
        print(f"Erro ao fazer push: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("LANGSMITH PROMPT PUSH")
    
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
        
    if not INPUT_PATH.exists():
        print(f"Arquivo nao encontrado: {INPUT_PATH}. Crie o prompt v2 primeiro.")
        return 1
        
    if push_prompt_to_langsmith():
        print("\nPush concluido com sucesso!")
        return 0
    else:
        print("\nFalha ao realizar o push.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
