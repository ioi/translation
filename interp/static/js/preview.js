var task_text, translation_text;
var ques_id;
var csrf_token;
var task_version_url;
var rtl;
var task_versions;
var last_task_version_text;

function getDirectionStr(is_rtl){
    if(is_rtl)
        return 'rtl'
    return 'ltr'
}

$(document).ready(function(){

        $('#left_rendered_text_box').css('direction', getDirectionStr(rtl));
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

        renderMarkdown('left_rendered_text_box', currentTranslationText());
        renderMarkdown('right_text_box', task_text);
//        $('#interactive-checkbox').prop("checked", false);
//        $('#editor-checkbox').prop("checked", false);
//        $('#original-checkbox').prop("checked", false);
//        $('#diff-checkbox').prop("checked", false);
//        $('#diff-selectbox').prop("disabled", true);
//        updateInteractive();
//        updateTranslationTextBox();
//        updateTaskTextBox();

//        toggleDiv(left_plain_text_box_id);

//        window.setInterval(saveVersionParticle,60*1000)
        getTaskVersions();
});

function currentTranslationText(){
    return $('#left_plain_text_box').text();
}

function renderMarkdown(id, text){
    $('#' + id).html(marked(text));
    renderMathInElement(document.getElementById(id));
}


function updateSyncTime(){
    //TODO
//    $('#sync_time').html(new Date().toLocaleString());
}



function updateTaskTextBox(){
    if($("#original-checkbox").is(":checked")){
        $('#right_text_box').html(task_text)
//        $('#diff_material').show()
    }else{
        renderMarkdown('right_text_box', task_text)
        $('#diff-checkbox').prop("checked", false);
//        $('#diff_material').hide()
    }
}

function updateDiffTextBox(){
    if($("#diff-checkbox").is(":checked")) {
//        $('#diff-selectbox').prop("disabled", false);
        var selected_for_diff = $("#diff-selectbox").val();
        var diff_fragment = DiffUtil.getDiffFragment(last_task_version_text, selected_for_diff);
        $('#right_text_box').html(diff_fragment);
    }else{
//        $('#diff-selectbox').prop("disabled", true);
        updateTaskTextBox()
    }
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
