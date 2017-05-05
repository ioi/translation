var task_text, translation_text;
var ques_id;
var version_particle_url, save_question_url , task_version_url, access_edit_translate_url,
        preview_url, unleash_trans_token_url;
var csrf_token;
var last_time_get_edit_token;
var latest_translation_text;
var simplemde;
var left_plain_text_box_id;
var rtl;
var last_version_particle_text;
var update_token_interval = 60 * 1000;
var previewInterval;

$(document).ready(function(){

    getEditTranslateAccess();

    if (rtl){
        left_plain_text_box_id = 'left_rtl_plain_text_box';
        $('#' + left_plain_text_box_id).moratab($('#'+left_plain_text_box_id).text(), {strings: {help: ''}});
        $('#left_rendered_text_box').css('direction', 'rtl');
    }
    else{

        left_plain_text_box_id = 'left_ltr_plain_text_box';
        $('#left_rendered_text_box').css('direction', 'ltr');
        simplemde = new SimpleMDE({
            element: document.getElementById('left_ltr_plain_text_box'),
            status: false,
            toolbar: false
        });
    }

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

    task_text = $("#right_text_box").html();
    translation_text = currentTranslationText();
    latest_translation_text = '';
    last_version_particle_text = currentTranslationText();
    window.setInterval(saveVersionParticle, update_token_interval)
    onPreviewClick();

});

function getDirectionStr(is_rtl){
    if(is_rtl)
        return 'rtl';
    return 'ltr';
}

function currentTranslationText(){
    if (rtl)
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
        renderMarkdown('right_text_box', current_text)
    }
}

function activeBtn(id){
    $('#preview-btn').removeClass('btn-active');
    $('#isc-preview-btn').removeClass('btn-active');
    $('#isc-markdown-btn').removeClass('btn-active');
    $(id).addClass('btn-active');
}

function onPreviewClick(){
    current_text = currentTranslationText();
    renderMarkdown('right_text_box', current_text);
    $('#right_text_box').css('direction', getDirectionStr(rtl));
    $('#right_text_box').css('whiteSpace', 'normal');
    previewInterval = setInterval(onlinePreview, 100);
    activeBtn('#preview-btn');
}

function onIscMarkdownClick(){
    $('#right_text_box').html(task_text);
    $('#right_text_box').css('direction', 'ltr');
    $('#right_text_box').css('whiteSpace', 'pre-wrap');
    clearInterval(previewInterval);
    activeBtn('#isc-markdown-btn');
}

function onIscPreviewClick(){
    renderMarkdown('right_text_box', task_text);
    $('#right_text_box').css('direction', 'ltr');
    $('#right_text_box').css('whiteSpace', 'normal');
    clearInterval(previewInterval);
    activeBtn('#isc-preview-btn');
}


function saveVersion() {
    getEditTranslateAccess();
    current_trans_text = currentTranslationText();
    var edit_token = sessionStorage.getItem('edit_translate_token_'+ques_id)
    $.ajax({
        url: save_question_url,
        data: {
            'content': currentTranslationText(),
             edit_token: edit_token,
            'id': ques_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            if (response.can_edit == false){
                window.location.replace(preview_url)
            }
            last_version_particle_text = current_trans_text;
            ToastrUtil.success('Successfully Saved ...');
        },
        complete: function () {
        },
        error: function (xhr, textStatus, thrownError) {
            alert('Error in connection');
        }
    });
    return false;
}

function saveVersionParticle() {
    current_trans_text = currentTranslationText();
    if (last_version_particle_text == current_trans_text)
        return;
    getEditTranslateAccess();
    var edit_token = sessionStorage.getItem('edit_translate_token_'+ques_id)
    $.ajax({
        url: version_particle_url,
        data: {
            'content': currentTranslationText(),
            'id': ques_id,
            edit_token: edit_token,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            if (response.can_edit == false){
                window.location.replace(preview_url)
            }
            last_version_particle_text = current_trans_text;
        },
        complete: function () {
        },
        error: function (xhr, textStatus, thrownError) {
            alert('Error in connection');
        }
    });
    return false;
}

function getEditTranslateAccess() {
    //TODO remove lag for transition to preview_url
    var edit_token = sessionStorage.getItem('edit_translate_token_'+ques_id)
    $.ajax({
        async: false,
        url: access_edit_translate_url,
        data: {
            id: ques_id,
            edit_token: edit_token,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            if (response.can_edit == false){
                window.location.replace(preview_url)
            }
            last_time_get_edit_token = new Date();
            sessionStorage.setItem('edit_translate_token_'+ques_id, response.edit_token)
        },
        error: function () {
            window.location.replace(preview_url)
        }
    });
}

window.onbeforeunload = function (e) {
    var edit_token = sessionStorage.getItem('edit_translate_token_'+ques_id)
    $.ajax({
        async: false,
        url: unleash_trans_token_url,
        data: {
            id: ques_id,
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

function checkIfCanChange(){
    current_date = new Date();
    if ((current_date - last_time_get_edit_token) >  update_token_interval)
        getEditTranslateAccess();
}
