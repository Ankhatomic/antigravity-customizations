# 🛠️ Skill Creator (Antigravity Edition)

Uma meta-skill avançada para o **Google Antigravity IDE** projetada para criar novas skills do zero, refatorar skills existentes, conduzir entrevistas guiadas, executar benchmarks automatizados (*evals*) e otimizar descrições de ativação para prevenir *undertriggering*.

---

## ✨ O que esta Skill faz

1. **Entrevista Guiada & Pesquisa:** Conduz o usuário pelo entendimento do problema, identificação de edge cases e formato esperado de saída.
2. **Arquitetura de Progressive Disclosure:** Garante que o `SKILL.md` principal fique enxuto (< 500 linhas) e distribui documentações pesadas para `references/` e códigos repetitivos para `scripts/`.
3. **Avaliações A/B Simultâneas (*Evals*):** Executa testes comparando a saída da IA **com a skill** vs. **sem a skill** (baseline).
4. **Relatório de Benchmark:** Gera relatório detalhado com taxa de sucesso das assertions, tempos de execução e tokens consumidos.
5. **Otimizador de Gatilhos (*Trigger Optimizer*):** Analisa e calibra a `description` da skill para garantir que a IA ative a ferramenta mesmo em pedidos indiretos.

---

## 🚀 Como Instalar no seu Antigravity

### Instalação Global (Disponível em todos os projetos)
```bash
# 1. Clone o repositório
git clone https://github.com/Ankhatomic/antigravity-customizations.git /tmp/antigravity-customizations

# 2. Copie para sua pasta global
mkdir -p ~/.gemini/config/skills
cp -r /tmp/antigravity-customizations/skills/skill-creator ~/.gemini/config/skills/
```

### Instalação no Projeto Atual (Workspace)
```bash
mkdir -p .agents/skills
cp -r /caminho/para/skill-creator .agents/skills/
```

---

## 💬 Exemplos de Uso

Basta pedir no chat do Antigravity usando comandos ou linguagem natural:

* `"/skill-creator"`
* *"Quero criar uma skill para formatar commits do Git"*
* *"Transforme esse fluxo da conversa em uma skill reutilizável"*
* *"Otimize a descrição da minha skill para ela ser ativada mais facilmente"*
* *"Crie testes automatizados (evals) para a minha skill"*

---

## 📁 Estrutura de Arquivos

```
skill-creator/
├── SKILL.md                          # Instruções principais da meta-skill
├── README.md                         # Guia de instalação e documentação
├── scripts/
│   ├── run_eval.py                   # Runner de evals e analisador de gatilhos
│   └── generate_review.py            # Gerador de relatório comparativo Markdown
├── references/
│   ├── schemas.md                    # Schema do evals.json e tipos de assertion
│   └── writing_guide.md              # Guia avançado de redação de skills
└── examples/
    └── example_skill/SKILL.md        # Exemplo prático de skill bem estruturada
```

---

## 📄 Licença

Distribuído sob a licença [MIT](../../LICENSE).
