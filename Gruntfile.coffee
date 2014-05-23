module.exports = (grunt) ->

  grunt.initConfig

    pkg: grunt.file.readJSON "package.json"

    app: "app"
    config: "config"
    src:
      coffee: "src/coffee"
      js: "gesvoip_project/gesvoip/src/js"
      css: "gesvoip_project/gesvoip/src/css"
      images: "src/images"
    public:
      js: "gesvoip_project/gesvoip/static/gesvoip/js"
      css: "gesvoip_project/gesvoip/static/gesvoip/css"
      fonts: "gesvoip_project/gesvoip/static/gesvoip/fonts"
      images: "public/images"
    bower: "bower_components"

    coffeelint:
      gruntfile:
        src: [
          "Gruntfile.coffee"
        ]
      server:
        src: [
          "server.coffee"
          "<%= app %>/**/*.coffee"
          "<%= config %>/**/*.coffee"
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
            "<%= bower %>/humanize/humanize.js"
            "<%= bower %>/momentjs/moment.js"
            "<%= src.js %>/plugins/jquery.dataTables.js"
            "<%= src.js %>/plugins/dataTables.bootstrap.js"
            "<%= src.js %>/plugins/sb-admin.js"
            "<%= src.js %>/*.js"
          ]

    clean:
      js: ["<%= src.js %>/*.js"]

    cssmin:
      css:
        src: [
          "<%= bower %>/bootstrap/dist/css/bootstrap.css"
          "<%= bower %>/font-awesome/css/font-awesome.css"
          "<%= src.css %>/dataTables.bootstrap.css"
          "<%= src.css %>/sb-admin.css"
        ]
        dest: "<%= public.css %>/combined.min.css"

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
        ,
          src: "<%= src.js %>/plugins/datatables.spanish.json"
          dest: "<%= public.js %>/datatables.spanish.json"
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
      gruntfile:
        files: ["Gruntfile.coffee"]
        tasks: ["build"]
      coffee_server:
        files: [
          "server.coffee"
          "<%= app %>/**/*.coffee"
          "<%= config %>/**/*.coffee"
        ]
        tasks: ["coffeelint:server"]
        options:
          livereload: true
      coffee_client:
        files: ["<%= src %>/*.coffee"]
        tasks: ["coffeelint:client", "coffee", "uglify", "clean"]
        options:
          livereload: true
      jade:
        files: ["<%= app %>/views/**"]
        options:
          livereload: true
      css:
        files: ["<%= src.css %>/*.css"]
        tasks: ["cssmin"]
        options:
          livereload: true
      images:
        files: ["<%= src.images %>**"]
        tasks: ["newer:imagemin"]
        options:
          livereload: true

    nodemon:
      dev:
        script: "server.coffee"
        options:
          args: ["--debug"]
          ignore: ["public/**"]
          ext: "js,coffee"
          delayTime: 1
          env:
            NODE_ENV: process.env.NODE_ENV
            PORT: process.env.PORT
            SERVER_IP: process.env.SERVER_IP
            CHECK_MAC: process.env.CHECK_MAC
            LOGS: process.env.LOGS
            SECRET: process.env.SECRET
            PAID_URL: process.env.PAID_URL
            MANDRILL_USER: process.env.MANDRILL_USER
            MANDRILL_API_KEY: process.env.MANDRILL_API_KEY
            ADMIN_EMAIL: process.env.ADMIN_EMAIL
          cwd: __dirname

    concurrent:
      tasks: ["nodemon", "watch"]
      options:
        logConcurrentOutput: true

    shell:
      loadFixtures:
        options:
          stdout: true
        command: "./node_modules/coffee-script/bin/coffee fixtures.coffee"

  grunt.loadNpmTasks "grunt-coffeelint"
  grunt.loadNpmTasks "grunt-contrib-coffee"
  grunt.loadNpmTasks "grunt-contrib-uglify"
  grunt.loadNpmTasks "grunt-contrib-clean"
  grunt.loadNpmTasks "grunt-contrib-cssmin"
  grunt.loadNpmTasks "grunt-contrib-copy"
  grunt.loadNpmTasks "grunt-contrib-imagemin"
  grunt.loadNpmTasks "grunt-contrib-watch"
  grunt.loadNpmTasks "grunt-nodemon"
  grunt.loadNpmTasks "grunt-concurrent"
  grunt.loadNpmTasks "grunt-shell"
  grunt.loadNpmTasks "grunt-newer"

  grunt.registerTask "default", ["build", "concurrent"]
  grunt.registerTask "build", [
    "coffeelint"
    "coffee"
    "uglify"
    "clean"
    "cssmin"
    "copy"
    "newer:imagemin"
  ]
