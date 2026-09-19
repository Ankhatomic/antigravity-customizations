# 📤 GitHub Customizations Publisher

Uma skill para o **Google Antigravity IDE** projetada para publicar, versionar e sincronizar suas customizações (skills, prompts, regras e workflows) diretamente em repositórios do GitHub de forma simples e segura, mesmo para quem nunca usou Git antes.

---

## ✨ Funcionalidades

- **Higienização Automática de Dados:** Remove caminhos absolutos e privados locais (ex: `/home/usuario/`) e substitui por caminhos portáteis relativos ou genéricos (`~/.gemini/config/...`).
- **Geração de Catálogo:** Cria e atualiza automaticamente o `README.md` central do repositório com tabela-resumo de todas as skills e instruções de instalação rápida.
- **Detecção de Repositório Remoto:** Conecta e sincroniza automaticamente com sua conta do GitHub.
- **Suporte a Iniciantes:** Ajuda a configurar o nome/email do Git e instrui como obter o token de acesso no GitHub passo a passo.
- **Múltiplos Tipos de Customização:** Suporte a `skills/`, `prompts/` e `rules/`.

---

## 🚀 Como Instalar no seu Antigravity

### Instalação Global (Disponível em todos os projetos)
Para ter essa skill disponível em qualquer conversa no seu computador:

```bash
# 1. Clone o repositório temporariamente
git clone https://github.com/Ankhatomic/antigravity-customizations.git /tmp/antigravity-customizations

# 2. Copie para a pasta global de skills do Antigravity
mkdir -p ~/.gemini/config/skills
cp -r /tmp/antigravity-customizations/skills/github-customizations-publisher ~/.gemini/config/skills/
```

### Instalação no Projeto Atual (Workspace)
Para compartilhar essa skill apenas no repositório de um projeto específico:

```bash
mkdir -p .agents/skills
cp -r /caminho/para/github-customizations-publisher .agents/skills/
```

---

## 💬 Exemplos de Uso

Uma vez instalada, você pode interagir naturalmente no chat do Antigravity:

* *"Quero subir essa skill para o GitHub"*
* *"Publique meu prompt no meu repositório"*
* *"Como compartilho essa customização com outros usuários?"*
* *"Atualize meu repositório de skills"*

---

## 📁 Estrutura de Arquivos

```
github-customizations-publisher/
├── SKILL.md                          # Instruções principais da skill
├── README.md                         # Guia de instalação e documentação
├── scripts/
│   └── sanitize_and_export.py        # Script Python de higienização e exportação
└── trigger_report.md                 # Relatório de teste dos gatilhos
```

---

## 📄 Licença

Distribuído sob a licença [MIT](../../LICENSE).
