jQuery(function($) {
    $('form').submit(function(e) {
        e.preventDefault();

        var form = $('form');
        var submitButton = $('button[type=submit]');
        submitButton.button('loading');

        $.ajax({
            url: form.attr('url'),
            type: form.attr('method'),
            data: form.serialize(),
            error: function(jqXHR) {
                Snackbar.show( {
                    text: "Your username and/or password are invalid. Please try again.",
                    actionTextColor: "#FFEB3B",
                });

                submitButton.button('reset');
            },
            success: function(data, textStatus, jqXHR) {
                window.location.href = "/"
            }
        });

        return false;
    });
});
