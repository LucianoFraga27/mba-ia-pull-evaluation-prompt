"""
Script para fazer pull de prompts do LangSmith Prompt Hub.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

# Carrega variáveis do .env
load_dotenv()

# Configuração: Mapeia LANGSMITH_API_KEY para LANGCHAIN_API_KEY se necessário
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path("prompts/bug_to_user_story_v1.yml")


def pull_prompts_from_langsmith():
    """Faz o pull do prompt e salva em formato YAML compatível com o projeto."""
    print(f"Iniciando pull do prompt: {PROMPT_NAME}...")
    
    try:
        client = Client()
        # Faz o pull do prompt do Hub
        prompt = client.pull_prompt(PROMPT_NAME)
        
        # Estrutura o dicionário para salvar como YAML
        # Nota: O prompt v1 geralmente é um ChatPromptTemplate
        system_prompt = ""
        user_prompt = ""
        
        if hasattr(prompt, 'messages'):
            for msg in prompt.messages:
                # Extrai o template dependendo do tipo de mensagem
                content = msg.prompt.template if hasattr(msg, 'prompt') else str(msg)
                
                if "System" in str(type(msg)):
                    system_prompt = content
                elif "Human" in str(type(msg)) or "User" in str(type(msg)):
                    user_prompt = content

        prompt_data = {
            "metadata": {
                "name": "bug_to_user_story_v1",
                "description": "Prompt inicial de baixa qualidade para conversão de bugs",
                "source": PROMPT_NAME,
                "version": "1.0.0"
            },
            "system_prompt": system_prompt or str(prompt),
            "user_prompt_template": user_prompt or "{bug_report}",
            "techniques_applied": []
        }
        
        # Salva o arquivo
        if save_yaml(prompt_data, str(OUTPUT_PATH)):
            print(f"Prompt salvo com sucesso em: {OUTPUT_PATH}")
            return True
        return False
        
    except Exception as e:
        print(f"Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("LANGSMITH PROMPT PULL")
    
    # Verifica variáveis obrigatórias
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
        
    if pull_prompts_from_langsmith():
        print("\nProcesso concluido com sucesso!")
        return 0
    else:
        print("\nOcorreram erros durante o processo.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
