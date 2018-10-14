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
                    text: "An error has occurred. Please try again.",
                    actionTextColor: "#FFEB3B",
                });

                submitButton.removeClass('disabled');
                submitButton.prop('disabled', false);
            },
            success: function(data, textStatus, jqXHR) {
                Snackbar.show( {
                        text: "Post successful!",
                        showActionButton: true,
                        actionText: "View Post",
                        actionTextColor: "#FFEB3B",
                        onActionClick: function() {
                            window.open("http://www.facebook.com/" + JSON.parse(jqXHR.responseText).id, "_blank");
                        }
                    }
                );

                submitButton.removeClass('disabled');
                submitButton.prop('disabled', false);
            },
        });

        return false;
    });

    $('#datetimepicker').datetimepicker();

    $('.btn-default').click(function() {
        $('textarea').val("");
        $('input[type=text]').val("");
        $('input[type=checkbox]').prop('checked', true);
    });
});
