var auto_translate_api_url;
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
        $("#content_for_translate").val(getSelectedText());
        $("#translate_submit").click()
    }
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