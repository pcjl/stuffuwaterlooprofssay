jQuery(function($) {
    $('form').submit(function(e) {
        e.preventDefault();

        var form = $('form');
        var submitButton = $('button[type=submit]');
        submitButton.addClass('disabled');
        submitButton.prop('disabled', true);

        $.ajax({
            url: form.attr('url'),
            type: form.attr('method'),
            data: form.serialize(),
            error: function(jqXHR) {
                Snackbar.show( {
                    text: "Your username and/or password are invalid. Please try again.",
                    actionTextColor: "#FFEB3B",
                });

                submitButton.removeClass('disabled');
                submitButton.prop('disabled', false);
            },
            success: function(data, textStatus, jqXHR) {
                window.location.href = "/"
            }
        });

        return false;
    });
});
