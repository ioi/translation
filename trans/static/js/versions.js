var version_url,
    particle_version_url,
    checkout_version_url,
    csrf_token,
    ques_id,
    version_to_revert_id,
    list_version_url;

$(document).ready(function () {
    var cont = $('#original').text();
    $('#original').html(cont);
    getListVersions();

});

function selectVersion(id){
    $(id).addClass('active').siblings().removeClass('active');
}

function diff(id1, id2){
    if(!id2){
        view_version(id1);
    }else {
        var first_version;
        var second_version;
        get_version(id1, function (response) {
            first_version = response;
            get_version(id2, function (res) {
                second_version = res;
                var diff_fragment = DiffUtil.getDiffFragment(second_version, first_version);
                $('#myversion').html(diff_fragment);
                selectVersion('#version-' + id1);
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
        selectVersion('#version-' + id);
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
            selectVersion('#particle-version-0');
            get_version(list_versions[0]['id'], function (res) {
                second_version = res;
                var diff_fragment = DiffUtil.getDiffFragment(res, response);
                $('#myversion').html(diff_fragment);
            });
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

function getListVersions() {
    $.ajax({
        url: list_version_url,
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            list_versions = response.versions;
            list_version_particles = response.version_particles;

            // onclick first row
            if(list_version_particles && list_version_particles.length){
                view_particle_version(list_version_particles[0]['id']);
            }else if(list_versions[0]){
                if(list_versions[1])
                    diff(list_versions[0]['id'], list_versions[1]['id']);
                else
                    view_version(list_versions[0]['id'])
            }
        }
    });
    return false;
}
