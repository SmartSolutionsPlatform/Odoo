# Smart Solutions Platform (SSP) - Odoo Connector

Este repositório contém o conector oficial da Smart Solutions Platform para Odoo, suportando múltiplas versões (17, 18 e 19).

## 📁 Estrutura do Projeto

- `addons/ssp_connector_versions/`: Contém os módulos específicos para cada versão do Odoo.
- `Makefile`: Script de automação para desenvolvimento e troca de versões.
- `addons/ssp_connector/`: Diretório de trabalho onde a versão ativa é vinculada (não deve ser commitado).

## 🚀 Como usar

O projeto utiliza um `Makefile` para facilitar a gestão das versões.

### 1. Iniciar Ambiente de Desenvolvimento
Para iniciar o ambiente com uma versão específica:

```bash
# Iniciar Odoo 18 (Padrão) + PostgreSQL + SSP
make start

# Iniciar Odoo 17
make start ODOO_VERSION=17

# Iniciar Odoo 19
make start ODOO_VERSION=19
```

### 2. Trocar de Versão
Se já estiver a correr e quiser trocar apenas o módulo:

```bash
make switch-version ODOO_VERSION=17
```

### 3. Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `make status` | Verifica o estado de todos os serviços |
| `make logs` | Mostra os logs do Odoo ativo |
| `make stop-all` | Para todos os containers e serviços |
| `make upgrade` | Reinicia o Odoo para forçar upgrade do módulo |

## 🛠️ Instalação em Produção

Para instalar em um servidor Odoo existente:

1. Aceda à pasta `addons/ssp_connector_versions/`.
2. Escolha a versão correspondente ao seu Odoo (`17.0`, `18.0` ou `19.0`).
3. Copie o conteúdo dessa pasta para o diretório de addons do seu servidor.
4. Certifique-se de que a pasta se chama `ssp_connector`.
5. No Odoo, ative o Modo de Desenvolvedor, vá a **Aplicações** > **Atualizar Lista de Aplicações**.
6. Procure por "Smart Solutions Platform Connector" e instale.

## ⚙️ Configuração

Depois de instalado, vá a **Configurações** > **SSP Connector** para configurar:
- **SSP URL**: URL da sua instância da plataforma.
- **SSO Token**: Token fornecido pela plataforma para acesso automático.

## 📄 Licença
LGPL-3

## 👨‍💻 Autor
Smart Solutions Platform
[https://smartsolutionsplatform.com](https://smartsolutionsplatform.com)
