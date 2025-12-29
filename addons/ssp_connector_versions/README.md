# Smart Solutions Platform Connector - Odoo Module

## 📦 Available Versions

This repository contains the SSP Connector module for multiple Odoo versions.

| Folder | Odoo Version | Status |
|-------|-------------|--------|
| `17.0/` | Odoo 17 | ✅ Ready |
| `18.0/` | Odoo 18 | ✅ Ready (Tested) |
| `19.0/` | Odoo 19 | 🔄 Prepared (based on 18) |

## 🚀 Features

- **Embedded Dashboard**: Opens the SSP platform directly inside Odoo (iframe)
- **Automatic SSO**: Automatic login via token
- **Simple Configuration**: Interface to configure URL and credentials
- **Multi-company**: One configuration per company

## 📋 Differences Between Versions

### Odoo 17 vs 18/19
- **Views**: Odoo 17 uses `<tree>`, Odoo 18+ uses `<list>`
- **view_mode**: Odoo 17 uses `tree,form`, Odoo 18+ uses `list,form`

## 🛠️ Installation

1. Copy the corresponding version folder to your Odoo `addons` directory
2. Rename it to `ssp_connector` (remove the version suffix)
3. Update the app list in Odoo
4. Install the "Smart Solutions Platform Connector" module

## 📁 Module Structure

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

To publish on the Odoo Marketplace, use separate **Git branches**:
- Branch `17.0` → Code from folder `17.0/`
- Branch `18.0` → Code from folder `18.0/`
- Branch `19.0` → Code from folder `19.0/`

## 📄 License

LGPL-3

## 👨‍💻 Author

Smart Solutions Platform
https://smartsolutionsplatform.com
