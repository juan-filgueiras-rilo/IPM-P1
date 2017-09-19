Feature: Tags with git
    In order to check if you completed the second part of the TGR
    As a wise person
    I want to check if you have done all the tasks

    Scenario: First tag
        Given I have cloned the repository in a temporary path
        When I list the tags
        Then I find "task1" in the list of tags

    Scenario: Contents of first tag
        Given I have cloned the repository in a temporary path
        When I checkout the tag "task1"
        Then I find a file named "nombres.txt"

    Scenario: Contents of file
        Given I have found a file named "nombres.txt" in the tag "task1"
        When I check the contents of "nombres.txt"
        Then I view that each line contains a string, a comma and a string
