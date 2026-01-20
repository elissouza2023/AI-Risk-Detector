# Kaida AI Risk Detector – MVP Acadêmico

## Descrição
Kaida AI Risk Detector é um produto digital desenvolvido em Python para analisar textos destinados a ferramentas de IA generativa, identificando riscos de segurança da informação em ambientes corporativos. O foco principal é a **prevenção de vazamento de dados**, alinhando-se a princípios de segurança da informação, **LGPD** e **governança de IA**.

Este MVP acadêmico combina **regras estáticas** e técnicas de **Processamento de Linguagem Natural (NLP)** para classificar riscos de forma eficiente e explicável. É uma continuação do projeto **Kaida Search**, com ênfase em abordagem preventiva e produto funcional.

## Objetivos
- Detectar riscos em prompts de IA com prioridade na redução de **falsos negativos** em classes sensíveis
- Fornecer explicações claras e recomendações práticas de uso seguro
- Simular cenários reais de qualidade de dados corporativos (inconsistências, valores ausentes, variações de formato)

## Público-Alvo
- Profissionais de TI
- Empresas em fase inicial de adoção de IA
- Estudantes e equipes de segurança da informação

## Tipos de Riscos Detectados (Escopo do MVP)

### 1. Dados Pessoais (LGPD)
- CPF
- E-mail
- Telefone
- Nome próprio em contexto sensível
- Dados de saúde (CIDs, gravidez, Lúpus, câncer)
- Orientação sexual
- Registros criminais

### 2. Dados Corporativos Sensíveis
- Informações internas
- Dados de clientes
- Projetos internos / sigilosos
- Relatórios ou indicadores estratégicos
- Segredos sobre falência
- Margens de lucro agressivas
- Situações de "caixa 2"
- Espionagem industrial
- Planos de demissão em massa

### 3. Credenciais e Segredos
- Senhas
- Tokens
- API Keys
- Logins
- Chaves SSH / PGP
- URLs de banco de dados com credenciais embutidas
- Tokens de serviços (GitLab, AWS, Slack, Twilio, Discord)
- Segredos de infraestrutura (Jenkins, Azure AD)

**Qualquer outro tipo de risco está fora do escopo do MVP.**

## Abordagem Técnica
Arquitetura **híbrida simplificada** (sem deep learning treinado do zero):

### Camada 1 – Regras Estáticas
- Expressões regulares (**regex**) para padrões estruturados (CPF, e-mail, credenciais, etc.)
- Palavras-chave de risco
- Vantagens: alta explicabilidade e alertas imediatos

**Limitação**: fraco em contexto semântico e dados corporativos narrativos → necessidade da camada NLP.

### Camada 2 – Processamento de Linguagem Natural (NLP)
- Identificação de entidades nomeadas (**NER**)
- Classificação simples de texto
- Análise semântica básica
- Representação numérica das classes para classificação

**Resultados do modelo**:
- Acurácia geral: **89%**
- **Elevado recall** nas classes sensíveis (credenciais e dados pessoais) → prioridade em minimizar falsos negativos

## Dataset
- **Quantidade**: 1.200 prompts
- **Tipo**: sintético + manual
- **Características**:
  - Contém intencionalmente valores ausentes, inconsistências e variações de formato (ex.: coluna `date`)
  - Simula problemas reais de qualidade de dados corporativos
  - Inclui viés de **comportamento do usuário** (dilemas éticos, cenários de risco práticos)
- **Classes**:
  - `baixo_risco`
  - `dado_pessoal`
  - `dado_corporativo`
  - `credencial`
- **Processamento**: ETL dedicado → DataFrame enxuto apenas com colunas relevantes para classificação

## Interface do Usuário
Desenvolvida em **Streamlit** (arquivo principal: `app.py`)

Funcionalidades:
- Campo de texto para inserir o prompt
- Botão “Analisar Risco”
- Resultados exibidos:
  - Nível de risco (**Baixo / Médio / Alto**)
  - Tipo de risco identificado
  - Explicação resumida
  - Recomendação de uso seguro

## Funcionalidades Incluídas no MVP
- ✅ Análise de texto manual
- ✅ Classificação de risco
- ✅ Exibição de explicação
- ✅ Interface web simples
- ✅ Código modularizado

## Diferencial Acadêmico
- Alinhamento com **segurança da informação**, **LGPD** e **governança de IA**
- Abordagem **preventiva** de vazamento de dados
- Produto **funcional e demonstrável** (não apenas teórico)
- Continuidade com projeto anterior (**Kaida Search**)

## Deploy
https://ai-risk-detector.streamlit.app/

## Instalação e Execução Local
```bash
# 1. Clone o repositório
git clone https://github.com/elissouza2023/AI-Risk-Detector.git
cd kaida-ai-risk-detector

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute a aplicação
streamlit run app.py
