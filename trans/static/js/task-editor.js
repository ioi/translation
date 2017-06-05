var simplemde,
    last_saved_content,
    csrf_token,
    save_task_url,
    publish_task_url,
    spellChecking;

$(document).ready(function(){

    simplemde = new SimpleMDE({
        element: document.getElementById("left_ltr_plain_text_box"),
        status: false,
        toolbar: false,
        spellChecker: false
    });

    spellChecking = false;

    last_saved_content = simplemde.value();
    window.setInterval(online_preview, 1000);
});

function onChangeSpellChecking(){
    spellChecking = !spellChecking;
    var value = simplemde.value();

    /* reset simpleMDE container */
    var element = document.getElementById("left_text_box_container");
    while (element.firstChild) {
       element.removeChild(element.firstChild);
    }
    var textarea = document.createElement('textarea');
    textarea.setAttribute('id', 'left_ltr_plain_text_box');
    element.appendChild(textarea);

    /* new simpleMDE */
    simplemde = new SimpleMDE({
        element: document.getElementById("left_ltr_plain_text_box"),
        status: false,
        toolbar: false,
        spellChecker: spellChecking,
        initialValue: value
    });
}


function online_preview() {
    var mycontent = simplemde.value();
    $('#task-preview').html(marked(mycontent));
    renderMathInElement(document.getElementById("task-preview"));
}

function save(publish) {
    var note = $('#release-note').val();
    if (publish & note == '') {
        alert('Release note is empty.');
        return false;
    }
    $.ajax({
        url: save_task_url,
        data: {
            'content': simplemde.value(),
            'publish': publish,
            'release_note': note,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            last_saved_content = simplemde.value();
            $('#saveModal').modal('hide');
            if (publish)
                ToastrUtil.success('Task Published...');
            else
                ToastrUtil.success('Saved...');
        }
    });
    return false;
}

window.onbeforeunload =  function(){
    if(last_saved_content != simplemde.value())
        return 'Leave without saving?';
};


/**
 * Created by ali on 4/21/17.
 */
