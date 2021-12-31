// Common JavaScript code for all pages

$(document).ready(function(){

    // initialize tooltip
    $('[title]').tooltip({
        placement: 'bottom',
        trigger : 'hover',
        delay: {show: 400}
    }).on('click', function () {
        $(this).tooltip('hide')
    });

    // focus on an elemnt when modal is shown
    $(".modal").on('shown.bs.modal', function () {
        $("[data-modalfocus]", this).focus();
    });

});


function sendPrint(print_task_url) {
    bootbox.confirm({
        title: 'Confirm',
        message: "Are you sure to print ONE copy of this version?",
        buttons: {
            confirm: {label: 'Print'},
        },
        callback: function (result) {
            if (result)
                sendPrintJob(print_task_url);
        }
    });
}


function sendPrintJob(print_task_url) {
    $.ajax({
        url: print_task_url,
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            ToastrUtil.success(
                    'Printouts will be put to the DRAFTs desk for YOUR PICK-UP shortly.',
                    'Print job submitted.'
            ).css('width', '400px');;
        },
        error: function (response) {
            ToastrUtil.error('Print request failed.');
        }
    });
}

function validateFinalizeTranslation(contest_slug, tasks_length) {
    const frozen_tasks = document.querySelectorAll(
        `.task-row[data-contest-slug="${contest_slug}"][data-task-frozen="True"]`
    );
    if (frozen_tasks.length === tasks_length) {
        return confirm('Are you sure?');
    }

    const unfrozen_tasks = document.querySelectorAll(
        `.task-row[data-contest-slug="${contest_slug}"][data-task-frozen="False"]`
    );
    const unfrozen_task_names = Array.from(unfrozen_tasks)
          .map((el) => { return el.dataset.taskName});
    alert(`Please freeze the following task(s) first: ${unfrozen_task_names}`);
    return false;
}

