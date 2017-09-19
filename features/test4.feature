Feature: More tags in Git
    In order to check if you completed the fourth part of the TGR
    As a wise person
    I want to check if you have done all the tasks

    Scenario: Second tag
        Given I have cloned the repository in a temporary path
        When I list the tags
        Then I find "task2" in the list of tags

    Scenario: Contents of the second tag
        Given I have cloned the repository in a temporary path
        When I checkout the tag "task2"
        Then I find a file named "holamundo.py"

    Scenario: The tag contains an app with a GtkWindow
        Given I find a file named "holamundo.py"
        When I run "holamundo.py" in the temporary path
        Then I view that the app has a Gtk Window with the title "Hola mundo"
