$(document).on('click', '.panel-heading span.icon_minim', function (e) {
    var $this = $(this);
    if (!$this.hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideUp();
        $this.addClass('panel-collapsed');
        $this.removeClass('glyphicon-minus').addClass('glyphicon-plus');
    } else {
        $this.parents('.panel').find('.panel-body').slideDown();
        $this.removeClass('panel-collapsed');
        $this.removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});
$(document).on('focus', '.panel-footer input.chat_input', function (e) {
    var $this = $(this);
    if ($('#minim_chat_window').hasClass('panel-collapsed')) {
        $this.parents('.panel').find('.panel-body').slideDown();
        $('#minim_chat_window').removeClass('panel-collapsed');
        $('#minim_chat_window').removeClass('glyphicon-plus').addClass('glyphicon-minus');
    }
});

$(document).keypress(function(e) {
    if(e.which == 13) {
       sendToBackend();
    }
});

function sendToBackend(){

 var message = $('#btn-input').val();
    document.getElementById('btn-input').value = ""
    $( ".panel-body" ).append('<div class="row msg_container base_sent"> <div class="col-md-10 col-xs-10"><div class="messages msg_sent"><p>' + message + '</p><time datetime="2009-11-13T20:00">Anonymous</time></div></div><div class="col-md-2 col-xs-2 avatar"><img src="https://steemit-production-imageproxy-upload.s3.amazonaws.com/DQmRMMdSnj3AyxttsqijcGXFPjBVMYr1TekkuJrJQfjCLX9" class=" img-responsive "></div></div>');
    var url = 'http://174.138.2.82/message';
    var data = {userMessage: message};

    fetch(url, {
      method: 'POST', // or 'PUT'
      body: JSON.stringify(data),
      headers: new Headers({
      'Content-Type': 'application/json'
      }),
      credentials: 'include'

    }).then(function(response) { return response.json(); })
  .then(function(data) {
    //for (var i = 0; i < data.products.length; i++) {
    //  var listItem = document.createElement('li');
    //  listItem.innerHTML = '<strong>' + data.products[i].Name + '</strong> can be found in ' +
     //                      data.products[i].Location +
      //                     '. Cost: <strong>£' + data.products[i].Price + '</strong>';
      //myList.appendChild(listItem);
//   alert(data.name);
 $( ".panel-body" ).append('<div class="row msg_container base_receive"><div class="col-md-2 col-xs-2 avatar"><img src="http://www.pinoystop.org/wp-content/uploads/2013/04/images-kiwi-bird-png.png" class=" img-responsive "></div><div class="col-md-10 col-xs-10"><div class="messages msg_receive"><p>'+ data+ '</p><time datetime="2009-11-13T20:00">Kiwi</time></div></div></div>');
   })

}

$(document).on('click', '#btn-chat', function (e) {
 sendToBackend()  
});



//.then(res => res.json())
//    .catch(error => console.error('Error:', error))
//    .then(response => console.log('Success:', response));
//});


$(document).on('click', '.icon_close', function (e) {
    //$(this).parent().parent().parent().parent().remove();
    $( "#chat_window_1" ).remove();
});

$(document).on('click', '#new_chat', function (e) {
    var size = $( ".chat-window:last-child" ).css("margin-left");
     size_total = parseInt(size) + 400;
    alert(size_total);
    var clone = $( "#chat_window_1" ).clone().appendTo( ".container" );
    clone.css("margin-left", size_total);
});


