# Técnicas Avançadas de Prompt Engineering (2026)

Referência completa de técnicas. Carregue apenas quando a Fase 4 do SKILL.md indicar necessidade.

---

## 1. Chain-of-Thought (CoT)

Força o modelo a externalizar o raciocínio antes de responder. Reduz alucinações em tarefas que exigem múltiplos passos lógicos.

**Quando usar:** Cálculos, análises multi-etapa, diagnósticos, tomada de decisão com critérios.

**Template:**
```xml
<instructions>
  Antes de responder, raciocine passo a passo dentro de <thinking></thinking>.
  Sua resposta final deve aparecer APENAS dentro de <answer></answer>.
  Não exponha seu <thinking> ao usuário final.
</instructions>
```

**Variante — Zero-Shot CoT:** Adicione ao final do prompt: `"Raciocine passo a passo."` — simples e eficaz para modelos frontier.

**Custo:** +20–40% tokens de output. Justificável apenas quando a qualidade do raciocínio é crítica.

---

## 2. Few-Shot Prompting

Fornece 1–3 exemplos de input/output antes da tarefa real. É a forma mais confiável de especificar formato e tom sem explicações longas.

**Quando usar:** Outputs com formato muito específico, extração de dados, classificação, geração de texto com tom padronizado.

**Sweet spot em 2026:** 1–3 exemplos. Mais do que isso raramente melhora e frequentemente degrada.

**Template:**
```xml
<examples>
  <example>
    <input>Cliente reclamou do prazo de entrega</input>
    <output>{"categoria": "reclamacao", "urgencia": "alta", "departamento": "logistica"}</output>
  </example>
  <example>
    <input>Quero saber o horário de funcionamento</input>
    <output>{"categoria": "informacao", "urgencia": "baixa", "departamento": "atendimento"}</output>
  </example>
</examples>
```

---

## 3. ReAct Pattern (Reason + Act)

Padrão padrão para agentes com ferramentas. O modelo alterna entre raciocinar sobre o próximo passo e executar uma ação, observando o resultado antes de continuar.

**Quando usar:** Agentes que usam ferramentas, workflows de múltiplos passos com decisões condicionais.

**Template de instrução:**
```xml
<instructions>
  Execute as tarefas seguindo o ciclo: Pensar → Agir → Observar → Repetir.

  Para cada ciclo:
  1. PENSAR: Analise o estado atual e decida a próxima ação necessária.
  2. AGIR: Execute exatamente uma ação usando as ferramentas disponíveis.
  3. OBSERVAR: Leia o resultado da ação antes de continuar.
  4. Repita até o objetivo ser alcançado ou até identificar que é impossível.

  Quando a tarefa estiver completa, produza o output final dentro de <final_answer></final_answer>.
</instructions>
```

---

## 4. Self-Consistency

Gera múltiplas respostas independentes para o mesmo prompt e seleciona por votação majoritária (ou pelo agente orquestrador). Aumenta confiabilidade em outputs com alta variância.

**Quando usar:** Classificações críticas, análises onde um erro é caro, outputs onde a consistência é mais importante que a velocidade.

**Custo:** Multiplica o custo de token pelo número de amostras. Use seletivamente.

**Implementação:** Envie o mesmo prompt N vezes com `temperature > 0`, depois agregue os resultados programaticamente.

---

## 5. Prompt Caching

A técnica de maior ROI para prompts recorrentes. A parte estática do prompt (prefixo) é armazenada em cache pelo provedor, eliminando o custo de reprocessamento.

**Suporte por provedor (2026):**
| Provedor | Desconto de Cache | Ativação |
| :--- | :--- | :--- |
| Anthropic (Claude) | 90% nos tokens de cache | Automático após 1024 tokens estáticos |
| OpenAI (GPT) | 50% nos tokens de cache | Automático após 1024 tokens estáticos |
| Google (Gemini) | 75% nos tokens de cache | API `context_cache` explícita |

**Regra de ouro:** Coloque TUDO que não muda (role, context, instructions, tools) no início do prompt. O input do usuário vai no final. Qualquer modificação no meio quebra o cache.

---

## 6. Orchestrator-Workers (Multi-Agente)

Padrão para tarefas complexas que exigem múltiplos agentes especializados.

```
Orquestrador
├── Decompõe a tarefa em subtarefas
├── Delega para Workers especializados
└── Agrega e valida os resultados

Worker A (contexto isolado)    Worker B (contexto isolado)
└── Recebe apenas sua subtarefa └── Recebe apenas sua subtarefa
```

**Regra de isolamento:** Cada Worker deve receber APENAS o contexto da sua subtarefa. Não compartilhe contexto completo entre Workers — isso é context bloat.

**Template de instrução para o Orquestrador:**
```xml
<role>
  Você é um orquestrador. Sua função é APENAS planejar e delegar.
  Você não executa tarefas diretamente.
</role>
<instructions>
  1. Analise o objetivo e decomponha em 2–5 subtarefas independentes.
  2. Para cada subtarefa, produza: {"subtarefa": "...", "input": "...", "worker": "..."}
  3. Após receber todos os outputs dos Workers, agregue e valide a consistência.
  4. Produza o output final consolidado.
</instructions>
```

---

## 7. Controle de Alucinação

Técnicas específicas para reduzir fabricação de informações:

1. **Âncora de contexto:** Instrua o modelo a só usar informações fornecidas explicitamente.
   ```xml
   <constraints>
     Responda APENAS com base nas informações dentro de <context></context>.
     Se a resposta não puder ser encontrada no contexto fornecido, responda: "Não tenho essa informação."
     Nunca complemente com conhecimento externo.
   </constraints>
   ```

2. **Citação obrigatória:** Exija que o modelo cite a fonte de cada afirmação.
   ```xml
   <output_contract>
     Cada afirmação factual deve ser seguida de [Fonte: trecho exato do contexto].
   </output_contract>
   ```

3. **Calibração de confiança:** Instrua o modelo a reportar quando não tem certeza.
   ```xml
   <constraints>
     Quando sua confiança for baixa, use: "Não tenho certeza, mas..." antes da afirmação.
     Prefira admitir incerteza a fabricar uma resposta.
   </constraints>
   ```
