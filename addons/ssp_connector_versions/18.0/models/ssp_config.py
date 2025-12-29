# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class SspConfig(models.Model):
    _name = 'ssp.config'
    _description = 'Smart Solutions Platform Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        readonly=True
    )
    
    admin_name = fields.Char(
        string='Admin Name',
        help='Your full name'
    )
    
    admin_email = fields.Char(
        string='Admin Email',
        required=True,
        help='Email for SSP account (will be your login)'
    )
    
    admin_password = fields.Char(
        string='Password',
        help='Password for SSP account (min 8 characters)'
    )
    
    api_key = fields.Char(
        string='API Key',
        readonly=True,
        help='Auto-generated after registration'
    )
    
    account_id = fields.Char(
        string='Account ID',
        readonly=True,
        help='Your SSP Account ID'
    )
    
    platform_url = fields.Char(
        string='Platform URL',
        default='https://smartsolutionsplatform.com',
        required=True,
        help='Smart Solutions Platform URL'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    state = fields.Selection([
        ('draft', 'Not Configured'),
        ('connected', 'Connected'),
        ('error', 'Connection Error')
    ], string='Status', default='draft', readonly=True)
    
    last_sync = fields.Datetime(
        string='Last Synchronization',
        readonly=True
    )
    
    # SQL Constraint: uma configuração por empresa
    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 
         'Only one configuration per company is allowed!')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para registrar automaticamente na SSP"""
        records = super(SspConfig, self).create(vals_list)
        
        for record in records:
            # Se tem password, fazer auto-registro na SSP
            if record.admin_password:
                try:
                    record._register_on_ssp()
                except Exception as e:
                    _logger.error(f'Failed to auto-register on SSP: {str(e)}')
                    # Não falha a criação, mas marca como erro
                    record.state = 'error'
        
        return records
    
    def _register_on_ssp(self):
        """Registra automaticamente a empresa na SSP"""
        self.ensure_one()
        
        if not self.admin_password:
            raise Exception('Password is required for registration')
        
        # Obter dados do Odoo atual
        odoo_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        odoo_database = self.env.cr.dbname
        odoo_username = self.env.user.login
        
        # Dados para enviar à SSP
        payload = {
            'company_name': self.company_id.name,
            'admin_email': self.admin_email,
            'admin_name': self.admin_name or self.env.user.name,
            'password': self.admin_password,
            'odoo_url': odoo_url,
            'odoo_database': odoo_database,
            'odoo_username': odoo_username,
            'odoo_api_key': self.admin_password,  # Usar a mesma password temporariamente
            'country': self.company_id.country_id.code if self.company_id.country_id else None
        }
        
        _logger.info(f'Registering on SSP: {payload["company_name"]} ({payload["admin_email"]})')
        
        try:
            response = requests.post(
                f'{self.platform_url}/api/odoo/register',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    # Atualizar com dados retornados
                    self.write({
                        'account_id': str(data.get('account_id')),
                        'api_key': data.get('sso_token', ''),  # 🆕 Guardar token SSO
                        'state': 'connected',
                        'last_sync': fields.Datetime.now()
                    })
                    
                    _logger.info(f'Successfully registered on SSP: Account ID {self.account_id}')
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success!',
                            'message': f'Account created on SSP! Account ID: {self.account_id}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    raise Exception(data.get('message', 'Unknown error'))
            else:
                raise Exception(f'HTTP {response.status_code}: {response.text}')
                
        except requests.exceptions.RequestException as e:
            _logger.error(f'SSP Registration Error: {str(e)}')
            self.state = 'error'
            raise Exception(f'Connection error: {str(e)}')
    
    def action_test_connection(self):
        """Testa a conexão com a plataforma SSP"""
        self.ensure_one()
        
        try:
            response = requests.post(
                f'{self.platform_url}/api/odoo/test-connection',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={'test': True},
                timeout=10
            )
            
            if response.status_code == 200:
                self.write({
                    'state': 'connected',
                    'last_sync': fields.Datetime.now()
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': 'Successfully connected to Smart Solutions Platform',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.state = 'error'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Error',
                        'message': f'Failed to connect: {response.status_code}',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f'SSP Connection Error: {str(e)}')
            self.state = 'error'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Error',
                    'message': f'Error: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    @api.model
    def get_config(self):
        """Retorna a configuração ativa da empresa atual"""
        return self.search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)
        ], limit=1)
    
    def action_open_ssp(self):
        """Abrir SSP - se não configurado, abre configuração"""
        config = self.env['ssp.config'].get_config()
        
        # Se não houver configuração, abrir página de configuração
        if not config:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Configure Smart Solutions Platform',
                'res_model': 'ssp.config',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_company_id': self.env.company.id},
            }
        
        # Se não tiver API key, mostrar a configuração existente
        if not config.api_key:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Configure Smart Solutions Platform',
                'res_model': 'ssp.config',
                'res_id': config.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Tudo configurado - abrir dashboard
        sso_url = f"{config.platform_url}/sso/odoo?token={config.api_key}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'ssp_connector.dashboard',
            'params': {
                'url': sso_url,
            }
        }
