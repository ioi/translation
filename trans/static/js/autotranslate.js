var auto_translate_api_url;
var original_text_changed_since_last_set = false;
function showTranslationPane() {
    var translationPaneDiv = document.getElementById('translation-pane');
    translationPaneDiv.classList.remove('closedPane');
}

function hideTranslationPane() {
    var translationPaneDiv = document.getElementById('translation-pane');
    translationPaneDiv.classList.add('closedPane');
}

function updateTranslate(response, textStatus, jqXHR) {
    if (jqXHR.status === 200) {
        if (response.success) {
            $("#translated_text").text(response.translated_text)
            $("#copy-translation-btn").removeClass("disabled")
            $("#user_translation_quota").text(response.new_quota)
        } else {
            $("#translated_text").text(response.message)
            
        }
    } else {
        $("#translated_text").text("Error.")
    }
    $("#translate_submit").removeAttr("disabled")
}
function sendTranslate() {
    $("#translate_submit").attr("disabled", true)
    $("#copy-translation-btn").removeClass("copied")
    $("#copy-translation-btn").addClass("disabled")
    $("#translated_text").text("Translating...")
    $.ajax({
        url: auto_translate_api_url,
        data: {
            input_lang: $("#input_lang").val(),
            output_lang: $("#output_lang").val(),
            content: $("#content_for_translate").val(),
            csrfmiddlewaretoken: csrf_token,
        },
        type: "POST",
        
    }).always(updateTranslate)
    
}

function translateSelectedText() {
    let selected_text =  getSelectedText();
    if (selected_text.length > 0)
    {
        var overwrite_text;
        if (original_text_changed_since_last_set)
            overwrite_text = confirm("You have changed the original content manually. Do you want to overwrite it with the selected text?")
        else
            overwrite_text = true;
        if (overwrite_text) {
            $("#content_for_translate").val(getSelectedText());
            $("#translate_submit").click()
            original_text_changed_since_last_set = false;
        }
    }
}

function translateDroppedText(event) {
    event.preventDefault();
    const data = event.dataTransfer.getData('text');
    $("#content_for_translate").val(data);
    $("#translate_submit").click()
    original_text_changed_since_last_set = false;
}

function rememberChanged() {
    original_text_changed_since_last_set = true;
}

function copyTranslatedText() {
    if ($("#copy-translation-btn").hasClass("disabled"))
        return null;
    navigator.clipboard.writeText($("#translated_text").text()).then(function () {
        $("#copy-translation-btn").addClass("copied")
    })
}

function resetCopyMarker() {
    $("#copy-translation-btn").removeClass("copied")
}