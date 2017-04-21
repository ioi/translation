var rtl;

$(document).ready(function(){

    if (rtl){
        $('#markdown-box').moratab($('#markdown-box').text(), {strings: {help: ''}});
        $('#preview-box').css('direction', 'rtl');
    }
    else{

        $('#preview-box').css('direction', 'ltr');
        simplemde = new SimpleMDE({
            element: document.getElementById('markdown-box'),
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


    renderMarkdown('preview-box', currentTranslationText());
    $('#markdown-box').hide();
});

function currentTranslationText(){
    if (rtl)
        return $('#markdown-box').text();
    return simplemde.value();
}

function renderMarkdown(id, text){
    $('#' + id).html(marked(text));
    renderMathInElement(document.getElementById(id));
}