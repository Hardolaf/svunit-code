#!/usr/bin/env python3

import os
import sys
import argparse
import re
from junit-xml import TestSuite, TestCase

regexPatterns = {
            # Summary Report of all Tests
            #   Group 1: ? TODO: Name
            "summary" : "^#[\s]*INFO:[\s]*\[([\d]+)\]\[testrunner\]:[\s]*(?P<passOrFail>PASSED|FAILED)[\s]*\((?P<numberOfPassingTests>[\d]+)[\s]*of[\s]*(?P<numberOfTests>[\d]+)[\s]*suites[\s]*passing\)[\s]*\[SVUnit (?P<version>v[\d]+.[\d]+)\]",
            # Summer Report of a Test Case
            "testcaseSummary" : "^#[\s]*INFO:[\s]*\[([\d]+)\]\[(?P<testcaseName>[\S]+)\]:[\s]*(?P<passOrFail>PASSED|FAILED)[\s]*\((?P<numberOfPassingTests>[\d]+)[\s]*of[\s]*(?P<numberOfTests>[\d]+)[\s]*tests[\s]*passing\)[\s]*",
            # Test summary
            "testSummary" : "^#[\s]*INFO:[\s]*\[([\d]+)\]\[(?P<testcaseName>[\S]+)\]:[\s]*(?P<testName>[a-zA-Z0-9][a-zA-Z_0-9]*)::(?P<passOrFail>PASSED|FAILED)",
            # Test started
            "testStart" : "^#[\s]*INFO:[\s]*\[([\d]+)\]\[(?P<testcaseName>[\S]+)\]:[\s]*(?P<testName>[a-zA-Z0-9][a-zA-Z_0-9]*)::RUNNING",
            # Error Report
            "errorReport" : "^#[\s]*ERROR:[\s]*\[([\d]+)\]\[(?P<testcaseName>[\S]+)\]:[\s]*[\s]*(?P<failCause>[\w\W]+)"
        }

def main(args):

    parser = argparse.ArgumentParser(
                description="Parses a SVUnit run.log into a junit formated report."
            )
    parser.add_argument(
                "run_log",
                help="The run.log file from SVUnit",
                type=argparse.FileType('r')
            )
    parser.add_argument(
                "-o", "--outfile",
                help="junit output file",
                default=sys.stdout,
                type=argparse.FileType('w')
            )
    try:
        args = parser.parse_args(args)
    except argparse.ArgumentError as e:
        print(e)
        return -1

    # Pre-compile all regexs
    compiledPatterns = dict()
    for patternName, pattern in regexPatterns.items():
        compiledPatterns[patternName] = re.compile(pattern, re.MULTILINE)

    line = args.run_log.readline()
    cnt = 1

    def parseLine(line, compiledPatterns):
        m = compiledPatterns["summary"].match(line)

        if m != None:
            print(f"Testsuite: {m.group('passOrFail')}")
            return True

        m = compiledPatterns["testcaseSummary"].match(line)

        if m != None:
            print(f"Testcase [{m.group('testcaseName')}]: {m.group('passOrFail')}")
            return True

        m = compiledPatterns["testSummary"].match(line)

        if m != None:
            print(f"{m.group('testcaseName')}:{m.group('testName')}: {m.group('passOrFail')}")
            return True

        m = compiledPatterns["testStart"].match(line)

        if m != None:
            print(f"Started test {m.group('testcaseName')}:{m.group('testName')}")
            return True

        m = compiledPatterns["errorReport"].match(line)

        if m != None:
            print(f"Error in testcase {m.group('testcaseName')}: {m.group('failCause')}")
            return True

        print(f"No match on: {line}")
        return False

    while line:
        parseLine(line, compiledPatterns)
        line = args.run_log.readline()
        cnt += 1
    print(cnt)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

