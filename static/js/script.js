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
                var response = JSON.parse(jqXHR.responseText);

                var published = response.post_id !== undefined;

                var appUrl = published ? "fb://photo/" + response.id : "fb://profile/" + response.page_id;
                var fallbackUrl = "http://www.facebook.com/" + response.id;

                Snackbar.show( {
                        text: "Post successful!",
                        showActionButton: true,
                        actionText: "View Post",
                        onActionClick: function() {
                            window.location = appUrl;
                            setTimeout(function(){
                                window.open(fallbackUrl, "_blank");
                            }, 500);
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
