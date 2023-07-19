package com.mellanox.jenkins
import java.util.regex.Pattern

def get_coverage_percentage(coverage_report, regex_key){
    def line_pattern = "${regex_key}.+?(\\d+)(?:\\.\\d+)?%"
    def pattern = Pattern.compile(line_pattern, Pattern.CASE_INSENSITIVE)
    def line_match = pattern.matcher(coverage_report)
    def line = line_match.find() ? line_match.group(0) : ""
    print line
    if (line) {
        //Get the percentage value
        def coverage_percentage  = line_match.group(1)
        print coverage_percentage
        return coverage_percentage
    } else {
        error "Cannot get coverage report file ${coverage_report}"
    }
}

def check_coverage_threshold(coverage_percentage, coverage_threshold){
    //true if coverage more than coverage_threshold
    return coverage_percentage.toInteger() > coverage_threshold.toInteger() ? true : false
}



return this
