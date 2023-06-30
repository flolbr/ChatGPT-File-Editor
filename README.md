# ChatGPT File Editor

This plugin allows you to create and edit files in a directory on your computer using ChatGPT.
_(If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).)_

The advantage of this plugin compared to similar offerings is that it is completely local.
Your project files don't need to be on a publicly available repository (as long as you trust OpenAI's privacy policy).
You also don't have to push your changes everytime you make a change.

⚠️ I would still recommend using a version control system like Git to keep track of your changes and to be able to revert them if needed.

## Setup locally

To install the required packages for this plugin, run the following command:

```bash
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "What files are in the project ?" 

## Managing projects

### Manually adding projects

The directories accessible by ChatGPT File Editor are stored in the [projects.yaml](projects.yaml) file.

To add a new project, add a new entry to the `projects` list.
- The `full_name` field is the name of the project that will be displayed in the File Editor.
- The `path` field is the path to the directory that contains the files for the project.
- The `slug` field is the name of the project that will be used in the URL for the File Editor.

### Using the dashboard

Projects can also be edited using the dashboard available at http://localhost:5003/dashboard.

Renaming and deleting does not affect the files on disk, only the `projects.yaml` file.

### Excluding files

Files can be excluded from the File Editor by adding a `.gpteditignore` file to the project directory.
The format of the `.gpteditignore` file is the same as the `.gitignore` file.

## Q & A

### How does this defer from GitHub Copilot ?

Copilot allows you to edit files on the fly, but it does not allow you to create new files or to list the files in a directory.
This plugin is able to know which files to edit based on your request.

### Is this only for code projects ?

No, this plugin can be used for any type of project.
I personally use it for slideshow presentations made with Beamer or Reveal.js.

### How do I add a new file ?

You can add a new file by asking a question like "Create a new file called `file_name`".

### How do I edit a file ?

You can edit a file by asking a question like "Edit `file_name`".

### How do I list all the files in the project ?

You can list all the files in the project by asking a question like "What files are in the project ?".

### How do I list all the files in a directory ?

You can list all the files in a directory by asking a question like "What files are in the `directory_name` directory ?".

### How do I delete a file ?

You can't delete files.
This is to prevent accidental deletion of files.
Maybe this will be added as an opt-in feature in the future.
