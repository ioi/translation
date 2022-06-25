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
        message: "Are you sure to print a copy of this version?",
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
                    'Your printout will be delivered to you shortly.',
                    'Print job submitted.'
            ).css('width', '400px');;
        },
        error: function (response) {
            ToastrUtil.error('Print request failed.');
        }
    });
}

function validateFinalizeTranslation(contest_slug, tasks_length, is_translating) {
    // Check tasks frozenness. Skip check for all not translating.
    if (is_translating == 'True') {
        const frozen_tasks = document.querySelectorAll(
            `.task-row[data-contest-slug="${contest_slug}"][data-task-frozen="True"]`
        );
        if (frozen_tasks.length !== tasks_length) {
            const unfrozen_tasks = document.querySelectorAll(
                `.task-row[data-contest-slug="${contest_slug}"][data-task-frozen="False"]`
            );
            const unfrozen_task_names = Array.from(unfrozen_tasks)
                  .map((el) => el.dataset.taskName);
            alert(`Please finalize the following task(s) first: ${unfrozen_task_names}`);
            return false;
        }
    }
    // It doesn't make sense for the two extra countries to be the same.
    const querySelectElementValue = (name) =>
          document.querySelector(
              `form[data-contest-slug="${contest_slug}"] select[name="${name}"]`
          ).value;
    const queryOptionElementText = (name, value) =>
          document.querySelector(
              `form[data-contest-slug="${contest_slug}"] select[name="${name}"] ` +
                  `option[value="${value}"]`
          ).text;
    const extra_country_1_code =
          querySelectElementValue('extra_country_1_code');
    const extra_country_1_count =
          parseInt(querySelectElementValue('extra_country_1_count'));
    const extra_country_1_text =
          queryOptionElementText('extra_country_1_code', extra_country_1_code);
    const extra_country_2_code =
          querySelectElementValue('extra_country_2_code');
    const extra_country_2_count =
          parseInt(querySelectElementValue('extra_country_2_count'));
    const extra_country_2_text =
          queryOptionElementText('extra_country_2_code', extra_country_2_code);
    if (extra_country_1_count > 0 && extra_country_2_count > 0 &&
        extra_country_1_code === extra_country_2_code &&
        extra_country_1_code.length > 0) {
        alert('Additional translations #1 & #2 should be different!');
        return false;
    }

    // Build final confirmation / error message.
    const confirmation_messages = [];
    const error_messages = [];
    if (extra_country_1_code.length > 0) {
        const detail = `${extra_country_1_text}: ${extra_country_1_count}`;
        if (extra_country_1_count === 0) {
            error_messages.push(
                `${detail}\n  Did you forget to specify the number of contestants?`
            );
        } else {
            confirmation_messages.push(detail);
        }
    } else if (extra_country_1_count > 0) {
        error_messages.push('Did you forget to specify additional translation #1?');
    }
    if (extra_country_2_code.length > 0 && extra_country_1_code !== extra_country_2_code) {
        const detail = `${extra_country_2_text}: ${extra_country_2_count}`;
        if (extra_country_2_count === 0) {
            error_messages.push(
                `${detail}\n  Did you forget to specify the number of contestants?`
            );
        } else {
            confirmation_messages.push(detail);
        }
    } else if (extra_country_2_code.length === 0 && extra_country_2_count > 0) {
        error_messages.push('Did you forget to specify additional translation #2?');
    }

    if (extra_country_1_count > 0 || extra_country_2_count > 0) {
        confirmation_messages.unshift('Requested additional translations:');
    }

    confirmation_messages.push('Are you sure you want to submit your translation? This CANNOT be undone!');

    if (error_messages.length > 0) {
        alert(error_messages.join('\n\n'));
        return false;
    }
    return confirm(confirmation_messages.join('\n\n'));
}
