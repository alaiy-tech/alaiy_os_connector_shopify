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

				<!-- Stats -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-bar-chart"></i></span>
						<div class="shopify-card-header-text">
							<h5>Overview</h5>
							<p>Current catalog and sync state.</p>
						</div>
					</div>
					<div class="shopify-card-body">
						<div id="shopify-stats-grid"></div>
					</div>
				</div>

				<!-- Orders -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-cart-plus"></i></span>
						<div class="shopify-card-header-text">
							<h5>Orders</h5>
							<p>Import Shopify orders into Alaiy OS.</p>
						</div>
					</div>
					<div class="shopify-card-body">
						<div class="shopify-import-mode">
							<button type="button" class="shopify-mode-btn shopify-mode-active" data-mode="All orders">
								<i class="fa fa-list"></i> All orders
							</button>
							<button type="button" class="shopify-mode-btn" data-mode="Date range">
								<i class="fa fa-calendar"></i> Date range
							</button>
						</div>

						<div id="orders-date-range" class="shopify-date-range">
							<div class="shopify-field-group">
								<label>From</label>
								<input type="date" id="orders-date-from" class="shopify-input">
							</div>
							<div class="shopify-field-group">
								<label>To</label>
								<input type="date" id="orders-date-to" class="shopify-input">
							</div>
						</div>

						<p class="shopify-text-muted">Choose the import range and bring Shopify orders into Alaiy OS.</p>
						<div class="shopify-info-strip">
							<span class="shopify-info-pill"><i class="fa fa-check-circle"></i> Sales Orders</span>
							<span class="shopify-info-pill"><i class="fa fa-file-text"></i> Invoices &amp; Payments</span>
							<span class="shopify-info-pill"><i class="fa fa-truck"></i> Fulfillments</span>
						</div>
						<button id="import-orders-btn" class="shopify-btn shopify-btn-primary">
							<i class="fa fa-cloud-download"></i> Import Orders from Shopify
						</button>
						<button id="import-orders-stop-btn" class="shopify-btn shopify-btn-danger" style="display:none;">
							<i class="fa fa-stop"></i> Stop
						</button>
						<div id="orders-log" class="shopify-sync-log"></div>
					</div>
				</div>

				<!-- Inventory -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-archive"></i></span>
						<div class="shopify-card-header-text">
							<h5>Inventory</h5>
							<p>Push stock levels from Alaiy OS to Shopify.</p>
						</div>
					</div>
					<div class="shopify-card-body">
						<p class="shopify-text-muted">Send the latest stock updates from Alaiy OS to Shopify.</p>
						<div class="shopify-info-strip">
							<span class="shopify-info-pill"><i class="fa fa-bolt"></i> Live stock sync</span>
							<span class="shopify-info-pill"><i class="fa fa-map-marker"></i> Multi-location</span>
							<span class="shopify-info-pill"><i class="fa fa-clock-o"></i> Scheduled runs</span>
						</div>
						<button id="sync-inventory-btn" class="shopify-btn shopify-btn-primary">
							<i class="fa fa-refresh"></i> Sync Inventory
						</button>
						<button id="sync-inventory-stop-btn" class="shopify-btn shopify-btn-danger" style="display:none;">
							<i class="fa fa-stop"></i> Stop
						</button>
						<div id="inventory-log" class="shopify-sync-log"></div>
					</div>
				</div>

				<!-- Products -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-cubes"></i></span>
						<div class="shopify-card-header-text">
							<h5>Products</h5>
							<p>Manage Shopify products and variants.</p>
						</div>
					</div>
					<div class="shopify-card-body">
						<p class="shopify-text-muted">Import products from Shopify or export local catalog items back to Shopify.</p>
						<div class="shopify-info-strip">
							<span class="shopify-info-pill"><i class="fa fa-exchange"></i> Import &amp; export</span>
							<span class="shopify-info-pill"><i class="fa fa-cubes"></i> Variants &amp; pricing</span>
							<span class="shopify-info-pill"><i class="fa fa-picture-o"></i> Media &amp; SEO</span>
						</div>
						<div class="shopify-sync-grid">
							<div class="shopify-sync-box">
								<h6><i class="fa fa-download"></i> Import</h6>
								<p class="shopify-text-muted">Import products from Shopify.</p>
								<button id="import-products-btn" class="shopify-btn shopify-btn-primary">
									Import Products from Shopify
								</button>
								<button id="import-products-stop-btn" class="shopify-btn shopify-btn-danger" style="display:none;">
									<i class="fa fa-stop"></i> Stop
								</button>
								<div id="products-log" class="shopify-sync-log"></div>
							</div>
							<div class="shopify-sync-box">
								<h6><i class="fa fa-upload"></i> Export</h6>
								<p class="shopify-text-muted">Push local (not-yet-linked) products to Shopify.</p>
								<button id="export-products-btn" class="shopify-btn shopify-btn-outline-primary">
									Export Products to Shopify
								</button>
								<button id="export-products-stop-btn" class="shopify-btn shopify-btn-danger" style="display:none;">
									<i class="fa fa-stop"></i> Stop
								</button>
								<div id="products-export-log" class="shopify-sync-log"></div>
							</div>
							<div class="shopify-sync-box">
								<h6><i class="fa fa-list"></i> Listings</h6>
								<p class="shopify-text-muted">Per-marketplace product listings (title, price, images, variants).</p>
								<button id="manage-listings-btn" class="shopify-btn shopify-btn-outline-primary">
									Manage Listings
								</button>
							</div>
						</div>
					</div>
				</div>

				<!-- Categories & Tags -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-tags"></i></span>
						<div class="shopify-card-header-text">
							<h5>Categories &amp; Tags</h5>
							<p>Refresh cached taxonomy, tags, collections and locations</p>
						</div>
					</div>
					<div class="shopify-card-body">
						<button id="sync-taxonomy-btn" class="shopify-btn shopify-btn-outline-secondary">
							Sync Categories
						</button>
						<button id="sync-tags-btn" class="shopify-btn shopify-btn-outline-secondary">
							Sync Tags
						</button>
						<button id="sync-collections-btn" class="shopify-btn shopify-btn-outline-secondary">
							Sync Collections
						</button>
						<button id="sync-locations-btn" class="shopify-btn shopify-btn-outline-secondary">
							Sync Locations
						</button>
						<div id="taxonomy-log" class="shopify-sync-log"></div>
					</div>
				</div>

				<!-- Sync Logs -->
				<div class="shopify-card">
					<div class="shopify-card-header">
						<span class="shopify-icon-badge"><i class="fa fa-history"></i></span>
						<div class="shopify-card-header-text">
							<h5>Sync Logs</h5>
							<p>Recent synchronization activity across all types</p>
						</div>
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

	// Orders mode toggle (All orders / Date range) -- kept inline in the card
	// itself instead of a popup dialog, so it toggles the date fields' visibility
	// directly rather than needing a live `.doc` to evaluate a depends_on against.
	var order_import_mode = 'All orders';

	function toggle_order_date_fields() {
		$(page.body).find('#orders-date-range').toggleClass('shopify-active', order_import_mode === 'Date range');
	}

	function import_orders() {
		var date_from = document.getElementById('orders-date-from').value;
		var date_to = document.getElementById('orders-date-to').value;

		if (order_import_mode === 'Date range' && (!date_from || !date_to)) {
			frappe.msgprint('Please pick both a From and To date.');
			return;
		}

		var btn = document.getElementById('import-orders-btn');
		var stop_btn = document.getElementById('import-orders-stop-btn');
		var log_container = document.getElementById('orders-log');
		btn.disabled = true;
		log_container.classList.add('shopify-active');
		log_container.innerHTML = '<div class="shopify-log-status-running">Starting import...<span class="shopify-spinner"></span></div>';

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.import_existing_orders',
			args: order_import_mode === 'Date range'
				? {date_from: date_from, date_to: date_to}
				: {},
			callback: function(r) {
				if (r.message && r.message.log_name) {
					log_container.innerHTML = '<div class="shopify-log-status-running">' + (r.message.message || 'Importing...') + '<span class="shopify-spinner"></span></div>';
					stop_btn.onclick = function() { stop_sync(r.message.log_name, stop_btn); };
					poll_import_progress(r.message.log_name, log_container, btn, stop_btn);
					setTimeout(refresh_logs, 1000);
				} else {
					btn.disabled = false;
					if (r.message) log_container.innerHTML = '<div class="shopify-log-entry">' + (r.message.message || 'Nothing to import') + '</div>';
				}
			},
			error: function() {
				btn.disabled = false;
				log_container.innerHTML = '<div class="shopify-log-entry shopify-alert-warning">Failed to start order import</div>';
			}
		});
	}

	function sync_inventory() {
		var btn = document.getElementById('sync-inventory-btn');
		var stop_btn = document.getElementById('sync-inventory-stop-btn');
		var log_container = document.getElementById('inventory-log');
		btn.disabled = true;
		log_container.classList.add('shopify-active');
		log_container.innerHTML = '<div class="shopify-log-status-running">Starting inventory sync...<span class="shopify-spinner"></span></div>';

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.trigger_inventory_push',
			callback: function(r) {
				if (r.message && r.message.log_name) {
					stop_btn.onclick = function() { stop_sync(r.message.log_name, stop_btn); };
					poll_import_progress(r.message.log_name, log_container, btn, stop_btn);
					setTimeout(refresh_logs, 1000);
				} else {
					btn.disabled = false;
				}
			},
			error: function() {
				btn.disabled = false;
				log_container.innerHTML = '<div class="shopify-log-entry shopify-alert-warning">Failed to start inventory sync</div>';
			}
		});
	}

	// Status picker shared by import and export. All three ticked by default --
	// the common case is "everything", and a merchant who wants a subset is
	// making a deliberate choice per run rather than editing settings first.
	function ask_statuses(title, blurb, primary_label, on_confirm) {
		var d = new frappe.ui.Dialog({
			title: title,
			fields: [
				{ fieldtype: 'HTML', options: '<p>' + blurb + '</p>' },
				{ fieldtype: 'Section Break', label: 'Product status' },
				{ fieldname: 'st_active', fieldtype: 'Check', label: 'Active', default: 1 },
				{ fieldname: 'st_draft', fieldtype: 'Check', label: 'Draft', default: 1 },
				{ fieldname: 'st_archived', fieldtype: 'Check', label: 'Archived', default: 1,
				  description: 'Archived products are hidden from Shopify sales channels but keep their order history.' }
			],
			primary_action_label: primary_label,
			primary_action: function(values) {
				var statuses = [];
				if (values.st_active) statuses.push('Active');
				if (values.st_draft) statuses.push('Draft');
				if (values.st_archived) statuses.push('Archived');
				if (!statuses.length) {
					frappe.msgprint('Pick at least one status.');
					return;
				}
				d.hide();
				on_confirm(statuses);
			}
		});
		d.show();
	}

	function import_products() {
		ask_statuses(
			'Import Products from Shopify',
			'New products are created, changed products are updated, unchanged ones are left alone. On the very first run only, any stray unlinked product data is wiped first as a safety net.',
			'Import',
			function(statuses) {
				var btn = document.getElementById('import-products-btn');
				var stop_btn = document.getElementById('import-products-stop-btn');
				var log_container = document.getElementById('products-log');
				btn.disabled = true;

				frappe.call({
					method: 'alaiy_os_connector_shopify.api.sync.trigger_product_import',
					args: { statuses: statuses },
					callback: function(r) {
						if (r.message && r.message.log_name) {
							log_container.classList.add('shopify-active');
							log_container.innerHTML = '<div class="shopify-log-status-running">Importing...<span class="shopify-spinner"></span></div>';
							stop_btn.onclick = function() { stop_sync(r.message.log_name, stop_btn); };
							poll_import_progress(r.message.log_name, log_container, btn, stop_btn);
							setTimeout(refresh_logs, 2000);
						} else {
							btn.disabled = false;
						}
					},
					error: function() {
						btn.disabled = false;
						frappe.msgprint('Failed to start product import');
					}
				});
			}
		);
	}

	function export_products() {
		ask_statuses(
			'Export Products to Shopify',
			'Pushes every local product that is not yet linked to Shopify. Only listings whose status is ticked below are sent.',
			'Export',
			function(statuses) {
				var btn = document.getElementById('export-products-btn');
				var stop_btn = document.getElementById('export-products-stop-btn');
				var log_container = document.getElementById('products-export-log');
				btn.disabled = true;

				frappe.call({
					method: 'alaiy_os_connector_shopify.api.sync.trigger_product_export',
					args: { statuses: statuses },
					callback: function(r) {
						if (r.message && r.message.log_name) {
							log_container.classList.add('shopify-active');
							log_container.innerHTML = '<div class="shopify-log-status-running">Exporting...<span class="shopify-spinner"></span></div>';
							stop_btn.onclick = function() { stop_sync(r.message.log_name, stop_btn); };
							poll_import_progress(r.message.log_name, log_container, btn, stop_btn);
							setTimeout(refresh_logs, 2000);
						} else {
							btn.disabled = false;
						}
					},
					error: function() {
						btn.disabled = false;
						frappe.msgprint('Failed to start product export');
					}
				});
			}
		);
	}

	function sync_taxonomy() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.refresh_shopify_taxonomy',
			callback: function(r) {
				if (r.message && r.message.queued) {
					frappe.show_alert({message: 'Category sync queued', indicator: 'blue'}, 5);
				}
			}
		});
	}

	function sync_tags() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.refresh_shopify_tags',
			callback: function(r) {
				if (r.message && r.message.queued) {
					frappe.show_alert({message: 'Tags sync queued', indicator: 'blue'}, 5);
				}
			}
		});
	}

	function sync_collections() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.refresh_shopify_collections',
			callback: function(r) {
				if (r.message && r.message.queued) {
					frappe.show_alert({message: 'Collections sync queued', indicator: 'blue'}, 5);
				}
			}
		});
	}

	function sync_locations() {
		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.refresh_shopify_locations',
			callback: function(r) {
				if (r.message && r.message.queued) {
					frappe.show_alert({message: 'Locations sync queued', indicator: 'blue'}, 5);
				}
			}
		});
	}

	function poll_import_progress(log_name, log_container, btn, stop_btn) {
		frappe.call({
			method: 'frappe.client.get',
			args: {doctype: 'Shopify Sync Log', name: log_name},
			callback: function(r) {
				if (r.message) {
					var log = r.message;
					var is_active = (log.status === 'running' || log.status === 'queued');
					var html = '<div class="shopify-log-status shopify-log-status-' + log.status + '">' + log.status.toUpperCase() + '</div>';
					if (log.items_processed) {
						var total = log.pages_total ? (' / ' + log.pages_total) : '';
						html += '<div class="shopify-log-entry">Processed: ' + log.items_processed + total + '</div>';
					}
					if (log.items_created) html += '<div class="shopify-log-entry">Created: ' + log.items_created + '</div>';
					if (log.items_failed) html += '<div class="shopify-log-entry">Failed: ' + log.items_failed + '</div>';
					if (log.error_message) html += '<div class="shopify-log-entry shopify-alert-warning"><strong>Error:</strong> ' + log.error_message + '</div>';

					log_container.innerHTML = html;

					if (stop_btn) stop_btn.style.display = is_active ? 'inline-block' : 'none';

					if (is_active) {
						setTimeout(function() { poll_import_progress(log_name, log_container, btn, stop_btn); }, 2000);
					} else {
						btn.disabled = false;
					}
				}
			}
		});
	}

	function stop_sync(log_name, stop_btn) {
		if (!log_name) return;
		stop_btn.disabled = true;
		frappe.call({
			method: 'alaiy_os_connector_shopify.shopify.sync_guard.request_cancel',
			args: {log_name: log_name},
			callback: function(r) {
				stop_btn.disabled = false;
				if (r.message && r.message.cancelled) {
					frappe.show_alert({message: 'Stopping... this may take a few seconds to finish the current item.', indicator: 'orange'}, 5);
				} else if (r.message) {
					frappe.show_alert({message: r.message.reason || 'Could not stop -- job already finished.', indicator: 'grey'}, 5);
				}
			}
		});
	}

	function escape_html(value) {
		return String(value || '')
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;');
	}

	function badge_html(value, color) {
		return '<span class="indicator-pill ' + color + '" title="' + escape_html(value || '') + '"><span>' + escape_html(value || '') + '</span></span>';
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

		var html = '<table class="shopify-logs-table"><thead><tr><th>Name</th><th>Type</th><th>Trigger</th><th>Status</th><th>Started</th><th>Progress</th></tr></thead><tbody>';
		logs.forEach(function(log) {
			var sync_type = log.sync_type || '-';
			var trigger = log.trigger || '-';
			var status = log.status || '-';
			var started = log.started_at ? new Date(log.started_at).toLocaleString() : '-';
			var progress = log.pages_total ? log.pages_done + '/' + log.pages_total + ' pages' : (log.items_created || 0) + ' created';
			var sync_color = sync_type === 'orders' ? 'pink' : sync_type === 'inventory' ? 'blue' : sync_type === 'products' || sync_type === 'product_export' ? 'green' : sync_type === 'collections' ? 'cyan' : sync_type === 'locations' ? 'purple' : 'darkgrey';
			var trigger_color = trigger === 'manual' ? 'orange' : trigger === 'scheduled' ? 'purple' : trigger === 'webhook' ? 'cyan' : 'darkgrey';
			var status_color = status === 'success' ? 'green' : status === 'failed' ? 'red' : status === 'running' ? 'blue' : status === 'queued' ? 'grey' : status === 'skipped' ? 'yellow' : 'darkgrey';
			var name_html = '<a href="#" class="shopify-log-link" data-name="' + escape_html(log.name || '') + '">' + escape_html(log.name || '') + '</a>';
			html += '<tr><td>' + name_html + '</td><td>' + badge_html(sync_type, sync_color) + '</td><td>' + badge_html(trigger, trigger_color) + '</td><td>' + badge_html(status, status_color) + '</td><td>' + escape_html(started) + '</td><td>' + escape_html(progress) + '</td></tr>';
		});
		html += '</tbody></table>';
		container.innerHTML = html;

		$(container).find('.shopify-log-link').on('click', function(e) {
			e.preventDefault();
			frappe.set_route('Form', 'Shopify Sync Log', $(this).data('name'));
		});

		var running = logs.some(function(l) { return l.status === 'running' || l.status === 'queued'; });
		if (running) setTimeout(refresh_logs, 3000);
	}

	function render_stat_group(title, cards, accent) {
		var html = '<div class="shopify-stat-group-title">' + title + '</div><div class="shopify-stats-grid">';
		cards.forEach(function(c) {
			html += '<div class="shopify-stat-tile shopify-stat-accent-' + accent + '">' +
				'<div class="shopify-stat-value">' + c.value + '</div>' +
				'<div class="shopify-stat-label">' + c.label + '</div>' +
				'</div>';
		});
		html += '</div>';
		return html;
	}

	function render_skeleton_group(title, count) {
		var html = '<div class="shopify-stat-group-title">' + title + '</div><div class="shopify-stats-grid">';
		for (var i = 0; i < count; i++) {
			html += '<div class="shopify-stat-tile shopify-stat-skeleton">' +
				'<div class="shopify-skeleton-bar shopify-skeleton-value"></div>' +
				'<div class="shopify-skeleton-bar shopify-skeleton-label"></div>' +
				'</div>';
		}
		html += '</div>';
		return html;
	}

	// Clicking a template-status tile jumps to the Listing list filtered to
	// that status -- delegated on the grid's parent since load_stats()
	// rewrites innerHTML on every refresh.
	function render_status_stat_group(s) {
		var html = '<div class="shopify-stat-group-title">Templates by status</div><div class="shopify-stats-grid">';
		[
			{label: 'Active', value: s.templates_active, status: 'Active'},
			{label: 'Draft', value: s.templates_draft, status: 'Draft'},
			{label: 'Archived', value: s.templates_archived, status: 'Archived'},
		].forEach(function(c) {
			html += '<div class="shopify-stat-tile shopify-stat-accent-local shopify-stat-clickable" data-status="' + c.status + '">' +
				'<div class="shopify-stat-value">' + c.value + '</div>' +
				'<div class="shopify-stat-label">' + c.label + '</div>' +
				'</div>';
		});
		html += '</div>';
		return html;
	}

	function load_stats() {
		var grid = document.getElementById('shopify-stats-grid');
		grid.innerHTML = render_skeleton_group('Alaiy OS (local)', 8);

		frappe.call({
			method: 'alaiy_os_connector_shopify.api.sync.get_dashboard_stats',
			callback: function(r) {
				var s = r.message;
				if (!s) return;
				grid.innerHTML = render_stat_group('Alaiy OS (local)', [
					{label: 'Total items (all)', value: s.items_total},
					{label: 'Product templates', value: s.templates_total},
					{label: 'Pushed to Shopify', value: s.templates_pushed},
					{label: 'Pending export', value: s.templates_pending},
					{label: 'Variants (total)', value: s.variants_total},
					{label: 'Variants pushed', value: s.variants_pushed},
					{label: 'Listings (enabled / total)', value: s.listings_enabled + ' / ' + s.listings_total},
					{label: 'Orders synced', value: s.orders_synced},
				], 'local') + render_status_stat_group(s) + '<div id="shopify-side-stats">' + render_skeleton_group('Shopify (live)', 3) + '</div>';

				frappe.call({
					method: 'alaiy_os_connector_shopify.api.sync.get_shopify_side_stats',
					callback: function(r2) {
						var ss = r2.message;
						var target = document.getElementById('shopify-side-stats');
						if (!ss || !target) return;
						target.innerHTML = render_stat_group('Shopify (live)', [
							{label: 'Products in store', value: ss.shopify_products},
							{label: 'Variants in store', value: ss.shopify_variants},
							{label: 'Orders in store', value: ss.shopify_orders},
						], 'shopify');
					},
					error: function() {
						var target = document.getElementById('shopify-side-stats');
						if (target) target.innerHTML = '<div class="shopify-stat-group-title">Shopify (live) -- failed to load</div>';
					}
				});
			}
		});
	}

	check_connection();
	load_stats();
	refresh_logs();
	toggle_order_date_fields();

	$(page.body).find('.shopify-import-mode .shopify-mode-btn').on('click', function() {
		order_import_mode = $(this).data('mode');
		$(this).siblings().removeClass('shopify-mode-active');
		$(this).addClass('shopify-mode-active');
		toggle_order_date_fields();
	});

	document.getElementById('import-orders-btn').addEventListener('click', import_orders);
	document.getElementById('sync-inventory-btn').addEventListener('click', sync_inventory);
	document.getElementById('import-products-btn').addEventListener('click', import_products);
	document.getElementById('export-products-btn').addEventListener('click', export_products);
	document.getElementById('sync-taxonomy-btn').addEventListener('click', sync_taxonomy);
	document.getElementById('sync-tags-btn').addEventListener('click', sync_tags);
	document.getElementById('sync-collections-btn').addEventListener('click', sync_collections);
	document.getElementById('sync-locations-btn').addEventListener('click', sync_locations);
	$(page.body).on('click', '#shopify-stats-grid .shopify-stat-clickable', function() {
		frappe.set_route('List', 'Shopify Product Listing', { sh_shopify_status: $(this).data('status') });
	});
	document.getElementById('manage-listings-btn').addEventListener('click', function() {
		frappe.set_route('List', 'Shopify Product Listing');
	});
};
