var selected_versions,
    task_version_url,
    csrf_token,
    task_versions;

$(document).ready(function () {

    getVersions();
    selected_versions = [];
});


function changeCheckbox(id) {
    var index = selected_versions.indexOf(id);
    if(index == -1){
        if(selected_versions.length == 2){
            var temp = selected_versions[0];
            $('#'+temp).prop('checked', false);
            selected_versions.splice(0, 1);
        }
        selected_versions.push(id);
    }else{
        selected_versions.splice(index, 1);
    }
}

function diff(){
    var f,s;
    $.each(task_versions, function(index, version) {
        if(version.id == selected_versions[0])
            f = version.text;
        if(version.id == selected_versions[1])
            s = version.text;
    });
    var diff_fragment = DiffUtil.getDiffFragment(f, s);
    $('#myversion').html(diff_fragment);
}

function view_version(id){
    $.each(task_versions, function(index, version) {
        if(version.id == id)
            $('#myversion').html(version.text);
    });
};


function getVersions() {
    $.ajax({
        url: task_version_url,
        data: {
            published: true,
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            task_versions = response.versions;
        }
    });
    return false;
}