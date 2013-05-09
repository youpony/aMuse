(function($) {
  $('.other-images').find('img').on('click', function(e) {
    var t = e.target;
    console.log(t + "clicked");
    $(t).closest('.image-wrapper').find('.item-image').attr('src', $(t).attr('src'));
  });
} (jQuery));
