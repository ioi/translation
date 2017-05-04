var version_url,
    particle_version_url,
    checkout_version_url,
    csrf_token,
    ques_id,
    version_to_revert_id;

$(document).ready(function () {
    var cont = $('#original').text();
    $('#original').html(cont);

});

function diff(id1, id2){

    $('#version-' + id1).addClass('active').siblings().removeClass('active');

    if(!id2){
        view_version(id1);
    }else {
        var first_version;
        var second_version;
        get_version(id1, function (response) {
            first_version = response;
            get_version(id2, function (res) {
                second_version = res;
                var diff_fragment = DiffUtil.getDiffFragment(first_version, second_version);
                $('#myversion').html(diff_fragment);
            });
        });
    }
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

function revert(version_id){
    version_to_revert_id = version_id;
}
function revert_confirm(){
    $.ajax({
        url: checkout_version_url,
        data: {
            'id': version_to_revert_id,
            csrfmiddlewaretoken: csrf_token
        },
        type: "POST",
        success: function (response) {
            location.reload();
        },
    });
}
