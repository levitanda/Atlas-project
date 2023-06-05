## Initial Setup Guide
### Initialization of Backend
1. [Install the latest version of Python](https://www.python.org/downloads/).
2. [Install the latest version of Git](https://git-scm.com/downloads).
3. [Install the latest version of Visual Studio Code](https://code.visualstudio.com/download).
4. [Install the latest version of the Python extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python).
5. created a new folder for our project source code named **src**.
6. install libraries using the following command:
    ```bash
    pip install -r requirements.txt
    ```
7. create a new file named **.gitignore** in the root of our project folder to ignore redundant files from source control.(i.e **.vscode** folder and **.pyc** files,venv folder and node_modules folder)
8. in ./src/Backend/ create a new django project named **RAICAT** using the following command(don't forget to enter to root folder **src** before run the command):
    ```bash
    django-admin startproject RAICAT ./src/Backend
    ```
### Initialization of Frontend
1. [Install the latest version of Node.js](https://nodejs.org/en/download/).
2. Create new react app using the following command:
    ```bash
    npx create-react-app ./src/Frontend --template cra-template-redux
    ```
3. Install all the dependencies using the following command:
    ```bash
    cd src/frontend
    npm install
    ```
