# 🧠 Prompt Engineer (Context Engineering Edition — 2026)

Skill para o **Google Antigravity IDE** focada em arquitetura e engenharia de prompts de alta fidelidade segundo as práticas de 2026, com ênfase em **Context Engineering**, estruturação semântica em XML, orquestração agentica e gestão rigorosa de tokens.

---

## ✨ Funcionalidades

- **Context Engineering vs. Prompting Tradicional:** Tratamento do LLM como CPU e contexto como RAM, operando com as 4 alavancas (*Write*, *Select*, *Compress*, *Isolate*).
- **Framework "Contrato" em XML:** Estruturação semântica com tags explícitas (`<role>`, `<context>`, `<instructions>`, `<constraints>`, `<output_contract>`, `<failure_modes>`).
- **Token Budget Management:** Auditoria de tokens em 3 camadas (identificação de prefixos estáticos para prompt caching, compressão de histórico e restrição estrita de output).
- **Técnicas Avançadas Integradas:** Referência para Chain-of-Thought (CoT), Few-Shot calibrado (1–3 exemplos), ReAct para agentes com ferramentas, Self-Consistency e Orchestrator-Workers.
- **Templates Prontos para Produção:** 6 templates plug-and-play cobrindo atendimento, extração estruturada, tom de marca, roteamento de modelos compactos, RAG e agentes autônomos.

---

## 📁 Estrutura da Skill

```
prompt-engineer/
├── SKILL.md                 # Instruções principais e workflow de diagnóstico
├── README.md                # Documentação da skill
└── references/
    ├── techniques.md        # Guias e templates de técnicas avançadas (CoT, ReAct, etc.)
    └── templates.md         # 6 templates prontos por tipo de caso de uso
```

---

## 🛠️ Como Instalar

### Opção 1: Instalação Global (Recomendada)
Disponível em qualquer workspace do Antigravity:
```bash
git clone https://github.com/Ankhatomic/antigravity-customizations.git /tmp/repo
mkdir -p ~/.gemini/config/skills
cp -r /tmp/repo/skills/prompt-engineer ~/.gemini/config/skills/
```

### Opção 2: Instalação no Workspace Atual
Ativa apenas no projeto onde for copiada:
```bash
mkdir -p .agents/skills
cp -r /tmp/repo/skills/prompt-engineer .agents/skills/
```

---

## 🚀 Como Usar

A skill ativa automaticamente quando você solicitar:
- *"Crie um prompt para meu agente de atendimento"*
- *"Otimize esse system prompt para gastar menos tokens"*
- *"Estruture esse prompt em formato XML de contrato"*
- *"Audite este prompt e me dê uma nota de 0 a 10 com melhorias"*
