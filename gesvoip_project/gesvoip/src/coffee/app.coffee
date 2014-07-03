$(document).ready ->
  $(".timepicker").timepicker
    showSeconds: true
    showMeridian: false
    defaultTime: false

  $(".datepicker").datetimepicker
    pickTime: false

  $(".select2").select2()
