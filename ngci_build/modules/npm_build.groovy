boolean pre(name) {
    boolean flag = true

    if (! env."${name}_npm_run" ){
        env."${name}_npm_run" = ""
    }
    if (! env."${name}_npm_audit" ){
        env."${name}_npm_audit" = ""
    }

    if (env."${name}_coverage_report" && env."${name}_coverage_report" == "true") {
        env."${name}_coverage_report" = "true"
    } else {
        env."${name}_coverage_report" = "false"
    }
    if ( ! env."${name}_publish_html_dir" ){
        env."${name}_publish_html_dir" = ""
    }
    if ( ! env."${name}_publish_html_files" ){
        // * - Publish All files in the given directory
        env."${name}_publish_html_files" = "*"
    }

    return flag
}


boolean run_step(name) {
    try {

        def branch    = env.gitlabTargetBranch ? env.gitlabTargetBranch : env.BRANCH_NAME

        def repo = (env.gitlabTargetRepoHttpUrl) ? gitlabTargetRepoHttpUrl : "${COMPONENT_REPO}"
        def component = repo.split('/')[-1].replace(".git", "")

        def execScript = (env."${name}_exec_script") ? env."${name}_exec_script" : ""
        def coverageThreshhold = (env."${name}_coverage_threshold") ? env."${name}_coverage_threshold" : env.AIR_COVERAGE_THRESHOLD
        def coverageReport   = env."${name}_coverage_report"

        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        def commands_str = (env."${name}_commands") ? env."${name}_commands" : ""
        def result_dir = (env."${name}_result_dir") ? env."${name}_result_dir" : "dist"

        if (!commands_str){
            error "Build commands are not defined. Please check"
        }
        def commands = commands_str.split(",")
        dir(sourceDir) {
            if (execScript){
                print "==> Execute script ${execScript}"
                NGCITools().ciTools.run_sh(" ${execScript}")
            }
            // support for standard ANSI escape sequences
            ansiColor('css') {
                 commands.each{cmd ->
                    cmd = cmd.trim()
                    println "${cmd}"
                    print "==> Run: ${cmd}"
                    NGCITools().ciTools.run_sh("${cmd}")
                }
                if (env."${name}_tar_result" && env."${name}_tar_result" == "true"){
                    // Create tar from the result directory
                    def tar_cmd = "tar -czvf ${env.TAG_CANDIDATE_NAME}.tar.gz -C ${result_dir}/ ."
                    NGCITools().ciTools.run_sh("${tar_cmd}")
                    NGCITools().ciTools.run_sh("ls -la")
                }
                if (coverageReport.toBoolean()) {
                    /*
                 * generates code coverage report
                */
                    def air_tools = NGCITools().ciTools.load_project_lib("${WORKSPACE}/devops_tools/${env.AIR_TOOLS_SCRIPT}")
                    def coverage_output = "${WORKSPACE}/npm_coverage_output.txt"
                    def coverage_report = readFile(file: "${coverage_output}")
                    print "COVERAGE REPORT"
                    print coverage_report
                    def coverage_percentage =  air_tools.get_coverage_percentage(coverage_report, "Lines")
                    print "Coverage percentage is ${coverage_percentage}"
                    if (!air_tools.check_coverage_threshold(coverage_percentage, coverageThreshhold)){
                        error "ERROR: Coverage below accepted threshold ${coverageThreshhold}!"
                    } else {
                        print "Coverage Threshold passed (${coverageThreshhold}%)"
                    }
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
