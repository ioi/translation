var csrf_token,
    notification_url,
    websocket_url,
    redis_heartbeat;


$(document).ready(function(){
   var ws4redis = WS4Redis({
       uri: websocket_url + 'notifications?subscribe-broadcast&publish-broadcast&echo',
       heartbeat_msg: redis_heartbeat,
       // receive a message though the Websocket from the server
       receive_message: function (msg) {
           //TODO
       }
   });

   // getTaskVersions();

});

function getTaskVersions() {
    $.ajax({
        url: notification_url,
        data: {
            csrfmiddlewaretoken: csrf_token
        },
        type: "GET",
        success: function (response) {
            var notifications = response.notifications;
            var dropdown = $("#notification-dropdown");
            $.each(notifications, function() {
                dropdown.append($("<li />").text(this.text));
            });
        }
    });
    return false;
}