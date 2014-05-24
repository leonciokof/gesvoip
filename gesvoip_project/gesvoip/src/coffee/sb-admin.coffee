$ ->
  $("#side-menu").metisMenu()

$ ->
  $(window).bind "load resize", ->
    if $(this).width() < 768
      $("div.sidebar-collapse").addClass "collapse"
    else
      $("div.sidebar-collapse").removeClass "collapse"
