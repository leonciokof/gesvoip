module.exports = (grunt) ->

  grunt.initConfig

    pkg: grunt.file.readJSON "package.json"

    src:
      coffee: "gesvoip_project/gesvoip/src/coffee"
      js: "gesvoip_project/gesvoip/src/js"
      css: "gesvoip_project/gesvoip/src/css"
      stylus: "gesvoip_project/gesvoip/src/stylus"
      images: "gesvoip_project/gesvoip/src/images"
    public:
      js: "gesvoip_project/gesvoip/static/gesvoip/js"
      css: "gesvoip_project/gesvoip/static/gesvoip/css"
      fonts: "gesvoip_project/gesvoip/static/gesvoip/fonts"
      images: "gesvoip_project/gesvoip/static/gesvoip/images"
    bower: "bower_components"

    coffeelint:
      gruntfile:
        src: [
          "Gruntfile.coffee"
        ]
      client:
        src: [
          "<%= src %>/*.coffee"
        ]

    coffee:
      build:
        files: [
          expand: true
          cwd: "<%= src.coffee %>"
          src: ["*.coffee"]
          dest: "<%= src.js %>"
          ext: ".js"
        ]

    uglify:
      js:
        files:
          "<%= public.js %>/combined.min.js": [
            "<%= bower %>/jquery/dist/jquery.js"
            "<%= bower %>/bootstrap/dist/js/bootstrap.js"
            "<%= bower %>/metisMenu/jquery.metisMenu.js"
            "<%= bower %>/bootstrap-3-timepicker/js/bootstrap-timepicker.js"
            "<%= bower %>/moment/moment.js"
            "<%= bower %>/eonasdan-bootstrap-datetimepicker/" +
            "build/js/bootstrap-datetimepicker.min.js"
            "<%= src.js %>/*.js"
          ]

    stylus:
      compile:
        files: [
          expand: true
          cwd: "<%= src.stylus %>"
          src: ["*.styl"]
          dest: "<%= src.css %>"
          ext: ".css"
        ]

    cssmin:
      css:
        src: [
          "<%= bower %>/bootstrap/dist/css/bootstrap.css"
          "<%= bower %>/font-awesome/css/font-awesome.css"
          "<%= bower %>/bootstrap-3-timepicker/css/bootstrap-timepicker.css"
          "<%= bower %>/eonasdan-bootstrap-datetimepicker/" +
          "build/css/bootstrap-datetimepicker.css"
          "<%= src.css %>/*.css"
        ]
        dest: "<%= public.css %>/combined.min.css"

    clean:
      js: ["<%= src.js %>/*.js"]
      css: ["<%= src.css %>/*.css"]

    copy:
      main:
        files: [
          cwd: "<%= bower %>/bootstrap/fonts"
          src: ["**"]
          dest: "<%= public.fonts %>"
          expand: true
        ,
          cwd: "<%= bower %>/font-awesome/fonts"
          src: ["**"]
          dest: "<%= public.fonts %>"
          expand: true
        ]

    imagemin:
      png:
        options:
          optimizationLevel: 7
          pngquant: true
        files: [
          expand: true,
          cwd: "<%= src.images %>"
          src: ["**/*.png"]
          dest: "<%= public.images %>"
          ext: ".png"
        ]
      jpg:
        options:
          progressive: true
        files: [
          expand: true
          cwd: "<%= src.images %>"
          src: ["**/*.jpg"]
          dest: "<%= public.images %>"
          ext: ".jpg"
        ]

    watch:
      options:
        livereload: true
      gruntfile:
        files: ["Gruntfile.coffee"]
        tasks: ["build"]
      coffee:
        files: ["<%= src.coffee %>/*.coffee"]
        tasks: ["coffeelint:client", "coffee", "uglify", "clean:js"]
      stylus:
        files: ["<%= src.stylus %>/*.styl"]
        tasks: ["stylus", "cssmin", "clean:css"]
      images:
        files: ["<%= src.images %>**"]
        tasks: ["newer:imagemin"]

    concurrent:
      tasks: ["watch"]
      options:
        logConcurrentOutput: true

  grunt.loadNpmTasks "grunt-coffeelint"
  grunt.loadNpmTasks "grunt-contrib-coffee"
  grunt.loadNpmTasks "grunt-contrib-uglify"
  grunt.loadNpmTasks "grunt-contrib-stylus"
  grunt.loadNpmTasks "grunt-contrib-cssmin"
  grunt.loadNpmTasks "grunt-contrib-clean"
  grunt.loadNpmTasks "grunt-contrib-copy"
  grunt.loadNpmTasks "grunt-contrib-imagemin"
  grunt.loadNpmTasks "grunt-contrib-watch"
  grunt.loadNpmTasks "grunt-concurrent"
  grunt.loadNpmTasks "grunt-newer"

  grunt.registerTask "default", ["build", "concurrent"]
  grunt.registerTask "build", [
    "coffeelint"
    "coffee"
    "uglify"
    "stylus"
    "cssmin"
    "clean"
    "copy"
    "newer:imagemin"
  ]
