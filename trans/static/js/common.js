// Common JavaScript code for all pages

$(document).ready(function(){

    // initialize tooltip
    $('[title]').tooltip({
        placement: 'bottom',
        trigger : 'hover',
        delay: {show: 400}
    });

    // focus on an elemnt when modal is shown
    $(".modal").on('shown.bs.modal', function () {
        $("[data-modalfocus]", this).focus();
    });

});
