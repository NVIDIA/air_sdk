boolean pre(name) {
    return true
}


boolean run_step(name) {
    try {

        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        def cmd= "${WORKSPACE}/devops_tools/ngci_build/jf-dist/dist.sh"
        print "==> Execute script '${cmd}' from ${sourceDir}"



        dir (sourceDir) {
            def secrets = NGCITools().ciTools.getVaultSecret("nvidia/nbu/sws/ngci/kv/artifactory", ["RT_PASSWORD": "api-token"])
            withVault([configuration: NGCITools().vaultConfiguration, vaultSecrets: secrets]) {

                NGCITools().ciTools.run_sh("${cmd}")
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
