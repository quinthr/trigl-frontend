$( document ).ready(function() {
  (function () {
    'use strict'
    // Example starter JavaScript for disabling form submissions if there are invalid fields
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }

          form.classList.add('was-validated')
        }, false)
      })
  })()
});

var input1IsFocused = false;
var input2IsFocused = false;
$("#inputUsername").focus( function () {
  $(".login__icon--1").addClass("login__icon--hover");
  input1IsFocused = true;
});
$("#inputUsername").blur( function () {
  $(".login__icon--1").removeClass("login__icon--hover");
  input1IsFocused = false;
});
$(".login__form--input--1").hover( function () {
  $(".login__icon--1").addClass("login__icon--hover");
}, function () {
  if (input1IsFocused == false) {
    $(".login__icon--1").removeClass("login__icon--hover");
  }
});
$("#inputPassword").focus( function () {
  $(".login__icon--2").addClass("login__icon--hover");
  input2IsFocused = true;
});
$("#inputPassword").blur( function () {
  $(".login__icon--2").removeClass("login__icon--hover");
  input2IsFocused = false;
});
$(".login__form--input--2").hover( function () {
  $(".login__icon--2").addClass("login__icon--hover");
}, function () {
  if (input2IsFocused == false) {
    $(".login__icon--2").removeClass("login__icon--hover");
  }
});
$(".login__icon--off").click( function () {
    var x = document.getElementById("inputPassword");
    x.type = "text";
    $(".login__icon--off").hide();
    $(".login__icon--on").show();
});
$(".login__icon--on").click( function () {
    var x = document.getElementById("inputPassword");
    x.type = "password";
    $(".login__icon--off").show();
    $(".login__icon--on").hide();
});
