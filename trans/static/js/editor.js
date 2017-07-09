var task_id, task_text, translation_text;
var save_task_url, task_version_url, access_edit_translate_url,
    home_page_url, finish_translation_url, list_version_url, release_task_url;
var csrf_token;
var last_time_get_edit_token;
var latest_translation_text;
var simplemde;
var left_plain_text_box_id;
var direction, language;
var last_autosaved_text;
var previewInterval;
var spellChecking = false;

// Settings
var markdown_render_interval = 100;
var autosave_interval = 30 * 1000;
var update_token_interval = 60 * 1000;


$(document).ready(function() {

    getEditTranslateAccess();
    loadTranslationText();

});


function loadTranslationText() {
    $.ajax({
        url: get_latest_translation_url,
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function(response) {
            var text = '';
            if (response)
                text = response;
            initial(text);
        },
        error: function() {
            initial('');
        }
    });
}

function initial(text){
    if (direction=='rtl') {
        left_plain_text_box_id = 'left_rtl_plain_text_box';
        $('#' + left_plain_text_box_id).moratab(text, {strings: {help: ''}});
    }
    else {
        left_plain_text_box_id = 'left_ltr_plain_text_box';
        simplemde = new SimpleMDE({
            element: document.getElementById('left_ltr_plain_text_box'),
            status: false,
            toolbar: false,
            spellChecker: false,
            initialValue: text
        });
    }

    $('#left_rendered_text_box').css('direction', direction);
    task_text = $("#temp").html();
    translation_text = currentTranslationText();
    latest_translation_text = '';
    last_autosaved_text = currentTranslationText();
    setInterval(autoSave, autosave_interval)
    setInterval(onlinePreview, markdown_render_interval);
    onPreviewClick();
}

function currentTranslationText(){
    if (direction=='rtl')
        return $('#' + left_plain_text_box_id).text();
    return simplemde.value();
}

function renderMarkdown(id, text){
    $('#' + id).html(marked(text));
    renderMathInElement(document.getElementById(id));
}

function onlinePreview() {
    current_text = currentTranslationText();
    if (current_text != latest_translation_text){
        latest_translation_text = current_text;
        renderMarkdown('preview', current_text)
    }
}

function switchTab(id){
    var tabs = ['preview', 'isc-preview', 'isc-markdown'];
    for (var i = 0 ; i < 3 ; i++) {
        $('#' + tabs[i]).hide();
        $('#' + tabs[i] + '-btn').removeClass('btn-active');
    }
    $('#' + id).show();
    $('#' + id + '-btn').addClass('btn-active');
}

function onPreviewClick(){
    current_text = currentTranslationText();
    renderMarkdown('preview', current_text);
    switchTab('preview');
}

function onIscPreviewClick(){
    renderMarkdown('isc-preview', task_text);
    switchTab('isc-preview');
}

function onIscMarkdownClick(){
    $('#isc-markdown').html(task_text);
    switchTab('isc-markdown');
}

function autoSave() {
    saveVersion(true);
}

function saveAndGo(url) {
    saveVersion(true, function() {
        window.location.href = url;
    });
}

function saveVersion(autosave=false, callback=null) {
    current_trans_text = currentTranslationText();
    if (autosave && last_autosaved_text == current_trans_text) {
        if (callback)
            callback();
        return;
    }
    getEditTranslateAccess(function() {
        var edit_token = sessionStorage.getItem('edit_translate_token_' + task_id)
        $.ajax({
            url: save_task_url,
            data: {
                content: currentTranslationText(),
                id: task_id,
                saved: !autosave,
                edit_token: edit_token,
                csrfmiddlewaretoken: csrf_token
            },
            type: "POST",
            success: function (response) {
                if (response.can_edit == false)
                    handleAccessDenied();
                else {
                    last_autosaved_text = current_trans_text;
                    if (callback)
                        callback();
                    else if (!autosave)
                        ToastrUtil.success('Successfully Saved ...');
                }
            }
        });
    });
}

function getEditTranslateAccess(callback) {
    var edit_token = sessionStorage.getItem('edit_translate_token_' + task_id)
    $.ajax({
        // TODO: remove async = false
        async: false,
        url: access_edit_translate_url,
        data: {
            id: task_id,
            edit_token: edit_token,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function(response) {
            if (response.can_edit == false) {
                handleAccessDenied();
            } else {
                last_time_get_edit_token = new Date();
                sessionStorage.setItem('edit_translate_token_' + task_id, response.edit_token);
                if (callback)
                    callback();
            }
        },
        error: function () {
            handleAccessDenied();
        }
    });
}

function releasToken() {
    var edit_token = sessionStorage.getItem('edit_translate_token_' + task_id)
    $.ajax({
        async: false,
        url: finish_translation_url,
        data: {
            id: task_id,
            edit_token: edit_token,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
        },
        error: function () {
        }
    });
};

function handleAccessDenied(){
    bootbox.alert({
        // title: 'Alert',
        message: "<b>The task is open somewhere else!</b>",
        buttons: {
            ok: {label: 'Back to Home'},
        },
        callback: function (result) {
            window.location.replace(home_page_url);
        }
    });
}

function checkIfCanChange(){
    current_date = new Date();
    if ((current_date - last_time_get_edit_token) >  update_token_interval)
        getEditTranslateAccess();
}

window.onbeforeunload = function(){
    autoSave();
    releasToken();
    document.getElementById(left_plain_text_box_id).reset();
};


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

function release() {
    autoSave();
    bootbox.prompt({
        title: 'Release Note:',
        buttons: {
            confirm: {label: 'Release'},
        },
        callback: function (result) {
            if (result)
                sendRelease(result);
            else if (result == '') {
                ToastrUtil.error('Release note cannot be empty.');
            }
        }
    });
}

function sendRelease(note) {
    $.ajax({
        url: release_task_url,
        data: {
            release_note: note,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            last_saved_content = simplemde.value();
            ToastrUtil.success('Task Released...');
        },
        error: function (response) {
            ToastrUtil.error('Release failed.');
        }
    });
}
