In this section, you will set up everything you need to complete the tutorial.

## Prerequisites

You should have a GitHub personal account.
See the "[Signing up for a new GitHub account][1]" page in the GitHub docs.

## Starting a new Codespace

To work through this tutorial, you will need to use Codespaces.
We have set up [a GitHub repository][2] for you to use to create a Codespace suitable for the tutorial.

??? tip "What's a Codespace?"
    A [Codespace][3] is cloud-hosted environment where you can write and run code.

    For more information, see our blog post: [Research-ready computers in the cloud[4]

To launch a new Codespace, go to [the GitHub repository][2] in your browser, click the green _Code_ button, ensure the _Codespaces_ tab is active, and click the _Create codespace on main_ button.

![A screenshot of the buttons that need to be clicked](green-buttons.png)

A new browser tab will open and you'll see a notification in the bottom right of the scrren saying "Building codespace..."

![A screenshot of the notification saying "Building codepsace..."](building-codespace.png)

After a minute or two you'll see a screen that looks like this:

![New Codespace screen](new-codespace-screen.png)

??? Warning "Firefox users may have to disable Enhanced Tracking Protection"
    If you see a message that says "Oh no, it looks like you are offline!" and you use Firefox, you will need to disable Enhanced Tracking Protection, which can be done via the shield icon to the left of the address bar:

    ![Enhanced Tracking Protection settings](enhanced-tracking-protection.png)

You can dismiss the notification in the bottom right, and close the terminal tab by clicking on the cross icon halfway up the screen on the right hand side.

To make sure everything's working correctly, open `dataset_definition.py` by clicking on it in the _Explorer_ tab on the left hand side, and then click the _Debug ehrQL_ button in the bottom right corner.

You should see a new window showing a table showing the contents of the `patients` table:

![Output from a sucessful run](successful-run.png)

If you don't see this, get in touch with the OpenSAFELY tech team via your copilot, or by emailing tech@opensafely.org.

Next: [Working with data with ehrQL](../working-with-data-with-ehrql/index.md)

[1]: https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github
[2]: https://github.com/opensafely/ehrql-tutorial/
[3]: https://docs.github.com/en/codespaces/overview
[4]: https://www.bennett.ox.ac.uk/blog/2024/07/research-ready-computers-in-the-cloud/
