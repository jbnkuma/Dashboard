//marquesina 
var scrl = " GEA-CUI ";
function scrlsts() {
    scrl = scrl.substring(1, scrl.length) + scrl.substring(0, 1);
    document.title = scrl;
    setTimeout("scrlsts()", 300);
}
//menu
jQuery.noConflict();

jQuery(function () {
    jQuery('#menu1 li a').click(function (event) {
        var elem = jQuery(this).next();
        if (elem.is('ul')) {
            event.preventDefault();
            jQuery('#menu1 ul:visible').not(elem).slideUp();
            elem.slideToggle();
        }
    });
});
