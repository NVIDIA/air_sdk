def pre(name) {
    return true
}


def run_step(name) {
    try {
        NGCITools().ciTools.run_sh("pwd")

        def desc = "${env.TAG_CANDIDATE_NAME}, Branch: ${env.BRANCH_NAME}"
        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."
        print "==> sourceDir : ${sourceDir}"

        dir(sourceDir) {

            def git_remote_str = (NGCITools().ciTools.run_sh_return_output("git remote -v | grep push")).split("\\s+")[1]
            NGCITools().ciTools.run_sh("git tag ${env.TAG_CANDIDATE_NAME} -m \"${desc}\" ")

            withCredentials([usernamePassword(credentialsId: "gitlab-user-token", passwordVariable: 'GIT_CREDENTIALS', usernameVariable: 'GIT_USER')]) {
                def git_remote = git_remote_str.replace("://", "://${GIT_USER}:${GIT_CREDENTIALS}@")
                NGCITools().ciTools.run_sh("git push ${git_remote} ${env.TAG_CANDIDATE_NAME}")
            }
        }

        return true
    }
    
    catch (Throwable ex) {
        NGCITools().ciTools.set_error_in_env(ex, "user", name)
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
