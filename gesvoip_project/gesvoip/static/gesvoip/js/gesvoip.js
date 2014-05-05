function validatePassword2(){
  if(inputPassword1.val() != inputPassword2.val()){
    reqPassword2.addClass("error");
    inputPassword2.addClass("error");
    return false;
  }else{
    reqPassword2.removeClass("error");
    inputPassword2.removeClass("error");
    return true;
  }
}

function MM_jumpMenu(targ,selObj,restore){
  eval(targ+".location='"+selObj.options[selObj.selectedIndex].value+"'");
  if(restore){
    selObj.selectedIndex=0;
  }
}

$.fn.accordion = function(custom) {
  var defaults = {
    keepOpen: false,
    startingOpen: false
  }
  var settings = $.extend({}, defaults, custom);
  if(settings.startingOpen){
    $(settings.startingOpen).show();
  }

  return this.each(function(){
    var obj = $(this);
    $('li a', obj).click(function(event){
        var elem = $(this).next();
        if(elem.is('ul')){
          event.preventDefault();
          if(!settings.keepOpen){
            obj.find('ul:visible').not(elem).not(elem.parents('ul:visible')).slideUp();
          }
          elem.slideToggle();
        }
    });
  });
};

$(document).ready(function(){
  <!-- Funcion Calendario -->
  $( "#fechaIngreso" ).datepicker();
  $( "#fechaIngreso" ).datepicker($.datepicker.regional['es']);
  $( "#fechaIngreso" ).datepicker('option', {dateFormat: 'yy-mm-dd'});
  $( "#fechaInicio" ).datepicker();
  $( "#fechaInicio" ).datepicker($.datepicker.regional['es']);
  $( "#fechaInicio" ).datepicker('option', {dateFormat: 'yy-mm-dd'});
  $( "#fechaFin" ).datepicker();
  $( "#fechaFin" ).datepicker($.datepicker.regional['es']);
  $( "#fechaFin" ).datepicker('option', {dateFormat: 'yy-mm-dd'});
  $( "#fechaInicio1" ).datepicker();
  $( "#fechaInicio1" ).datepicker($.datepicker.regional['es']);
  $( "#fechaInicio1" ).datepicker('option', {dateFormat: 'yymmdd'});
  $( "#fechaFin1" ).datepicker();
  $( "#fechaFin1" ).datepicker($.datepicker.regional['es']);
  $( "#fechaFin1" ).datepicker('option', {dateFormat: 'yymmdd'});
  $( "#fechaFact" ).datepicker();
  $( "#fechaFact" ).datepicker($.datepicker.regional['es']);
  $( "#fechaFact" ).datepicker('option', {dateFormat: 'yymmdd'});
  $('#HorarioHabilNormalInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioHabilNormalFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioHabilReducidoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioHabilReducidoFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioHabilNocturnoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioHabilNocturnoFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoNormalInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoNormalFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoReducidoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoReducidoFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoNocturnoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioSabadoNocturnoFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoNormalInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoNormalFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoReducidoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoReducidoFin').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoNocturnoInicio').datetime({ withDate: false, format: 'hh:ii' });
  $('#HorarioFestivoNocturnoFin').datetime({ withDate: false, format: 'hh:ii', steap: 1 });

  // Valida si el RUT fue ingresado correctamente
  $('#rut').Rut({
    on_error: function(){
      alert('Rut incorrecto');
      document.ingresaCompania.rut.value = "";
    }
  });

  //variables globales
  var searchBoxes = $(".text");
  var inputUsername = $("#username");
  var reqUsername = $("#req-username");
  var inputPassword1 = $("#password1");
  var reqPassword1 = $("#req-password1");
  var inputPassword2 = $("#password2");
  var reqPassword2 = $("#req-password2");
  var inputEmail = $("#email");
  var reqEmail = $("#req-email");

  //controlamos la validacion en los distintos eventos
  // Perdida de foco
  inputPassword2.blur(validatePassword2);

  // Pulsacion de tecla
  inputPassword2.keyup(validatePassword2);

  // Envio de formulario
  $("#modificaUserPost").submit(function(){
    if(validatePassword2()){
      return true;
    }else{
      return false;
    }
  });

  $("#ingresaUser").submit(function(){
    if(validatePassword2()){
      return true;
    }else{
      return false;
    }
  });

  $('.dataTable').dataTable({
    "bPaginate": false,
    "bLengthChange": false,
    "bFilter": false,
    "bSort": false,
    "bInfo": false,
    "bAutoWidth": false,
    "oLanguage": {
      "sLengthMenu": "Ver _MENU_ registros por pagina",
      "sZeroRecords": "No se han encontrado datos",
      "sInfo": "Viendo _START_ a _END_ de _TOTAL_ registros",
      "sInfoEmpty": "Viendo 0 a 0 de 0 registros",
      "sInfoFiltered": "(filtrando de _MAX_ registros totales)",
      "sSearch": "Buscar:"
    }
  });

  $('#tabla').dataTable({
    "oLanguage": {
      "sLengthMenu": "Ver _MENU_ registros por pagina",
      "sZeroRecords": "No se han encontrado datos",
      "sInfo": "Viendo _START_ a _END_ de _TOTAL_ registros",
      "sInfoEmpty": "Viendo 0 a 0 de 0 registros",
      "sInfoFiltered": "(filtrando de _MAX_ registros totales)",
      "sSearch": "Buscar:"
    }
  });

  $('#menu').accordion({keepOpen:false, startingOpen: '#open'});

  for (i = new Date().getFullYear(); i > 2000; i--) {
    $('#year').append($('<option />').val(i).html(i));
  }
});
