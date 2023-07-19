def pre(name) {
    return true
}


def run_step(name) {
    try {
        NGCITools().ciTools.run_sh("pwd && env")

        def branch = env.gitlabTargetBranch ? env.gitlabTargetBranch : env.BRANCH_NAME
        def sourceDir = (env."${name}_source_dir") ? env."${name}_source_dir" : "."

        print "==> sourceDir : ${sourceDir}"

        /*
         * build docker for main or develop
        */
        if ( branch == "main" || branch == "develop" ){
            env.SKIP_DOCKER_BUILD=false
        }else{
            env.SKIP_DOCKER_BUILD=true
        }


        print "SKIP_DOCKER_BUILD : ${env.SKIP_DOCKER_BUILD} ,[ only build for develop and main branches] "

        dir(sourceDir) {
            if (!env.FORMAL_VERSION) {
                def tag_prefix = "${env.BRANCH_NAME}_"
                print "Tag prefix is ${tag_prefix}"
                try {
                    print "Getting previous tag..."
                    prev_tag = NGCITools().ciTools.get_last_tag("^${tag_prefix}")
                    print "Previous tag found - '${prev_tag}'"
                    def old_build_num
                    if (prev_tag =~ /\-\d{3}$/) {
                        old_build_num = prev_tag.split("-")[-1]
                        version = prev_tag.replace("-${old_build_num}", "-")
                        env.FORMAL_VERSION = version + ((old_build_num.toInteger() + 1).toString()).padLeft(3, "0")
                    } else {
                        env.FORMAL_VERSION = prev_tag + "-001"
                    }
                    print "FORMAL VERSION is ${env.FORMAL_VERSION}"
                } catch (Throwable tag_exc) {
                    print "Previous tag not found"
                    error "Define FORMAL_VERSION in the build"
                }
            } else {
                def tag = "${env.BRANCH_NAME}_${env.FORMAL_VERSION}"
                def git_tag_exist_check = NGCITools().ciTools.run_sh_return_output_without_console("git tag -l ${tag}*")
                if (git_tag_exist_check.contains("${tag}")) {
                    error "Version ${env.FORMAL_VERSION} already defined"
                } else {
                    env.FORMAL_VERSION = "${env.BRANCH_NAME}_${env.FORMAL_VERSION}-001"
                    print "FORMAL VERSION is ${env.FORMAL_VERSION}"
                }
            }
        }
        env.TAG_CANDIDATE_NAME = env.FORMAL_VERSION
        print "Using tag candidate - '${env.TAG_CANDIDATE_NAME}'"
        return true
    } catch (Throwable exc) {
        NGCITools().ciTools.set_error_in_env(exc, "devops", name)
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
    if (env."${name}_status" == "Failure") {
        return "exception: " + env."${name}_status"
    } else {
        return env."${name}_status"
    }
}


return this