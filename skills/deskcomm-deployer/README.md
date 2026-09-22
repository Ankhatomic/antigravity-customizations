# 🚀 Deskcomm Deployer

Uma skill para o **Google Antigravity IDE** projetada para automatizar com máxima segurança e robustez o processo de onboarding e implantação completa do **DeskcommCRM** em VPS de clientes novos (HostGator, Hetzner, DigitalOcean, Contabo, etc.), do clone do repositório até o CRM no ar com WhatsApp conectado e IA pronta para atender.

---

## ✨ Funcionalidades

- **Diagnóstico Pré-Voo Não-Destrutivo:** Script em modo somente-leitura que audita recursos (RAM, CPU, portas 80/443, Docker e arquitetura) antes de qualquer alteração no servidor.
- **Coleta e Validação Segura de 17+ Variáveis:** Validação rígida de credenciais (Supabase, Evolution API, OpenRouter, domínios, chaves criptográficas). Secrets nunca são expostos em logs.
- **Detecção Anti-IPv6 para Supabase:** Previne automaticamente o erro comum de conexão com pooler de banco via IPv6 na VPS.
- **Proteção Anti-Lockout no Firewall:** Detecta a porta SSH em uso antes de habilitar o firewall UFW, garantindo que o acesso nunca seja perdido.
- **Deploy Idempotente e Automatizado:** Configura o `.env` e aciona o `install.sh --yes` oficial do DeskcommCRM.
- **Auditoria de Saúde pós-deploy:** Checagem ativa de status de todos os containers Docker.
- **Dossiê de Entrega Formatado:** Gera ao final um relatório executivo pronto para ser enviado ao cliente com URLs de acesso e passos de uso.

---

## 🚀 Como Instalar no seu Antigravity

### Instalação Global (Recomendado — disponível em qualquer conversa)

```bash
# 1. Clone o repositório temporariamente
git clone https://github.com/Ankhatomic/antigravity-customizations.git /tmp/antigravity-customizations

# 2. Copie para a pasta global de skills do Antigravity
mkdir -p ~/.gemini/config/skills
cp -r /tmp/antigravity-customizations/skills/deskcomm-deployer ~/.gemini/config/skills/
```

### Instalação no Projeto Atual (Workspace)

```bash
mkdir -p .agents/skills
cp -r /caminho/para/deskcomm-deployer .agents/skills/
```

---

## 💬 Exemplos de Uso

Uma vez instalada, você pode interagir naturalmente no chat do Antigravity:

* *"Instale o DeskcommCRM para um novo cliente"*
* *"Subir o DeskcommCRM na VPS"*
* *"Novo cliente comprou o CRM, vamos fazer o deploy"*
* *"Onboarding de cliente do Deskcomm"*
* *"Deploy do Deskcomm na HostGator"*

---

## 📁 Estrutura de Arquivos

```
deskcomm-deployer/
├── SKILL.md                          # Instruções completas do fluxo em 7 fases
├── README.md                         # Documentação e guia de instalação rápida
├── references/
│   └── env_fields.md                 # Dicionário e regras de validação das 17 variáveis do .env
└── scripts/
    └── preflight.sh                  # Script de diagnóstico pré-voo (read-only)
```

---

## 📄 Licença

Distribuído sob a licença [MIT](../../LICENSE).
