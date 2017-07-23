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
                Snackbar.show( {
                        text: "Post successful!",
                        showActionButton: true,
                        actionText: "View Post",
                        onActionClick: function() {
                            window.open("http://www.facebook.com/" + JSON.parse(jqXHR.responseText).id, "_blank");
                        }
                    }
                );

                submitButton.button('reset');
            },
        });

        return false;
    });

    $('#datetime').datetimepicker({
        showClear: true,
        showClose: true,
        focusOnShow: false,
    });

    $('.btn-default').click(function() {
        $('textarea').val("");
        $('input[type=text]').val("");
    });
});
