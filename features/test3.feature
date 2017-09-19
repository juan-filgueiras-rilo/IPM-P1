Feature: Hello world in python
    In order to check if you completed the third part of the TGR
    As a wise person
    I want to check if you have done all the tasks

    Scenario: File is under version control
        Given I have a local repository in the current directory
        When I list the files under version control
        Then I view that "holamundo.py" is under version control

    Scenario: Gtk window is implemented
        Given I have found a file named "holamundo.py" in the local repository
        When I run "holamundo.py"
        Then I view that the app has a Gtk Window with the title "Hola mundo"
