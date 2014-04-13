gulp = require 'gulp'
gutil = require 'gulp-util'

coffee = require 'gulp-coffee'
concat = require 'gulp-concat'
sass = require 'gulp-sass'
ngmin = require 'gulp-ngmin'
html2js = require 'gulp-ng-html2js'
htmlmin = require 'gulp-htmlmin'
cssmin = require 'gulp-minify-css'
rename = require "gulp-rename"
bowerFiles = require 'gulp-bower-files'

lr = require 'tiny-lr'
livereload = require 'gulp-livereload'
server = lr()

STATIC_PATH = '/static/'

# Livereload server
gulp.task 'livereload', (next) ->
    server.listen 35729, (err) ->
        gutil.log(err)
        next()

gulp.task('coffee', ->
    gulp.src('app/**/*.coffee')
        .pipe(coffee({bare: true}).on('error', gutil.log))
        .pipe(concat('app.js'))
        .pipe(ngmin())
        .pipe(gulp.dest("#{STATIC_PATH}js/"))
        .pipe(livereload(server))
)

gulp.task('scss', ->
    gulp.src('style/main.scss')
        .pipe(sass().on('error', gutil.log))
        .pipe(cssmin({keepSpecialComments: 0}))
        .pipe(gulp.dest("#{STATIC_PATH}css"))
        .pipe(livereload(server))
)

gulp.task('html2js', ->
    gulp.src('app/**/*.template')
        .pipe(htmlmin({collapseWhitespace: true}))
        .pipe(html2js({
            moduleName:'ngTemplates'
            rename: (url) -> url.split('/').pop()}))
        .pipe(concat('templates.js'))
        .pipe(gulp.dest("#{STATIC_PATH}js/"))
        .pipe(livereload(server))
)

gulp.task('vendor', ->
    # Make sure angular is at the top of the file.
    bowerFiles()
        .pipe(concat('vendor.js'))
        .pipe(gulp.dest("#{STATIC_PATH}/js/"))
        .pipe(livereload(server))
)

gulp.task 'watch', ->
    # Watch coffee files.
    gulp.watch('app/**/*.coffee', ['coffee'])
    # Watch SCSS files.
    gulp.watch('style/**/*.scss', ['scss'])
    # Watch template files.
    gulp.watch('app/**/*.template', ['html2js'])


gulp.task('build', ['coffee', 'vendor', 'scss', 'html2js'])
gulp.task('default', ['livereload', 'build', 'watch'])