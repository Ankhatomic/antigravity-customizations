# Campos do .env — DeskcommCRM

Referência completa de todas as variáveis do `.env` para o instalador em modo `--yes`.

## Campos Obrigatórios (fornecidos pelo usuário)

| Variável | Formato esperado | Validação |
|:---------|:-----------------|:----------|
| `DOMAIN` | FQDN sem protocolo, ex: `crm.empresa.com.br` | Sem `https://`, sem IP, sem espaços |
| `ACME_EMAIL` | E-mail válido | Formato `usuario@dominio.tld` |
| `APP_IMAGE` | `ghcr.io/melgarafael/deskcommcrm:stable` | Instalador detecta automaticamente a versão |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxxxxxx.supabase.co` | Começa com `https://` e termina com `.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Começa com `eyJ` ou `sb_publishable_` | String longa, não secreta |
| `SUPABASE_SERVICE_ROLE_KEY` | String longa | Secreta — não ecoe na tela |
| `SUPABASE_DB_URL` | `postgresql://postgres.xxx:SENHA@aws-xxx.pooler.supabase.com:5432/postgres` | Deve conter `pooler.supabase.com` (Session Pooler IPv4, NÃO `@db.`) |
| `OWNER_EMAIL` | E-mail válido | Será o login do administrador |
| `OWNER_PASSWORD` | String | Mínimo 8 caracteres — secreta |

## Campos de IA (um dos três obrigatórios)

Apenas um dos três grupos abaixo é necessário:

**OpenRouter (recomendado para começar):**
```
OPENROUTER_API_KEY=sk-or-...
```

**Anthropic (Claude):**
```
ANTHROPIC_API_KEY=sk-ant-...
```

**OpenAI:**
```
OPENAI_API_KEY=sk-...
```

**Nota sobre OpenAI adicional:** Se o provedor escolhido NÃO for OpenAI, uma chave
`OPENAI_API_KEY` adicional opcional permite transcrição de áudio (WhatsApp) e
indexação de base de conhecimento com embeddings. Sem ela, tudo funciona exceto
essas duas features.

## Campos Opcionais

| Variável | Descrição | Padrão |
|:---------|:----------|:-------|
| `APP_NAME` | Nome que aparece na interface | `DeskcommCRM` |
| `APP_LOCALE` | Idioma: `pt-BR` ou `es` | `pt-BR` |
| `APP_ACCENT_HEX` | Cor da marca em hex ex `#7a5cd6` | Cor padrão do sistema |
| `SUPPORT_EMAIL` | E-mail de suporte visível ao cliente final | Vazio |
| `RESEND_API_KEY` | Chave Resend para e-mails transacionais | Vazio (e-mails desativados) |
| `RESEND_FROM_EMAIL` | Remetente verificado na Resend | Vazio |
| `SUPABASE_ACCESS_TOKEN` | Token da Management API do Supabase (configura links de e-mail) | Vazio — NÃO é salvo no .env |

## Segredos Gerados Automaticamente pelo Instalador

Estes campos são gerados com `openssl rand` — **não forneça valores manuais**:

- `INTERNAL_SECRET` — segredo interno entre serviços
- `INTERNAL_CRON_SECRET` — segredo do agendador
- `WAHA_API_KEY` — chave do WhatsApp Engine
- `WAHA_API_KEY_SHA512` — hash SHA512 da chave WAHA
- `WAHA_HMAC_SECRET` — assinatura dos webhooks do WhatsApp
- `SRH_TOKEN` — token do Redis HTTP bridge
- `CPF_ENCRYPTION_KEY` — criptografia de dados sensíveis LGPD
- `AI_CRED_AES_KEY` — criptografia das chaves de IA no banco
- `IMPERSONATE_COOKIE_SECRET` — segurança de sessão
- `LGPD_SIGNING_KEY` — assinatura de tokens de esquecimento LGPD
- `NUVEMSHOP_OAUTH_ENCRYPTION_KEY` — OAuth da Nuvemshop
- `WAHA_BYO_ENCRYPTION_KEY` — criptografia WAHA
- `WACALLS_ADMIN_USER` / `WACALLS_ADMIN_PASSWORD` / `WACALLS_API_TOKEN` — módulo de voz (inativo por padrão)

## Derivados (calculados pelo instalador a partir do DOMAIN)

- `NEXT_PUBLIC_APP_URL` = `https://${DOMAIN}`
- `NEXT_PUBLIC_ADMIN_URL` = `https://${DOMAIN}`
- `UPSTASH_REDIS_REST_TOKEN` = mesmo valor que `SRH_TOKEN`

## Exemplo de .env Mínimo (para teste)

```dotenv
DOMAIN="crm.cliente.com.br"
ACME_EMAIL="seu@email.com"
NEXT_PUBLIC_SUPABASE_URL="https://abcdef.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_DB_URL="postgresql://postgres.abcdef:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
OPENROUTER_API_KEY="sk-or-v1-..."
OWNER_EMAIL="admin@cliente.com.br"
OWNER_PASSWORD="senhaSegura123"
APP_NAME="CRM da Empresa"
APP_LOCALE="1"
```
