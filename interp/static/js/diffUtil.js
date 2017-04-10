
function DiffUtil(){

    /**
     *
     * @param original, text
     * @param changed, text
     * @returns {DocumentFragment}, diff of original and changed. Highlight added part by green color and removed part by red color
     */
    DiffUtil.getDiffFragment = function(original, changed){

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

    /**
     *
     * @param element
     */
    DiffUtil.clearElement = function(element){
        while (element.firstChild) {
           element.removeChild(element.firstChild);
        }
    }

    /**
     * clear element and append diff of original and changed text to it
     *
     * @param original
     * @param changed
     * @param element
     */
    DiffUtil.appendDiffFragmentToElement = function(original, changed, element){
        var fragment = DiffUtil.getDiffFragment(original, changed);
        DiffUtil.clearElement(element);
        element.appendChild(fragment);
    }

}

DiffUtil();
