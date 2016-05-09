$(document).ready(function() {

    $("#createAccountButton").click(function () {
        $(".vbox-login").fadeOut(1, function () {
            $(".vbox-create-user").fadeIn(1);
        })
    });

    $(".vbox-intro-message").fadeOut(1, function () {
        $(".vbox-login").fadeIn(1);
    });
});
