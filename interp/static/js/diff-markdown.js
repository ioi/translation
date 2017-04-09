/**
 *
 * @param original
 * @param changed
 * @returns {DocumentFragment}
 */
function diff_markdown(original, changed){

    var diff = JsDiff.diffChars(original, changed),
        fragment = document.createDocumentFragment();

    diff.forEach(function(part){
      var color = part.added ? 'green' :
        part.removed ? 'red' : 'grey';
      var span = document.createElement('span');
      span.style.color = color;
      span.appendChild(document.createTextNode(part.value));
      fragment.appendChild(span);
    });

    return fragment;
}

