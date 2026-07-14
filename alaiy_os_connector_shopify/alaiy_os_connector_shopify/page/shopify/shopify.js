frappe.ready(function() {
	var page = cur_page;

	function test_connection() {
		var btn = document.getElementById('test-connection-btn');
		btn.disabled = true;
		btn.innerHTML = '<span class="shopify-spinner"></span> Testing...';

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.test_connection.test_connection',
			callback: function(r) {
				if (r.message) {
					document.getElementById('connection-test-status').textContent = 'Connected';
					document.getElementById('connection-test-status').className = 'shopify-badge shopify-badge-success';
					document.getElementById('store-name').textContent = r.message.store || 'Connected';
				} else {
					document.getElementById('connection-test-status').textContent = 'Failed';
					document.getElementById('connection-test-status').className = 'shopify-badge shopify-badge-danger';
				}
				btn.disabled = false;
				btn.innerHTML = '<i class="fa fa-plug"></i> Test Connection';
			},
			error: function() {
				document.getElementById('connection-test-status').textContent = 'Error';
				document.getElementById('connection-test-status').className = 'shopify-badge shopify-badge-danger';
				btn.disabled = false;
				btn.innerHTML = '<i class="fa fa-plug"></i> Test Connection';
			}
		});
	}

	function sync_orders() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.trigger_orders_sync',
			callback: function(r) {
				if (r.message && r.message.log_name) {
					frappe.msgprint('Orders sync queued. Log: ' + r.message.log_name);
					setTimeout(refresh_logs, 1000);
				}
			}
		});
	}

	function import_orders() {
		if (!confirm('Import all historical orders from Shopify?')) return;
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.import_existing_orders',
			callback: function(r) {
				if (r.message) {
					frappe.msgprint(r.message.message || 'Import queued');
					setTimeout(refresh_logs, 1000);
				}
			}
		});
	}

	function sync_inventory() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.trigger_inventory_push',
			callback: function(r) {
				if (r.message && r.message.log_name) {
					frappe.msgprint('Inventory sync queued. Log: ' + r.message.log_name);
					setTimeout(refresh_logs, 1000);
				}
			}
		});
	}

	function import_products() {
		if (!confirm('This will DELETE all local products and import ALL from Shopify. Continue?')) return;

		var btn = document.getElementById('import-products-btn');
		var log_container = document.getElementById('products-log');
		btn.disabled = true;

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.trigger_product_import',
			callback: function(r) {
				if (r.message && r.message.log_name) {
					log_container.classList.add('shopify-active');
					log_container.innerHTML = '<div class="shopify-log-status-running">Importing...<span class="shopify-spinner"></span></div>';
					frappe.msgprint('Product import started. Log: ' + r.message.log_name);
					poll_import_progress(r.message.log_name, log_container, btn);
					setTimeout(refresh_logs, 2000);
				}
				btn.disabled = false;
			},
			error: function() {
				btn.disabled = false;
				frappe.msgprint('Failed to start product import');
			}
		});
	}

	function poll_import_progress(log_name, log_container, btn) {
		frappe.call({
			method: 'frappe.client.get',
			args: {doctype: 'Shopify Sync Log', name: log_name},
			callback: function(r) {
				if (r.message) {
					var log = r.message;
					var html = '<div class="shopify-log-status shopify-log-status-' + log.status + '">' + log.status.toUpperCase() + '</div>';
					if (log.items_processed) html += '<div class="shopify-log-entry">Processed: ' + log.items_processed + '</div>';
					if (log.items_created) html += '<div class="shopify-log-entry">Created: ' + log.items_created + '</div>';
					if (log.items_failed) html += '<div class="shopify-log-entry">Failed: ' + log.items_failed + '</div>';
					if (log.error_message) html += '<div class="shopify-log-entry shopify-alert-warning"><strong>Error:</strong> ' + log.error_message + '</div>';

					log_container.innerHTML = html;

					if (log.status === 'running' || log.status === 'queued') {
						setTimeout(function() { poll_import_progress(log_name, log_container, btn); }, 2000);
					} else {
						btn.disabled = false;
					}
				}
			}
		});
	}

	function refresh_logs() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.get_sync_status',
			callback: function(r) {
				if (r.message) render_logs_table(r.message);
			}
		});
	}

	function render_logs_table(logs) {
		var container = document.getElementById('sync-logs-container');
		if (!logs || logs.length === 0) {
			container.innerHTML = '<p class="shopify-text-muted">No sync logs yet.</p>';
			return;
		}

		var html = '<table class="shopify-logs-table"><thead><tr><th>Type</th><th>Status</th><th>Trigger</th><th>Started</th><th>Progress</th></tr></thead><tbody>';
		logs.forEach(function(log) {
			var status_class = log.status === 'success' ? 'shopify-badge-success' : log.status === 'failed' ? 'shopify-badge-danger' : log.status === 'running' ? 'shopify-badge-info' : 'shopify-badge-secondary';
			var started = log.started_at ? new Date(log.started_at).toLocaleString() : '-';
			var progress = log.pages_total ? log.pages_done + '/' + log.pages_total + ' pages' : (log.items_created || 0) + ' created';
			html += '<tr><td><strong>' + log.sync_type + '</strong></td><td><span class="shopify-badge ' + status_class + '">' + log.status + '</span></td><td>' + log.trigger + '</td><td>' + started + '</td><td>' + progress + '</td></tr>';
		});
		html += '</tbody></table>';
		container.innerHTML = html;

		var running = logs.some(function(l) { return l.status === 'running' || l.status === 'queued'; });
		if (running) setTimeout(refresh_logs, 3000);
	}

	test_connection();
	refresh_logs();
	document.getElementById('test-connection-btn').addEventListener('click', test_connection);
	document.getElementById('sync-orders-btn').addEventListener('click', sync_orders);
	document.getElementById('import-orders-btn').addEventListener('click', import_orders);
	document.getElementById('sync-inventory-btn').addEventListener('click', sync_inventory);
	document.getElementById('import-products-btn').addEventListener('click', import_products);
});
