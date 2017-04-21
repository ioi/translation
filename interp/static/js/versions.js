var version_url,
    particle_version_url,
    save_question_url,
    csrf_token,
    ques_id;

var selected_versions;

$(document).ready(function () {
    var cont = $('#original').text();
    $('#original').html(cont);

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

    var first_version;
    var second_version;
    get_version(selected_versions[0], function (response) {
        first_version = response;
        get_version(selected_versions[1], function (res) {
            second_version = res;
            var diff_fragment = DiffUtil.getDiffFragment(first_version, second_version);
            $('#myversion').html(diff_fragment);
        });
    });
}


function get_version(id, callback) {
    $.ajax({
        url: version_url,
        data: {
            'id': id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: callback
    });
}

function view_version(id){
    get_version(id, function (response) {
        $('#myversion').html(response);
    });
};

function view_particle_version(id){
    $.ajax({
        url: particle_version_url,
        data: {
            'id': id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            $('#myversion').html(response);
        }
    });

};


function revert(content){
    $.ajax({
        url: save_question_url,
        data: {
            'content': content,
            'id': ques_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            location.reload();
        },
    });
}

function revert_version(id) {
    $.ajax({
        url: version_url,
        data: {
            'id': id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            revert(response);
        }
    });
    return false;
}
function revert_particle_version(id) {
    $.ajax({
        url: particle_version_url,
        data: {
            'id': id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            revert(response);
        },
    });
}