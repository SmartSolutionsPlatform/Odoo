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
        help='Your full name (auto-filled if empty)'
    )
    
    admin_email = fields.Char(
        string='Admin Email',
        required=True,
        help='Email for SSP account (will be your login)'
    )
    
    odoo_api_key = fields.Char(
        string='Communication Token',
        required=False,
        help='Auto-generated token for platform communication'
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
        default='https://app.smartsolutionsplatform.com',
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
    
    # SQL Constraint: one configuration per company
    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 
         'Only one configuration per company is allowed!')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically register on SSP"""
        import secrets
        for vals in vals_list:
            # Generate automatic Communication Token if not in vals
            if not vals.get('odoo_api_key'):
                vals['odoo_api_key'] = secrets.token_urlsafe(32)
            
            # Auto-fill name if empty
            if not vals.get('admin_name'):
                vals['admin_name'] = self.env.user.name

        records = super(SspConfig, self).create(vals_list)
        
        for record in records:
            try:
                record._register_on_ssp()
            except Exception as e:
                _logger.error(f'Failed to auto-register on SSP: {str(e)}')
                record.state = 'error'
        
        return records
    
    def _register_on_ssp(self):
        """Automatically registers the company on SSP"""
        self.ensure_one()
        
        # The key will be generated in create if empty
        token = self.odoo_api_key or secrets.token_urlsafe(32)
        
        # Get current Odoo data
        odoo_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        odoo_database = self.env.cr.dbname
        odoo_username = self.env.user.login
        
        # Data to send to SSP
        payload = {
            'company_name': self.company_id.name,
            'admin_email': self.admin_email,
            'admin_name': self.admin_name or self.env.user.name,
            'odoo_url': odoo_url,
            'odoo_database': odoo_database,
            'odoo_username': odoo_username,
            'odoo_api_key': self.odoo_api_key,
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
                    # Update with returned data
                    self.write({
                        'account_id': str(data.get('account_id')),
                        'api_key': data.get('sso_token', ''),  # 🆕 Save SSO token
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
            elif response.status_code == 409:
                # If the email is already registered, we mark as connected
                # Note: Ideally SSP would return tokens here too
                self.state = 'connected'
                raise Exception('This email is already registered on the platform. Your configuration was marked as connected, but you might need to update the token manually if the dashboard does not open.')
            else:
                raise Exception(f'HTTP {response.status_code}: {response.text}')
                
        except requests.exceptions.RequestException as e:
            _logger.error(f'SSP Registration Error: {str(e)}')
            self.state = 'error'
            raise Exception(f'Connection error: {str(e)}')
    
    @api.model
    def get_config(self):
        """Returns the active configuration for the current company"""
        return self.search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)
        ], limit=1)
    
    def action_open_ssp(self):
        """Open SSP - if not configured, opens configuration"""
        config = self.env['ssp.config'].get_config()
        
        # If no configuration exists, open configuration page
        if not config:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Configure Smart Solutions Platform',
                'res_model': 'ssp.config',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_company_id': self.env.company.id},
            }
        
        # If there is no API key, show existing configuration
        if not config.api_key:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Configure Smart Solutions Platform',
                'res_model': 'ssp.config',
                'res_id': config.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Everything configured - open dashboard
        sso_url = f"{config.platform_url}/sso/odoo?token={config.api_key}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'ssp_connector.dashboard',
            'params': {
                'url': sso_url,
            }
        }
