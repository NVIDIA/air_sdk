boolean pre(name) {
    return true
}


boolean run_step(name) {
    try {
        /*
         * It takes some time for the docker daemon to start
         */
        NGCITools().ciTools.run_sh("sleep 30")
        NGCITools().ciTools.run_sh("docker version")

        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        //sleep(300)

        dir(sourceDir) {
            NGCITools().ciTools.run_sh("docker build --network host --pull -t ${env."${name}_IMAGE"} .")
        }
        NGCITools().ciTools.run_sh("docker image ls")
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
