"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_yaml

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"

@pytest.fixture
def prompt_data():
    """Fixture para carregar o prompt otimizado v2."""
    if not PROMPT_PATH.exists():
        pytest.fail(f"Arquivo de prompt não encontrado: {PROMPT_PATH}. Crie o arquivo v2 antes de rodar os testes.")
    return load_yaml(str(PROMPT_PATH))

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert 'system_prompt' in prompt_data, "Campo 'system_prompt' não encontrado no YAML."
        assert len(prompt_data['system_prompt'].strip()) > 0, "O 'system_prompt' não pode estar vazio."

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        content = prompt_data['system_prompt'].lower()
        # Aceita variações em português e inglês
        assert any(phrase in content for phrase in ["você é", "you are", "atue como", "act as"]), \
            "O prompt deve definir explicitamente um papel ou persona (ex: 'Você é um...')."

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        content = prompt_data['system_prompt'].lower()
        assert any(word in content for word in ["markdown", "user story", "história de usuário"]), \
            "O prompt deve mencionar o formato de saída desejado (Markdown ou User Story)."

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        # Verifica se o campo examples existe ou se há exemplos hardcoded no prompt
        # O padrão do desafio sugere um campo 'examples' ou exemplos dentro do system_prompt
        has_examples_field = 'examples' in prompt_data and len(prompt_data['examples']) > 0
        has_embedded_examples = "exemplo" in prompt_data['system_prompt'].lower() or "example" in prompt_data['system_prompt'].lower()
        
        assert has_examples_field or has_embedded_examples, \
            "O prompt deve conter exemplos de Few-shot (entrada/saída)."

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        content = str(prompt_data)
        assert "[TODO]" not in content, "O prompt ainda contém marcadores de [TODO]."

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get('techniques_applied', [])
        
        # Busca recursiva simples nos metadados
        if not techniques and 'metadata' in prompt_data:
            metadata = prompt_data['metadata']
            techniques = metadata.get('techniques_applied') or metadata.get('techniques') or []
            
        assert len(techniques) >= 2, f"Pelo menos 2 técnicas de prompt engineering devem ser listadas nos metadados. Encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])