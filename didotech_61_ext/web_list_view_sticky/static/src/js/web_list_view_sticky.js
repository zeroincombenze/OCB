openerp.web_list_view_sticky = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    //Sticky Table Header
    $(window).scroll(function() {
        var active_tab = $('li.ui-state-active');
        if(active_tab.length == 1){
            var active_tab_div_id = active_tab.find("a")[0].hash;
            if(active_tab_div_id.length > 1){
                var active_tab_div = $(active_tab_div_id);
                if(active_tab_div.length >= 1){
                    var one2many_length = active_tab_div.find('.oe_form_frame_cell.oe_form_field_one2many').length;
                    if(one2many_length == 0) {
                        active_tab_div.find('table.oe-listview-content').addClass('stickty_table_header');
                        var firstSection = active_tab_div.find("tr.oe-listview-header-columns:first").outerHeight();
                        if(firstSection) {
                            header_last_child = active_tab_div.find('tr.oe-listview-header-columns:last-child').children();
                            header_last_child.css('top', firstSection);
                        }
                    }
                }
            }
        }
    });
};