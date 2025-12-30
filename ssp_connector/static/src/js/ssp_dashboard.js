/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class SSPDashboard extends Component {
    setup() {
        console.log("SSP Dashboard Initialized with URL:", this.props.action.params.url);
    }

    get url() {
        return this.props.action.params.url || "about:blank";
    }

    openInNewTab() {
        window.open(this.url, '_blank');
    }
}

SSPDashboard.template = "ssp_connector.SSPDashboard";

registry.category("actions").add("ssp_connector.dashboard", SSPDashboard);
