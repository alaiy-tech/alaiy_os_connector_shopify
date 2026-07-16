frappe.pages["shopify"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Shopify",
		single_column: true,
	});

	page.set_secondary_action("Settings", function() {
		frappe.set_route("Form", "Shopify Connector Settings");
	}, "settings");

	$(page.body).html(`
		<div class="shopify-page">
			<div class="container shopify-container">
				<!-- Connection Status Card (branded icon/name/status; populated below) -->
				<div class="shopify-card">
					<div class="shopify-card-body">
						<div id="shopify-connector-status" class="shopify-connector-status"></div>
					</div>
				</div>

				<!-- Sync Actions -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<h5>Synchronization</h5>
					</div>
					<div class="shopify-card-body">
						<div class="shopify-sync-grid">
							<!-- Orders Sync -->
							<div class="shopify-sync-box">
								<h6><i class="fa fa-cart-plus"></i> Orders</h6>
								<p class="shopify-text-muted">Pull orders from Shopify</p>
								<button id="import-orders-btn" class="shopify-btn shopify-btn-outline-primary">
									Import Orders from Shopify
								</button>
								<div id="orders-log" class="shopify-sync-log"></div>
							</div>

							<!-- Inventory Sync -->
							<div class="shopify-sync-box">
								<h6><i class="fa fa-box"></i> Inventory</h6>
								<p class="shopify-text-muted">Push inventory to Shopify</p>
								<button id="sync-inventory-btn" class="shopify-btn shopify-btn-outline-primary">
									Sync Inventory
								</button>
								<div id="inventory-log" class="shopify-sync-log"></div>
							</div>

							<!-- Products Import -->
							<div class="shopify-sync-box">
								<h6><i class="fa fa-cubes"></i> Products</h6>
								<p class="shopify-text-muted">Import products from Shopify</p>
								<button id="import-products-btn" class="shopify-btn shopify-btn-outline-primary">
									Import Products from Shopify
								</button>
								<div id="products-log" class="shopify-sync-log"></div>
							</div>

							<!-- Products Export -->
							<div class="shopify-sync-box">
								<h6><i class="fa fa-upload"></i> Products</h6>
								<p class="shopify-text-muted">Push local products to Shopify</p>
								<button id="export-products-btn" class="shopify-btn shopify-btn-outline-primary">
									Export Products to Shopify
								</button>
								<div id="products-export-log" class="shopify-sync-log"></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Sync Logs -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<h5>Sync Logs</h5>
					</div>
					<div class="shopify-card-body">
						<div id="sync-logs-container" class="shopify-logs-container">
							<p class="shopify-text-muted">Loading logs...</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	`);

	function render_connector_status() {
		frappe.call({
			method: "alaiy_os.api.connectors.get_all_connectors",
			callback: function(r) {
				var connector = (r.message || []).find(function(c) {
					return c.connector_id === "shopify";
				});
				if (!connector) return;
				document.getElementById('shopify-connector-status').innerHTML =
					alaiy_os.connector_card._html(connector);
			}
		});
	}

	function check_connection() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.test_connection.test_connection',
			callback: function() { render_connector_status(); },
			error: function() { render_connector_status(); }
		});
	}

	function import_orders() {
		// Tracked here instead of via depends_on's "eval:doc.mode==..." --
		// frappe.ui.Dialog doesn't reliably expose a live `.doc` to evaluate
		// against in every version, and 'mode' isn't a real input field
		// anyway (it's the button pair below), so there's nothing for
		// depends_on to read from the model.
		var mode = 'All orders';

		var dialog = new frappe.ui.Dialog({
			title: 'Import Orders from Shopify',
			fields: [
				{
					fieldname: 'mode', fieldtype: 'HTML',
					options: `
						<div class="shopify-import-mode">
							<button type="button" class="shopify-mode-btn shopify-mode-active" data-mode="All orders">
								<i class="fa fa-list"></i> All orders
							</button>
							<button type="button" class="shopify-mode-btn" data-mode="Date range">
								<i class="fa fa-calendar"></i> Date range
							</button>
						</div>
					`,
				},
				{
					fieldname: 'date_from', fieldtype: 'Date', label: 'From',
				},
				{
					fieldname: 'date_to', fieldtype: 'Date', label: 'To',
				},
			],
			primary_action_label: 'Import',
			primary_action: function(values) {
				if (mode === 'Date range' && (!values.date_from || !values.date_to)) {
					frappe.msgprint('Please pick both a From and To date.');
					return;
				}
				dialog.hide();
				frappe.call({
					method: 'alaiy_os_connector_shopify.api.sync.import_existing_orders',
					args: mode === 'Date range'
						? {date_from: values.date_from, date_to: values.date_to}
						: {},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(r.message.message || 'Import queued');
							setTimeout(refresh_logs, 1000);
						}
					}
				});
			}
		});

		function toggle_date_fields() {
			dialog.fields_dict.date_from.$wrapper.toggle(mode === 'Date range');
			dialog.fields_dict.date_to.$wrapper.toggle(mode === 'Date range');
		}
		toggle_date_fields();

		dialog.$wrapper.find('.shopify-mode-btn').on('click', function() {
			mode = $(this).data('mode');
			dialog.$wrapper.find('.shopify-mode-btn').removeClass('shopify-mode-active');
			$(this).addClass('shopify-mode-active');
			toggle_date_fields();
		});
		dialog.show();
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
		if (!confirm('Import all products from Shopify?')) return;

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

	function export_products() {
		if (!confirm('Export all local (not-yet-linked) products to Shopify?')) return;

		var btn = document.getElementById('export-products-btn');
		var log_container = document.getElementById('products-export-log');
		btn.disabled = true;

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.trigger_product_export',
			callback: function(r) {
				if (r.message && r.message.log_name) {
					log_container.classList.add('shopify-active');
					log_container.innerHTML = '<div class="shopify-log-status-running">Exporting...<span class="shopify-spinner"></span></div>';
					frappe.msgprint('Product export started. Log: ' + r.message.log_name);
					poll_import_progress(r.message.log_name, log_container, btn);
					setTimeout(refresh_logs, 2000);
				}
				btn.disabled = false;
			},
			error: function() {
				btn.disabled = false;
				frappe.msgprint('Failed to start product export');
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

	check_connection();
	refresh_logs();
	document.getElementById('import-orders-btn').addEventListener('click', import_orders);
	document.getElementById('sync-inventory-btn').addEventListener('click', sync_inventory);
	document.getElementById('import-products-btn').addEventListener('click', import_products);
	document.getElementById('export-products-btn').addEventListener('click', export_products);
};
