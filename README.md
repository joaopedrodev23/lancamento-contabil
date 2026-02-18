# Microservico de Lancamento Contabil (Journal Entry)

## Objetivo
Este microservico recebe um JSON do ServiceNow, obtem um token OAuth2 (client_credentials) no SAP BTP e chama uma API externa do SAP via Connectivity. Ele devolve o status e o payload retornados pelo SAP.
Observacao: o servico atua como proxy e nao valida o esquema completo do payload. Campos adicionais sao aceitos e o contrato deve seguir a especificacao oficial do SAP.

## Estrutura rapida
- `app/main.py`: bootstrap da aplicacao FastAPI
- `app/api/routes.py`: endpoint `/journal-entry`
- `app/services/auth_service.py`: token OAuth2 no SAP BTP
- `app/services/sap_service.py`: envio do Journal Entry ao SAP
- `app/services/attachment_service.py`: regras de attachment (PDF)
- `app/integrations/sap_attachment_client.py`: chamada HTTP do attachment
- `app/models/`: modelos de entrada e saida

## Fluxo de autenticacao
1. ServiceNow envia o payload para POST /journal-entry
2. O servico chama o endpoint OAuth2 do SAP BTP com client_credentials
3. O token retornado eh usado para chamar a API do SAP
4. Se o Journal Entry for bem-sucedido e o attachment estiver habilitado, o servico envia o PDF para o endpoint AttachmentDocument
5. A resposta do SAP para o Journal Entry e o status do envio de attachment sao retornados ao caller

## Como rodar localmente
1. Crie e ative um ambiente virtual
2. Instale as dependencias
3. Defina as variaveis de ambiente
4. Inicie o servidor

Exemplo:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.lock
Copy-Item .env.example .env
# edite o .env com suas credenciais reais
uvicorn app.main:app --reload
```

Se voce preferir instalar com versoes flexiveis:
```powershell
pip install -r requirements.txt
```

## Reprodutibilidade
- Versao recomendada do Python: 3.12.10 (ver `.python-version`)
- Dependencias fixadas em `requirements.lock`

## Rodar sem credenciais (modo mock)
Para desenvolver localmente sem credenciais reais do SAP, habilite o modo mock no `.env`:
```dotenv
USE_MOCK_AUTH=true
USE_MOCK_SAP=true
```
Neste modo:
- O token eh simulado
- A resposta do SAP eh simulada e devolve o payload de entrada em `echo`
- Se attachment estiver habilitado, o envio de attachment tambem eh simulado

Dica: se voce tiver `environment=dev` (minusculo) no `.env`, troque para `ENVIRONMENT=dev`.

## Variaveis de ambiente
- `SAP_OAUTH_URL`: URL do token OAuth2 (BTP)
- `SAP_CLIENT_ID`: client_id do OAuth2
- `SAP_CLIENT_SECRET`: client_secret do OAuth2
- `SAP_API_URL`: URL da API do SAP
- `SAP_ATTACHMENT_URL`: URL da API de AttachmentDocument via Connectivity
- `HTTP_TIMEOUT_SECONDS`: timeout das chamadas HTTP (padrao 15)
- `ENVIRONMENT`: dev | hml | prod (padrao dev)
- `LOG_LEVEL`: nivel do log (padrao INFO)
- `USE_MOCK_AUTH`: habilita token mock (padrao false)
- `USE_MOCK_SAP`: habilita resposta mock do SAP (padrao false)
- `ENABLE_ATTACHMENT`: habilita envio opcional de attachment apos sucesso do Journal Entry (padrao false)

## Attachment opcional (PDF base64)
Quando `ENABLE_ATTACHMENT=true`, o servico tenta enviar attachment apos o sucesso do Journal Entry.

Campos aceitos no payload de entrada para conteudo PDF:
- `AttachmentContent`
- `AttachmentPdf`
- `pdf_content`
- `pdf`

Regras:
- Se nao houver PDF no payload, o envio de attachment e ignorado.
- Se houver erro no envio de attachment, o erro e logado e a resposta do Journal Entry ainda e retornada.
- O status do envio de attachment e incluido na resposta da API.

## Exemplo de requisicao
Observacao: os campos sao ilustrativos e podem variar conforme o contrato SAP.
```json
{
  "OriginalReferenceDocumentType": "BKPFF",
  "OriginalReferenceDocument": "REF123456",
  "OriginalReferenceDocumentLogicalSystem": "ServiceNow",
  "BusinessTransactionType": "RFBU",
  "AccountingDocumentType": "SA",
  "DocumentReferenceID": "DOC123456789012",
  "DocumentHeaderText": "Lancamento ServiceNow",
  "CreatedByUser": "SERVICENOW_USR",
  "CompanyCode": "1000",
  "DocumentDate": "2026-01-26",
  "PostingDate": "2026-01-26",
  "itens": [
    {
      "ReferenceDocumentItem": "1",
      "GLAccount": "1234567890",
      "AmountInTransactionCurrency": "2366.57",
      "DebitCreditCode": 1,
      "TransactionCurrency": "BRL",
      "DocumentItemText": "S",
      "AssignmentReference": "Item de debito",
      "TradingPartner": "ATRIB001",
      "ValueDate": "2026-01-26",
      "ProfitCenter": "PC001",
      "CostCenter": "CC001"
    },
    {
      "ReferenceDocumentItem": "2",
      "GLAccount": "0987654321",
      "AmountInTransactionCurrency": "2366.57",
      "DebitCreditCode": -1,
      "TransactionCurrency": "BRL",
      "DocumentItemText": "H",
      "AssignmentReference": "Item de credito",
      "TradingPartner": "ATRIB002",
      "ValueDate": "2026-01-26",
      "ProfitCenter": "PC002",
      "CostCenter": "CC002"
    }
  ]
}
```

## Resposta
O servico retorna o status do SAP, o payload retornado pelo SAP e o resultado do envio de attachment.
Possiveis status de `attachment.status`:
- `disabled`: attachment desabilitado
- `not_attempted`: Journal Entry falhou ou nao foi processado
- `skipped_no_pdf`: attachment habilitado, mas sem PDF no payload
- `sent`: attachment enviado com sucesso
- `failed`: falha no envio do attachment
- `mock`: simulacao de attachment (modo mock)

Exemplo:
```json
{
  "sap_status_code": 201,
  "sap_payload": { "exemplo": "conteudo retornado pelo SAP" },
  "attachment": {
    "status": "sent",
    "status_code": null,
    "error": null,
    "response": { "exemplo": "conteudo retornado pelo SAP" }
  }
}
```
