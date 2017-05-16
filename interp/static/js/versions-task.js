var task_version_url,
    csrf_token,
    task_versions;

$(document).ready(function () {
    getVersions();
});


function diff(id1, id2){
    $('#version-' + id1).addClass('active').siblings().removeClass('active');
    var text1, text2;
    $.each(task_versions, function(index, version) {
        if(version.id == id1)
            text1 = version.text;
        if(version.id == id2)
            text2 = version.text;
    });
    if(!text2){
        view_version(text1)
    }else {
        var diff_fragment = DiffUtil.getDiffFragment(text2, text1);
        $('#myversion').html(diff_fragment);
    }

}

function view_version(text){
    $('#myversion').html(text);
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

            // onclick first row
            if(task_versions[0]){
                if(task_versions[1])
                    diff(task_versions[0].id, task_versions[1].id)
                else
                    view_version(task_versions[0].text)
            }
        }
    });
    return false;
}