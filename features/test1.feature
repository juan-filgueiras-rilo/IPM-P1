Feature: First steps with git
    In order to check if you completed the first part of the TGR
    As a wise person
    I want to check if you have done all the tasks

    Scenario: First commit
        Given I have a local repository in the current directory
        When I check the git logs
        Then I view some commits

    Scenario: Remote repository
        Given I have a local repository in the current directory
        When I check if there is a remote repository
        Then I view the url of the remote repository

    Scenario: First push
        Given I have a remote repository linked to the local repository
        When I clone the remote repository in a temporary path
        Then I view the same commits than in the local version
