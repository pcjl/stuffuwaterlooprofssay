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
                $('.form-group[name="password"]').addClass("has-error");
                submitButton.button('reset');
            },
            success: function(data, textStatus, jqXHR) {
                window.location = "/"
            }
        });

        return false;
    });
});
