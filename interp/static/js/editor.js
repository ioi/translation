var task_text, translation_text;
var ques_id;
var version_particle_url;
var csrf_token;
var save_question_url;
var task_version_url;
var latest_translation_text;
var online_prev;
var simplemde;
var left_plain_text_box_id;
var rtl;
var task_versions;
var last_task_version_text;
var last_version_particle_text;


var interactive_checkbox;
var markdown_checkbox;
var diff_checkbox;

function getDirectionStr(is_rtl){
    if(is_rtl)
        return 'rtl'
    return 'ltr'
}

function toggleDiv(id){
    $('#'+id).siblings().hide();
    $('#'+id).show();
}

$(document).ready(function(){

        if (rtl){
            left_plain_text_box_id = 'left_rtl_plain_text_box';
            $('#' + left_plain_text_box_id).moratab($('#'+left_plain_text_box_id).text(), {strings: {help: ''}});
            $('#left_rendered_text_box').css('direction', 'rtl');
        }
        else{

            left_plain_text_box_id = 'left_ltr_plain_text_box';
            $('#left_rendered_text_box').css('direction', 'ltr');
            simplemde = new SimpleMDE({
            element: document.getElementById('left_ltr_plain_text_box')[0],
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


        interactive_checkbox = false;
        markdown_checkbox = false;
        diff_checkbox = false;
        updateInteractive();

        window.setInterval(saveVersionParticle,60*1000)
        getTaskVersions();
});

function changeActive(id, active){
    if(active)
        $(id).addClass('active');
    else
        $(id).removeClass('active');
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


function updateSyncTime(){
    //TODO
//    $('#sync_time').html(new Date().toLocaleString());
}


function updateInteractive() {
    interactive_checkbox = !interactive_checkbox;
    changeOnlinePreview(interactive_checkbox);
    changeActive('#interactive-btn', interactive_checkbox);

    if(interactive_checkbox){
        markdown_checkbox = false;
        diff_checkbox = false;
        $('#markdown-btn').hide();
        $('#diff-btn').hide();
        $('#diff-selectbox').hide();
        changeActive('#diff-btn', diff_checkbox);
        changeActive('#markdown-btn', markdown_checkbox);
    }else{
        $('#markdown-btn').show();
        updateMarkdown();
    }
}

function updateMarkdown(){
    markdown_checkbox = !markdown_checkbox;
    changeActive('#markdown-btn', markdown_checkbox);

    if(markdown_checkbox){
        toggleDiv(left_plain_text_box_id);
        $('#right_text_box').html(task_text);
        $('#diff-btn').show();
    }else{
        renderMarkdown('right_text_box', task_text);
        renderMarkdown('left_rendered_text_box', currentTranslationText())
        toggleDiv('left_rendered_text_box');

        diff_checkbox = false;
        changeActive('#diff-btn', diff_checkbox);
        $('#diff-btn').hide();
        $('#diff-selectbox').hide();
    }
}

function updateDiff(){
    diff_checkbox = !diff_checkbox;
    changeActive('#diff-btn', diff_checkbox);

    if(diff_checkbox) {
        $('#diff-selectbox').show();
        updateVersion();
    }else{
        $('#diff-selectbox').hide();
        $('#right_text_box').html(task_text);
    }
}

function updateVersion(){
    var selected_for_diff = $("#diff-selectbox").val();
    var diff_fragment = DiffUtil.getDiffFragment(last_task_version_text, selected_for_diff);
    $('#right_text_box').html(diff_fragment);
}

function changeOnlinePreview(is_enable){
    if (is_enable){
        $('#right_text_box').css('direction', getDirectionStr(rtl));
        online_prev = true;
        window.setInterval(onlinePreview,100);
    }
    else{
        $('#right_text_box').css('direction', 'ltr');
        online_prev = false;
        window.setInterval(onlinePreview,1000*1000);
    }
    latest_translation_text = '';
    onlinePreview()
}

function onlinePreview() {
    if (online_prev == true){
        current_text = currentTranslationText();
        if (current_text != latest_translation_text){
            latest_translation_text = current_text;
            renderMarkdown('right_text_box', current_text)
        }
    }
}

function saveVersion() {
    $.ajax({
        url: save_question_url,
        data: {
            'content': currentTranslationText(),
            'id': ques_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            updateSyncTime();
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
    $.ajax({
        url: version_particle_url,
        data: {
            'content': currentTranslationText(),
            'id': ques_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            last_version_particle_text = current_trans_text;
            updateSyncTime();
        },
        complete: function () {
        },
        error: function (xhr, textStatus, thrownError) {
            alert('Error in connection');
        }
    });
    return false;
}

function getTaskVersions() {
    $.ajax({
        url: task_version_url,
        data: {
            published: true,
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            task_versions = response.versions;
            var options = $("#diff-selectbox");
            $.each(task_versions, function() {
                options.append($("<option />").val(this.text).text(this.create_time));
                last_task_version_text = this.text;
            });
        }
    });
    return false;
}
