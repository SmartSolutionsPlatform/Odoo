# Makefile for Odoo Multi-Version + SSP Environment
# Usage: make start | make stop | make restart | make logs | make status
# Version specific: make start-17 | make start-18 | make start-19

.PHONY: help start stop restart status logs logs-ssp clean upgrade switch-version

# Colors
GREEN  := \033[0;32m
YELLOW := \033[1;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
NC     := \033[0m

# Paths
SSP_PATH := $(HOME)/SSP-Internal/smartsolutions_main_files
ADDONS_PATH := $(shell pwd)/addons
VERSIONS_PATH := $(shell pwd)/addons/ssp_connector_versions

# Default version (can be overridden: make start ODOO_VERSION=17)
ODOO_VERSION ?= 18

# Container names based on version
ODOO_CONTAINER := odoo$(ODOO_VERSION)
ODOO_IMAGE := odoo:$(ODOO_VERSION).0

help: ## Show this help message
	@echo "$(GREEN)══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)        Odoo Multi-Version + SSP Management$(NC)"
	@echo "$(GREEN)══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(BLUE)Current Version: Odoo $(ODOO_VERSION)$(NC)"
	@echo ""
	@echo "Usage: make [target] [ODOO_VERSION=17|18|19]"
	@echo ""
	@echo "$(YELLOW)Version Shortcuts:$(NC)"
	@echo "  $(YELLOW)start-17$(NC)       Start Odoo 17 environment"
	@echo "  $(YELLOW)start-18$(NC)       Start Odoo 18 environment"
	@echo "  $(YELLOW)start-19$(NC)       Start Odoo 19 environment"
	@echo ""
	@echo "$(YELLOW)General Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

# ═══════════════════════════════════════════════════════════
# VERSION SHORTCUTS
# ═══════════════════════════════════════════════════════════

start-17: ## Start Odoo 17 + SSP
	@$(MAKE) start ODOO_VERSION=17

start-18: ## Start Odoo 18 + SSP
	@$(MAKE) start ODOO_VERSION=18

start-19: ## Start Odoo 19 + SSP
	@$(MAKE) start ODOO_VERSION=19

stop-17: ## Stop Odoo 17
	@$(MAKE) stop ODOO_VERSION=17

stop-18: ## Stop Odoo 18
	@$(MAKE) stop ODOO_VERSION=18

stop-19: ## Stop Odoo 19
	@$(MAKE) stop ODOO_VERSION=19

logs-17: ## Show Odoo 17 logs
	@docker logs -f odoo17

logs-18: ## Show Odoo 18 logs
	@docker logs -f odoo18

logs-19: ## Show Odoo 19 logs
	@docker logs -f odoo19

# ═══════════════════════════════════════════════════════════
# MAIN COMMANDS
# ═══════════════════════════════════════════════════════════

start: ## Start services (PostgreSQL + Odoo + SSP)
	@echo "$(YELLOW)Starting Odoo $(ODOO_VERSION) environment...$(NC)"
	@echo ""
	@echo "$(YELLOW)[1/4]$(NC) Copying SSP Connector v$(ODOO_VERSION) to addons..."
	@rm -rf $(ADDONS_PATH)/ssp_connector/*
	@cp -r $(VERSIONS_PATH)/$(ODOO_VERSION).0/* $(ADDONS_PATH)/ssp_connector/ 2>/dev/null || echo "$(YELLOW)⚠ Version $(ODOO_VERSION).0 not found, using current$(NC)"
	@echo "$(GREEN)✓ SSP Connector v$(ODOO_VERSION) ready$(NC)"
	@echo ""
	@echo "$(YELLOW)[2/4]$(NC) Starting PostgreSQL..."
	@docker start postgres-odoo 2>/dev/null || docker ps | grep -q postgres-odoo && echo "$(GREEN)✓ PostgreSQL running$(NC)" || (echo "$(RED)✗ PostgreSQL failed$(NC)" && exit 1)
	@sleep 3
	@echo ""
	@echo "$(YELLOW)[3/4]$(NC) Starting Odoo $(ODOO_VERSION)..."
	@docker start $(ODOO_CONTAINER) 2>/dev/null || (echo "$(YELLOW)Container $(ODOO_CONTAINER) not found, creating...$(NC)" && $(MAKE) create-odoo-container)
	@docker ps | grep -q $(ODOO_CONTAINER) && echo "$(GREEN)✓ Odoo $(ODOO_VERSION) running$(NC)" || (echo "$(RED)✗ Odoo $(ODOO_VERSION) failed$(NC)" && exit 1)
	@sleep 5
	@echo ""
	@echo "$(YELLOW)[4/4]$(NC) Starting SSP..."
	@-pkill -f 'php artisan serve' 2>/dev/null || true
	@cd $(SSP_PATH) && nohup php artisan serve --host=0.0.0.0 --port=8007 > /tmp/ssp.log 2>&1 &
	@sleep 2
	@echo "$(GREEN)✓ SSP started$(NC)"
	@echo ""
	@$(MAKE) --no-print-directory status ODOO_VERSION=$(ODOO_VERSION)

stop: ## Stop all services
	@echo "$(YELLOW)Stopping Odoo $(ODOO_VERSION) services...$(NC)"
	@docker stop $(ODOO_CONTAINER) 2>/dev/null || true
	@docker stop postgres-odoo 2>/dev/null || true
	@-pkill -f 'php artisan serve' 2>/dev/null || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

stop-all: ## Stop ALL Odoo versions
	@echo "$(YELLOW)Stopping ALL services...$(NC)"
	@docker stop odoo17 odoo18 odoo19 postgres-odoo 2>/dev/null || true
	@-pkill -f 'php artisan serve' 2>/dev/null || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

restart: ## Restart all services
	@$(MAKE) --no-print-directory stop ODOO_VERSION=$(ODOO_VERSION)
	@sleep 2
	@$(MAKE) --no-print-directory start ODOO_VERSION=$(ODOO_VERSION)

status: ## Check status of all services
	@echo "$(GREEN)═══════════════════════════════════════$(NC)"
	@echo "$(GREEN)   SERVICE STATUS (Odoo $(ODOO_VERSION))$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════$(NC)"
	@echo ""
	@docker ps | grep -q postgres-odoo && echo "$(GREEN)✓ PostgreSQL:$(NC)  Running (port 5432)" || echo "$(RED)✗ PostgreSQL:$(NC)  Stopped"
	@docker ps | grep -q odoo17 && echo "$(GREEN)✓ Odoo 17:$(NC)     Running → http://localhost:8017" || echo "$(RED)✗ Odoo 17:$(NC)     Stopped"
	@docker ps | grep -q odoo18 && echo "$(GREEN)✓ Odoo 18:$(NC)     Running → http://localhost:8069" || echo "$(RED)✗ Odoo 18:$(NC)     Stopped"
	@docker ps | grep -q odoo19 && echo "$(GREEN)✓ Odoo 19:$(NC)     Running → http://localhost:8019" || echo "$(RED)✗ Odoo 19:$(NC)     Stopped"
	@lsof -ti:8007 > /dev/null 2>&1 && echo "$(GREEN)✓ SSP:$(NC)         Running → http://localhost:8007" || echo "$(RED)✗ SSP:$(NC)         Stopped"
	@echo ""
	@echo "$(BLUE)SSP Connector Version: $(shell cat $(ADDONS_PATH)/ssp_connector/__manifest__.py 2>/dev/null | grep version | head -1 | cut -d"'" -f2 || echo 'N/A')$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════
# DOCKER CONTAINER MANAGEMENT
# ═══════════════════════════════════════════════════════════

create-odoo-container: ## Create Odoo container for specified version
	@echo "$(YELLOW)Creating Odoo $(ODOO_VERSION) container...$(NC)"
ifeq ($(ODOO_VERSION),17)
	@docker run -d --name odoo17 \
		-p 8017:8069 \
		--link postgres-odoo:db \
		-v $(ADDONS_PATH):/mnt/extra-addons \
		-e HOST=db \
		-e USER=odoo \
		-e PASSWORD=odoo \
		odoo:17.0
else ifeq ($(ODOO_VERSION),18)
	@docker run -d --name odoo18 \
		-p 8069:8069 \
		--link postgres-odoo:db \
		-v $(ADDONS_PATH):/mnt/extra-addons \
		-e HOST=db \
		-e USER=odoo \
		-e PASSWORD=odoo \
		odoo:18.0
else ifeq ($(ODOO_VERSION),19)
	@docker run -d --name odoo19 \
		-p 8019:8069 \
		--link postgres-odoo:db \
		-v $(ADDONS_PATH):/mnt/extra-addons \
		-e HOST=db \
		-e USER=odoo \
		-e PASSWORD=odoo \
		odoo:19.0
endif
	@echo "$(GREEN)✓ Odoo $(ODOO_VERSION) container created$(NC)"

remove-odoo-container: ## Remove Odoo container for specified version
	@echo "$(YELLOW)Removing Odoo $(ODOO_VERSION) container...$(NC)"
	@docker rm -f $(ODOO_CONTAINER) 2>/dev/null || true
	@echo "$(GREEN)✓ Container removed$(NC)"

# ═══════════════════════════════════════════════════════════
# LOGS
# ═══════════════════════════════════════════════════════════

logs: ## Show Odoo logs (follow mode)
	@docker logs -f $(ODOO_CONTAINER)

logs-ssp: ## Show SSP logs (follow mode)
	@tail -f /tmp/ssp.log

logs-tail: ## Show last 50 lines of Odoo logs
	@docker logs $(ODOO_CONTAINER) --tail 50

# ═══════════════════════════════════════════════════════════
# MODULE MANAGEMENT
# ═══════════════════════════════════════════════════════════

upgrade: ## Upgrade SSP Connector module in Odoo
	@echo "$(YELLOW)Upgrading SSP Connector module (Odoo $(ODOO_VERSION))...$(NC)"
	@docker restart $(ODOO_CONTAINER)
	@sleep 10
	@echo "$(GREEN)✓ Odoo $(ODOO_VERSION) restarted$(NC)"
	@echo ""
	@echo "Now go to Odoo → Apps → Search 'SSP' → Update"

switch-version: ## Switch SSP Connector to specified version
	@echo "$(YELLOW)Switching SSP Connector to version $(ODOO_VERSION).0...$(NC)"
	@rm -rf $(ADDONS_PATH)/ssp_connector/*
	@cp -r $(VERSIONS_PATH)/$(ODOO_VERSION).0/* $(ADDONS_PATH)/ssp_connector/
	@echo "$(GREEN)✓ SSP Connector switched to v$(ODOO_VERSION)$(NC)"
	@echo ""
	@echo "Now restart Odoo: make restart ODOO_VERSION=$(ODOO_VERSION)"

# ═══════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════

clean: ## Clean logs and temporary files
	@echo "$(YELLOW)Cleaning logs...$(NC)"
	@rm -f /tmp/ssp.log
	@docker exec $(ODOO_CONTAINER) rm -f /var/log/odoo/*.log 2>/dev/null || true
	@echo "$(GREEN)✓ Logs cleaned$(NC)"

ps: ## Show running containers
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "odoo|postgres|NAMES"

db-backup: ## Backup Odoo database
	@echo "$(YELLOW)Backing up Odoo database...$(NC)"
	@docker exec postgres-odoo pg_dump -U odoo ssp-pedro > ~/odoo-backup-$(shell date +%Y%m%d-%H%M%S).sql
	@echo "$(GREEN)✓ Backup created$(NC)"

shell-odoo: ## Enter Odoo container shell
	@docker exec -it $(ODOO_CONTAINER) bash

shell-postgres: ## Enter PostgreSQL container shell
	@docker exec -it postgres-odoo psql -U odoo -d ssp-pedro

dev: ## Start in development mode (with logs visible)
	@$(MAKE) --no-print-directory start ODOO_VERSION=$(ODOO_VERSION)
	@echo ""
	@echo "$(GREEN)Development mode (Odoo $(ODOO_VERSION)) - Press Ctrl+C to see logs$(NC)"
	@sleep 2
	@$(MAKE) --no-print-directory logs ODOO_VERSION=$(ODOO_VERSION)

# ═══════════════════════════════════════════════════════════
# VERSION INFO
# ═══════════════════════════════════════════════════════════

versions: ## Show available SSP Connector versions
	@echo "$(GREEN)═══════════════════════════════════════$(NC)"
	@echo "$(GREEN)   SSP Connector Versions$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════$(NC)"
	@echo ""
	@ls -la $(VERSIONS_PATH) 2>/dev/null | grep -E "^d" | grep -v "^\." | awk '{print "  📦 " $$NF}'
	@echo ""
	@echo "$(BLUE)Currently active: $(shell cat $(ADDONS_PATH)/ssp_connector/__manifest__.py 2>/dev/null | grep version | head -1 | cut -d"'" -f2 || echo 'N/A')$(NC)"
	@echo ""