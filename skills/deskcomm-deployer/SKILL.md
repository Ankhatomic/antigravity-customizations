---
name: deskcomm-deployer
description: >-
  Instala o DeskcommCRM do zero em uma VPS de cliente novo, do clone do repositório
  até o CRM no ar com WhatsApp conectado. Use esta skill quando o usuário vender o
  DeskcommCRM para um cliente e precisar instalar na VPS, ou quando disser frases
  como "instalar o CRM para um cliente", "subir o DeskcommCRM na VPS", "novo cliente
  precisa do CRM", "deploy do Deskcomm", "onboarding de cliente", "implantar o CRM",
  ou qualquer variação de instalar o DeskcommCRM em um servidor remoto. Ative mesmo
  que o usuário não mencione o nome da skill explicitamente.
---

# DeskcommCRM — Deployer de Cliente

Instala o DeskcommCRM do zero em uma VPS de um novo cliente, de forma segura e
idempotente, usando o modo não-interativo do instalador oficial (`install.sh --yes`).

> **Referências (leia quando precisar):**
> - Campos completos do .env → [`references/env_fields.md`](./references/env_fields.md)
> - Script de pré-voo → [`scripts/preflight.sh`](./scripts/preflight.sh)

---

## Visão Geral

```
Você (Antigravity)
   └─ SSH na VPS do cliente
         ├─ Fase 1: Pré-voo (leitura apenas — sem alterar nada)
         ├─ Fase 2: Coleta de credenciais (entrevista com o usuário)
         ├─ Fase 3: Preparação da VPS (firewall, Docker, clone)
         ├─ Fase 4: Geração do .env e execução do install.sh --yes
         └─ Fase 5: Verificação de saúde + dossiê de entrega
```

**Princípio de segurança:** Nunca execute `rm -rf`, comandos destrutivos, formatação
ou alterações em serviços existentes de outros projetos no servidor. Em caso de
dúvida, pare e pergunte ao usuário.

---

## Fase 1 — Coleta de Dados de Acesso SSH

Antes de qualquer ação, colete os dados de acesso ao servidor:

```
Dados que preciso para começar:
1. IP do servidor (VPS do cliente)
2. Porta SSH (padrão 22; a HostGator frequentemente usa 22022 ou 2222)
3. Usuário SSH (geralmente `root`)
4. Senha ou caminho para a chave privada SSH
```

Se o usuário já tiver fornecido esses dados nesta conversa, não pergunte de novo.

---

## Fase 2 — Pré-voo (Diagnóstico sem Alterações)

Execute os comandos abaixo via SSH. **Não modifique nada** nesta fase.

```bash
# Memória e swap
free -h
# Sistema operacional
cat /etc/os-release | grep -E 'NAME|VERSION'
# Docker e Compose
docker --version 2>/dev/null || echo "Docker: não instalado"
docker compose version 2>/dev/null || echo "Docker Compose: não instalado"
# Portas em uso que podem conflitar (80, 443)
ss -tulpn | grep -E ':80|:443' || echo "Portas 80/443: livres"
# Porta SSH ativa desta sessão (CRÍTICO para o firewall)
echo "Porta SSH desta sessão: $SSH_CLIENT"
# Espaço em disco
df -h /
# Git
git --version 2>/dev/null || echo "Git: não instalado"
```

**Avalie e reporte ao usuário:**
- RAM < 3.5 GB → avise que pode ser instável; recomende upgrade
- Portas 80/443 ocupadas → identifique o processo e pergunte como proceder
- Docker não instalado → será instalado na Fase 3 (informe ao usuário)

---

## Fase 3 — Coleta de Credenciais do Cliente

Colete os dados a seguir na ordem exata. Consulte
[`references/env_fields.md`](./references/env_fields.md) para regras de validação.

| # | Variável | O que pedir | Secreto? |
|:--|:---------|:------------|:---------|
| 1 | `DOMAIN` | Domínio do CRM (ex: `crm.cliente.com.br`) | Não |
| 2 | `ACME_EMAIL` | E-mail para avisos de SSL | Não |
| 3 | `NEXT_PUBLIC_SUPABASE_URL` | Supabase Project URL (`https://xxx.supabase.co`) | Não |
| 4 | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Não |
| 5 | `SUPABASE_SERVICE_ROLE_KEY` | Supabase service_role key — **não ecoe na tela** | Sim |
| 6 | `SUPABASE_DB_URL` | Connection string do Session Pooler — **não ecoe** | Sim |
| 7 | `AI_PROVIDER` | Qual IA? `1` OpenRouter / `2` Anthropic / `3` OpenAI | Não |
| 8 | Chave da IA escolhida | `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` ou `OPENAI_API_KEY` | Sim |
| 9 | `OPENAI_API_KEY` (opcional) | Necessário para áudio e RAG se não escolheu OpenAI | Sim |
| 10 | `OWNER_EMAIL` | E-mail do administrador inicial do CRM | Não |
| 11 | `OWNER_PASSWORD` | Senha do admin (mín. 8 caracteres) — **não ecoe** | Sim |
| 12 | `APP_NAME` | Nome na interface (Enter = `DeskcommCRM`) | Não |
| 13 | `APP_LOCALE` | Idioma: `1` Português / `2` Español | Não |
| 14 | `APP_ACCENT_HEX` | Cor da marca em hex, ex.: `#7a5cd6` (opcional) | Não |
| 15 | `SUPPORT_EMAIL` | E-mail de suporte visível ao cliente final (opcional) | Não |
| 16 | `RESEND_API_KEY` | Chave Resend para e-mails transacionais (opcional) | Sim |
| 17 | `RESEND_FROM_EMAIL` | Remetente dos e-mails Resend (opcional) | Não |

**Validações críticas obrigatórias:**
- `DOMAIN`: sem `https://`, sem IP — deve ser FQDN (ex: `crm.empresa.com.br`)
- `SUPABASE_DB_URL`: deve conter `pooler.supabase.com`. Se contiver `@db.` é IPv6
  — recuse e explique que deve usar o Session Pooler
- `OWNER_PASSWORD`: mínimo 8 caracteres

**Apresente um resumo** com campos secretos mascarados (`***`) e peça confirmação
antes de prosseguir para a instalação.

---

## Fase 4 — Preparação da VPS

### 4.1 — Firewall (CRÍTICO)

> ⚠️ **Sempre identifique a porta SSH ativa antes de ativar o firewall.**
> Ativar sem liberar a porta correta tranca você fora do servidor.

```bash
# Identifique a porta ativa
echo "Porta SSH: $(echo $SSH_CLIENT | awk '{print $3}')"

# Libere as portas (substitua PORTA_SSH pelo número real)
ufw allow PORTA_SSH/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 4.2 — Docker (se não estiver instalado)

```bash
curl -fsSL https://get.docker.com | sh
docker --version && docker compose version
```

### 4.3 — Clone do Repositório

```bash
git clone --depth 1 https://github.com/melgarafael/DeskcommCRM.git deskcommcrm
cd deskcommcrm
```

---

## Fase 5 — Geração do .env e Instalação

### 5.1 — Escreva o arquivo .env no servidor

Use `cat > .env << 'EOF'` para escrever o arquivo. Configure as permissões:

```bash
chmod 600 .env
```

O instalador gerará automaticamente os segredos internos (INTERNAL_SECRET,
WAHA_API_KEY, SRH_TOKEN, etc.) — você não precisa fornecê-los.

Para o mapeamento completo das variáveis, consulte
[`references/env_fields.md`](./references/env_fields.md).

### 5.2 — Execute o Instalador

```bash
bash hostgator-setup-kit/install.sh --yes
```

Fases automáticas do instalador:
1. Verificação de dependências
2. Verificação de DNS, schema Supabase, criação do admin
3. Download de imagens Docker, subida dos containers, emissão do SSL
4. Healthcheck de todos os serviços

**Tempo esperado:** 5–15 minutos (maior parte é download das imagens Docker ~1–2 GB).

O instalador é **idempotente**: se falhar, pode ser rodado novamente com segurança.

---

## Fase 6 — Verificação de Saúde

```bash
# Status dos containers
docker compose -f docker-compose.prod.yml ps

# Healthcheck HTTP
curl -sS -o /dev/null -w "%{http_code}" https://${DOMAIN}/api/health

# Logs de erro
docker compose -f docker-compose.prod.yml logs --tail=50 app
```

**Critérios de sucesso:**
- Containers `app`, `worker`, `waha`, `scheduler`, `redis`, `srh` com status `healthy`/`running`
- `https://<DOMAIN>` retorna HTTP 200
- SSL ativo (cadeado verde)

**Troubleshooting:**

| Sintoma | Ação |
|:--------|:-----|
| Container `app` em `Exit` | Verifique logs — geralmente chave Supabase errada |
| SSL não emitido | DNS ainda não propagou: `dig +short A <DOMAIN>` deve retornar o IP |
| `Network unreachable` | Connection string é IPv6. Corrija para Session Pooler |
| Porta 80/443 ocupada | Outro processo no servidor — reporte ao usuário |

---

## Fase 7 — Dossiê de Entrega

Ao final da instalação, gere um documento de entrega para o usuário enviar ao cliente:

```markdown
# DeskcommCRM — Credenciais de Acesso
**Cliente:** [Nome]  **Data:** [Data]

## Acesso
- **URL:** https://[DOMAIN]
- **E-mail admin:** [OWNER_EMAIL]
- **Senha:** entregue por canal seguro

## Próximos Passos
1. Acesse o CRM e faça login.
2. Configure o MFA com Google Authenticator ou Authy.
   Guarde os códigos de recuperação.
3. Conecte o WhatsApp: aponte o celular para o QR Code no onboarding.
4. Configure o Agente de IA em Agente de IA → Agentes.

## Manutenção
- Atualizar: `bash hostgator-setup-kit/update.sh`
- Backup: `bash hostgator-setup-kit/backup.sh`
- Saúde: `bash hostgator-setup-kit/healthcheck.sh`
```

---

## Regras de Segurança (Inegociáveis)

- Nunca salve senhas ou chaves em logs, histórico do shell ou artefatos desta conversa.
- Nunca execute `docker system prune`, `rm -rf` ou comandos destrutivos sem
  confirmação explícita do usuário.
- Nunca modifique containers ou serviços de outros projetos já no servidor.
- Se encontrar proxy reverso ativo (Traefik, nginx), pare e reporte ao usuário
  antes de prosseguir.
- A `SUPABASE_SERVICE_ROLE_KEY` vai apenas para o `.env` no servidor — jamais
  aparece em output, log ou artefato desta conversa.
