boolean pre(name) {

    boolean flag = true
    if ( ! env."${name}_pip_install" ){
        env."${name}_pip_install" = ""
    }

    if (env."${name}_coverage_report" && env."${name}_coverage_report" == "true") {
        env."${name}_coverage_report" = "true"
    } else {
        env."${name}_coverage_report" = "false"
    }

    if ( ! env."${name}_publish_html_dir" ){
        env."${name}_publish_html_dir" = ""
    }

    if ( ! env."${name}_source_dir" ){
        env."${name}_source_dir" = "."
    }

    /*
     * hold execution by adding sleep ( for debug purpose )
     */
    if ( ! env."${name}_sleep_sec" ){
        env."${name}_sleep_sec" = ""
    }

    if ( ! env."${name}_publish_html_files" ){
        // * - Publish All files in the given directory
        env."${name}_publish_html_files" = "*"
    }
    if (! env."${name}_cmd" ){
        NGCILogger.error("module's parameter 'cmd' is missing", this.getClass().getSimpleName())
        flag = false
    }

    return flag
}


def run_step(name) {
    try {
        def pipInstall       = env."${name}_pip_install"
        def cmd              = env."${name}_cmd"
        def coverageReport   = env."${name}_coverage_report"
        def publishHtmlDir   = env."${name}_publish_html_dir"
        def publishHtmlFiles = env."${name}_publish_html_files"
        def sleepSec         = env."${name}_sleep_sec"
        def reportName= (env."${name}_report_name") ? env."${name}_report_name" : "Coverage Report"
        def coverageThreshhold = (env."${name}_coverage_threshold") ? env."${name}_coverage_threshold" : env.AIR_COVERAGE_THRESHOLD

        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        /*
         * build properties are not available in the container
         */
        dir (sourceDir) {
            NGCITools().ciTools.run_sh("pwd")

            if  ( env.LOG_LEVEL == 'DEBUG' ){
                NGCITools().ciTools.run_sh("env|sort")
            }

            if (pipInstall) {
                NGCITools().ciTools.run_sh("pip install ${pipInstall}")
            }

            NGCITools().ciTools.run_sh("pip freeze")

            if (sleepSec) {
                sleep(sleepSec)
            }
            NGCITools().ciTools.run_sh("${cmd}")

            if (coverageReport.toBoolean()) {
                /*
             * generates code coverage report
            */
                def coverage_output = "${WORKSPACE}/${PYTHON_COVERAGE_OUTPUT}"
                def air_tools = NGCITools().ciTools.load_project_lib("${WORKSPACE}/${CLONE_PATH}/${env.AIR_TOOLS_SCRIPT}")
                NGCITools().ciTools.run_sh("coverage report -m | tee ${coverage_output} && coverage html")
                print "FILE CONTENT"
                NGCITools().ciTools.run_sh("cat ${coverage_output}")
                def coverage_report = readFile(file: "${coverage_output}")
                print "COVERAGE REPORT"
                print coverage_report
                def coverage_percentage =  air_tools.get_coverage_percentage(coverage_report, "total")
                print "Coverage percentage is ${coverage_percentage}"
                if (!air_tools.check_coverage_threshold(coverage_percentage, coverageThreshhold)){
                    error "ERROR: Coverage below accepted threshold ${coverageThreshhold}!"
                } else {
                    print "Coverage Threshold passed (${coverageThreshhold}%)"
                }
                if (publishHtmlDir) {
                    publishHTML(target: [allowMissing         : true,
                                         alwaysLinkToLastBuild: false,
                                         reportDir            : "${publishHtmlDir}",
                                         keepAll              : true,
                                         reportFiles          : "${publishHtmlFiles}",
                                         reportName           : "${reportName}",
                                         escapeUnderscores    : false,
                                         reportTitles         : "The Coverage Report"])
                }
            }
        }
        return true

    } catch (Throwable exc) {
        NGCITools().ciTools.set_error_in_env(exc, "devops", name)
        return false
    }
}


boolean cleanup(name) {
    return true
}

def headline(name) {
    return "${name} " + env."${name}_status"
}

def summary(name) {
    if (env."${name}_status" == "Failure") {
        return "exception: " + env."${name}_status"
    } else {
        return env."${name}_status"
    }
}


return this
