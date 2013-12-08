$.easing.drop = function (x,t,b,c,d){
    return -c * (Math.sqrt(1-(t/=d)*t) -1)+b;
}

$(".darken").hover(
  function(){
    $(this).css('color', '#3B4A59');
  },
  function(){
    $(this).css('color', '#E5E9EE');
  }
)

$("span.class").hover(
  function(){
    $(this).css('border', 'black');
  },
  function(){
    $(this).css('border', '#B5BEC4');
  }
)

$(".portfolio-circle").hover(
    function(){
      $(this).find(".circle-underlay").stop().animate({left:'50%'}, 5000);
    },
    function(){
      $(this).find(".circle-underlay").stop().animate({'left': "0"}, 5000);
    }
)
$(".portfolio-circle-vert").hover(
    function(){
      $(this).find(".circle-underlay").stop().animate({marginTop:'100%'}, 5000);
    },
    function(){
      $(this).find(".circle-underlay").stop().animate({marginTop: "-100%"}, 5000);
    }
)
function relative_time(time_value) {
  var values = time_value.split(" ");
  time_value = values[1] + " " + values[2] + ", " + values[5] + " " + values[3];
  var parsed_date = Date.parse(time_value);
  var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
  var delta = parseInt((relative_to.getTime() - parsed_date) / 1000);
  delta = delta + (relative_to.getTimezoneOffset() * 60);

  var r = '';
  if (delta < 60) {
        r = 'a minute ago';
  } else if(delta < 120) {
        r = 'couple of minutes ago';
  } else if(delta < (45*60)) {
        r = (parseInt(delta / 60)).toString() + ' minutes ago';
  } else if(delta < (90*60)) {
        r = 'an hour ago';
  } else if(delta < (24*60*60)) {
        r = '' + (parseInt(delta / 3600)).toString() + ' hours ago';
  } else if(delta < (48*60*60)) {
        r = '1 day ago';
  } else {
        r = (parseInt(delta / 86400)).toString() + ' days ago';
  }
      return r;
  }
  
 
// Initialize the form 
function init_form() {
 
  // Hide the form initially.
  // Make submitForm() the form’s submit handler.
  // Position the form so it sits in the centre of the browser window.
  //$('#contactForm').hide().submit( submitForm ).addClass( 'positioned' );
 
  // When the "Send us an email" link is clicked:
  // 1. Fade the content out
  // 2. Display the form
  // 3. Move focus to the first field
  // 4. Prevent the link being followed
 
  $('a[href="#contactForm"]').click( function() {
    $('#content').fadeTo( 'slow', .2 );
    $('#contactForm').fadeIn( 'slow', function() {
      $('#senderName').focus();
    } )
  });
    
    
  // When the "Cancel" button is clicked, close the form
  $('#cancel').click( function() { 
    $('#contactForm').fadeOut();
    $('#content').fadeTo( 'slow', 1 );
  } );  
 
  // When the "Escape" key is pressed, close the form
  $('#contactForm').keydown( function( event ) {
    if ( event.which == 27 ) {
      $('#contactForm').fadeOut();
      $('#content').fadeTo( 'slow', 1 );
    }
  } );
 
}
// Submit the form via Ajax
 
function submitForm() {
  var contactForm = $(this);
 
  // Are all the fields filled in?
 
  if ( !$('#senderName').val() || !$('#senderEmail').val() || !$('#message').val() ) {
 
    // No; display a warning message and return to the form
    $('#incompleteMessage').fadeIn().delay(messageDelay).fadeOut();
    contactForm.fadeOut().delay(messageDelay).fadeIn();
 
  } else {
 
    // Yes; submit the form to the PHP script via Ajax
 
    $('#sendingMessage').fadeIn();
    contactForm.fadeOut();
 
    $.ajax( {
      url: contactForm.attr( 'action' ) + "?ajax=true",
      type: contactForm.attr( 'method' ),
      data: contactForm.serialize(),
      success: submitFinished
    } );
  }
 
  // Prevent the default form submission occurring
  return false;
}
// Handle the Ajax response
 
function submitFinished( response ) {
  response = $.trim( response );
  $('#sendingMessage').fadeOut();
 
  if ( response == "success" ) {
 
    // Form submitted successfully:
    // 1. Display the success message
    // 2. Clear the form fields
    // 3. Fade the content back in
 
    $('#successMessage').fadeIn().delay(messageDelay).fadeOut();
    $('#senderName').val( "" );
    $('#senderEmail').val( "" );
    $('#message').val( "" );
 
    $('#content').delay(messageDelay+500).fadeTo( 'slow', 1 );
 
  } else {
 
    // Form submission failed: Display the failure message,
    // then redisplay the form
    $('#failureMessage').fadeIn().delay(messageDelay).fadeOut();
    $('#contactForm').delay(messageDelay+500).fadeIn();
  }
}

  // Init the form once the document is ready
$( init_form );