const gulp = require("gulp");

const css = () => {
    const postCSS = require("gulp-postcss");
    const sass = require("gulp-sass")(require("sass"));
    const minify = require("gulp-csso");
    sass.compiler = require("node-sass");
    return gulp
        .src("assets/scss/styles.scss") // just find the folder's route
        .pipe(sass().on("error", sass.logError))
        .pipe(postCSS([
            require("tailwindcss"),
            require("autoprefixer")
        ]))
        .pipe(minify()) // minimize code
        .pipe(gulp.dest("static/css")); // send result
};

exports.default = css;