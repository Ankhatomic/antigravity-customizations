---
name: prompt-engineer
description: >-
  Especialista em engenharia e arquitetura de prompts segundo as práticas de
  2026, com foco em Context Engineering, gestão de tokens e design de sistemas
  cognitivos. Ative esta skill quando o usuário pedir para criar, melhorar,
  refatorar ou auditar um prompt, instrução de sistema, ou workflow agentico.
  Também ative em pedidos como: "crie um prompt para meu agente", "melhore esse
  system prompt", "reduza os tokens desse prompt", "estruture esse prompt em
  XML", "crie um prompt de sistema para X", "esse prompt está custando muito",
  "quero que o agente faça Y de forma confiável", "audita esse prompt", ou
  qualquer variação de projetar, otimizar ou estruturar instruções para LLMs.
  Use esta skill mesmo quando o pedido for vago, como "me ajuda a falar com a
  IA de forma melhor" ou "como faço o agente funcionar direito".
---

# Prompt Engineer — Context Engineering Edition (2026)

Skill de criação, refatoração, auditoria e otimização de prompts segundo os
padrões de 2026. O paradigma evoluiu de "escrever prompts" para **Context
Engineering**: projetar o pipeline completo que alimenta o modelo com a
informação certa, na estrutura certa, no momento certo.

> **Referências detalhadas (carregar quando necessário):**
> - Técnicas avançadas e exemplos → [`references/techniques.md`](./references/techniques.md)
> - Templates de prompts por tipo de tarefa → [`references/templates.md`](./references/templates.md)

---

## O Paradigma de 2026: Context Engineering

> "O maior modo de falha em produção não é um prompt mal escrito.
> É uma montagem de contexto ruim." — Padrão de mercado 2026

**A analogia do SO:** Trate o LLM como a CPU e a janela de contexto como RAM.
Seu papel é o do sistema operacional: garantir que o código e os dados certos
estejam na memória de trabalho para cada tarefa específica.

### As 4 Alavancas de Contexto
| Alavanca | O que é | Quando usar |
| :--- | :--- | :--- |
| **Write** | Persistir estado externamente (arquivos, memória) | Agents de longa duração |
| **Select** | Recuperar só o relevante (RAG, busca semântica) | Bases de conhecimento grandes |
| **Compress** | Resumir e compactar histórico | Conversas longas, loops agenticos |
| **Isolate** | Contextos separados por subtarefa | Workflows multi-agente |

---

## Fase 1 — Diagnóstico

Antes de criar ou refatorar qualquer prompt, diagnostique o cenário:

1. **Qual o objetivo do prompt?**
   - Tarefa única (one-shot) ou workflow agentico recorrente?
   - Output determinístico (JSON, código) ou criativo (texto, análise)?

2. **Qual o custo de falha?**
   - Baixo (chat pessoal) → pode ser mais liberal
   - Alto (produção, dados de cliente) → exige contrato rígido + modos de falha

3. **Qual o perfil de token?**
   - Estimar: `tokens_de_entrada x frequência = custo mensal`
   - Identificar quais seções do prompt são estáticas (cacheáveis) vs. dinâmicas

4. **Qual modelo será usado?**
   - Frontier (Gemini, GPT-4o, Claude): suporta raciocínio complexo
   - Compacto (Flash, Haiku, mini): precisa de prompts mais diretos e estruturados
   - Rotear tarefas simples para modelos menores é a maior alavanca de custo

---

## Fase 2 — A Anatomia do Prompt Moderno (Framework "Contrato")

Um prompt de alta performance em 2026 é um **contrato**, não uma conversa.
Estrutura recomendada em XML semântico:

```xml
<system>
  <role>
    <!-- Papel específico e limitado. Evite personas exageradas. -->
    <!-- Ex: "Você é um analisador de dados B2B especializado em..." -->
  </role>

  <context>
    <!-- Informações estáticas que definem o ambiente de execução. -->
    <!-- Colocar PRIMEIRO para maximizar o hit de cache de prompt. -->
    <!-- Inclua: quem é o usuário, qual o produto, quais as regras do negócio. -->
  </context>

  <instructions>
    <!-- O contrato central. Use listas numeradas para passos sequenciais. -->
    <!-- Use linguagem imperativa direta: "Faça X", não "Você deve fazer X". -->
    <!-- Máximo 7±2 itens por nível de lista para preservar atenção do modelo. -->
  </instructions>

  <constraints>
    <!-- O que NUNCA fazer. Seja explícito nos limites. -->
    <!-- Ex: "Nunca assuma dados que não foram fornecidos explicitamente." -->
    <!-- Ex: "Nunca produza outputs fora do schema JSON abaixo." -->
  </constraints>

  <output_contract>
    <!-- Schema exato do output esperado. -->
    <!-- Para JSON: inclua o schema com tipos e exemplos. -->
    <!-- Para texto: inclua template com placeholders. -->
  </output_contract>

  <failure_modes>
    <!-- O que fazer quando algo der errado. CRÍTICO para agentes. -->
    <!-- Ex: "Se a informação necessária não estiver disponível, retorne {...}" -->
    <!-- Ex: "Se o usuário pedir algo fora do escopo, responda: '...'" -->
  </failure_modes>
</system>
```

### Regras de Ouro da Estrutura
- **Estático primeiro:** Coloque `<context>` e `<role>` no topo — são cacheáveis.
- **Dinâmico por último:** Dados variáveis (input do usuário, dados recuperados) vão no final.
- **Sem walls of text:** Quebre em seções XML nomeadas. Modelos leem melhor limites explícitos.
- **Sem theatrical prompting:** "Aja como se sua vida dependesse disso" não funciona mais. Clareza estrutural supera drama emocional.

---

## Fase 3 — Gestão de Tokens (Token Budget Management)

### Auditoria de Token em 3 Camadas

**Camada 1 — Estático vs. Dinâmico**
```
Mapa de token do prompt:
├── ESTÁTICO (cacheável)
│   ├── Role            ~50 tokens
│   ├── Context base    ~200 tokens
│   ├── Instructions    ~300 tokens
│   └── Constraints     ~100 tokens
│       Subtotal: ~650 tokens → candidatos a prompt caching
└── DINÂMICO (por chamada)
    ├── Dados do usuário   ~variável
    ├── Histórico          ~variável (comprimir agressivamente!)
    └── RAG chunks         ~variável (limitar a top-3 por padrão)
```

**Camada 2 — Estratégias de Compressão**
| Técnica | Redução Típica | Quando Usar |
| :--- | :--- | :--- |
| Remover instruções redundantes | 10–20% | Sempre |
| Substituir exemplos por schema | 30–50% | Outputs estruturados |
| Compactar histórico de conversa | 40–70% | Após 5+ turnos |
| RAG em vez de contexto inteiro | 60–80% | Bases de conhecimento |
| Roteamento para modelo menor | 80–95% custo | Tarefas simples |

**Camada 3 — Controle de Output**
- Sempre defina `max_tokens` ou instrua no prompt: `"Sua resposta DEVE ter no máximo X palavras."`
- Para outputs estruturados, use `response_format: json_schema` quando a API suportar.
- Evite pedir `"Explique detalhadamente"` sem necessidade — cada token de output tem custo.

### Checklist de Eficiência de Token
- [ ] Seções estáticas identificadas e marcadas para caching
- [ ] Histórico de conversa comprimido após N turnos (definir N)
- [ ] Exemplos few-shot: máximo 3 (1–3 é o sweet spot em 2026)
- [ ] Instrução de limite de output presente (`max X palavras/tokens`)
- [ ] RAG configurado para retornar top-K chunks (K menor ou igual a 5)
- [ ] Tarefa pode ser roteada para modelo menor? (sim/não)

---

## Fase 4 — Técnicas Avançadas (Selecionar por Caso)

Carregue [`references/techniques.md`](./references/techniques.md) para detalhes completos.
Resumo de decisão rápida:

| Cenário | Técnica Recomendada |
| :--- | :--- |
| Raciocínio complexo | Chain-of-Thought (CoT) com `<thinking>` explícito |
| Output de formato específico | Few-Shot (1–3 exemplos) + Output Schema |
| Agente com múltiplos passos | ReAct Pattern (Reason → Act → Observe) |
| Alta variabilidade no output | Self-Consistency (múltiplas amostras + votação) |
| Prompt longo e recorrente | Prompt Caching (prefixo estático no topo) |
| Múltiplos agentes | Orchestrator-Workers com contextos isolados |

---

## Fase 5 — Entrega e Formato

### Para Prompts Novos
Sempre entregue:
1. **O prompt completo** em bloco de código com a estrutura XML
2. **Estimativa de token** (input estático + dinâmico médio estimado)
3. **Estratégias de cache** identificadas (o que pode ser prefixo fixo)
4. **Modo de falha** documentado (o que o modelo deve fazer quando não sabe)

### Para Refatorações
Sempre entregue:
1. **Diff comentado** — o que mudou e por quê
2. **Estimativa de redução de tokens** (antes vs. depois)
3. **Alerta de comportamento:** se a refatoração pode alterar o comportamento, sinalize

### Para Auditorias
Gere um relatório estruturado:
```
## Auditoria de Prompt
### Score Geral: X/10

| Dimensão          | Score | Problemas Encontrados |
|:------------------|:------|:----------------------|
| Clareza           | X/10  | ...                   |
| Eficiência Token  | X/10  | ...                   |
| Estrutura         | X/10  | ...                   |
| Modos de Falha    | X/10  | ...                   |
| Cacheabilidade    | X/10  | ...                   |

### Top 3 Melhorias Prioritárias
1. ...
2. ...
3. ...
```

---

## Armadilhas Comuns (Anti-Patterns de 2026)

| Anti-Pattern | Por Que Falha | Solução |
| :--- | :--- | :--- |
| **Theatrical prompting** | "Aja como se sua vida dependesse disso" não produz ganho mensurável | Use estrutura e exemplos |
| **Context stuffing** | Encher a janela não é igual a melhor performance; causa "lost in the middle" | Selecione e comprima |
| **Sem modos de falha** | Agente trava ou alucina quando encontra input inesperado | Defina `<failure_modes>` explícito |
| **Exemplos demais** | Mais de 5 exemplos few-shot geralmente degradam performance | Limite a 1–3 exemplos |
| **Histórico sem compressão** | Custo cresce exponencialmente em agents | Compactar a cada N turnos |
| **Prompt monolítico** | Uma instrução de 2.000 tokens sem estrutura | Dividir em seções XML |
| **Ignorar roteamento** | Usar frontier model para parsing simples | Definir critério de roteamento |
