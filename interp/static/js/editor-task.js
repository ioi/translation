var simplemde,
    last_saved_content,
    csrf_token,
    task_id,
    save_task_url,
    publish_task_url;

$(document).ready(function(){

    simplemde = new SimpleMDE({
        element: document.getElementById("task-markdown"),
        status: false,
        toolbar: false
    });

    marked.setOptions({
        renderer: new marked.Renderer(),
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: false,
        smartLists: true,
        smartypants: false
    });



    last_saved_content = simplemde.value();
    window.setInterval(online_preview, 1000);
});


function online_preview() {
    var mycontent = simplemde.value();
    $('#task-preview').html(marked(mycontent));
    renderMathInElement(document.getElementById("task-preview"));
}

function send_data() {
    $.ajax({
        url: save_task_url,
        data: {
            'title': $('#task-title').val(),
            'content': simplemde.value(),
            'id': task_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            last_saved_content = simplemde.value();
            ToastrUtil.success('Saved ...');
        }
    });
    return false;
}

function publishLastVersion() {
    //TODO required change_log_note
    $.ajax({
        url: publish_task_url,
        data: {
            'id': task_id,
            'is_published': 'True',
            'change_log': $('#change-log').val(),
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            $('#change_log').val("");
            $('#myModal').modal('toggle');
            ToastrUtil.success('Published...');
        }
    });
}/**
 * Created by ali on 4/21/17.
 */
