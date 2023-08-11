def pre(name) {
    return true
}


def run_step(name) {
    try {
        env.ENV = "development"
        env.DB_HOST = "127.0.0.1"
        env.DB_PASSWORD = 'Disengage^UnburnedGrading0LashObedience'
        env.DB_USERNAME = "root"
        env.SECRET_KEY = 'Party6Polyester!CarlessEtherAlone'
        env.AIR_API = 'http://localhost:8000/api/v1/'
        env.AIR_API_EXT = 'http://localhost:8000/api/v1/'
        env.AIR_USERNAME='foo'
        env.AIR_PASSWORD='bar'
        env.SIGNING_KEY='Ensnare@Excavate6LappedReawakeSeltzer'
        env.SMTP_USERNAME='foo'
        env.SMTP_PASSWORD='bar'

        NGCITools().ciTools.run_sh("env")
        //NGCITools().ciTools.run_sh("sleep 3600")
        dir("${WORKSPACE}/cadet/api"){
            NGCITools().ciTools.run_sh("pip3 install .; pip3 install .[dev]")
            NGCITools().ciTools.run_sh("coverage run --omit='*/tests.py,app/settings.py,app/*sgi.py,manage.py,util/test/*' --source='.' manage.py test --noinput")
        }
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

