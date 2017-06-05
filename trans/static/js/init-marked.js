
// Initilize Makrded.js Renderer

var renderer = new marked.Renderer();

// enable resize option for images
renderer.image = function(href, title, text) {
    var tags = '';
    if (title) {
        size = title.split('x');
        if (size[1])
            tags = 'width=' + size[0] + ' height=' + size[1];
        else
            tags = 'width=' + size[0];
    }
    return ('<img src="' + href + '" alt="' + text + '" ' + tags + '>');
};

// remove trailing newline in code blocks
renderer.code = function(code, language) {
    return ('<pre><code>' + code + '</code></pre>');
};

// global options
marked.setOptions({
    renderer: renderer,
    gfm: true,
    tables: true,
    breaks: true,
    pedantic: false,
    sanitize: false,
    smartLists: true,
    smartypants: false
});
