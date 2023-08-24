boolean pre(name) {
    return true
}


boolean run_step(name) {
    try {
        NGCITools().ciTools.run_sh("pwd ; semgrep-agent --config p/r2c-ci")
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
