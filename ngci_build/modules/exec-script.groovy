boolean pre(name) {

    boolean flag = true

    if (! env."${name}_exec_script" ){
        NGCILogger.error("Mandatory parameter 'exec_script' is missing", this.getClass().getSimpleName())
        flag = false
    }


    return flag

}


boolean run_step(name) {
    try {

        def script             = env."${name}_exec_script"
        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        dir (sourceDir) {
            NGCITools().ciTools.run_sh("${script}")
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
