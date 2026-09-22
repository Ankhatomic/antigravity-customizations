#!/usr/bin/env bash
# preflight.sh — Diagnóstico de pré-voo para instalação do DeskcommCRM
# Execute na VPS do cliente via SSH. Apenas leitura — não altera nada.
# Uso: bash preflight.sh

set -euo pipefail

ok()   { printf '  ✅ %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }
fail() { printf '  ❌ %s\n' "$*"; }
sep()  { printf '\n─────────────────────────────────────\n'; }

echo ""
echo "======================================"
echo " DeskcommCRM — Pré-voo de Instalação"
echo "======================================"

sep
echo "Sistema Operacional:"
cat /etc/os-release | grep -E '^(NAME|VERSION)=' || uname -a

sep
echo "Memória RAM:"
free -h
RAM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
if [ "$RAM_KB" -lt 3500000 ]; then
  warn "RAM abaixo de 3.5 GB ($((RAM_KB/1024)) MB). Pode ser instável. Recomendado: 4 GB."
else
  ok "RAM suficiente: $((RAM_KB/1024)) MB"
fi

sep
echo "Espaço em disco (/):"
df -h /
DISCO_LIVRE=$(df / | awk 'NR==2 {print $4}' | sed 's/G//')
echo "  Livre: ${DISCO_LIVRE}G"

sep
echo "Docker e Compose:"
if docker --version 2>/dev/null; then
  ok "Docker instalado"
else
  warn "Docker NÃO instalado — será instalado automaticamente"
fi

if docker compose version 2>/dev/null; then
  ok "Docker Compose instalado"
else
  warn "Docker Compose não encontrado — será instalado com Docker"
fi

sep
echo "Portas 80 e 443:"
PORTA_80=$(ss -tulpn 2>/dev/null | grep ':80 ' || echo "")
PORTA_443=$(ss -tulpn 2>/dev/null | grep ':443 ' || echo "")
if [ -z "$PORTA_80" ]; then
  ok "Porta 80: livre"
else
  fail "Porta 80 OCUPADA: $PORTA_80"
fi
if [ -z "$PORTA_443" ]; then
  ok "Porta 443: livre"
else
  fail "Porta 443 OCUPADA: $PORTA_443"
fi

sep
echo "Porta SSH desta sessão (IMPORTANTE para o firewall):"
PORTA_SSH=$(echo "${SSH_CLIENT:-desconhecida}" | awk '{print $3}')
if [ "$PORTA_SSH" = "desconhecida" ]; then
  warn "Não foi possível detectar a porta SSH automaticamente. Verifique manualmente."
  warn "Use: ss -tnp | grep sshd"
else
  ok "Porta SSH: $PORTA_SSH — use este valor ao configurar ufw"
fi

sep
echo "Git:"
if git --version 2>/dev/null; then
  ok "Git instalado"
else
  warn "Git não instalado — pode ser necessário instalar"
fi

sep
echo ""
echo "Pré-voo concluído. Nenhuma alteração foi feita."
echo "Compartilhe este relatório com o agente para continuar."
