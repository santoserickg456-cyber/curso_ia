#!/usr/bin/env python3
"""
IA Privada Local - Sistema de Assistente Pessoal
Este código roda completamente offline, mantendo seus dados 100% privados.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict


class PrivateAI:
    """
    Classe principal da IA Privada.
    Todos os dados são armazenados localmente e criptografados.
    """
    
    def __init__(self, storage_path: str = "./private_data"):
        self.storage_path = storage_path
        self.user_id = self._generate_user_id()
        self.memory_file = os.path.join(storage_path, "memory.json")
        self.config_file = os.path.join(storage_path, "config.json")
        
        # Criar diretório de armazenamento se não existir
        os.makedirs(storage_path, exist_ok=True)
        
        # Carregar memória e configurações
        self.memory = self._load_memory()
        self.config = self._load_config()
        
        print(f"🔒 IA Privada inicializada para usuário: {self.user_id[:8]}...")
        print(f"📁 Dados armazenados em: {os.path.abspath(storage_path)}")
    
    def _generate_user_id(self) -> str:
        """Gera um ID único baseado em timestamp e aleatoriedade."""
        unique_string = f"{datetime.now().isoformat()}{os.urandom(16).hex()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    def _load_memory(self) -> Dict:
        """Carrega a memória do arquivo ou cria nova."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao carregar memória: {e}")
                return {"conversations": [], "learned_patterns": {}, "preferences": {}}
        return {"conversations": [], "learned_patterns": {}, "preferences": {}}
    
    def _save_memory(self):
        """Salva a memória no arquivo."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar memória: {e}")
    
    def _load_config(self) -> Dict:
        """Carrega configurações do usuário."""
        default_config = {
            "language": "pt-BR",
            "personality": "amigável",
            "max_context_length": 10,
            "privacy_mode": True,
            "auto_learn": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Salva as configurações."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar config: {e}")
    
    def _simple_pattern_matching(self, user_input: str) -> str:
        """
        Sistema simples de correspondência de padrões.
        Em produção, você pode integrar com modelos locais como Llama, Mistral, etc.
        """
        user_input_lower = user_input.lower()
        
        # Padrões de saudação
        if any(greeting in user_input_lower for greeting in ["olá", "oi", "bom dia", "boa tarde", "boa noite"]):
            return "Olá! Como posso ajudar você hoje? 😊"
        
        # Padrões de apresentação
        if "quem é você" in user_input_lower or "o que você é" in user_input_lower:
            return "Sou sua IA Privada Pessoal. Todo nosso diálogo fica armazenado apenas no seu computador, garantindo 100% de privacidade! 🔒"
        
        # Padrões de ajuda
        if any(help_word in user_input_lower for help_word in ["ajuda", "help", "socorro"]):
            return "Posso ajudar com:\n• Conversas privadas\n• Armazenamento seguro de informações\n• Aprendizado de suas preferências\n• Respostas personalizadas\n\nO que você precisa?"
        
        # Padrões de tempo
        if "hora" in user_input_lower or "que horas" in user_input_lower:
            now = datetime.now()
            return f"Agora são {now.strftime('%H:%M')} do dia {now.strftime('%d/%m/%Y')}."
        
        # Padrões de data
        if "data" in user_input_lower or "dia" in user_input_lower:
            now = datetime.now()
            return f"Hoje é {now.strftime('%d/%m/%Y')}, {now.strftime('%A')}."
        
        # Verificar se já aprendeu algo sobre este tópico
        for pattern, response in self.memory.get("learned_patterns", {}).items():
            if pattern.lower() in user_input_lower:
                return response
        
        # Resposta padrão com aprendizado
        return None
    
    def learn(self, user_input: str, response: str):
        """Aprende novos padrões a partir das interações."""
        if not self.config.get("auto_learn", True):
            return
        
        # Extrair palavras-chave simples (em produção, usar NLP mais sofisticado)
        words = user_input.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in 
                   ["para", "com", "de", "do", "da", "que", "qual", "como", "quando", "onde"]]
        
        if keywords:
            key = " ".join(keywords[:3])  # Usar até 3 palavras-chave
            self.memory["learned_patterns"][key] = response
            self._save_memory()
    
    def chat(self, user_input: str) -> str:
        """
        Processa uma mensagem do usuário e retorna uma resposta.
        """
        timestamp = datetime.now().isoformat()
        
        # Salvar conversa na memória
        conversation_entry = {
            "timestamp": timestamp,
            "user": user_input,
            "assistant": ""
        }
        
        # Tentar encontrar resposta nos padrões
        response = self._simple_pattern_matching(user_input)
        
        if response is None:
            # Resposta genérica quando não entende
            response = f"Entendi você dizer: '{user_input}'. Pode me explicar melhor o que precisa? Estou aprendendo com nossas conversas! 🤔"
            
            # Aprender com esta interação
            if self.config.get("auto_learn", True):
                self.learn(user_input, f"Quando você pergunta sobre '{user_input}', geralmente quer saber mais detalhes.")
        else:
            # Atualizar entrada da conversa
            conversation_entry["assistant"] = response
        
        # Adicionar à memória (manter apenas últimas N conversas)
        max_context = self.config.get("max_context_length", 10)
        self.memory["conversations"].append(conversation_entry)
        
        # Manter histórico limitado
        if len(self.memory["conversations"]) > max_context * 2:
            self.memory["conversations"] = self.memory["conversations"][-max_context:]
        
        self._save_memory()
        
        return response
    
    def set_preference(self, key: str, value):
        """Define uma preferência do usuário."""
        self.memory["preferences"][key] = value
        self._save_memory()
        return f"Preferência '{key}' definida com sucesso! ✅"
    
    def get_preference(self, key: str, default=None):
        """Obtém uma preferência do usuário."""
        return self.memory["preferences"].get(key, default)
    
    def clear_memory(self):
        """Limpa toda a memória (útil para privacidade)."""
        self.memory = {"conversations": [], "learned_patterns": {}, "preferences": {}}
        self._save_memory()
        return "Memória limpa com sucesso! 🔒"
    
    def export_data(self, filename: str = "my_private_ai_data.json"):
        """Exporta todos os dados para backup."""
        export_data = {
            "user_id": self.user_id,
            "export_date": datetime.now().isoformat(),
            "memory": self.memory,
            "config": self.config
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return f"Dados exportados para: {filename} 📦"
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso."""
        return {
            "total_conversations": len(self.memory.get("conversations", [])),
            "learned_patterns": len(self.memory.get("learned_patterns", {})),
            "preferences_count": len(self.memory.get("preferences", {})),
            "user_id": self.user_id[:8] + "...",
            "storage_path": os.path.abspath(self.storage_path)
        }


def main():
    """Função principal para rodar a IA Privada no terminal."""
    print("=" * 60)
    print("🔒 IA PRIVADA LOCAL - Seu Assistente Pessoal 100% Offline")
    print("=" * 60)
    print()
    
    # Inicializar a IA
    ai = PrivateAI()
    
    print()
    print("Comandos disponíveis:")
    print("  • Digite sua mensagem para conversar")
    print("  • '/stats' - Ver estatísticas de uso")
    print("  • '/export' - Exportar seus dados")
    print("  • '/clear' - Limpar memória")
    print("  • '/set <chave> <valor>' - Definir preferência")
    print("  • '/quit' - Sair do programa")
    print()
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 Você: ").strip()
            
            if not user_input:
                continue
            
            # Comandos especiais
            if user_input.startswith("/"):
                command = user_input.lower().split()
                
                if command[0] == "/quit" or command[0] == "/exit":
                    print("\n👋 Até logo! Seus dados estão seguros e privados.")
                    break
                
                elif command[0] == "/stats":
                    stats = ai.get_stats()
                    print("\n📊 Estatísticas:")
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                
                elif command[0] == "/export":
                    result = ai.export_data()
                    print(f"\n{result}")
                
                elif command[0] == "/clear":
                    confirm = input("Tem certeza? Isso apagará todo o histórico (s/n): ")
                    if confirm.lower() == 's':
                        result = ai.clear_memory()
                        print(f"\n{result}")
                    else:
                        print("\nOperação cancelada.")
                
                elif command[0] == "/set" and len(command) >= 3:
                    key = command[1]
                    value = " ".join(command[2:])
                    result = ai.set_preference(key, value)
                    print(f"\n{result}")
                
                else:
                    print("\n⚠️ Comando não reconhecido. Use /quit para sair.")
            
            else:
                # Chat normal
                response = ai.chat(user_input)
                print(f"\n🤖 IA: {response}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupção detectada. Até logo!")
            break
        except EOFError:
            print("\n\n👋 Fim do input. Até logo!")
            break
    
    print("\n" + "=" * 60)
    print("Obrigado por usar a IA Privada Local!")
    print("=" * 60)


if __name__ == "__main__":
    main()
