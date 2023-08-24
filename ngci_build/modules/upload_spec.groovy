import groovy.json.JsonOutput

def pre(name) {
    if (! env."${name}_build_result" ){
        error "Build result for upload is not defined"
    }
    return true
}
def run_step(name) {
    try {

        def upload_spec_map = [:]
        env.UPLOAD_SPEC_FILE = "${WORKSPACE}/upload_spec.json"
        upload_tar_name = env."${name}_build_result"
        target_dir = "${env.COMPONENT_REPO}".split("/")[-1].replace(".git", "")
        upload_spec_map["files"] = [[pattern : "${upload_tar_name}", target : "sw-nbu-sws-air-generic-local/${target_dir}/${env.TAG_CANDIDATE_NAME}/", flat : "true"]]
        def json_content = JsonOutput.toJson(upload_spec_map)
        json_content_beauty = JsonOutput.prettyPrint(json_content)
        print "upload_spec content"
        print json_content_beauty
        writeFile file: "${env.UPLOAD_SPEC_FILE}", text: json_content_beauty
        print "File ${env.UPLOAD_SPEC_FILE}"
        NGCITools().ciTools.run_sh("cat ${env.UPLOAD_SPEC_FILE}")
        return true
    } catch (Throwable exc) {
        NGCITools().ciTools.set_error_in_env(exc, "user", name)
        return false
    }
}


def cleanup(name) {
    return true
}

def headline(name) {
    return "${name} " + env."${name}_status"
}


def summary(name) {
    if (env."${name}_status" != "Success") {
        return env."${name}_status" + " - exception: " + env."${name}_error"
    } else {
        return env."${name}_status"
    }
}

return this

