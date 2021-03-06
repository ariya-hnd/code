odoo.define('loyality_point_history.loyality_point_history', function (require) {
"use strict";
	var pos_orders = require('pos_orders.pos_orders');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var QWeb = core.qweb;
	var screens = require('point_of_sale.screens');
	var models = require('point_of_sale.models');
	var PopupWidget = require('point_of_sale.popups');
	var _t = core._t;
	var SuperOrder = models.Order;
	var SuperOrderline =  models.Orderline.prototype;
	var SuperPosModel = models.PosModel.prototype;
	var formats = require('web.formats');

	models.load_fields('pos.order','loyalty_points');
	var order_model = null;
	var order_line_model = null;
	var model_list = models.PosModel.prototype.models
	for(var i = 0,len = model_list.length;i<len;i++){
		if(model_list[i].model == "pos.order")
			order_model = model_list[i];
		else if(model_list[i].model == "pos.order.line")
			order_line_model = model_list[i];
	}
	order_model.fields.push('return_order_id','statement_ids','is_return_order','return_status','amount_total','loyalty_points');

    pos_orders.include({
        render_list: function(order, input_txt) {
			var self = this;
			var customer_id = this.get_customer();
			var new_order_data = [];
			if(customer_id != undefined){
				for(var i=0; i<order.length; i++){
					if(order[i].partner_id[0] == customer_id)
						new_order_data = new_order_data.concat(order[i]);
				}
				order = new_order_data;
			}
			if (input_txt != undefined && input_txt != '') {
				var new_order_data = [];
				var search_text = input_txt.toLowerCase()
				for (var i = 0; i < order.length; i++) {
					if (order[i].partner_id == '') {
						order[i].partner_id = [0, '-'];
					}
					if (((order[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
						new_order_data = new_order_data.concat(order[i]);
					}
				}
				order = new_order_data;
			}
			var contents = this.$el[0].querySelector('.wk-order-list-contents');
			contents.innerHTML = "";
			var wk_orders = order;
			for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
				var wk_order = wk_orders[i];
				var orderline_html = QWeb.render('WkOrderLine', {
					widget: this,
					order: wk_orders[i],
					customer_id:wk_orders[i].partner_id[0],
				});
				var orderline = document.createElement('tbody');
				orderline.innerHTML = orderline_html;
				orderline = orderline.childNodes[1];
				contents.appendChild(orderline);
			}
		}
    });

});

