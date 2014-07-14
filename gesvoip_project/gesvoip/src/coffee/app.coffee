$(document).ready ->
  $(".timepicker").timepicker
    showSeconds: true
    showMeridian: false
    defaultTime: false
    minuteStep: 1
    secondStep: 1

  $(".datepicker").datetimepicker
    pickTime: false

  $(".select2").select2()
