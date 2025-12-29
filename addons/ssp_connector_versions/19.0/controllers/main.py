# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SspController(http.Controller):
    
    @http.route('/ssp_connector/dashboard', type='http', auth='user')
    def ssp_dashboard(self, **kwargs):
        """Redireciona para SSP com SSO em nova aba"""
        
        # Buscar configuração
        config = request.env['ssp.config'].sudo().get_config()
        
        if not config:
            return request.render('ssp_connector.ssp_no_config')
        
        if not config.api_key:
            return request.render('ssp_connector.ssp_no_token')
        
        # URL SSO com token
        sso_url = f"{config.platform_url}/sso/odoo?token={config.api_key}"
        
        # Redirecionar direto
        return request.redirect(sso_url)
