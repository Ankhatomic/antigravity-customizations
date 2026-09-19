# 🥩 Grill With Docs

Uma skill para o **Google Antigravity IDE** que combina uma **sabatina implacável de planejamento técnico** com a **persistência automática de decisões** no repositório (em formato ADR ou `DECISOES.md`).

Inspirada no clássico `/grill-me`, o **`grill-with-docs`** impede que o assistente comece a programar às cegas, forçando um alinhamento completo de arquitetura e registrando todas as escolhas para que nenhuma decisão se perca entre sessões de chat.

---

## ✨ Como Funciona

1. **Leitura de Contexto:** Antes da primeira pergunta, a skill inspeciona o projeto (arquivos de configuração, linguagens e documentação existente) para fazer perguntas embasadas na sua stack real.
2. **Sabatina em Rodadas Ordenadas:** As perguntas são agrupadas por dependências (árvore de decisão). O assistente sempre fornece **opções de múltipla escolha** e **sua recomendação técnica com justificativa**.
3. **Registro Automático de Decisões:**
   - **Projetos médios/grandes:** Cria arquivos individuais de ADR em `docs/decisions/001-nome.md`.
   - **Projetos rápidos:** Adiciona ao arquivo unificado `DECISOES.md` na raiz do projeto.
4. **Memória de Longo Prazo:** Os arquivos de decisões gerados passam a ser lidos nas próximas conversas pelo Antigravity, eliminando sugestões contraditórias.

---

## 🚀 Como Instalar no seu Antigravity

### Instalação Global (Disponível em todos os projetos)
```bash
# 1. Clone o repositório
git clone https://github.com/Ankhatomic/antigravity-customizations.git /tmp/antigravity-customizations

# 2. Copie para a pasta global de skills
mkdir -p ~/.gemini/config/skills
cp -r /tmp/antigravity-customizations/skills/grill-with-docs ~/.gemini/config/skills/
```

### Instalação no Projeto Atual (Workspace)
```bash
mkdir -p .agents/skills
cp -r /caminho/para/grill-with-docs .agents/skills/
```

---

## 💬 Exemplos de Uso no Chat

Você pode ativar a skill dizendo:

* *"Quero usar grill-with-docs para planejar a autenticação da minha API"*
* *"Questione meu plano de banco de dados e salve nossas decisões"*
* *"Faça uma sabatina da arquitetura deste microsserviço"*
* *"Valide as decisões técnicas antes de começarmos a codificar"*

---

## 📁 Estrutura da Skill

```
grill-with-docs/
├── SKILL.md                          # Instruções da metodologia e fluxo
├── README.md                         # Este guia explicativo
└── references/
    └── adr_template.md               # Modelo padrão de registro de decisão (ADR)
```

---

## 📄 Licença

Distribuído sob a licença [MIT](../../LICENSE).
