# Smart Solutions Platform Connector - Odoo Module

## 📦 Versões Disponíveis

Este repositório contém o módulo SSP Connector para múltiplas versões do Odoo.

| Pasta | Versão Odoo | Status |
|-------|-------------|--------|
| `17.0/` | Odoo 17 | ✅ Pronto |
| `18.0/` | Odoo 18 | ✅ Pronto (Testado) |
| `19.0/` | Odoo 19 | 🔄 Preparado (baseado no 18) |

## 🚀 Funcionalidades

- **Dashboard Embutido**: Abre a plataforma SSP diretamente dentro do Odoo (iframe)
- **SSO Automático**: Login automático via token
- **Configuração Simples**: Interface para configurar URL e credenciais
- **Multi-empresa**: Uma configuração por empresa

## 📋 Diferenças entre Versões

### Odoo 17 vs 18/19
- **Views**: Odoo 17 usa `<tree>`, Odoo 18+ usa `<list>`
- **view_mode**: Odoo 17 usa `tree,form`, Odoo 18+ usa `list,form`

## 🛠️ Instalação

1. Copie a pasta da versão correspondente para o diretório `addons` do seu Odoo
2. Renomeie para `ssp_connector` (remover o sufixo da versão)
3. Atualize a lista de apps no Odoo
4. Instale o módulo "Smart Solutions Platform Connector"

## 📁 Estrutura do Módulo

```
ssp_connector/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── models/
│   ├── __init__.py
│   └── ssp_config.py
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       │   └── ssp_dashboard.js
│       └── xml/
│           └── ssp_dashboard.xml
└── views/
    ├── ssp_config_views.xml
    ├── ssp_dashboard_views.xml
    └── ssp_iframe_template.xml
```

## 🏪 Odoo Marketplace

Para publicar no Odoo Marketplace, use **branches Git** separadas:
- Branch `17.0` → Código da pasta `17.0/`
- Branch `18.0` → Código da pasta `18.0/`
- Branch `19.0` → Código da pasta `19.0/`

## 📄 Licença

LGPL-3

## 👨‍💻 Autor

Smart Solutions Platform
https://smartsolutionsplatform.com
